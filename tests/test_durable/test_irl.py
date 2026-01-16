import requests
import json
import uuid
import base64
import pytest


def test_irl():
    url = "http://localhost:7071/api/durable/agent_orchestrator"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "max_steps": 10,
        "mode": "irl",
        "upn": "y.fujimori@estyle-inc.jp",
        "session_id": str(uuid.uuid4()),
        "messages": [
            {"role": "user", "content":[{"type": "text", "text": "ニトリル手袋"}]}
        ]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)

        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")
