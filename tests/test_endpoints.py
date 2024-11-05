async def test_health_check(client):
    """
    Test the health check endpoint
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


async def test_get_bill_info_valid_url(client, sample_bill_url):
    """
    Test getting bill info with valid URL
    """
    response = client.get(f"/api/bill?url={sample_bill_url}")
    assert response.status_code == 200
    data = response.json()
    assert "bill_number" in data
    assert "bill_type" in data
    assert "status" in data


async def test_get_bill_info_invalid_url(client):
    """
    Test getting bill info with invalid URL
    """
    invalid_url = "https://invalid-url.com"
    response = client.get(f"/api/bill?url={invalid_url}")
    assert response.status_code == 400
