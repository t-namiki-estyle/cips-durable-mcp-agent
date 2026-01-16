import azure.durable_functions as d_func
import logging
import json

import openai
from pydantic import BaseModel, Field, ValidationError

from i_style.llm import AzureOpenAI, ModelRegistry
from i_style.aiohttp import AsyncHttpClient
from i_style.messages import Messages

from blueprints.activity.util import get_history, check_token
from blueprints.activity.helper import get_datetime
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
async def choose_tool(payload: dict) -> dict:
    """
    ユーザーとのやり取り、ツールの説明をもとにエージェントが実行すべきツールを選択するactivity関数。

    Args:
        payload (dict): ツール選択に必要な情報を含む辞書。
            - session_id
            - agent_id
            - upn
            - mode
            - submode
            - messages (List[dict], optional): ユーザーとのやり取り
            - agent_system_prompt (str): エージェントのシステムプロンプト
            - tool_list (List[dict]): 使用可能なツールの情報（name, description を含む辞書）。
            - model_name (str, optional): 使用するLLMモデルの名前（デフォルト: "gpt4.1"）。
            - summarize_threshold（dict, optional）: 履歴要約の閾値設定（デフォルト：{ "min_input_token_model": "o4-mini", "margin": 0 }）。

    Returns:
        dict: エージェントの思考、行動、選択されたツール名を含む辞書。
              形式: {"thought": "...", "action": "...", "tool": "ツール名"}

    Raises:
        Exception: OpenAIからの応答に関するエラー、もしくは構造化データの解析エラー。
    """
    data = payload if isinstance(payload, dict) else json.loads(payload)

    session_id = data.get("session_id", "")
    agent_id = data.get("agent_id", "")
    upn = data.get("upn", None)
    mode = data.get("mode", "default")
    submode: str | bool = data.get("submode", False)

    messages = data.get("messages", [])
    agent_system_prompt = data.get("agent_system_prompt", "")
    tool_list = data.get("tool_list", [])

    model_name = data.get("model_name", "gpt4.1")

    summarize_threshold = data.get("summarize_threshold", {})
    min_input_token_model = summarize_threshold.get("min_input_token_model", "o4-mini") # 少なめのo seriesのものをデフォルトに指定
    margin = summarize_threshold.get("margin", 0)

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

    # CosmosDBから今までの実行履歴を取得
    async_http_client= AsyncHttpClient()
    history = await get_history(mode, upn, session_id, agent_id, async_http_client)

    history_tokens = check_token(history)
    logging.info(f"tokens: {history_tokens}")

    # AOAIで出力する形式の定義
    class ChooseToolOutput(BaseModel):
        thought: str = Field(..., description="ここにあなたの思考プロセスを詳しく書いてください")
        action:  str = Field(..., description="具体的に何をするのかを端的かつ詳細に書いてください")
        tool:    str = Field(
            ...,
            description="実行するツール名",
            json_schema_extra={"enum":[t["name"] for t in tool_list]}
        )

    # token数を確認してtoolを選択させるか分岐
    ## 使用するモデルの中で最小の入力トークン数のモデルを基準に、任意のマージンを引いた値を閾値とすることで、トークン数超過前に実行履歴の削減を行う
    if history_tokens <= registry.get_available_input_token(min_input_token_model) - margin:
        # AOAIでtoolを選択
        prompt_system = agent_system_prompt.format(
            history=history,
            tool_explanation="\n".join(f'{t["name"]}: {t["description"]}' for t in tool_list),
            get_datetime=get_datetime()
        )
        # Messagesクラスでmessagesを整形
        msgs_instance = await Messages.init_with_conversion(
            text_extractor=FILE_TEXT_EXTRACTOR, 
            messages=messages, 
            prefix=f"{upn}/{mode}",
            blob_service_client=BLOB_SERVICE_CLIENT
        )
        messages = await msgs_instance.get_messages("aoai") # messagesをAOAI形式に変換
        choose_tool_messages = [{"role": "system", "content": prompt_system}] + messages

        max_retries = 5
        for i in range(max_retries):
            response = await AzureOpenAI(
                messages=choose_tool_messages,
                raise_for_error=True,
                json_mode=True,
                model_name=model_name,
                registry=registry,
                tools=[openai.pydantic_function_tool(ChooseToolOutput)],
                tool_choice="required"
            )
            choose_tool_response = response["choices"][0]["message"]["tool_calls"][0]
            try:
                choose_tool_response = ChooseToolOutput.parse_raw(choose_tool_response["function"]["arguments"])
                choose_tool_response = choose_tool_response.model_dump()
                break
            except ValidationError as e:
                logging.warning(f"validate_error_{i+1}: {e}, args: {choose_tool_response['function']['arguments']}")
                if i == max_retries-1:
                    logging.error(f"validate_error")
                    choose_tool_response = ChooseToolOutput(
                        thought="次のツールを選択することができなかったため、現状でわかっている情報を最大限に活かしてユーザーに対して回答を行う必要がある",
                        action="final_answerを用いてユーザーへの最終回答を作成する",
                        tool="final_answer"
                    ).model_dump()

    else:
        # tool実行履歴の削減
        choose_tool_response = ChooseToolOutput(
            thought="これまでのやり取りで会話履歴が長くなり、プロンプトのトークン数が上限に近づいている。エラーを回避するため、履歴を要約する必要がある。",
            action="`summarize_history`ツールを使い、これまでの会話とツール実行の履歴を要約する。",
            tool="summarize_history"
        ).model_dump()

    # 履歴の登録
    request_data = {
        "items": [
            {
                "sessionId": session_id,
                "agentId": agent_id,
                "upn": upn,
                "content": [
                    {"type": "text", "text": json.dumps(choose_tool_response, ensure_ascii=False)},
                ],
                "role": "assistant",
                "type": "agent",
                "model": model_name,
                **({"submode": submode} if submode else {})
            }
        ]
    }

    url = f"{HISTORY_API_URL}/api/history/{mode}"
    api_name = "add_history"
    try:
        response = await async_http_client.post(url=url, api_key=HISTORY_API_KEY, json_data=request_data, process_name=api_name)
    except Exception as e:
        logging.warning(f"LLMによるTool選択結果を追加: {e}")


    return choose_tool_response  # {"thought": "...", "action": "...", "tool": "..."}

