import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch API key and base URL once
API_KEY = os.getenv('STRIPE_API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://api.stripe.com/v1') # Define BASE_URL

# Skip all tests in this module if API key is not set
pytestmark = pytest.mark.skipif(not API_KEY, reason='STRIPE_API_KEY environment variable not set')


@pytest.fixture
def stripe_headers():
    return {
        "Authorization": f"Bearer {API_KEY}", # Use defined API_KEY
        "Content-Type": "application/json"
    }

def test_authenticate(stripe_headers):
    # Example: test accessing a protected endpoint (e.g., list customers)
    response = requests.get(f"{BASE_URL}/customers", headers=stripe_headers)
    assert response.status_code == 200 # Expect success with valid key

def test_invalid_auth():
    # Use f-string for the URL
    response = requests.get(f"{BASE_URL}/charges", headers={"Authorization": "Bearer invalid_key"})
    assert response.status_code == 401 # Expect Unauthorized