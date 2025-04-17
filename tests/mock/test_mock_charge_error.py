import requests
import requests_mock
import os

def test_mock_charge_failure():
    with requests_mock.Mocker() as m:
        base_url = os.getenv("BASE_URL")
        mocked_url = f"{base_url}/charges"
        m.post(mocked_url, json={
            "error": {
                "type": "card_error",
                "message": "Your card was declined.",
                "code": "card_declined"
            }
        }, status_code=402)

        response = requests.post(mocked_url, headers={}, data={})
        body = response.json()

        assert response.status_code == 402
        assert body["error"]["code"] == "card_declined"
