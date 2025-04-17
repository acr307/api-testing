# Stripe API Testing Suite 🧪

This project contains a comprehensive API testing suite built on **Stripe's sandbox environment**, targeting the full user flow of `Customer`, `Card`, and `Charge` objects. It combines **live and mocked API techniques** to validate regression, integration, smoke, security, and performance behaviors.

---

## 🔍 Overview

This suite is designed to simulate real-world Stripe usage in a secure, scalable way. Tests are modular, CI-friendly, and organized to cover:

- ✅ Functional happy-paths
- ✅ End-to-end integration flows
- ✅ Regression drift and schema stability
- ✅ Security edge cases and auth validation
- ✅ Token usage and performance under rate-limited conditions

---

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

---

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