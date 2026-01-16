import requests
import json
import uuid
import base64
import pytest


def test_research():
    url = "http://localhost:7071/api/durable/agent_orchestrator"
    api_key = ""

    headers = {
        "Content-Type": "application/json",
        "x-functions-key": api_key
    }

    data = {
        "max_steps": 10,
        "mode": "research",
        "upn": "y.takeuchi@estyle-inc.jp",
        "session_id": str(uuid.uuid4()),
        "messages": [
            # TODO 複数のcontentの型への対応追加
            # {"role": "user", "content":[{"type": "text", "text": "自律開発型のエージェントについて最新の技術動向を調査してください。"}]}
            # {"role": "user", "content":[{"type": "text", "text": "メタキシレンスルホン酸(m-Xylene-4-sulfonic Acid)が日本国内及び海外のどこで誰により製造され、誰により加工され、誰によって消費されているか、どんな用途があるか、などをレポートにしてほしい。"}]}
            # {"role": "user", "content":[{"type": "text", "text": "中国のcitic銀行の利ざやについて2025年度までの推移を調査してください"}]}
            {"role": "user", "content":[{"type": "text", "text": "openaiの各種llm, googleのgemini, anthoripicのclaudeなど各種大手のLLMについて、コンテキスト長、消費トークンのコスト、推定モデルサイズを調査してもらいたいです。"}]}
            # {"role": "user", "content": "動作確認のため、最終回答のみ作成してみてください。中身は自己紹介で良いです。"}
        ]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)

        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")
