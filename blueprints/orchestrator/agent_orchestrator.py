import json
import logging
from copy import deepcopy
import azure.durable_functions as d_func
from blueprints.orchestrator.agent import AGENT_CONFIG

bp = d_func.Blueprint()

retry_options = d_func.RetryOptions(
    first_retry_interval_in_milliseconds=5000,
    max_number_of_attempts=3
)


@bp.orchestration_trigger(context_name="context")
def agent_orchestrator(context: d_func.DurableOrchestrationContext):
    """
    Durable Functionsのオーケストレーター関数。
    エージェントを初期化し、ツールを登録し、ユーザーの入力に基づいた処理を実行する。

    Args:
        context: Durable Functionsのオーケストレーションコンテキスト。
            get_input()で取得されるペイロード(dict)の主な内容:
                - session_id (str): セッションID
                - agent_id (str): エージェントID
                - messages (list): ユーザーからのメッセージ履歴
                - upn (str): ユーザー識別子
                - mail (str): ユーザーメールアドレス
                - mode (str): エージェントの動作モード
                - max_steps (int, 任意): エージェントの最大ステップ数
                - model_name (str, 任意): 使用するモデル名

    Returns:
        dict:
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": [
                                {"type": "text", "text": ...},
                                ...
                            ]
                        }
                    }
                ]
            }
            contentはAOAIのmessagesの型にほぼ準拠。
    """
    if not context.is_replaying:
        logging.info("starting agent orchestrator")

    # ユーザーからの入力を取得
    payload = context.get_input()
    session_id = payload.get("session_id", "")
    agent_id = payload.get("agent_id", "")

    messages = payload.get("messages", [])
    upn = payload.get("upn", "")
    mail = payload.get("mail", "")
    mode = payload.get("mode", "default")

    sendFrom = payload.get("from", "web")

    if not context.is_replaying:
        logging.info(f"session_id: {session_id}")
        logging.info(f"agent_id: {agent_id}")

        logging.info(f"messages: {messages}")
        logging.info(f"upn: {upn}")
        logging.info(f"mail: {mail}")
        logging.info(f"mode: {mode}")

        logging.info(f"from: {sendFrom}")

    # modeの実行権限をチェック
    perm_payload = {"upn": upn, "mode": mode}
    perm_result = yield context.call_activity_with_retry(
        "check_mode_permission",
        retry_options,
        json.dumps(perm_payload)
    )

    # 権限がない場合は、ここでオーケストレーターを終了させる
    if not (perm_result or {}).get("is_authorized", False):
        if not context.is_replaying:
            logging.warning(
                f"Permission denied for UPN {upn} in mode {mode}. Terminating orchestration.")
        error_content = [
            {"type": "text", "text": "現在の権限ではこの機能をご利用いただけません。管理者にお問い合わせください。"}]
        return {
            "choices": [{
                "message": {"role": "assistant", "content": error_content}
            }],
            "blobs": []
        }

    if not context.is_replaying:
        logging.info("finished check_mode_permission")

    # modeによってserverとpromptを切り替える
    try:
        MCP_SERVERS = AGENT_CONFIG[mode]["servers"]
        PROMPTS = AGENT_CONFIG[mode]["prompts"]
        MCP_CODE_INPUTS = AGENT_CONFIG[mode]["code_inputs"]
        SUMMARIZE_THRESHOLD = AGENT_CONFIG[mode].get("summarize_threshold", {})
        submode: str | bool = AGENT_CONFIG[mode].get("submode", False)
        terminal_tools = []
        for server in MCP_SERVERS:
            terminal_tools += server.get("terminal_tools", [])
    except Exception as e:
        # TODO エラー時の挙動を決める
        logging.exception("modeの登録が間違っています。")
        raise ValueError(f"mode({mode})のconfigが取得できません。設定を確認してください")

    if not terminal_tools:
        logging.error("terminal_toolsが登録されていません。")
        raise ValueError(f"mode({mode})のterminal_toolsが登録されていません。設定を確認してください")

    # submode
    origin_mode = mode
    if submode:
        submode = mode
        mode = "genie"
        if not context.is_replaying:
            logging.debug(f"update mode!")

    mcp_code_inputs = deepcopy(MCP_CODE_INPUTS)

    # toolとの接続の確認、必要に応じてagent_idの払い出し
    agent_settings = yield context.call_activity_with_retry("init_agent", retry_options, {"servers": MCP_SERVERS, "agent_id": agent_id})
    if not context.is_replaying:
        logging.info("finished init_agent")

    # messagesの整形（添付ファイル処理）
    messages_data = yield context.call_activity_with_retry("process_messages", retry_options, {
        "messages": messages,
        "mode": mode,
        "upn": upn
    })
    messages = messages_data["messages"]
    blobs = messages_data["blobs"]
    blob_names = [blob["name"] for blob in blobs]
    if not context.is_replaying:
        logging.info(f"processed messages: {messages}")
        logging.info(f"blobs: {blob_names}")

    # 入力の保存
    request_data = {
        "mode": mode,
        "status": "running",
        "items": [
            {
                "sessionId": session_id,
                "upn": upn,
                "mail": mail,
                "content": messages[-1]["content"],
                "role": "user",
                "model": payload.get("model_name", "gpt4.1"),
                "from": sendFrom,
                **({"submode": submode} if submode else {})
            }
        ],
    }

    _ = yield context.call_activity_with_retry("add_history", retry_options, request_data)

    agent_id = agent_settings["agent_id"]
    tool_list = agent_settings["tool_name_list"]
    max_steps = payload.get("max_steps", 3)
    if not context.is_replaying:
        for idx, tool in enumerate(tool_list, start=1):
            logging.info(
                f"Tool {idx}: name={tool['name']}, description={tool['description']}")

    step = 1
    choose_tool_result = {"tool": None, "thought": None, "action": None}
    if not context.is_replaying:
        logging.info("Starting Agent...")

    # エージェントを実行
    # 最大ステップ数に達した場合、強制的に最終回答生成ツールを呼び出す。
    while choose_tool_result["tool"] not in terminal_tools:
        if step > max_steps:
            if "final_answer" in terminal_tools:
                final_tool = "final_answer"
            else:
                final_tool = terminal_tools[-1]
            logging.warning(f"最大ステップ数超過のため、{final_tool}を呼び出します")
            choose_tool_result = {
                "tool": final_tool, "thought": "エージェントの最大ステップ数に達しました", "action": "最終回答生成ツールを呼び出します。"}
        else:
            data_choose = {
                "session_id": session_id,
                "agent_id": agent_id,
                "upn": upn,
                "mail": mail,
                "mode": mode,
                "submode": submode,
                "messages": messages,
                "agent_system_prompt": PROMPTS["agent_system_prompt"],
                "tool_list": tool_list,
                "model_name": "gpt4.1",
                "summarize_threshold": SUMMARIZE_THRESHOLD
            }

            # 実行するツールを選択する。
            choose_tool_result = yield context.call_activity_with_retry("choose_tool", retry_options, json.dumps(data_choose))

        tool_name = choose_tool_result["tool"]
        if not context.is_replaying:
            logging.info(f"selected tool in step {step}: {tool_name}")

        # TODO ハードコーディングを解消する
        # 選択されたツールのパラメータを更新
        mcp_code_inputs[tool_name]["_code_messages"] = messages
        mcp_code_inputs[tool_name]["_code_thought"] = choose_tool_result["thought"]
        mcp_code_inputs[tool_name]["_code_action"] = choose_tool_result["action"]
        mcp_code_inputs[tool_name]["_code_upn"] = upn
        mcp_code_inputs[tool_name]["_code_mail"] = mail
        mcp_code_inputs[tool_name]["_code_mode"] = origin_mode

        # 選択されたツールを実行する。
        data_call = {
            "session_id": session_id,
            "agent_id": agent_id,
            "upn": upn,
            "mail": mail,
            "mode": mode,
            "submode": submode,
            "tool_name": tool_name,
            "messages": messages,
            "thought": choose_tool_result["thought"],
            "action": choose_tool_result["action"],
            "mcp_code_inputs": mcp_code_inputs.get(tool_name, {}),
            "model_name": "gpt4.1",
            "servers": MCP_SERVERS,
        }
        # ツールの実行結果を取得する。
        content: list[dict] = yield context.call_activity_with_retry("call_tool", retry_options, json.dumps(data_call))

        if not context.is_replaying:
            logging.info(f"result from {tool_name} in step {step}: {content}")
        step += 1

    request_data = {
        "mode": mode,
        "status": "completed",
        "items": [
            {
                "sessionId": session_id,
                "agentId": agent_id,
                "upn": upn,
                "mail": mail,
                "content": content,
                "role": "assistant",
                "model": payload.get("model_name", "gpt4.1"),
                "from": sendFrom,
                **({"submode": submode} if submode else {})
            }
        ],
    }

    _ = yield context.call_activity_with_retry("add_history", retry_options, request_data)

    return {"choices": [{
        "message": {"role": "assistant", "content": content, },
    }],
        "blobs": blob_names
    }
