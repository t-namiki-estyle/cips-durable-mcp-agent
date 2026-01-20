import json
import logging
import azure.durable_functions as d_func
from i_style.aiohttp import AsyncHttpClient
from config import GENIE_AUTH_URL, GENIE_AUTH_API_KEY

bp = d_func.Blueprint()

@bp.activity_trigger(input_name="payload")
async def check_mode_permission(payload: dict) -> dict:
    """
    ユーザーが指定されたmodeを実行する権限を持っているかを確認する。
    mode名に"_gpt"を付与した文字列が、権限リストのいずれかの項目に完全一致すれば許可する。
    """
    payload = json.loads(payload)
    upn = payload.get("upn")
    mode = payload.get("mode")

    if not all([upn, mode]):
        logging.error(f"Invalid input: 'upn' and 'mode' are required. Payload: {payload}")
        return {"status": 400, "error": "Invalid input: 'upn' and 'mode' are required.", "is_authorized": False}

    # APIリクエスト
    url = GENIE_AUTH_URL
    params = {"upn": upn}
    headers = {}
    if GENIE_AUTH_API_KEY:
        headers["x-functions-key"] = GENIE_AUTH_API_KEY
    
    allowed_permissions = []
    try:
        client = AsyncHttpClient()
        resp = await client.get(url, params=params, headers=headers)
        logging.info(f"Response from GENIE AUTH API: {json.dumps(resp, indent=2, ensure_ascii=False)}")
        
        # レスポンスチェック
        if not isinstance(resp, dict) or resp.get("status") != 200:
            logging.warning(f"Failed to get valid permissions for upn: {upn}. Assuming no permissions.")
        else:
            perms = (resp.get("data") or {}).get("permissions") or {}
            allowed_permissions = perms.get("allowed", []) or []

    except Exception as e:
        logging.exception("check_mode_permission: request failed") # 例外時もallowed_permissionsは空リストのまま

    # 権限チェックロジック
    is_authorized = f"{mode}_gpt" in allowed_permissions
    
    if is_authorized:
        logging.info(f"UPN: {upn} is AUTHORIZED for mode: '{mode}'.")
    else:
        logging.warning(f"UPN: {upn} is NOT AUTHORIZED for mode: '{mode}'.")

    return {"status": 200, "is_authorized": is_authorized}