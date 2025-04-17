import requests
import pytest
import os

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
        # Check that the response body contains an error object
        assert "error" in body
        assert "message" in body["error"] # Further check for a message

@pytest.mark.parametrize("missing_param", ["amount", "currency", "source"])
def test_charge_missing_parameters(stripe_headers, missing_param):
    """Test creating a charge with missing required parameters."""
    base_url = os.getenv("BASE_URL")
    data = {
        "amount": 1000,
        "currency": "usd",
        "source": "tok_visa",
        "description": "Charge missing param test"
    }
    # Remove the parameter being tested
    del data[missing_param]

    response = requests.post(f"{base_url}/charges", headers=stripe_headers, data=data)
    assert response.status_code == 400  # Expect Bad Request

    body = response.json()
    assert "error" in body
    assert "message" in body["error"]
    # Check if the error message mentions the missing parameter
    assert missing_param in body["error"].get("param", "") or missing_param in body["error"].get("message", "")
    print(f"Validated missing parameter: {missing_param}, Error: {body['error']}")

def test_charge_invalid_currency(stripe_headers):
    """Test creating a charge with an invalid currency code."""
    base_url = os.getenv("BASE_URL")
    data = {
        "amount": 1000,
        "currency": "XYZ",  # Invalid currency code
        "source": "tok_visa",
        "description": "Charge invalid currency test"
    }

    response = requests.post(f"{base_url}/charges", headers=stripe_headers, data=data)
    assert response.status_code == 400  # Expect Bad Request

    body = response.json()
    assert "error" in body
    assert "message" in body["error"]
    assert body["error"].get("param") == "currency"
    print(f"Validated invalid currency, Error: {body['error']}")

@pytest.mark.parametrize("token, expected_error_code", [
    ("tok_chargeDeclined", "card_declined"),
    ("tok_chargeDeclinedInsufficientFunds", "card_declined") # Stripe often returns generic card_declined even for insufficient funds in test mode
])
def test_charge_declined_tokens(stripe_headers, token, expected_error_code):
    """Test creating a charge with tokens that simulate declines."""
    base_url = os.getenv("BASE_URL")
    data = {
        "amount": 2000, # Use a different amount to avoid identical requests
        "currency": "usd",
        "source": token, # Use the declined token
        "description": f"Charge decline test ({token})"
    }

    response = requests.post(f"{base_url}/charges", headers=stripe_headers, data=data)
    assert response.status_code == 402  # Payment Required is the typical code for declines

    body = response.json()
    assert "error" in body
    assert "message" in body["error"]
    assert body["error"].get("code") == expected_error_code
    # Note: Stripe might sometimes return a more specific decline_code like 'insufficient_funds'
    # assert body["error"].get("decline_code") == expected_decline_code
    print(f"Validated declined token: {token}, Error: {body['error']}")