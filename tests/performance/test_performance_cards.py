# Performance tests for Stripe Card objects
import pytest
import requests
import os
import time
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

# Performance thresholds (in seconds)
CREATE_CARD_THRESHOLD = 1.5 # Example: 1.5 seconds
LIST_CARDS_THRESHOLD = 1.0 # Example: 1.0 second

@pytest.fixture(scope="function")
def perf_customer_fixture():
    """Fixture to create a customer for performance tests and delete it afterwards."""
    customer_url = f'{BASE_URL}/customers'
    customer_data = {'description': 'Customer for card perf testing'}
    response = requests.post(customer_url, headers=HEADERS, data=customer_data)
    assert response.status_code == 200, f"Failed to create customer: {response.text}"
    customer_id = response.json()['id']
    print(f"\nCreated customer {customer_id} for perf test")
    
    yield customer_id # Provide the customer ID to the test
    
    # Teardown: Delete Customer
    print(f"\nDeleting customer {customer_id} after perf test")
    delete_response = requests.delete(f"{customer_url}/{customer_id}", headers=HEADERS)
    assert delete_response.status_code in [200, 404], f"Failed to delete customer: {delete_response.text}"
    print(f"Deleted customer {customer_id}")

def test_performance_create_card(perf_customer_fixture):
    """Measure the performance of creating a single card."""
    customer_id = perf_customer_fixture
    card_url = f'{BASE_URL}/customers/{customer_id}/sources'
    card_data = {'source': 'tok_visa'}
    
    start_time = time.time()
    response = requests.post(card_url, headers=HEADERS, data=card_data)
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nCreate Card API call took {duration:.4f} seconds")
    assert response.status_code == 200, f"Create card failed: {response.text}"
    assert duration < CREATE_CARD_THRESHOLD, f"Card creation took too long ({duration:.4f}s > {CREATE_CARD_THRESHOLD}s)"
    
    card_id = response.json()['id']
    print(f"Card {card_id} created successfully for perf test.")

def test_performance_list_cards(perf_customer_fixture):
    """Measure the performance of listing cards for a customer (after adding a few)."""
    customer_id = perf_customer_fixture
    card_url = f'{BASE_URL}/customers/{customer_id}/sources'
    num_cards_to_create = 3 # Create a small number of cards for the list test
    
    print(f"Creating {num_cards_to_create} cards for list performance test...")
    created_card_ids = []
    for i in range(num_cards_to_create):
        # Use different test tokens if available/needed, otherwise tok_visa is fine
        token = 'tok_visa' 
        card_data = {'source': token, 'metadata[index]': i}
        response = requests.post(card_url, headers=HEADERS, data=card_data)
        assert response.status_code == 200, f"Failed to create card {i+1} for list test: {response.text}"
        created_card_ids.append(response.json()['id'])
    print(f"Created cards: {created_card_ids}")
        
    # Now measure the list operation
    list_url = f'{BASE_URL}/customers/{customer_id}/sources'
    params = {'object': 'card', 'limit': 10} # Requesting cards, limit is optional
    
    start_time = time.time()
    response = requests.get(list_url, headers=HEADERS, params=params)
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nList Cards API call took {duration:.4f} seconds")
    assert response.status_code == 200, f"List cards failed: {response.text}"
    assert duration < LIST_CARDS_THRESHOLD, f"Card listing took too long ({duration:.4f}s > {LIST_CARDS_THRESHOLD}s)"
    
    # Verify the result (optional but good practice)
    body = response.json()
    assert body['object'] == 'list'
    assert len(body['data']) >= num_cards_to_create
    print(f"Successfully listed {len(body['data'])} cards.")

# TODO: Add performance tests for card creation and listing - DONE
