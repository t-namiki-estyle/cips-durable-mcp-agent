import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from config import BLOB_SERVICE_CLIENT, FILE_CONTAINER_NAME

def get_datetime(timezone: str = "Asia/Tokyo", include_seconds: bool = False) -> str:
    # 日本時間のタイムゾーンを取得
    japan_tz = ZoneInfo(timezone)

    # 現在の日本時間を取得
    japan_time = datetime.now(japan_tz)

    # 日付を文字列としてフォーマット
    if include_seconds:
        date_string = japan_time.strftime("%Y-%m-%d_%H:%M:%S")
    else:
        date_string = japan_time.strftime("%Y-%m-%d")

    return date_string

async def upload_blob(prefix: str, name: str, content: bytes) -> str:
    container_client = BLOB_SERVICE_CLIENT.get_container_client(FILE_CONTAINER_NAME)

    blob_name = prefix + name.replace("/", "_")
    blob_client = container_client.get_blob_client(blob_name)
    base, ext = blob_name.rsplit(".", 1)
    while await blob_client.exists():
        blob_name = f"{base}_{uuid.uuid4().hex}.{ext}"
        blob_client = container_client.get_blob_client(blob=blob_name)

    await blob_client.upload_blob(content, overwrite=False)
    return blob_name