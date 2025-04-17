import requests
import pytest

@pytest.fixture
def stripe_headers():
    return {
        "Authorization": f"Bearer {os.getenv('STRIPE_API_KEY')}",
        "Content-Type": "application/json"
    }

def test_authenticate(stripe_headers):
    response = requests.get("https://api.stripe.com/v1/charges", headers=stripe_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "charge"
    assert body["amount"] == 2500
    assert body["currency"] == "usd"
    assert body["status"] == "succeeded"

def test_invalid_auth():
    response = requests.get("{base_url}/charges", headers={"Authorization": "Bearer invalid_key"})
    assert response.status_code == 401