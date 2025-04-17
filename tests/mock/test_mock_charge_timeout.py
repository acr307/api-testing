def test_mock_charge_timeout(requests_mock):
    base_url = os.getenv("BASE_URL")
    mocked_url = f"{base_url}/charges"
    requests_mock.post(mocked_url, exc=requests.exceptions.Timeout)

    import requests
    with pytest.raises(requests.exceptions.Timeout):
        requests.post(mocked_url, headers={}, data={})
