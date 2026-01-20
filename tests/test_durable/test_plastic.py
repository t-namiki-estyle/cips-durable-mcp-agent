import requests
import json
import uuid
import base64
import pytest

def test_mode():
    url = "http://localhost:7071/api/durable/agent_orchestrator"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "max_steps": 10,
        "mode": "plastic",
        "upn": "y.fujimori@estyle-inc.jp",
        "session_id": str(uuid.uuid4()),
        "messages": [
            # {"role": "user", "content":[{"type": "text", "text": "グレードS1003のMFRを教えてください。"}]}
            # {"role": "user", "content":[{"type": "text", "text": "FCFCのPPの生産キャパシティを教えてください。"}]}
            {"role": "user", "content":[{"type": "text", "text": "MFRが5付近のグレードをリストアップしてください。"}]}
        ]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)
        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")
