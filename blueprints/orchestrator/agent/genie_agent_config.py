from config import MCP_SERVER_FUNC_NAME, MCP_CODE

# キーなどの値はrootディレクトリ直下のconfigファイルに定義してこのファイルに読み込んで使用するようにすること

# mcpサーバーとの接続情報
MCP_SERVERS = [
    {
        "domain": MCP_SERVER_FUNC_NAME,
        "key": MCP_CODE,
        "enable_tools": [
            "accounting_fraud", "audit_flowchart", "audit_precheck",
            "company_info", "search", "plastic", "panel_sales_enquiry",
            "product", "research", "final_answer",
        ], # "tariff", "plastic",
        "terminal_tools": ["final_answer"],
        "custom_mapping": {
            "accounting_fraud": {
                "tool": "call_agent",
                "description": (
                    "accounting_fraud エージェントを呼び出します。"
                    "一問一答形式となっており、今までのメッセージは伝わりません。"
                    "このエージェントは、会計元帳や会計元帳に類するデータから不正会計を検出します。"
                    "呼び出しを行う際には必ずこのエージェント側の視点となって必要十分な質問を渡すようにしてください。"
                )
            },
            "audit_flowchart": {
                "tool": "call_agent",
                "description": (
                    "audit_flowchart エージェントを呼び出します。"
                    "一問一答形式となっており、今までのメッセージは伝わりません。"
                    "このエージェントは、業務監査を行う際の監査のポイントを回答します。"
                    "呼び出しを行う際には必ずこのエージェント側の視点となって必要十分な質問を渡すようにしてください。"
                )
            },
            "audit_precheck": {
                "tool": "call_agent",
                "description": (
                    "audit_precheck エージェントを呼び出します。"
                    "一問一答形式となっており、今までのメッセージは伝わりません。"
                    "このエージェントは、過去の監査報告書を分析し、インサイトを提供します。"
                    "呼び出しを行う際には必ずこのエージェント側の視点となって必要十分な質問を渡すようにしてください。"
                )
            },
            "company_info": {
                "tool": "call_agent",
                "description": (
                    "company_info エージェントを呼び出します。"
                    "一問一答形式となっており、今までのメッセージは伝わりません。"
                    "このエージェントは、投資に適した会社情報を調査して提供します。"
                    "呼び出しを行う際には必ずこのエージェント側の視点となって必要十分な質問を渡すようにしてください。"
                )
            },
            "search": {
                "tool": "call_agent",
                "description": (
                    "search エージェントを呼び出します。"
                    "一問一答形式となっており、今までのメッセージは伝わりません。"
                    "このエージェントはGoogle検索を行い、得られた結果を応答します。"
                    "呼び出しを行う際には必ずこのエージェント側の視点となって必要十分な質問を渡すようにしてください。"
                )
            },
            "plastic": {
                "tool": "call_agent",
                "description": (
                    "plastic エージェントを呼び出します。"
                    "一問一答形式となっており、今までのメッセージは伝わりません。"
                    "このエージェントは伊藤忠の事業会社である伊藤忠リテールリンクの扱う製品と、その販売実績を検索します。"
                    "また、プラスチックの原材料についても回答できます。"
                    "呼び出しを行う際には必ずこのエージェント側の視点となって必要十分な質問を渡すようにしてください。"
                )
            },
            "panel_sales_enquiry": {
                "tool": "call_agent",
                "description": (
                    "panel_sales_enquiry エージェントを呼び出します。"
                    "一問一答形式となっており、今までのメッセージは伝わりません。"
                    "このエージェントは、エネルギー化学品カンパニーの再生可能エネルギー課が扱う製品に関する質問に回答します。"
                    "呼び出しを行う際には必ずこのエージェント側の視点となって必要十分な質問を渡すようにしてください。"
                )
            },
            "product": {
                "tool": "call_agent",
                "description": (
                    "product エージェントを呼び出します。"
                    "一問一答形式となっており、今までのメッセージは伝わりません。"
                    "このエージェントは化学品カンパニーの化学品部門が扱う、プラスチック原材料に関する情報を収集できます。"
                    "呼び出しを行う際には必ずこのエージェント側の視点となって必要十分な質問を渡すようにしてください。"
                )
            },
            "research": {
                "tool": "call_agent",
                "description": (
                    "research エージェントを呼び出します。"
                    "一問一答形式となっており、今までのメッセージは伝わりません。"
                    "このエージェントはWebを極めて深く検索し、レポートを提供します。呼び出しに時間がかかるため事前にユーザーに確認してください。"
                    "呼び出しを行う際には必ずこのエージェント側の視点となって必要十分な質問を渡すようにしてください。"
                )
            },
            "final_answer": {
                "tool": "call_llm",
                "description": (
                    "ユーザーに直接回答を渡すためのツールです。"
                    "LLMを用いて今までのやり取りを全て確認してユーザーに対しての回答を生成します。"
                    "ユーザーからの要望に十分に応えるための情報が出揃った場合か、これ以上は既存のツールでは情報を取得できないと判断した場合にこのツールを呼び出してください。"
                )
            },
        }
    },
]

AGENT_SYSTEM_PROMPT = """あなたは複数のAgentなどの機能を呼び出してユーザーの要望に適切に応じる統合型エージェントのメインブレインです。
提供されたツールを適切に選択することが可能です。
ユーザーから受けた質問に対して、思考し行動を決め、以下の「出力形式」にしたがって出力してください。

あなたのタスクは、ユーザーの質問に正確に回答することです。

### 行動指針
- ユーザーの質問をどのエージェントを用いることで適切にこなすことができるか論理的に切り分けを行ってください。
- 各Agentの機能を必要以上に高く見積ったり、低く見積ったりしないように気をつけてください。
- 常に複数のエージェントを組み合わせることで新たなシナジーを生み出すことはできるかの検討を行ってください。

### 出力形式
回答は **以下の JSON** のみを返してください（追加の文章を付与しないこと）。

```json
{{
    "thought": "あなたの思考プロセスを詳細に書く",
    "action": "実際に行う具体的なステップを端的に書く",
    "tool": "利用するツール名を 1 つだけ記載"
}}
```
- thought
    - あなたの思考過程を書き出してください。ユーザー意図の推測、必要なデータや情報ソース、確認すべきポイントなど、推論の過程をできる限り詳細に記載してください。
    - 必要な情報源や条件、さらに検討すべき制約や不足情報を洗い出す。
    - 過去のやり取り（履歴）との整合性や、矛盾が生じないかの確認を行う。
- action
    - thought で導き出した結論を踏まえて、「何をするか」を端的かつ具体的に記載してください。
        - 社内DBの情報を元に、ユーザーの求める回答を組み立てるための方針を決定する。
- tool
    - 実行する行動に対応するツールを、指定された候補から**必ず1つだけ**記載してください。

### 注意事項
- あなたの知識は最新のものではない場合があります。自分の知識を過信せずにツールを実行するようにしてください。
- 本日の日付は{get_datetime}です。

### 利用可能なツール
各ツールには、それぞれの説明や必要とする引数が定義されています。ツールを使うときは必ず正しいツール名を一つだけ `tool` に指定してください。
以下のツールが参照可能です。
{tool_explanation}

### あなたの行ったタスクの履歴
下記に、これまでのタスク実行履歴が表示されます。（初回の場合は空欄です）
**履歴に記載された内容を必ず確認し、今回のステップと重複・矛盾しないように注意してください。**
{history}
"""

# エージェント、ツールのプロンプト
PROMPTS = {
    "agent_system_prompt": AGENT_SYSTEM_PROMPT,
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
        あなたはユーザーの質問に対して今までのAgentの実行結果を統合して、最終回答を生成する役割を担っています。
        エージェントが行った推論とタスク実行履歴をもとに、ユーザーの質問に対する結論や見解を明確に伝える最終回答を作成してください。
        どのツールでどのような情報が得られたかの記載を行う。有用な情報が得られたツールについてのみの記載とする。冗長になりすぎないように注意。

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

    "accounting_fraud": {
        "_code_upn": "",
        "_code_mail": "",
        "_code_call_mode": "accounting_fraud",
    },
    "audit_flowchart": {
        "_code_upn": "",
        "_code_mail": "",
        "_code_call_mode": "audit_flowchart",
    },
    "audit_precheck": {
        "_code_upn": "",
        "_code_mail": "",
        "_code_call_mode": "audit_precheck",
    },
    "company_info": {
        "_code_upn": "",
        "_code_mail": "",
        "_code_call_mode": "company_info",
    },
    "search": {
        "_code_upn": "",
        "_code_mail": "",
        "_code_call_mode": "web_search",
    },
    "plastic": {
        "_code_upn": "",
        "_code_mail": "",
        "_code_call_mode": "plastic",
    },
    "panel_sales_enquiry": {
        "_code_upn": "",
        "_code_mail": "",
        "_code_call_mode": "panel_sales_enquiry",
    },
    "product": {
        "_code_upn": "",
        "_code_mail": "",
        "_code_call_mode": "product",
    },
    "research": {
        "_code_upn": "",
        "_code_mail": "",
        "_code_call_mode": "research",
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
        "_code_model_name": "gpt5",
        "_code_temperature": 0,
        "_code_reasoning_effort": "high",
    },
}
