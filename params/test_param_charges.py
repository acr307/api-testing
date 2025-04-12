import requests
import pytest

@pytest.mark.parametrize("amount,expected_status", [
    (1000, 200),  # valid
    (0, 400),     # too low
    (-500, 400),  # negative
    (999999999, 400)  # too high (Stripe will likely reject it)
])
def test_charge_with_varied_amounts(base_url, stripe_headers, amount, expected_status):
    data = {
        "amount": amount,
        "currency": "usd",
        "source": "tok_visa"
    }
    response = requests.post(f"{base_url}/charges", headers=stripe_headers, data=data)
    assert response.status_code == expected_status
