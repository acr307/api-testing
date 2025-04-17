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
