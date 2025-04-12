import requests

def test_create_charge(base_url, stripe_headers):
    data = {
        "amount": 2500,
        "currency": "usd",
        "source": "tok_visa",
        "description": "Charge from PyTest"
    }
    response = requests.post(f"{base_url}/charges", headers=stripe_headers, data=data)
    print("Response: ", response.json())
    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "charge"
    assert body["amount"] == 2500
    assert body["currency"] == "usd"
    assert body["status"] == "succeeded"
