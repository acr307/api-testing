# Security tests related to Stripe Card objects
import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch API key and base URL
API_KEY = os.getenv('STRIPE_API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://api.stripe.com/v1')

# Define valid headers for setup purposes (e.g., creating a customer to test against)
VALID_HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Define invalid/missing headers for testing
INVALID_HEADERS = {'Authorization': 'Bearer sk_test_invalidkey'}
NO_AUTH_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

# Placeholder IDs (replace with actual IDs created during tests if needed, but often not necessary for auth checks)
DUMMY_CUSTOMER_ID = "cus_dummy_sec_test"
DUMMY_CARD_ID = "card_dummy_sec_test"

# Skip all tests in this module if API key is not set
pytestmark = pytest.mark.skipif(not API_KEY, reason='STRIPE_API_KEY environment variable not set')

# --- Test Card Operations without Authentication ---

def test_security_create_card_no_auth():
    """Verify creating a card fails without authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources'
    data = {'source': 'tok_visa'}
    response = requests.post(url, headers=NO_AUTH_HEADERS, data=data)
    assert response.status_code == 401

def test_security_retrieve_card_no_auth():
    """Verify retrieving a card fails without authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources/{DUMMY_CARD_ID}'
    response = requests.get(url, headers=NO_AUTH_HEADERS)
    assert response.status_code == 401

def test_security_list_cards_no_auth():
    """Verify listing cards fails without authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources'
    response = requests.get(url, headers=NO_AUTH_HEADERS)
    assert response.status_code == 401

def test_security_update_card_no_auth():
    """Verify updating a card fails without authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources/{DUMMY_CARD_ID}'
    data = {'name': 'Update Attempt No Auth'}
    response = requests.post(url, headers=NO_AUTH_HEADERS, data=data)
    assert response.status_code == 401

def test_security_delete_card_no_auth():
    """Verify deleting a card fails without authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources/{DUMMY_CARD_ID}'
    response = requests.delete(url, headers=NO_AUTH_HEADERS)
    assert response.status_code == 401

# --- Test Card Operations with Invalid Authentication ---

def test_security_create_card_invalid_auth():
    """Verify creating a card fails with invalid authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources'
    data = {'source': 'tok_visa'}
    response = requests.post(url, headers=INVALID_HEADERS, data=data)
    assert response.status_code == 401

def test_security_retrieve_card_invalid_auth():
    """Verify retrieving a card fails with invalid authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources/{DUMMY_CARD_ID}'
    response = requests.get(url, headers=INVALID_HEADERS)
    assert response.status_code == 401

def test_security_list_cards_invalid_auth():
    """Verify listing cards fails with invalid authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources'
    response = requests.get(url, headers=INVALID_HEADERS)
    assert response.status_code == 401

def test_security_update_card_invalid_auth():
    """Verify updating a card fails with invalid authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources/{DUMMY_CARD_ID}'
    data = {'name': 'Update Attempt Invalid Auth'}
    response = requests.post(url, headers=INVALID_HEADERS, data=data)
    assert response.status_code == 401

def test_security_delete_card_invalid_auth():
    """Verify deleting a card fails with invalid authentication."""
    url = f'{BASE_URL}/customers/{DUMMY_CUSTOMER_ID}/sources/{DUMMY_CARD_ID}'
    response = requests.delete(url, headers=INVALID_HEADERS)
    assert response.status_code == 401

# TODO: Add tests for accessing cards across different customers (if feasible/needed)
