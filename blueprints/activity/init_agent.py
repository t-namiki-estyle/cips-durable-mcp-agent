import os
import uuid
import logging
from collections import defaultdict

import azure.durable_functions as d_func

from blueprints.activity.util import mcp_list_tools

bp = d_func.Blueprint()


@bp.activity_trigger(input_name="payload")
async def init_agent(payload: dict) -> dict:
    """
    エージェントの初期化処理を行うactivity関数。
    この関数は、エージェントがツール選択を行うために必要な情報を準備する。

    Args:
        payload (dict): 関数トリガーの入力
            - agent_id (str): エージェントID。渡されない場合はこの関数内で作成する。
            - servers (List[dict]): MCPサーバーのドメインとキーのリスト。

    Returns:
        dict: エージェントの初期化に必要な情報を含む辞書。
            - agent_id (str): 生成または指定されたエージェントID。
            - tool_name_list (List[dict]): MCPから取得したツール情報のリスト。
                各ツールは name, description, inputSchema を含む。

    Raises:
        Exception: MCP通信またはツール取得中にエラーが発生した場合。
    """
    logging.info("starting init_agent")

    # agent_idの確認
    agent_id = payload.get("agent_id", "")
    if not agent_id:
        agent_id = str(uuid.uuid4())

    # 各mcpサーバーとの接続、toolのschemaの取得
    servers = payload.get("servers", [])
    all_tools = []
    for server in servers:
        domain = server["domain"]
        key = server["key"]
        enable_tools = set(server.get("enable_tools", []))
        custom_mapping = server.get("custom_mapping", {})

        # mcpサーバー側のtool名をkeyとしたmappingを作成
        tool_mapping = defaultdict(list)
        for custom_tool, config in custom_mapping.items():
            ## mappingされたtool名を除去
            enable_tools.remove(custom_tool)
            tool_mapping[config["tool"]].append({
                "name": custom_tool,
                "description": config.get("description", "")
            })

        # MCPサーバーよりツール情報を取得
        resp = await mcp_list_tools(code=key, mcp_server_func_name=domain)

        # ツール情報をフィルタリング
        for t in resp.tools:
            ## mappingしていないtoolの場合
            if t.name in enable_tools:
                enable_tools.remove(t.name)
                all_tools.append({
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.inputSchema
                })
            ## mappingされているtoolの場合
            elif t.name in tool_mapping.keys():
                _mapping = tool_mapping.pop(t.name)
                for item in _mapping:
                    all_tools.append({
                        "name": item["name"],
                        "description": item["description"] if item["description"] else t.description,
                        "inputSchema": t.inputSchema
                    })

            if not (enable_tools or tool_mapping):
                break

        # 登録できなかったtoolが存在する場合
        if enable_tools or tool_mapping:
            raise ValueError(f"toolが存在しません: {enable_tools}, {tool_mapping}")

    return {
        "agent_id": agent_id,
        "tool_name_list": all_tools,
    }
