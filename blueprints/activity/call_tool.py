import os
import json
import base64
import logging
import azure.durable_functions as d_func
from mcp import types

from i_style.llm import AzureOpenAI
from i_style.aiohttp import AsyncHttpClient
from i_style.messages import Messages
from blueprints.activity.util import mcp_list_tools, mcp_call_tool, get_history
from config import (
    BLOB_SERVICE_CLIENT,
    FILE_TEXT_EXTRACTOR,
    LLM_REGISTRY,
    RESEARCH_REGISTRY,
    COMPANY_REGISTRY,
    HISTORY_API_URL,
    HISTORY_API_KEY
)

bp = d_func.Blueprint()


@bp.activity_trigger(input_name="payload")
async def call_tool(payload: dict) -> list[dict]:
    """
    指定されたツールを実行し、実行結果を返すactivity関数。

    Args:
        payload (dict): ツール呼び出しに必要な情報を含む辞書。
            - session_id
            - agent_id
            - upn
            - mode
            - submode
            - tool_name (str): 呼び出すツール名
            - messages (List[dict], optional): ユーザーとのやり取り
            - thought (str, optional): エージェントの推論内容。
            - action (str, optional): 実行すべきアクション内容。
            - mcp_code_inputs (dict)
            - model_name (str, optional): 使用するLLMモデル
            - servers (List[dict]): MCPサーバーのドメインとキーのリスト。

    Returns:
        list: ツールの実行結果を変換して返却。

    Raises:
        ValueError: OpenAIのレスポンスに `tool_calls` が含まれていない場合。
        Exception: パラメータ生成やMCP実行中に発生したその他のエラー。
    """
    # 入力の読み込み
    data = payload if isinstance(payload, dict) else json.loads(payload)

    session_id = data.get("session_id", "")
    agent_id = data.get("agent_id", "")
    upn = data.get("upn", None)
    mode = data.get("mode", "default")
    submode: str | bool = data.get("submode", False)

    tool_name = data["tool_name"]
    messages = data.get("messages", [])

    thought = data.get("thought", None)
    action = data.get("action", None)
    mcp_code_inputs = data.get("mcp_code_inputs", {})
    model_name = data.get("model_name", "gpt4.1")

    servers = data.get("servers", [])

    origin_mode = mode
    if submode:
        origin_mode = submode

    match origin_mode:
        case "research":
            registry = RESEARCH_REGISTRY
        case "company_info" | "company_research":
            registry = COMPANY_REGISTRY
        case _:
            registry = LLM_REGISTRY

    # 呼び出すtoolに対応したサーバーの情報を取得
    mcp_tool_name = tool_name
    tool_description = ""
    for server in servers:
        if tool_name in server["enable_tools"]:
            mcp_server_func_name = server["domain"]
            mcp_code = server["key"]

            if tool_name in server["custom_mapping"].keys():
                mcp_tool_name = server["custom_mapping"][tool_name]["tool"]
                tool_description = server["custom_mapping"][tool_name].get("description", "")
                logging.debug("updated tool_name")
            break

    # CosmosDBから今までの実行履歴を取得
    async_http_client= AsyncHttpClient()
    mcp_code_inputs["_code_history"] = history = await get_history(mode, upn, session_id, agent_id, async_http_client)
    if "_code_messages" in mcp_code_inputs:
        try:
            msgs_instance = await Messages.init_with_conversion(
                text_extractor=FILE_TEXT_EXTRACTOR, 
                messages=mcp_code_inputs["_code_messages"], 
                prefix=f"{upn}/{mode}", 
                blob_service_client=BLOB_SERVICE_CLIENT
            )
            mcp_code_inputs["_code_messages"] = await msgs_instance.get_messages("aoai")  # messagesをAOAI形式に変換
        except Exception as e:
            logging.warning(f"_code_messages の整形に失敗しました: {e}")

    # ツール一覧を取得
    response = await mcp_list_tools(code=mcp_code, mcp_server_func_name=mcp_server_func_name)
    available_tools = response.tools

    tools = []
    args = {}
    llm_properties = {}
    code_properties = {}

    for tool in available_tools:
        if tool.name != mcp_tool_name:
            continue

        # ツールのプロパティをcode管理するパラメータとLLM管理するパラメータに分ける
        code_properties = {
            k: v for k, v in tool.inputSchema.get("properties", {}).items()
            if k.startswith("_code_")
        }
        code_required = [
            k for k in tool.inputSchema.get("required", [])
            if k.startswith("_code_")
        ]
        llm_properties = {
            k: v for k, v in tool.inputSchema.get("properties", {}).items()
            if not k.startswith("_code_")
        }
        llm_required = [
            k for k in tool.inputSchema.get("required", [])
            if not k.startswith("_code_")
        ]

        if llm_properties:
            for param, item in llm_properties.items():
                # array非対応のため、暫定で対応
                _type: str = item["type"]
                if _type.startswith("array"):
                    # array_stringのような形式を想定
                    item["type"] = "array"
                    item["items"] = {"type": _type.split("_")[1]}
                    logging.warning(f"updated property: {param}, {item}")

            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_description if tool_description else tool.description,
                    "parameters": {
                        "type": tool.inputSchema.get("type", "object"),
                        "properties": llm_properties,
                        "required": llm_required
                    }
                }
            }

            tools.append(tool_schema)
        break
    logging.info(f"tools: {tools}")

    # LLMに考えさせるパラメータがある場合のみLLMを呼び出す
    if llm_properties:
        logging.info(f"LLMに考えさせるパラメータがあります: {list(llm_properties.keys())}")
        # ツールのパラメータの値を生成
        prompt = (
            f"ReActエージェントがツール '{tool_name}' の実行に必要な引数をJSONで出力します。\n"
            f"推論: {thought}\n行動: {action}\n履歴: {history}\n"
            f"必要なフィールド: {list(tools[0]['function']['parameters']['properties'].keys())}"
        )
        # Messagesクラスでmessagesを整形
        msgs_instance = await Messages.init_with_conversion(
                text_extractor=FILE_TEXT_EXTRACTOR, 
                messages=messages, 
                prefix=f"{upn}/{mode}", 
                blob_service_client=BLOB_SERVICE_CLIENT
            )
        aoai_msgs = await msgs_instance.get_messages("aoai") # messagesをAOAI形式に変換
        aoai_msgs = [{"role": "system", "content": prompt}] + aoai_msgs

        try:
            resp = await AzureOpenAI(
                messages=aoai_msgs,
                raise_for_error=True,
                json_mode=True,
                tools=tools,
                model_name=model_name,
                tool_choice={"type": "function", "function": {"name": tool_name}},
                registry=registry,
            )
            calls = resp["choices"][0]["message"].get("tool_calls", [])
            if not calls:
                raise ValueError("AOAI から tool_calls が返ってきませんでした。")
            args = json.loads(calls[0]["function"]["arguments"])

        except Exception as e:
            logging.error(f"パラメータ生成中のエラー: {e}")
            raise
    else:
        logging.info(f"LLMに考えさせるパラメータがないため、LLMの呼び出しをスキップ")
        calls = []
        args = {}

    # 固定値の引数を登録
    if code_properties:
        for k, _ in code_properties.items():
            if k in mcp_code_inputs:
                args[k] = mcp_code_inputs[k]
            elif k in code_required:
                raise ValueError(f"ツール '{mcp_tool_name}'({tool_name}) の引数 '{k}' が必要ですが、指定されていません。")

    # mcpサーバーからのレスポンス形式
    """
    CallToolResult(
        content = [
            TextContent(type="text", text=<text or json.dumpsされた内容>),
        ],
        ...
    )
    """

    # ツールを呼び出し結果をmessages形式へと変換
    ## str, dict, listそれぞれのデータの形式がlist[dict]になるように加工
    try:
        result = await mcp_call_tool(mcp_code, mcp_server_func_name, mcp_tool_name, args)
        _content = result.content[0].text
        _content = json.loads(_content)
    except json.JSONDecodeError:
        logging.warning(f"jsonのデコードに失敗しました。レスポンスの形式が不正な可能性があります。tool: {mcp_tool_name}")
        _content = {"type": "text", "text": _content}
    except Exception:
        logging.exception("error in call_tool")
        _content = {"type": "text", "text": "サーバーからの応答がありません。混雑の可能性があるため、時間をおいてお試しください。"}

    if isinstance(_content, dict):
        logging.warning(f"辞書型のレスポンスを受け取りました。レスポンスの形式が不正な可能性があります。tool: {mcp_tool_name}")
        _content = [_content, ]

    _tool_message = [{"role": "tool", "content": _content},]
    msgs_instance = await Messages.init_with_conversion(
                text_extractor=FILE_TEXT_EXTRACTOR, 
                messages=_tool_message, 
                prefix=f"{upn}/{mode}", 
                blob_service_client=BLOB_SERVICE_CLIENT
            )
    tool_message = await msgs_instance.get_messages()

    content = tool_message[0]["content"]

    # 履歴の登録
    request_data = {
        "items": [
            # パラメータ
            {
                "sessionId": session_id,
                "agentId": agent_id,
                "upn": upn,
                "content": calls,
                "role": "assistant",
                "toolInfo": {
                    "toolName": tool_name,
                    "url": mcp_server_func_name
                },
                "type": "agent",
                "model": model_name,
                **({"submode": submode} if submode else {})
            },
            # 返り値
            {
                "sessionId": session_id,
                "agentId": agent_id,
                "upn": upn,
                "content": content,
                "role": "tool",
                "toolInfo": {
                    "toolName": tool_name,
                    "url": mcp_server_func_name
                },
                "type": "agent",
                "model": "",
                **({"submode": submode} if submode else {})
            }
        ]
    }

    url = f"{HISTORY_API_URL}/api/history/{mode}"
    api_name = "add_history"
    try:
        response = await async_http_client.post(url=url, api_key=HISTORY_API_KEY, json_data=request_data, process_name=api_name)
    except Exception as e:
        logging.warning(f"履歴への登録: {e}")

    return content
