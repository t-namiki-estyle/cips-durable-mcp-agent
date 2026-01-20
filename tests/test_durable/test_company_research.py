import requests
import json
import uuid
import pytest

def test_company_research():
    url = "http://localhost:7071/api/durable/agent_orchestrator"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "max_steps": 10,
        "mode": "company_research",
        "upn": "A227003@intra.itochu.co.jp",
        "mail": "takeuchi-yuki@itochu.co,jp",
        "session_id": str(uuid.uuid4()),
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": "調査対象企業の詳細調査を開始してください。\n\n### 引き継ぎ情報\n- 調査対象企業: 株式会社ニップン\n- 法人番号: 9011001017684\n- 企業住所: 東京都千代田区麹町４丁目８番地\n\n上記の企業について、包括的な投資調査を実行してください。"}]}
        ]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)
        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
        
        # company_research モードの基本動作確認
        if response.status_code == 200:
            # 同期レスポンスの場合
            assert "messages" in response_json, "messages not found in response"
        elif response.status_code == 202:
            # Durable Functions の非同期処理の場合
            assert "id" in response_json, "orchestration id not found"
            print("✅ Company research orchestration started successfully")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")