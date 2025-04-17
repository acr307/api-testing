# Integration tests for the Customer -> Card -> Charge flow
import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch API key and base URL
API_KEY = os.getenv('STRIPE_API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://api.stripe.com/v1')

# Headers for authenticated requests
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Skip all tests in this module if API key is not set
pytestmark = pytest.mark.skipif(not API_KEY, reason='STRIPE_API_KEY environment variable not set')


def test_customer_card_charge_integration():
    """Tests the integrated flow of creating a customer, adding a card, and charging."""
    customer_id = None # Initialize for cleanup
    try:
        # --- Step 1: Create Customer ---
        print("\n--- Integration Test: Step 1: Create Customer ---")
        customer_url = f'{BASE_URL}/customers'
        customer_data = {
            'description': 'Integration Test Customer',
            'email': 'integration.test@example.com'
        }
        customer_response = requests.post(customer_url, headers=HEADERS, data=customer_data)
        print(f"Create Customer Response: {customer_response.status_code} {customer_response.text[:200]}...")
        assert customer_response.status_code == 200, "Failed to create customer"
        customer_id = customer_response.json()['id']
        print(f"Created Customer ID: {customer_id}")

        # --- Step 2: Create Card (Source) for Customer ---
        print("\n--- Integration Test: Step 2: Create Card Source ---")
        card_url = f'{BASE_URL}/customers/{customer_id}/sources'
        card_data = {'source': 'tok_visa'} # Use a standard test token
        card_response = requests.post(card_url, headers=HEADERS, data=card_data)
        print(f"Create Card Response: {card_response.status_code} {card_response.text[:200]}...")
        assert card_response.status_code == 200, "Failed to create card source"
        card_id = card_response.json()['id']
        print(f"Created Card ID: {card_id}")

        # --- Step 3: Create Charge using Customer and Card ---
        print("\n--- Integration Test: Step 3: Create Charge ---")
        charge_url = f'{BASE_URL}/charges'
        charge_data = {
            'amount': 500, # $5.00
            'currency': 'usd',
            'customer': customer_id,
            'source': card_id, # Charge the specific card added to the customer
            'description': f'Integration Test Charge for {customer_id}'
        }
        charge_response = requests.post(charge_url, headers=HEADERS, data=charge_data)
        print(f"Create Charge Response: {charge_response.status_code} {charge_response.text[:200]}...")
        assert charge_response.status_code == 200, "Failed to create charge"
        
        charge_body = charge_response.json()
        assert charge_body['object'] == 'charge'
        assert charge_body['status'] == 'succeeded'
        assert charge_body['customer'] == customer_id
        # Verify the charge used the correct source (card)
        assert charge_body['source']['id'] == card_id
        assert charge_body['amount'] == 500
        print(f"Successfully created Charge ID: {charge_body['id']}")

    finally:
        # --- Cleanup: Delete Customer (if created) ---
        if customer_id:
            print(f"\n--- Integration Test: Cleanup: Deleting Customer {customer_id} ---")
            delete_url = f'{BASE_URL}/customers/{customer_id}'
            delete_response = requests.delete(delete_url, headers=HEADERS)
            print(f"Delete Customer Response: {delete_response.status_code}")
            assert delete_response.status_code in [200, 404], "Customer cleanup failed" # Allow 404 if already gone
