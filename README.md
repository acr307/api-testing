# Stripe API Testing Suite 🧪

This project contains a suite of automated tests for interacting with the Stripe API, focusing on core objects like Customers, Charges, and Cards.

## Project Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd api-testing
    ```
2.  **Create a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    *   Create a `.env` file in the project root.
    *   Add your Stripe secret key to the `.env` file:
        ```dotenv
        STRIPE_API_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        BASE_URL=https://api.stripe.com/v1
        ```
    *   Replace `sk_test_...` with your actual Stripe *test* secret key.

## Running Tests

Ensure your virtual environment is active and the `.env` file is configured.

*   **Run all tests:**
    ```bash
    pytest -v
    ```
*   **Run tests in a specific file:**
    ```bash
    pytest -v tests/functional/test_cards.py
    ```
*   **Run a specific test function:**
    ```bash
    pytest -v tests/functional/test_cards.py::test_create_card_for_customer
    ```
*   **Run tests marked with a specific type (e.g., functional):**
    *(Requires adding `@pytest.mark.<marker_name>` decorators to tests)*
    ```bash
    pytest -v -m functional
    ```

## Test Suite Overview

The tests are organized into the following categories within the `tests/` directory:

*   **Functional (`tests/functional/`):** Tests that interact directly with the live Stripe API (using test keys). They cover:
    *   Customer management (Create)
    *   Charge creation (including varied amounts, missing parameters, declined tokens)
    *   Card management (Create, Retrieve, List, Update, Delete)
    *   Negative scenarios (e.g., invalid data, non-existent resources).
*   **Mock (`tests/mock/`):** Tests that use `requests-mock` to simulate Stripe API responses without making actual API calls. Useful for testing specific scenarios (like errors, timeouts) quickly and reliably. Covers:
    *   Customer creation (Success, Invalid Email)
    *   Charge creation (Error, Timeout)
    *   Card operations (Create, Retrieve, List, Update, Delete, Not Found).
*   **Performance (`tests/performance/`):** Tests that measure the response time of key API calls against defined thresholds. Covers:
    *   Customer creation
    *   Charge creation
    *   Card creation
    *   Listing cards.
*   **Security (`tests/security/`):** Tests focused on authentication and authorization. Covers:
    *   Accessing endpoints with valid, invalid, and missing API keys.
    *   Specific security-related scenarios (e.g., invalid tokens for charges).
*   **Integration (`tests/integration/`):** Tests that verify the interaction between multiple API resources in a typical user flow. Covers:
    *   The full flow of creating a customer, adding a card to them, and then creating a charge using that customer and card.

## CI/CD

A GitHub Actions workflow (`.github/workflows/api-tests.yml`) is configured to run the full test suite automatically on pushes to the `main` branch.

## 🔍 Overview

This suite is designed to simulate real-world Stripe usage in a secure, scalable way. Tests are modular, CI-friendly, and organized to cover:

- ✅ Functional happy-paths
- ✅ End-to-end integration flows
- ✅ Regression drift and schema stability
- ✅ Security edge cases and auth validation
- ✅ Token usage and performance under rate-limited conditions

## ⚙️ Tech Stack

- **Language:** Python 3.11+  
- **Testing Framework:** PyTest  
- **Libraries:**  
  - `requests` for HTTP requests  
  - `pytest-mock` for mocking/stubbing  
  - `pytest-snapshot` for regression checks  
- **Mocking:** Postman Mock Server, WireMock (optional)  
- **CI/CD:** GitHub Actions  
- **Reports:** HTML (`pytest-html`), snapshot diffs, semantic logs

## 📁 Directory Structure

```bash
.
├── .github/workflows/
│   └── api-tests.yml              # GitHub Actions workflow
├── tests/
│   ├── functional/
│   │   ├── test_customers.py
│   │   ├── test_charges.py
│   │   └── test_cards.py
│   ├── integration/
│   │   └── test_customer_flow.py  # Multi-step charge flow
│   ├── mock/
│   │   ├── test_mock_customer.py
│   │   ├── test_mock_charge.py
│   │   └── test_mock_card.py
│   ├── security/
│   │   └── test_auth.py
│   └── performance/
│       └── test_rate_limits.py
├── conftest.py                    # PyTest fixtures (auth, envs, headers)
├── .env                           # API keys (never committed)
├── requirements.txt
└── README.md
```

## 🔑 Environment Setup

1. Clone the repository
2. Create a `.env` file in the root directory:

```bash
STRIPE_API_KEY=sk_test_...
OPENAI_API_KEY=sk-...         # Optional
BASE_URL=https://api.stripe.com/v1
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run all tests:
```bash
pytest --html=report.html --self-contained-html
```

## 🧪 Test Categories

| Type	| Description
| :--- | :---
| Smoke | Basic endpoint availability and happy-path response structure
| Regression | Snapshot comparisons and schema validation across runs
| Integration | Multi-step flows: create → charge → summarize
| Security | Auth checks, missing fields, injection attempts
| Performance | Retry logic, rate limit handling, timeout assertions

## ✅ Sample Test: Creating and Charging a Customer

```python
def test_charge_customer(stripe_headers, base_url):
    # Create a customer
    cust_data = {"email": "test@example.com", "name": "Test User"}
    r1 = requests.post(f"{base_url}/customers", headers=stripe_headers, data=cust_data)
    cid = r1.json()["id"]

    # Charge the customer
    charge_data = {"amount": 1500, "currency": "usd", "customer": cid, "source": "tok_visa"}
    r2 = requests.post(f"{base_url}/charges", headers=stripe_headers, data=charge_data)
    assert r2.status_code == 200
    assert r2.json()["status"] == "succeeded"
```

## 🔄 CI Integration: GitHub Actions

`.github/workflows/api-tests.yml`

```yaml
name: Stripe API Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    env:
      STRIPE_API_KEY: ${{ secrets.STRIPE_API_KEY }}
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: 3.11

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Run tests
      run: pytest --html=report.html --self-contained-html
```

## 📊 Reporting

* **HTML reports** are generated with pytest-html
* **Snapshot reports** track content drift over time (e.g., AI completions)
* **CI artifacts** include response logs, failure outputs, and summary reports

## 🙌 Credits

This test suite was designed as part of an advanced API testing capstone project. It reflects real-world QA practices for testing critical payment infrastructure using both sandboxed live data and mock simulations.

## 📬 License

MIT License – open for modification and adaptation.

## 📝 Notes

For further reading on this API testing suite, see the Google doc here:
https://docs.google.com/document/d/1yCkSsgiecbK5aIwD0sEVk39nyWZK-FHyMuqgs8F4lgk/edit?usp=sharing