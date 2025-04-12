import requests

def test_create_customer(base_url, stripe_headers):
    data = {
        "email": "pytest_user@example.com",
        "name": "PyTest User"
    }
    response = requests.post(f"{base_url}/customers", headers=stripe_headers, data=data)
    print("Response: ", response.json())
    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "customer"
    assert body["email"] == "pytest_user@example.com"