# conftest.py
import pytest
import os
import requests

# Only load .env when running locally
if os.getenv("GITHUB_ACTIONS") != "true":
    from dotenv import load_dotenv
    load_dotenv()

@pytest.fixture
def stripe_headers():
    api_key = os.getenv('STRIPE_API_KEY')
    if not api_key:
        raise RuntimeError("Missing STRIPE_API_KEY environment variable.")
    return {
        "Authorization": f"Bearer {api_key}",
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

