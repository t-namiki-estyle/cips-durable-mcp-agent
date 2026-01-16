import requests
import json
import uuid
import pytest


def test_hana():
    """HANAエージェントの動作確認テスト"""
    url = "http://localhost:7071/api/durable/agent_orchestrator"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "max_steps": 10,
        "mode": "hana",
        "upn": "y.xxxxxx@estyle-inc.jp",  # TODO: 自分のメールアドレスに変更
        "session_id": str(uuid.uuid4()),
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "売上金額が100万円以上の日本アクセスとの取引の伝票Noを教えて。"
                    }
                ]
            }
        ]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)
        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")
