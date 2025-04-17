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

def test_get_non_existent_customer(stripe_headers):
    """Test retrieving a customer ID that does not exist."""
    base_url = os.getenv("BASE_URL")
    customer_id = "cus_invalid" # Non-existent ID
    response = requests.get(f"{base_url}/customers/{customer_id}", headers=stripe_headers)
    assert response.status_code == 404 # Expect Not Found
    body = response.json()
    assert "error" in body
    assert body["error"].get("code") == "resource_missing"
    print(f"Validated GET non-existent customer, Error: {body['error']}")

def test_update_non_existent_customer(stripe_headers):
    """Test updating a customer ID that does not exist."""
    base_url = os.getenv("BASE_URL")
    customer_id = "cus_invalid" # Non-existent ID
    data = {"description": "Updated description for non-existent customer"}
    response = requests.post(f"{base_url}/customers/{customer_id}", headers=stripe_headers, data=data)
    assert response.status_code == 404 # Expect Not Found
    body = response.json()
    assert "error" in body
    assert body["error"].get("code") == "resource_missing"
    print(f"Validated UPDATE non-existent customer, Error: {body['error']}")

def test_delete_non_existent_customer(stripe_headers):
    """Test deleting a customer ID that does not exist."""
    base_url = os.getenv("BASE_URL")
    customer_id = "cus_invalid" # Non-existent ID
    response = requests.delete(f"{base_url}/customers/{customer_id}", headers=stripe_headers)
    assert response.status_code == 404 # Expect Not Found
    body = response.json()
    assert "error" in body
    assert body["error"].get("code") == "resource_missing"
    print(f"Validated DELETE non-existent customer, Error: {body['error']}")
