from config import MCP_SERVER_FUNC_NAME, MCP_CODE

# キーなどの値はrootディレクトリ直下のconfigファイルに定義してこのファイルに読み込んで使用するようにすること

# mcpサーバーとの接続情報
MCP_SERVERS = [
    {
        "domain": MCP_SERVER_FUNC_NAME,
        "key": MCP_CODE,
        "enable_tools": ["enquire", "summarize_history", "final_answer"],
        "terminal_tools": ["enquire", "final_answer"],
        "custom_mapping": {
            "enquire": {
                "tool": "call_llm",
                "description": (
                    "ユーザーからの問い合わせに対して、現状の情報だけでは十分な回答が得られない場合に必要な追加情報を明確にするための追加入力を促す質問文を生成するツールです。"
                    "エージェントが過去のやりとりやタスク履歴をもとに不足している内容を特定し、ユーザーに対して具体的かつ分かりやすい質問を提示することで、ユーザーが正確な情報を提供するのを実現するのが目的です。"
                )
            },
            "summarize_history": {
                "tool": "call_llm",
                "description": (
                    "このツールはシステムの内部処理用に提供されています。"
                    "ユーザー向けの機能は提供しておらず、有用な応答を返すことはありません。"
                    "いかなるユーザーリクエストに対しても呼び出さないでください。"
                )
            },
            "final_answer": {
                "tool": "call_llm",
                "description": (
                    "このツールは、ユーザーへの最終回答を生成するためのものです。"
                    "過去のやりとりや取得済みのデータを踏まえて、ユーザーの問い合わせに対する最終回答を出力します。"
                )
            },
        }
    },
    # 他のMCPサーバーの情報を追加
    # {
    #     "domain": "http://example.com",
    #     "key": "syste_key",
    #     "enable_tools": ["tool1", "tool2"]
    # }
]

# エージェント、ツールのプロンプト
PROMPTS = {
    "agent_system_prompt": """実行するツールを選んでください。出力はjsonでお願いします。
    利用可能なツール:
    {tool_explanation}
    
    履歴: {history}""",
    "enquire_system_prompt": """
        ### 役割
        あなたは「ReActエージェント」の一部として、ユーザーの質問に回答するために不足している情報を補完する役割を担っています。
        エージェントが提示した推論と実施したタスク履歴をもとに、ユーザーに追加で提供してほしい情報を明確にするため、具体的で回答しやすい質問文を作成してください。

        ### 目的
        - これまでのやりとりおよびタスク履歴から、既に得られている情報と不足している情報を正確に整理する。
        - ユーザーが追加で回答すべき具体的な情報（例：対象、条件、範囲など）を特定する。
        - ユーザーが迷わず回答できるよう、平易で簡潔な追加質問文を作成する。

        ### 出力要件
        - 出力はユーザーへの追加質問文のみとする。
        - 平易な日本語で記述し、必要な場合は箇条書きで不足情報を整理して提示する。
        - 既に提供された情報は繰り返さず、追加で必要な情報だけを問いかけること。

        ### エージェントの情報
        - 推論: {thought}
        - 行動: {action}
        - タスク実行履歴: {history}
        """,
    "summarize_history_system_prompt": """
        ### 役割
        あなたは「ReActエージェント」の一部として、トークン超過対策でエージェントのタスク実行履歴を整理する役割を担っています。
        エージェントのタスク履歴をもとに、意味のある情報のみを残して整理した文章を作成してください。

        ### 目的
        - タスク履歴を整理してエージェントが次の行動を決めることができる意味のある情報のみを残す。
            - どのようなツールを呼び出したか
            - どのようなツールの使い方が有効 / 無効であったか
            - 今までのタスク履歴から得られた情報
        - 簡潔な要約を作成するよりも元の意味のある情報をそのまま受け渡すことができる方が価値があります。その前提を踏まえて長くなりすぎることを恐れずに回答を行なってください。

        ### エージェントの情報
        - 推論: {thought}
        - 行動: {action}
        - タスク実行履歴: {history}
        """,
    "final_answer_system_prompt": """
        ### 役割
        あなたは「ReActエージェント」の一部として、ユーザーの質問に対する最終回答を生成する役割を担っています。
        エージェントが行った推論とタスク実行履歴をもとに、ユーザーの質問に対する結論や見解を明確に伝える最終回答を作成してください。

        ### 目的
        - ユーザーの質問に対して、直接的かつ分かりやすい回答を提示する。
        - 必要に応じて、追加確認が必要な点について質問文を含めてもよい。

        ### エージェントの情報
        - 推論: {thought}
        - 行動: {action}
        - タスク実行履歴: {history}
        """,
}

## ツール固有のパラメータ
MCP_CODE_INPUTS = {
    "enquire": {
        "_code_messages": [],
        "_code_thought": "",
        "_code_action": "",
        "_code_history": "",
        "_code_system_prompt": PROMPTS["enquire_system_prompt"],
        "_code_model_name": "gpt4.1",
        "_code_temperature": 0,
        "_code_reasoning_effort": "low",
    },
    "summarize_history": {
        "_code_messages": [],
        "_code_thought": "",
        "_code_action": "",
        "_code_history": "",
        "_code_system_prompt": PROMPTS["summarize_history_system_prompt"],
        "_code_model_name": "gpt4.1",
        "_code_temperature": 0,
        "_code_reasoning_effort": "low",
    },
    "final_answer": {
        "_code_messages": [],
        "_code_thought": "",
        "_code_action": "",
        "_code_history": "",
        "_code_system_prompt": PROMPTS["final_answer_system_prompt"],
        "_code_model_name": "gpt4.1",
        "_code_temperature": 0,
        "_code_reasoning_effort": "low",
    },
    # 以下、他のツールを追加
    # "tool_name": {
    #     "_code_system_prompt": PROMPTS["tool_name_system_prompt"],
    #     "_code_cosmos_str": "yyyy="
    # },
}
