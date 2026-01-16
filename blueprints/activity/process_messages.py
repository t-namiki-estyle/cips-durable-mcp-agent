import os
import uuid
import logging
from collections import defaultdict

import azure.durable_functions as d_func
from i_style.messages import Messages

from blueprints.activity.util import mcp_list_tools
from config import LLM_REGISTRY, FILE_TEXT_EXTRACTOR, BLOB_SERVICE_CLIENT
from helper import FINANCE_DEPARTMENT_FILE_TEXT_EXTRACTOR

bp = d_func.Blueprint()


@bp.activity_trigger(input_name="payload")
async def process_messages(payload: dict) -> dict:
    """
    messagesの添付ファイル処理を行うactivity関数。
    この関数は、messagesの整形を行い、添付ファイルの場合、blobに保存し、messagesの内容をBlobパスに変換します。

    Args:
        payload (dict): 関数トリガーの入力
            - messages (list): ユーザーからのメッセージ履歴
            - mode (str): エージェントID。渡されない場合はこの関数内で作成する。
            - upn (str): MCPサーバーのドメインとキーのリスト。

    Returns:
        dict: エージェントの初期化に必要な情報を含む辞書。
            - messages (list): 整形されたメッセージのリスト。
            - blobs (dict): 添付ファイルの情報を含む辞書。

    Raises:
        Exception: MCP通信またはツール取得中にエラーが発生した場合。
    """
    # messagesを整形（添付ファイルの処理など）
    messages = payload.get("messages", [])
    mode = payload.get("mode", "default")
    upn = payload.get("upn", "")

    # modeに応じてFileTextExtractorを選択
    if mode == "finance_department":
        text_extractor = FINANCE_DEPARTMENT_FILE_TEXT_EXTRACTOR
    else:
        text_extractor = FILE_TEXT_EXTRACTOR

    try:
        msgs = await Messages.init_with_conversion(
            text_extractor=text_extractor,
            messages=messages, prefix=f"{upn}/{mode}",
            blob_service_client=BLOB_SERVICE_CLIENT
        )
        return {
            "messages": await msgs.get_messages(),
            "blobs": msgs.blobs
        }
    except Exception as e:
        logging.error(f"Error processing messages: {e}")
        raise