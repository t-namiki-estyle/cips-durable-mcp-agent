import requests
import json
import uuid
import pytest

def test_company_info():
    url = "http://localhost:7071/api/durable/agent_orchestrator"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "max_steps": 10,
        "mode": "genie_agent",
        "upn": "y.takeuchi@estyle-inc.jp",
        "session_id": str(uuid.uuid4()),
        "messages": [
            {"role": "user", "content":[{"type": "text", "text": "あなたなりに複数のツールを合わせてすごい提案をしてください。伊藤忠商事でビジネスの文脈で役にたつものが良いです。ただし、商材、監査関連の各種ツールは動きません。"}]},
        ]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)
        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")
