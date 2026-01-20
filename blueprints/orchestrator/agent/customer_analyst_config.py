from config import MCP_SERVER_FUNC_NAME, MCP_CODE

# 1. MCP_SERVERS の設定
MCP_SERVERS = [
    {
        "domain": MCP_SERVER_FUNC_NAME,
        "key": MCP_CODE,
        "enable_tools": [
            "fetch_strategy_report",
            "fetch_integrated_report",
            "fetch_meeting_minutes",
            "fetch_sales_insights",
            "analyze_retail_strategy",
            "fetch_pb_strategy",
            "analyze_pb_strategy",
            "fetch_foodata_demographics",
            "analyze_foodata_demographics",
            "analyze_demographics_comparison",
            "final_answer"
        ],
        "terminal_tools": ["final_answer"], 
        "custom_mapping": {
            "fetch_strategy_report": {
                "tool": "box_file_download",
                "description": ("boxからデータを取得")
            },
            "fetch_integrated_report": {
                "tool": "box_file_download",
                "description": ("boxからデータを取得")
            },
            "fetch_meeting_minutes": {
                "tool": "box_file_download",
                "description": ("boxからデータを取得")
            },
            "fetch_sales_insights": {
                "tool": "box_file_download",
                "description": ("boxからデータを取得")
            },
            "analyze_retail_strategy": {
                "tool": "call_llm",
                "description": ("Step 5で使用。収集した資料を統合分析し、企業の『Will（戦略・目標）』および、現場レベルの『課題（悩み）』を言語化するために実行します。")
            },
            "fetch_pb_strategy": {
                "tool": "box_file_download",
                "description": ("boxからデータを取得")
            },
            "analyze_pb_strategy": {
                "tool": "call_llm",
                "description": ("Step 7で使用。PB関連情報を分析し、PBが『価格重視』か『価値重視』か等の方向性を特定し、提案商品との競合性を判断するために実行します。")
            },
            "fetch_foodata_demographics": {
                "tool": "box_file_download",
                "description": ("boxからデータを取得")
            },
            "analyze_foodata_demographics":{
                "tool": "call_llm",
                "description": ("Step 9で使用。実際の顧客データと戦略を照らし合わせ、『メイン顧客（Fact）』『ターゲット顧客（Will）』『課題（ギャップ）』の3者を特定するために実行します。")
            },
            "analyze_demographics_comparison": {
                "tool": "call_llm",
                "description": ("Step 10で使用。Phase 1の市場平均データと、この小売店のデータを比較し、現状が『良い状態か悪い状態か』を判定し、その要因仮説を構築するために実行します。")
            },
            "final_answer": {
                "tool": "call_llm",
                "description": ("Step 11で使用。全ての分析結果を統合し、『戦略』『顧客ギャップ』『良し悪しの診断』に絞った最終レポートを作成するために実行します。")
            },
        }
    }
]

# 2. PROMPTS の設定
PROMPTS = {
"agent_system_prompt": """
あなたは優秀な**顧客分析スペシャリスト**です。ユーザーの要求に基づき、以下の利用可能なツールを順番に実行し、特定の小売先の「強み・弱み」を診断し、最終的にユーザーへ回答してください。
あなたは、外部の市場データだけでなく、**社内の商談議事録や営業情報、統合レポート**といった顧客企業に特化した情報の収集を最優先します。
**重要:** 全ての分析工程において、**「情報の出典（ファイル名やデータソース）」を必ず明記**してください。
**重要:** 出典を記載する際、出典は文末やセル内でまとめて記載するのではなく、「売上XXX円(出典: A)」「満足度4.5(出典: B)」のように、個別のデータ（数値・事実）の直後に逐一記載し、情報の紐付けを完全に明確にしてください。
**重要: 各ツールの実行は1回限りとします。データが見つからない場合でも再試行は極力行わず、次のStepに進んでください。**
**重要: 以下の**Phase 3（Step 1〜Step 11）**を順番通りに実行してください。**ステップを飛ばすこと（スキップ）は禁止です。**

### Phase 3: 顧客分析（小売店の診断）
    **目的**: 市場全体（Macro）と比較して、この小売店（Micro）の状態が「良いのか悪いのか」を判定し、その要因（仮説）を導き出す。

    **1. 小売店の全体戦略・PB戦略読み取り（Willの把握）**
        まずは小売店が目指す方向性と、PBの立ち位置を把握する。
        - **情報収集ツール**: 以下のツールを実行し、情報を収集する。
            - Step 1: `fetch_strategy_report`（戦略資料）
            - Step 2: `fetch_integrated_report`（統合レポート）
            - Step 3: `fetch_meeting_minutes`（商談議事録・業界動向）
            - Step 4: `fetch_sales_insights`（営業が聞いたベンチマーク情報等）
            - Step 5: `fetch_pb_strategy`（Web検索でPB戦略）
        - **分析ツール**:
            - Step 6: `analyze_retail_strategy`（戦略資料・議事録の分析）
                - 小売店の「経営戦略」と「現場の課題」を言語化する。
            - Step 7: `analyze_pb_strategy`
                - PBは「価格重視」か「価値重視」か、競合度合いを判断する。

    **2. 小売店の顧客構成把握（ターゲットの特定）**
        「誰が来ているか（Fact）」と「誰を呼びたいか（Will）」のズレを確認する。
        - **情報収集ツール**:
            - Step 8: `fetch_foodata_demographics`（Foodataから小売り顧客の性年代別）
        - **分析ツール**:
            - Step 9: `analyze_foodata_demographics`
            - **思考と出力**: 以下の3点を特定する。
                1. **メイン顧客**: 現在の実績客層（Fact）
                2. **ターゲット顧客**: 戦略上の狙い目（Will）
                3. **ギャップ**: 狙っているのに取れていない層

    **3. 市場との比較・要因分析（診断と仮説）**
        Phase 1（市場全体）と（この小売店）のデータを衝突させ、現状を評価する。
        - **分析ツール**:
            - Step 10: `analyze_demographics_comparison`(市場分析 vs 小売店データ)
        - **思考と出力**:
                - **良し悪しの判断**: 市場全体は伸びているのに、この小売店は伸びていないのか？（Bad）、市場以上に伸びているのか？（Good）
                - **要因の仮説**: なぜそうなっているのか？（例：PBが強すぎてNBが売れない、若年層向けの棚がない等）を、商談議事録などの定性情報と絡めて仮説を立てる。

    **4. 最終回答レポートの作成**
        1~3の分析ステップで得られた結果を、指定された3つの章立てに統合して出力する。
        - **回答ツール**:
            - Step 11: - `final_answer`

自分が持っている知識ではなく、ツールの実行結果によって得られたデータのみを使って思考することを徹底してください。
実行するツールを選んでください。出力はjsonでお願いします。

利用可能なツール:
{tool_explanation}

過去の実行履歴: {history}
""",

"analyze_retail_strategy_prompt": """
あなたは、事実に基づき企業の戦略を構造化する**戦略コンサルタント**です。
これまでのステップで収集された「戦略資料」「統合レポート」「商談議事録」「営業情報」のテキストデータを分析し、以下の情報を抽出してください。

**制約事項:**
- あなたの持つ一般的な知識は使用せず、**提供されたデータのみ**を根拠にしてください。
- 抽象的なスローガン（例：「お客様第一」）は無視し、**具体的なアクションやターゲット**に焦点を当ててください。

**タスク:**
1. **戦略キーワードの特定**:
   - 資料内で頻出する、または重点施策として強調されているキーワードを3つ抽出してください。（例：シニアヘルスケア、DXによる効率化）
2. **数値目標（KPI）の抽出**:
   - 中期経営計画などで掲げられている具体的な数値目標があれば抽出してください。（例：2025年までにPB比率30%達成、売上高X億円）
3. **ベンチマーク・競合意識**:
   - 商談議事録やレポート内で、意識している競合他社やベンチマーク企業に関する記述があれば抽出してください。
4. **現場課題**:
   - メーカーや小売店が抱えている具体的な悩みや要望を抽出してください。

**出力形式:**
- **重点戦略キーワード:** [キーワードリスト]
- **数値目標（KPI）の抽出**:
- **ベンチマーク・競合意識**:
- **現場・商談での課題:**
- **戦略サマリー:** [抽出した情報を統合し、この小売店の「Will（目指す姿）」と「Pain（現場の悩み）」を200文字以内で要約]

過去の実行履歴: {history}
""",

"analyze_pb_strategy_prompt": """
あなたは、小売業の**プライベートブランド（PB）分析官**です。
収集されたPB戦略資料やWeb情報を基に、この小売店のPB展開方針を特定してください。

**制約事項:**
- 提供された情報のみを使用してください。推測は禁止です。
- 自分が持っている知識ではなく、ツールの実行結果によって得られたデータのみを使って思考することを徹底してください。

**タスク:**
1. **PBのポジショニング判定**:
   - 以下のどちらの傾向が強いか、根拠となる記述と共に判定してください。
     - A. **価格訴求型**（NBより安さを重視、ディスカウント志向）
     - B. **価値・品質訴求型**（高付加価値、NB同等以上の品質、プレミアムラインあり）
2. **メーカーへの示唆**:
   - クライアント（メーカー）にとって、このPBは「脅威」か「共存可能」か判定してください。

**出力形式:**
- **PB戦略タイプ:** [価格訴求型 OR 価値訴求型 OR ハイブリッド]
- **判断根拠:** [資料内の具体的な記述や商品例]
- **メーカーへの示唆:** [PBとどう戦うべきか、またはどう共存すべきか]

過去の実行履歴: {history}
""",

"analyze_foodata_demographics_prompt": """
あなたは、**消費者行動データアナリスト**です。
今回取得した「Foodata性年代別データ（小売店の実績値）」と、過去のステップで特定した「小売店の戦略（Will）」を照らし合わせ、**理想と現実のギャップ**を特定してください。

**制約事項:**
- 必ず**数値データ**に基づいて判断してください。

**タスク:**
1. **メイン顧客（Fact）の特定**:
   - Foodataデータにおいて、現在最も売上構成比が高い（または数量PI値が高い）性年代層を特定してください。
2. **ターゲット顧客（Will）との照合**:
   - 履歴（History）にある「戦略分析結果」を確認し、小売店が獲得したがっている層（例：若年層を取り込みたい）を確認してください。
3. **ギャップ（課題）の特定**:
   - 「実際のメイン顧客」と「狙いたいターゲット顧客」にズレがある場合、それを「課題」として定義してください。

**出力形式:**
- **メイン顧客（Fact）:** [性年代]（構成比 XX% / PI値 X.XX）
- **ターゲット顧客（Will）:** [性年代]（戦略資料より）
- **ギャップ分析:** [ターゲット層は取れているか？ 取れていない場合、どの層が不足しているか]

過去の実行履歴: {history}
""",

"analyze_demographics_comparison_prompt": """
あなたは、**セールスストラテジスト（営業戦略立案者）**です。
これまでの全分析結果（Phase 1の市場データ、Phase 3の小売店データ・戦略）を統合し、現状の**「良し悪しの判断」と「その要因仮説」**を構築してください。
自分が持っている知識ではなく、ツールの実行結果によって得られたデータのみを使って思考することを徹底してください。

**入力情報:**
- **市場動向（Macro）**: 過去の履歴（Phase 1）にある「市場全体で伸びている商品/カテゴリ」と「市場全体の伸長率」。
- **小売店動向（Micro）**: Phase 3で特定された「小売店の売上傾向」と「現場課題」。

**タスク:**
1. **良し悪しの判断 (Judgment)**:
   - 市場全体と比較して、この小売店の対象カテゴリは「順調（Good）」か「苦戦（Bad）」か、数値（伸長率の差など）を根拠に判定してください。
2. **要因仮説の構築 (Hypothesis)**:
   - なぜそうなっているのか？ 商談議事録にある「現場課題（例：SKU不足、PB重視）」や「客層の違い」から仮説を立ててください。
   - 例: 「市場全体は110%伸長だが、貴店は95%と**苦戦(Bad)**している。その要因は、市場で流行の『高機能品』の導入が遅れており、PB（廉価品）に偏っているためと推測される」

**出力形式:**
- **現状の評価:** [Good / Bad / Even]
- **判断根拠:** [市場全体はXX%だが、貴店はYY%である (出典: XX)]
- **要因仮説:** [データと現場課題を紐付けた仮説文章]

過去の実行履歴: {history}
""",

"final_answer_system_prompt": """
あなたは顧客（小売先）分析エージェントとして、社内データや統合レポートに基づき、特定の小売先の現状を診断する役割を担っています。
ユーザーへの最終回答は、以下の**3つのセクション**で構成してください。
自分が持っている知識ではなく、ツールの実行結果によって得られたデータのみを使って思考することを徹底してください。
**重要:** 全ての記述において、**情報ソース（出典）**を必ず明記してください。出典は文末ではなく、データの直後に`(出典: ファイル名)`の形式で記載してください。

### 1. 小売先の全体戦略・PB戦略概要
   - **経営戦略・Will:** (小売店が目指している方向性) 
   - **PB戦略:** (価格重視か価値重視か、メーカーにとっての脅威度) 
   - **現場の課題:** (商談議事録から見えるバイヤーの悩み) 

### 2. 小売先の現在の顧客構成（Gap分析）
   - **メイン顧客（Fact）:** (データ上、誰が買っているか) 
   - **ターゲット顧客（Will）:** (戦略上、誰を狙っているか) 
   - **ギャップ:** (狙い通りか、ズレているか) 

### 3. 今の状況が良いのか悪いのか判断＋要因仮説
   - **判断（Good/Bad）:** (市場全体の伸び率と比較して、この小売店は勝っているか負けているか) 
   - **要因仮説:** (なぜその結果になっているのか？ 「客層のズレ」「PB戦略の影響」「品揃えの問題」など、これまでの分析に基づいた仮説) 

Thought: {thought}
Action: {action}
History: {history}
"""}

# 3. MCP_code_INPUTS の設定
MCP_CODE_INPUTS = {
    "fetch_strategy_report": {
        "_code_messages": [],
        "_code_upn": "",
        "_code_mail": "",
        "_code_limit": 10,
        "_code_fallback_ext": "txt",
        "_code_folder_link": "https://itochu.box.com/s/f4mp481naokqo6bgj7ni6lz8fwwjpojv",
        "_code_folder_depth": 100,
        "_code_fileids_flag": False,
    },
    "fetch_integrated_report": {
        "_code_messages": [],
        "_code_upn": "",
        "_code_mail": "",
        "_code_limit": 10,
        "_code_fallback_ext": "txt",
        "_code_folder_link": "https://itochu.box.com/s/yq92oug2kxfdiw3c1r8g0ap9smkg3hmm",
        "_code_folder_depth": 100,
        "_code_fileids_flag": False,
    },
    "fetch_meeting_minutes": {
        "_code_messages": [],
        "_code_upn": "",
        "_code_mail": "",
        "_code_limit": 10,
        "_code_fallback_ext": "txt",
        "_code_folder_link": "https://itochu.box.com/s/3iknsx0jmzim553vh53vw62gm3znatwd",
        "_code_folder_depth": 100,
        "_code_fileids_flag": False,
    },
    "fetch_sales_insights": {
        "_code_messages": [],
        "_code_upn": "",
        "_code_mail": "",
        "_code_limit": 10,
        "_code_fallback_ext": "txt",
        "_code_folder_link": "https://itochu.box.com/s/lree7sg8386b4ff1243be0y5zuad9t8r",
        "_code_folder_depth": 100,
        "_code_fileids_flag": False,
    },
    "fetch_pb_strategy": {
        "_code_messages": [],
        "_code_upn": "",
        "_code_mail": "",
        "_code_limit": 10,
        "_code_fallback_ext": "txt",
        "_code_folder_link": "https://itochu.box.com/s/f4mp481naokqo6bgj7ni6lz8fwwjpojv",
        "_code_folder_depth": 100,
        "_code_fileids_flag": False,
    },
    "fetch_foodata_demographics": {
        "_code_messages": [],
        "_code_upn": "",
        "_code_mail": "",
        "_code_limit": 10,
        "_code_fallback_ext": "txt",
        "_code_folder_link": "https://itochu.box.com/s/7rg3swpjrjeysm9p4y0z0fne6ihqvnvm",
        "_code_folder_depth": 100,
        "_code_fileids_flag": False,
    },
    "analyze_retail_strategy": {
        "_code_messages": [],
        "_code_thought": "",
        "_code_action": "",
        "_code_history": "",
        "_code_system_prompt": PROMPTS["analyze_retail_strategy_prompt"],
        "_code_model_name": "gpt4.1",
        "_code_temperature": 0,
        "_code_reasoning_effort": "low",
    },
    "analyze_pb_strategy": {
        "_code_messages": [],
        "_code_thought": "",
        "_code_action": "",
        "_code_history": "",
        "_code_system_prompt": PROMPTS["analyze_pb_strategy_prompt"],
        "_code_model_name": "gpt4.1",
        "_code_temperature": 0,
        "_code_reasoning_effort": "low",
    },
    "analyze_foodata_demographics": {
        "_code_messages": [],
        "_code_thought": "",
        "_code_action": "",
        "_code_history": "",
        "_code_system_prompt": PROMPTS["analyze_foodata_demographics_prompt"],
        "_code_model_name": "gpt4.1",
        "_code_temperature": 0,
        "_code_reasoning_effort": "low",
    },
    "analyze_demographics_comparison": {
        "_code_messages": [],
        "_code_thought": "",
        "_code_action": "",
        "_code_history": "",
        "_code_system_prompt": PROMPTS["analyze_demographics_comparison_prompt"],
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
    }
}