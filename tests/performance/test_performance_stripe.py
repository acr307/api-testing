import pytest
import stripe
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fixture to set up Stripe API key
@pytest.fixture(scope='module', autouse=True)
def setup_stripe():
    api_key = os.getenv('STRIPE_API_KEY')
    if not api_key:
        pytest.skip('STRIPE_API_KEY environment variable not set')
    stripe.api_key = api_key
    # Optional: Set API base if needed, though stripe library often handles this
    # stripe.api_base = os.getenv('BASE_URL', 'https://api.stripe.com/v1')

def test_performance_create_customer(benchmark):
    """Benchmark creating a Stripe customer."""
    # Use benchmark() function for the code to be measured
    result = benchmark(stripe.Customer.create,
                       email='perf-test@example.com',
                       description='Performance Test Customer')
    assert result.id is not None
    # Clean up the created customer (optional but good practice)
    try:
        stripe.Customer.delete(result.id)
    except Exception as e:
        print(f"Warning: Could not delete test customer {result.id}: {e}")

def test_performance_create_charge(benchmark):
    """Benchmark creating a Stripe charge using a test token."""
    # Need a source (test token) to create a charge
    result = benchmark(stripe.Charge.create,
                       amount=100,  # amount in cents
                       currency='usd',
                       source='tok_visa', # Use Stripe's standard test card token
                       description='Performance Test Charge')
    assert result.id.startswith('ch_')
    assert result.status == 'succeeded' # Test charges usually succeed immediately
