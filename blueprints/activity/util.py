import json
import logging
import asyncio
import random

import tiktoken
from httpx import (
    ReadTimeout,
    ConnectError,
    ConnectTimeout as HTTPXConnectTimeout
)
from httpcore import ConnectTimeout as HTTPCoreConnectTimeout
from mcp import ClientSession, McpError
from mcp.client.sse import sse_client

from config import (
    HISTORY_API_URL,
    HISTORY_API_KEY
)

async def mcp_list_tools(
    code: str, 
    mcp_server_func_name: str, 
    max_retries: int = 3, 
    initial_delay: float = 1.0
):
    """
    この関数は、指定されたMCPサーバーに接続し、利用可能なツールのリストを取得します。
    リトライ機能を備えており、接続エラーやタイムアウトが発生した場合に再試行します。
    Args:
        code (str): MCPサーバーのキー
        mcp_server_func_name (str): MCPサーバーのドメイン名
        max_retries (int): リトライの最大回数
        initial_delay (float): 初回リトライまでの待機時間（秒）
    Returns:
        response : ツールのリスト
    Raises:
        eg: 予期しないエラー
        RuntimeError: リトライ上限を超えた場合
    """
    delay = initial_delay
    for attempt in range(0, max_retries+1):
        try:
            logging.debug(f"[mcp_list_tool] Attempt {attempt+1} - Opening SSE")
            async with sse_client(f"{mcp_server_func_name}/runtime/webhooks/mcp/sse?code={code}", timeout=30, sse_read_timeout=888) as (stdio, write):
                async with ClientSession(stdio, write) as session:
                    await session.initialize()
                    response = await session.list_tools()
                    return response
        except* (
            HTTPXConnectTimeout,
            HTTPCoreConnectTimeout,
            ConnectionError,
            ConnectError,
            ReadTimeout
        ) as timeout_eg:
            # タイムアウトエラーまたは接続エラーの場合
            for i, timeout_error in enumerate(timeout_eg.exceptions):
                logging.warning(
                    f"[mcp_list_tool] Attempt {attempt+1} failed with error {i+1}/{len(timeout_eg.exceptions)}: {timeout_error!r}. Retrying after {delay:.1f}s"
                )
            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay *= 2
                jitter = delay * 0.2 * random.random()
                delay = delay + jitter
        except* Exception as eg:
            # 上記以外の例外が発生した場合
            for i, unexpected_error in enumerate(eg.exceptions):
                logging.error(
                    f"[mcp_list_tool] Attempt {attempt+1} failed with error {i+1}/{len(eg.exceptions)}: {unexpected_error!r}"
                )
            raise eg

    # リトライ上限超過の場合
    raise RuntimeError(f"[mcp_list_tool] failed after {max_retries} attempts")


async def mcp_call_tool(
    code: str,
    mcp_server_func_name: str,
    mcp_tool_name: str,
    args: dict,
    max_retries: int = 3,
    initial_delay: float = 1.0,
):
    """
    この関数は、指定されたMCPサーバーに接続し、指定されたツールを呼び出して結果を返します。
    リトライ機能を備えており、MCPツール内で発生するエラーを除いて、接続エラーやタイムアウトなどが発生した場合に再試行します。
    Args:
        code (str): MCPサーバーのキー
        mcp_server_func_name (str): MCPサーバーのドメイン名
        mcp_tool_name (str): 呼び出すMCPツールの名前
        args (dict): ツールに渡す引数
        max_retries (int): リトライの最大回数
        initial_delay (float): 初回リトライまでの待機時間（秒）
    Returns:
        response : ツールの実行結果
    Raises:
        mcp_err_eg: MCPツール内でのエラー
        RuntimeError: リトライ上限を超えた場合
    """
    delay = initial_delay

    for attempt in range(0, max_retries+1):
        try:
            logging.debug(f"[mcp_call_tool] Attempt {attempt+1} - Opening SSE")
            async with sse_client(f"{mcp_server_func_name}/runtime/webhooks/mcp/sse?code={code}", timeout=30, sse_read_timeout=888) as (stdio, write):
                async with ClientSession(stdio, write) as session:
                    await session.initialize()
                    logging.info(f"Calling tool {mcp_tool_name} with args: {args}")
                    response = await session.call_tool(mcp_tool_name, args)
                    return response
        except* McpError as mcp_err_eg:  
            # MCPツール内でのエラーが発生した場合
            for i, mcp_error in enumerate(mcp_err_eg.exceptions):
                logging.error(f"[mcp_call_tool] Attempt {attempt+1} failed with MCP error {i+1}/{len(mcp_err_eg.exceptions)}: {mcp_error!r}")
            raise mcp_err_eg
        except* Exception as eg:
            # タイムアウトエラーなどその他のエラーが発生した場合
            for i, unexpected_error in enumerate(eg.exceptions):
                logging.warning(f"[mcp_call_tool] Attempt {attempt+1} failed with error {i+1}/{len(eg.exceptions)}: {unexpected_error!r}")
            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay *= 2
                jitter = delay * 0.2 * random.random()
                delay = delay + jitter

    # リトライ上限超過の場合
    raise RuntimeError(
        f"[mcp_call_tool] failed after {max_retries} attempts"
    )


async def get_history(mode, upn, session_id, agent_id, client) -> str:
    """
    history functionとやりとりを行い、今までの実行履歴を取得する関数
    最新のtool実行履歴から順に確認し、summarize_historyが呼び出されていたらそこまでをhistoryに追加して終了する。
    """
    url = f"{HISTORY_API_URL}/api/history/{mode}/{upn}"
    params = {"sessionId": session_id, "agentId": agent_id}
    api_name = "get_history"
    try:
        history_json = await client.get(url=url, api_key=HISTORY_API_KEY, params=params, process_name=api_name)
    except Exception as e:
        logging.warning(f"tool実行履歴の読み込み: {e}")
        raise

    agents = history_json["agents"]

    # 3件で1回のtool呼び出し
    total_groups = len(agents) // 3
    history = ""

    # 最新の呼び出しから逆順に処理
    for group_index in reversed(range(total_groups)):
        # tool関連の情報を取得
        step = group_index + 1
        base = group_index * 3
        choose_tool_response = json.loads(agents[base]["content"][0]["text"])
        tool = choose_tool_response.get("tool", "")
        thought = choose_tool_response.get("thought", "")
        action = choose_tool_response.get("action", "")

        result_text = agents[base+2]["content"][0]["text"]

        history = (
            f"<Step {step}>\n"
            f"tool selected: {tool}\n"
            f"thought:\n{thought}\n"
            f"action:\n{action}\n"
            f"result of {tool}:\n{result_text}\n"
            f"</Step {step}>\n"
        ) + history

        # 要約を行なっている場合は終了
        if tool == "summarize_history":
            break
    return history

def check_token(text: str) -> int:
    encoding = tiktoken.get_encoding("o200k_base")
    token_integers = encoding.encode(text)
    return len(token_integers)
