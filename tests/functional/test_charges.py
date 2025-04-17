import requests
import pytest

@pytest.mark.parametrize("amount,expected_status", [
    (1000, 200),  # valid
    (0, 400),     # too low
    (-500, 400),  # negative
    (999999999, 400)  # too high (Stripe will likely reject it)
])
def test_charge_with_varied_amounts(stripe_headers, amount, expected_status):
    base_url = os.getenv("BASE_URL")
    data = {
        "amount": amount,
        "currency": "usd",
        "source": "tok_visa",
        "description": "Charge from PyTest"
    }
    response = requests.post(f"{base_url}/charges", headers=stripe_headers, data=data)
    assert response.status_code == expected_status
    body = response.json()
    if expected_status == 200:
        assert body["object"] == "charge"
        assert body["amount"] == amount
        assert body["currency"] == "usd"
        assert body["status"] == "succeeded"
    else:
        print("Failed response: ", body)
        assert False