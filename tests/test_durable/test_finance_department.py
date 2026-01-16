import requests
import json
import uuid
import base64
import pytest
import os


def test_finance_department():
    url = "http://localhost:7071/api/durable/agent_orchestrator"
    api_key = os.environ.get("DURABLE_FUNCTIONS_API_KEY")
    if not api_key:
        pytest.fail(
            "Environment variable DURABLE_FUNCTIONS_API_KEY is not set. Please set it before running the test.")

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "max_steps": 10,
        "mode": "finance_department",
        "upn": "n.tobita@estyle-inc.jp",
        "session_id": str(uuid.uuid4()),
        "messages": [
            # TODO: エージェントの入力を記載する
            {"role": "user", "content": [{"type": "text", "text": "試したい入力"}]}
        ]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)
        print(
            f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(
            f"Request failed with status {response.status_code}: {response.text}")
