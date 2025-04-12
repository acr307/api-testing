# conftest.py
import pytest
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def stripe_headers():
    return {
        "Authorization": f"Bearer {os.getenv('STRIPE_API_KEY')}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

@pytest.fixture
def base_url():
    return "https://api.stripe.com/v1"

@pytest.fixture
def test_customer(base_url, stripe_headers):
    data = {"email": "param_fixture@example.com", "name": "Fixture Param"}
    response = requests.post(f"{base_url}/customers", headers=stripe_headers, data=data)
    return response.json()["id"]

