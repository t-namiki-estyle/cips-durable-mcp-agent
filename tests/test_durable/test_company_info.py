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
        "mode": "company_info",
        # "upn": "A227003@intra.itochu.co.jp",
        # "mail": "takeuchi-yuki@itochu.co,jp",
        "upn": "y.takeuchi@estyle-inc.jp",
        "mail": "y.takeuchi@estyle-inc.jp",
        "session_id": str(uuid.uuid4()),
        "messages": [
            # {"role": "user", "content":[{"type": "text", "text": "株式会社ミツカンの投資調査をお願いします"}]},
            # {
            #     "message": {
            #     "role": "assistant",
            #     "content": [
            #             {
            #             "type": "text",
            #             "text": "株式会社ミツカンに関連する企業が複数見つかっています。調査対象とする法人を特定するため、以下の中からご希望の企業名または法人番号を教えてください。\n\n- 株式会社Mizkan Holdings（法人番号：1180001091920、愛知県半田市中村町２丁目６番地）\n- 株式会社Mizkan（法人番号：7120001149272、愛知県半田市中村町２丁目６番地）\n- その他、上記以外の関連会社\n\nどの法人を調査対象としますか？企業名または法人番号でご指定ください。"
            #             }
            #         ]
            #     }
            # },
            # {"role": "user", "content":[{"type": "text", "text": "株式会社Mizkan（法人番号：7120001149272）でお願いします"}]},
            {"role": "user", "content":[{"type": "text", "text": "アイルランドのAccenture"}]},
            {"role": "assistant", "content":[{"type": "text", "text": "ご指定いただいた「アイルランドのAccenture」について、調査対象を特定するために以下の情報をご確認ください。\n\n- 調査対象は本社である「Accenture plc（アイルランド法人）」でよろしいでしょうか？\n- もし他の現地法人や日本法人ではなく、アイルランド本社で問題なければ「はい」とご回答ください。\n- もし法人番号や所在地など、追加でご指定があればあわせてご教示ください。\n\nご回答をお願いいたします。"}]},
            {"role": "user", "content":[{"type": "text", "text": "はい"}]},
            {"role": "assistant","content": [{"type": "text", "text": "調査対象企業について、以下の内容で間違いないかご確認ください。\n\n- 企業名：Accenture plc\n- 法人番号：471706\n- 所在地：1 Grand Canal Square, Grand Canal Harbour, Dublin 2, Ireland\n\nこの企業で調査を開始してよろしいでしょうか？「はい」または修正があればご指摘ください。"}]},
            {"role": "user", "content":[{"type": "text", "text": "はい"}]},
            # {"role": "user", "content":[{"type": "text", "text": "株式会社ニップンの投資調査をお願いします"}]},
            # {
            #     "role": "assistant",
            #     "content": [
            #         {
            #             "type": "text",
            #             "text": "株式会社ニップンの調査対象として、以下の企業情報で進めてよろしいでしょうか？\n\n- 企業名：株式会社ニップン\n- 法人番号：9011001017684\n- 住所：東京都千代田区麹町４丁目８番地\n\nご確認のうえ、問題なければ「はい」とご回答ください。"
            #         },
            #     ]
            # },
            # {"role": "user", "content":[{"type": "text", "text": "はい"}]},
        ]
    }

    data_encode = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_encode)

    try:
        response_json = json.loads(response.text)
        print(f"response_json: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

    except Exception:
        pytest.fail(f"Request failed with status {response.status_code}: {response.text}")
