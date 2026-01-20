import os
import logging

import azure.durable_functions as d_func

from i_style.aiohttp import AsyncHttpClient
from config import HISTORY_API_URL, HISTORY_API_KEY

bp = d_func.Blueprint()

@bp.activity_trigger(input_name="payload")
async def add_history(payload: dict) -> None:
    """
    プロンプト履歴への登録を行うactivity関数。
    この関数は、ユーザーからの入力、エージェントからの回答をプロンプト履歴に登録する。
    ステータスが指定されている場合、セッションステータスも更新する。

    Args:
        payload (dict): 関数トリガーの入力
            - mode(str): agentのmode名。submodeが設定されているときは`genie`として渡される。
            - items(list): 履歴に登録するメッセージのリスト
            - status (str, optional): セッションのステータス。指定されている場合、セッションステータスも更新する。

    Returns:
        None

    Raises:
        Exception: history functionとの接続中にエラーが発生した場合。
    """
    logging.info("starting add_history")

    async_http_client= AsyncHttpClient()

    mode = payload.get("mode", "default")
    status = payload.get("status", "")
    items = payload.get("items", [])
    upn = items[0].get("upn", "")
    if not upn:
        logging.warning("upn is missing in the items.")
    session_id = items[0].get("sessionId", "")
    if not session_id:
        logging.warning("session_id is missing in the items.")

    url = f"{HISTORY_API_URL}/api/history/{mode}"
    request_data = {
        "items": items
    }

    api_name = "add_history"
    try:
        response = await async_http_client.post(url=url, api_key=HISTORY_API_KEY, json_data=request_data, process_name=api_name)
    except Exception as e:
        logging.warning(f"履歴の追加: {e}")
        raise

    if status:
        update_history_url = f"{HISTORY_API_URL}/api/history/{mode}/{upn}"
        update_data = {
            "session_id": session_id,
            "status": status
        }

        api_name = "update_session_status"
        try:
            response = await async_http_client.post(url=update_history_url, api_key=HISTORY_API_KEY, json_data=update_data, process_name=api_name)
        except Exception as e:
            logging.warning(f"セッションステータスの更新: {e}")

    return None
