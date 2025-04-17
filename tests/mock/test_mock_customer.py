import pytest
import os

def test_mock_create_customer(requests_mock):
    base_url = os.getenv("BASE_URL")
    mocked_url = f"{base_url}/customers"
    mock_response = {
        "id": "cus_mock123",
        "object": "customer",
        "email": "mocked@example.com",
        "name": "Mocked User"
    }

    # Register the mock
    requests_mock.post(mocked_url, json=mock_response, status_code=200)

    import requests
    response = requests.post(mocked_url, headers={}, data={})
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == "cus_mock123"
    assert data["object"] == "customer"
    assert data["email"] == "mocked@example.com"

def test_mock_create_customer_invalid_email(requests_mock):
    """Test mocking customer creation failure due to invalid email."""
    base_url = os.getenv("BASE_URL", "https://api.stripe.com/v1") # Provide default
    mocked_url = f"{base_url}/customers"
    # Mimic Stripe's error response for invalid email
    mock_error_response = {
        "error": {
            "code": "parameter_invalid_string",
            "doc_url": "https://stripe.com/docs/error-codes/parameter-invalid-string",
            "message": "Invalid email address.",
            "param": "email",
            "type": "invalid_request_error"
        }
    }

    # Register the mock to return 400 for any POST
    requests_mock.post(mocked_url, json=mock_error_response, status_code=400)

    import requests
    # Attempt to create customer with (implicitly) invalid data for this mock
    response = requests.post(mocked_url, headers={}, data={"email": "invalid-email", "name": "Test User"})
    data = response.json()

    assert response.status_code == 400
    assert "error" in data
    assert data["error"]["code"] == "parameter_invalid_string"
    assert data["error"]["param"] == "email"
    assert "Invalid email address." in data["error"]["message"]
