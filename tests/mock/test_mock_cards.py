# Mock tests for Stripe Card objects
import pytest
import requests
import requests_mock
import os

# Mock Base URL (can be anything for mocks)
BASE_URL = "mock://api.stripe.com/v1"

def test_mock_create_card_success(requests_mock):
    """Test mocking the successful creation of a card for a customer."""
    customer_id = "cus_mock_test_123"
    card_url = f'{BASE_URL}/customers/{customer_id}/sources'
    expected_card_id = "card_mock_visa_1234"
    
    # Define the expected response for a successful card creation
    mock_response_body = {
        "id": expected_card_id,
        "object": "card",
        "customer": customer_id,
        "last4": "4242",
        "brand": "Visa",
        "exp_month": 12,
        "exp_year": 2025,
        "funding": "credit",
        "country": "US",
        "name": None,
        "address_zip": None,
        "cvc_check": "pass",
        "metadata": {}
    }
    
    # Register the mock: POST to the card URL returns 200 with the body
    requests_mock.post(card_url, json=mock_response_body, status_code=200)
    
    # Simulate the API call from the application
    # In a real scenario, this would call the application code that makes the request
    response = requests.post(card_url, data={'source': 'tok_visa'}) # Data doesn't matter much for mock
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == expected_card_id
    assert data['object'] == 'card'
    assert data['customer'] == customer_id
    assert data['last4'] == '4242'
    
    # Verify the mock was called correctly
    assert requests_mock.called
    assert requests_mock.call_count == 1
    history = requests_mock.request_history
    assert history[0].url == card_url
    assert history[0].method == 'POST'

def test_mock_retrieve_card_success(requests_mock):
    """Test mocking the successful retrieval of a specific card."""
    customer_id = "cus_mock_test_123"
    card_id = "card_mock_visa_1234"
    retrieve_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    
    # Define the expected card response
    mock_response_body = {"id": card_id, "object": "card", "customer": customer_id, "last4": "4242", "brand": "Visa"}
    
    # Register the mock: GET to the specific card URL returns 200
    requests_mock.get(retrieve_url, json=mock_response_body, status_code=200)
    
    # Simulate the API call
    response = requests.get(retrieve_url)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == card_id
    assert data['customer'] == customer_id

def test_mock_list_cards_success(requests_mock):
    """Test mocking the successful listing of cards for a customer."""
    customer_id = "cus_mock_test_123"
    list_url = f'{BASE_URL}/customers/{customer_id}/sources'
    card1_id = "card_mock_visa_1234"
    card2_id = "card_mock_mc_5678"
    
    # Define the expected list response
    mock_response_body = {
        "object": "list",
        "data": [
            {"id": card1_id, "object": "card", "customer": customer_id, "last4": "4242", "brand": "Visa"},
            {"id": card2_id, "object": "card", "customer": customer_id, "last4": "5454", "brand": "MasterCard"}
        ],
        "has_more": False,
        "url": f"/v1/customers/{customer_id}/sources"
    }
    
    # Register the mock: GET to the sources URL returns 200
    # Match query params if filtering is important (e.g., params={'object': 'card'}) 
    requests_mock.get(list_url, json=mock_response_body, status_code=200)
    
    # Simulate the API call (potentially with params)
    response = requests.get(list_url, params={'object': 'card'})
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['object'] == 'list'
    assert len(data['data']) == 2
    assert data['data'][0]['id'] == card1_id
    assert data['data'][1]['id'] == card2_id

def test_mock_update_card_success(requests_mock):
    """Test mocking the successful update of a card."""
    customer_id = "cus_mock_test_123"
    card_id = "card_mock_visa_1234"
    update_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    updated_name = "My Updated Visa"
    
    # Define the expected response after update
    mock_response_body = {"id": card_id, "object": "card", "customer": customer_id, "last4": "4242", "brand": "Visa", "name": updated_name}
    
    # Register the mock: POST to the specific card URL returns 200 with updated data
    requests_mock.post(update_url, json=mock_response_body, status_code=200)
    
    # Simulate the API call
    response = requests.post(update_url, data={'name': updated_name})
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == card_id
    assert data['name'] == updated_name

def test_mock_delete_card_success(requests_mock):
    """Test mocking the successful deletion of a card."""
    customer_id = "cus_mock_test_123"
    card_id = "card_mock_visa_1234"
    delete_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    
    # Define the expected deletion response
    mock_response_body = {"id": card_id, "object": "card", "deleted": True}
    
    # Register the mock: DELETE to the specific card URL returns 200
    requests_mock.delete(delete_url, json=mock_response_body, status_code=200)
    
    # Simulate the API call
    response = requests.delete(delete_url)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == card_id
    assert data['deleted'] is True

def test_mock_retrieve_card_not_found(requests_mock):
    """Test mocking the retrieval of a non-existent card (404)."""
    customer_id = "cus_mock_test_123"
    card_id = "card_nonexistent_789"
    retrieve_url = f'{BASE_URL}/customers/{customer_id}/sources/{card_id}'
    
    # Define the expected error response
    mock_error_body = {
        "error": {
            "code": "resource_missing",
            "doc_url": "https://stripe.com/docs/error-codes/resource-missing",
            "message": f"No such source: {card_id}",
            "param": "id",
            "type": "invalid_request_error"
        }
    }
    
    # Register the mock: GET to the specific card URL returns 404
    requests_mock.get(retrieve_url, json=mock_error_body, status_code=404)
    
    # Simulate the API call
    response = requests.get(retrieve_url)
    
    # Assertions
    assert response.status_code == 404
    data = response.json()
    assert 'error' in data
    assert data['error']['code'] == 'resource_missing'
    assert card_id in data['error']['message']

# TODO: Add mock tests for failure scenarios (e.g., invalid create token)
