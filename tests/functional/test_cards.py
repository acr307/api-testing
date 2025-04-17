# Functional tests for Stripe Card objects
import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch API key and base URL
API_KEY = os.getenv('STRIPE_API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://api.stripe.com/v1')

# Headers for authenticated requests (form-encoded for creating card sources)
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Skip all tests in this module if API key is not set
pytestmark = pytest.mark.skipif(not API_KEY, reason='STRIPE_API_KEY environment variable not set')

@pytest.fixture(scope="function")
def create_customer_fixture():
    """Fixture to create a customer for tests and delete it afterwards."""
    customer_url = f'{BASE_URL}/customers'
    customer_data = {'description': 'Customer for card testing'}
    response = requests.post(customer_url, headers=HEADERS, data=customer_data)
    assert response.status_code == 200, f"Failed to create customer: {response.text}"
    customer_id = response.json()['id']
    print(f"\nCreated customer {customer_id} for test")
    
    yield customer_id # Provide the customer ID to the test
    
    # Teardown: Delete Customer
    print(f"\nDeleting customer {customer_id} after test")
    delete_response = requests.delete(f"{customer_url}/{customer_id}", headers=HEADERS)
    # Allow 404 if deleted during test, otherwise expect 200
    assert delete_response.status_code in [200, 404], f"Failed to delete customer: {delete_response.text}"
    print(f"Deleted customer {customer_id}")

@pytest.fixture(scope="function")
def create_customer_and_card_fixture(create_customer_fixture):
    """Fixture that creates a customer and a card, yielding their IDs."""
    customer_id = create_customer_fixture
    card_url = f'{BASE_URL}/customers/{customer_id}/sources'
    card_data = {'source': 'tok_visa'} # Use a standard Stripe test token
    
    response = requests.post(card_url, headers=HEADERS, data=card_data)
    assert response.status_code == 200, f"Failed to create card for customer {customer_id}: {response.text}"
    card = response.json()
    card_id = card['id']
    print(f"Created card {card_id} for customer {customer_id}")
    
    yield customer_id, card_id
    # Customer deletion is handled by create_customer_fixture teardown

def test_create_card_for_customer(create_customer_fixture):
    """Test creating a card source for a given customer."""
    customer_id = create_customer_fixture
    card_url = f'{BASE_URL}/customers/{customer_id}/sources'
    
    # Use a standard Stripe test token
    card_data = {'source': 'tok_visa'}
    
    response = requests.post(card_url, headers=HEADERS, data=card_data)
    print(f"Create card response: {response.status_code} {response.text}")
    assert response.status_code == 200
    
    body = response.json()
    assert body['object'] == 'card'
    assert body['customer'] == customer_id
    assert body['last4'] == '4242' # Standard for tok_visa
    assert body['brand'] == 'Visa'
    print(f"Successfully created card {body['id']} for customer {customer_id}")

def test_retrieve_card(create_customer_and_card_fixture):
    """Test retrieving a specific card for a customer."""
    customer_id, card_id = create_customer_and_card_fixture
    retrieve_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    
    response = requests.get(retrieve_url, headers=HEADERS)
    print(f"Retrieve card response: {response.status_code} {response.text}")
    assert response.status_code == 200
    
    body = response.json()
    assert body['object'] == 'card'
    assert body['id'] == card_id
    assert body['customer'] == customer_id
    assert body['last4'] == '4242'

def test_list_cards_for_customer(create_customer_and_card_fixture):
    """Test listing all cards associated with a customer."""
    customer_id, card_id = create_customer_and_card_fixture
    list_url = f'{BASE_URL}/customers/{customer_id}/sources'
    params = {'object': 'card'} # Filter to only list cards
    
    response = requests.get(list_url, headers=HEADERS, params=params)
    print(f"List cards response: {response.status_code} {response.text}")
    assert response.status_code == 200
    
    body = response.json()
    assert body['object'] == 'list'
    assert 'data' in body
    assert len(body['data']) >= 1
    
    # Check if the created card is in the list
    card_ids_in_list = [card['id'] for card in body['data']]
    assert card_id in card_ids_in_list
    print(f"Found card {card_id} in list for customer {customer_id}")

def test_update_card(create_customer_and_card_fixture):
    """Test updating a card's metadata (e.g., name)."""
    customer_id, card_id = create_customer_and_card_fixture
    update_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    update_data = {
        'name': 'Updated Test Card Name',
        'metadata[test_key]': 'test_value' # Example metadata
    }
    
    response = requests.post(update_url, headers=HEADERS, data=update_data)
    print(f"Update card response: {response.status_code} {response.text}")
    assert response.status_code == 200
    
    body = response.json()
    assert body['id'] == card_id
    assert body['name'] == 'Updated Test Card Name'
    assert body['metadata']['test_key'] == 'test_value'
    print(f"Successfully updated card {card_id}")

def test_delete_card(create_customer_and_card_fixture):
    """Test deleting a card from a customer."""
    customer_id, card_id = create_customer_and_card_fixture
    delete_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    
    response = requests.delete(delete_url, headers=HEADERS)
    print(f"Delete card response: {response.status_code} {response.text}")
    assert response.status_code == 200
    
    body = response.json()
    assert body['id'] == card_id
    assert body['deleted'] is True
    print(f"Successfully marked card {card_id} as deleted")
    
    # Verify the card is gone (retrieve should fail)
    retrieve_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    get_response = requests.get(retrieve_url, headers=HEADERS)
    print(f"Post-delete retrieve response: {get_response.status_code} {get_response.text}")
    assert get_response.status_code == 404 # Expect Not Found
    print(f"Verified card {card_id} is no longer retrievable.")

# --- Negative Functional Tests ---

def test_create_card_invalid_token(create_customer_fixture):
    """Test creating a card with an invalid token fails correctly."""
    customer_id = create_customer_fixture
    card_url = f'{BASE_URL}/customers/{customer_id}/sources'
    card_data = {'source': 'tok_invalid'} # Invalid token
    
    response = requests.post(card_url, headers=HEADERS, data=card_data)
    print(f"Create card invalid token response: {response.status_code} {response.text}")
    assert response.status_code == 400 # Expect Bad Request or similar client error
    body = response.json()
    assert 'error' in body
    assert body['error'].get('code') == 'resource_missing' # Stripe often says token doesn't exist
    assert body['error'].get('param') == 'source'

def test_create_card_non_existent_customer():
    """Test creating a card for a customer ID that does not exist."""
    customer_id = 'cus_nonexistent'
    card_url = f'{BASE_URL}/customers/{customer_id}/sources'
    card_data = {'source': 'tok_visa'}
    
    response = requests.post(card_url, headers=HEADERS, data=card_data)
    print(f"Create card non-existent customer response: {response.status_code} {response.text}")
    assert response.status_code == 400 # Stripe returns 400 for missing customer on card creation
    error_data = response.json()['error']
    assert error_data['code'] == 'resource_missing'
    assert error_data['param'] == 'customer'
    assert customer_id in error_data['message']

def test_retrieve_non_existent_card(create_customer_fixture):
    """Test retrieving a card ID that does not exist for a valid customer."""
    customer_id = create_customer_fixture
    card_id = 'card_nonexistent'
    retrieve_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    
    response = requests.get(retrieve_url, headers=HEADERS)
    print(f"Retrieve non-existent card response: {response.status_code} {response.text}")
    assert response.status_code == 404 # Expect Not Found
    body = response.json()
    assert 'error' in body
    assert body['error'].get('code') == 'resource_missing'
    assert 'No such source' in body['error'].get('message', '') # Check message for source

def test_update_non_existent_card(create_customer_fixture):
    """Test updating a card ID that does not exist for a valid customer."""
    customer_id = create_customer_fixture
    card_id = 'card_nonexistent'
    update_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    update_data = {'name': 'Trying to update non-existent'}
    
    response = requests.post(update_url, headers=HEADERS, data=update_data)
    print(f"Update non-existent card response: {response.status_code} {response.text}")
    assert response.status_code == 404 # Expect Not Found
    body = response.json()
    assert 'error' in body
    assert body['error'].get('code') == 'resource_missing'

def test_delete_non_existent_card(create_customer_fixture):
    """Test deleting a card ID that does not exist for a valid customer."""
    customer_id = create_customer_fixture
    card_id = 'card_nonexistent'
    delete_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    
    response = requests.delete(delete_url, headers=HEADERS)
    print(f"Delete non-existent card response: {response.status_code} {response.text}")
    assert response.status_code == 404 # Expect Not Found
    body = response.json()
    assert 'error' in body
    assert body['error'].get('code') == 'resource_missing'

# TODO: Add negative tests (invalid token, non-existent customer/card, etc.) - DONE (Basic cases)
