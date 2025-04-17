import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch API key and base URL once
API_KEY = os.getenv('STRIPE_API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://api.stripe.com/v1')

# Headers for authenticated requests
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/x-www-form-urlencoded' # Stripe uses form-encoded data
}

# Skip all tests in this module if API key is not set
pytestmark = pytest.mark.skipif(not API_KEY, reason='STRIPE_API_KEY environment variable not set')

# --- Authentication Tests --- 

def test_security_no_auth_customer():
    """Verify accessing customer endpoint fails without authentication."""
    customer_url = f'{BASE_URL}/customers'
    response = requests.get(customer_url) # No Auth header
    assert response.status_code == 401 # Expect Unauthorized

def test_security_no_auth_charge():
    """Verify accessing charge endpoint fails without authentication."""
    charge_url = f'{BASE_URL}/charges'
    response = requests.get(charge_url) # No Auth header
    assert response.status_code == 401 # Expect Unauthorized

def test_security_invalid_auth_customer():
    """Verify accessing customer endpoint fails with invalid authentication."""
    customer_url = f'{BASE_URL}/customers'
    invalid_headers = HEADERS.copy()
    invalid_headers['Authorization'] = 'Bearer sk_test_invalidkey'
    response = requests.get(customer_url, headers=invalid_headers)
    assert response.status_code == 401 # Expect Unauthorized

# --- Input Validation / Basic Authorization Tests --- 

def test_security_create_charge_invalid_token():
    """Verify creating a charge with an invalid token fails correctly."""
    charge_url = f'{BASE_URL}/charges'
    data = {
        'amount': 500,
        'currency': 'usd',
        'source': 'tok_invalid_token' # A non-existent token
    }
    response = requests.post(charge_url, headers=HEADERS, data=data)
    # Expect a client error (e.g., 400 Bad Request or specific Stripe error code)
    assert 400 <= response.status_code < 500 
    # Check for Stripe-specific error structure (optional but good)
    error_data = response.json().get('error', {})
    assert error_data.get('type') == 'invalid_request_error'
    assert 'part of the token that is not valid' in error_data.get('message', '')

def test_security_get_nonexistent_customer():
    """Verify fetching a non-existent customer fails correctly."""
    customer_url = f'{BASE_URL}/customers/cus_nonexistentid'
    response = requests.get(customer_url, headers=HEADERS)
    # Expect Not Found or similar error
    assert response.status_code == 404 
    error_data = response.json().get('error', {})
    assert error_data.get('type') == 'invalid_request_error'
    assert 'No such customer' in error_data.get('message', '')

def test_security_create_customer_invalid_email():
    """Verify creating a customer with an invalid email fails."""
    customer_url = f'{BASE_URL}/customers'
    data = {'email': 'invalid-email-format'}
    response = requests.post(customer_url, headers=HEADERS, data=data)
    # Expect a client error due to invalid parameter
    assert 400 <= response.status_code < 500
    error_data = response.json().get('error', {})
    assert error_data.get('type') == 'invalid_request_error'
    assert error_data.get('param') == 'email'
