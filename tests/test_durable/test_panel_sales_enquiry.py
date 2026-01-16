import requests
import json
import uuid
import base64
import pytest

def test_panel_sales_enquiry():
    url = "http://localhost:7071/api/durable/agent_orchestrator"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "max_steps": 4,
        "mode": "panel_sales_enquiry",
        "model": "gpt4.1",
        "upn": "y.yamamoto@estyle-inc.jp",
        "session_id": str(uuid.uuid4()),
        "messages": [
            {"role": "user", "content":[{"type": "text", "text": "ダイヤゼブラのPCSについて商品の故障だと思われるがどのように対応したらよいか"}]}
        ]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)
        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")