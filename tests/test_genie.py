import requests
import json
import base64
import pytest

@pytest.mark.skip(reason="サンプルコードのためスキップします。")
def test_genie(id_token, upn, mail):
    base_url = "http://localhost:7071/api/genie"
    url = f"{base_url}?id_token={id_token}"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "mode": "others",
        "model": "gpt4o",
        "from": "web",
        "upn": upn,
        "mail": mail,
        "messages": [{ "role": "user", "content": "自己紹介してください" }]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)

        print(f"response_json: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        assert "choices" in response_json, "Response lacks 'choices' key"
    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")


def test_sample_with_name():
    url = "http://localhost:7071/api/durable/greed_manager"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "name": "toriiii"
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)

        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")

def test_sample_without_name():
    url = "http://localhost:7071/api/durable/greed_manager"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {}

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)

        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")