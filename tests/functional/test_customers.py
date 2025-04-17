import requests
import pytest
import os

@pytest.mark.parametrize("email,name", [
    ("param1@example.com", "Param One"),
    ("param2@example.com", "Param Two"),
    ("param3@example.com", "Param Three")
])
def test_create_customer_param(stripe_headers, email, name):
    base_url = os.getenv("BASE_URL")
    data = {
        "email": email,
        "name": name
    }
    response = requests.post(f"{base_url}/customers", headers=stripe_headers, data=data)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == email
    assert body["name"] == name
