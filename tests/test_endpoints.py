import pytest
from unittest.mock import patch
import httpx


@pytest.mark.asyncio
async def test_health_check(app_client):  # Changed from client to app_client
    """Test health check endpoint"""
    response = app_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "message": "Parliament bill scraper is running",
    }


@pytest.mark.asyncio
async def test_get_bill_info_valid(
    app_client, mock_bill_xml, mock_mp_xml
):  # Changed from client to app_client
    """Test getting bill info with valid URL and mock responses"""
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/c-422"

    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200

            def __init__(self, url):
                self.url = url

            @property
            def text(self):
                if "parl.ca/legisinfo" in self.url:
                    return mock_bill_xml
                elif "ourcommons.ca/members" in self.url:
                    return mock_mp_xml
                return ""

            def raise_for_status(self):
                pass

        return MockResponse(args[0])

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        response = app_client.get(f"/api/bill?url={url}")
        assert response.status_code == 200
        data = response.json()

        assert data["bill_number"] == "c-422"
        assert data["bill_type"] == "Private Member's Bill"
        assert data["sponsor_name"] == "Bonita Zarrillo"
        assert data["sponsor_party"] == "NDP"


@pytest.mark.asyncio
async def test_get_senate_bill(
    app_client, mock_senate_bill_xml
):  # Changed from client to app_client
    """Test getting Senate bill info"""
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/s-2"

    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200
            text = mock_senate_bill_xml

            def raise_for_status(self):
                pass

        return MockResponse()

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        response = app_client.get(f"/api/bill?url={url}")
        assert response.status_code == 200
        data = response.json()
        assert data["bill_number"] == "s-2"
        assert data["bill_type"] == "Senate Public Bill"
        assert data["sponsor_party"] == "Senate"


@pytest.mark.asyncio
async def test_invalid_url_formats(app_client):  # Changed from client to app_client
    """Test handling of various invalid URL formats"""
    invalid_urls = [
        "https://example.com",
        "not-a-url",
        "https://parl.ca/wrong/path",
        "https://www.parl.ca/legisinfo/en/wrong-format",
        "",
    ]

    for url in invalid_urls:
        response = app_client.get(f"/api/bill?url={url}")
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_http_errors(app_client):  # Changed from client to app_client
    """Test handling of HTTP errors"""
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/c-422"

    async def mock_error(*args, **kwargs):
        raise httpx.RequestError("Mocked HTTP error")

    with patch("httpx.AsyncClient.get", side_effect=mock_error):
        response = app_client.get(f"/api/bill?url={url}")
        assert response.status_code == 500
        assert "Processing failed: Mocked HTTP error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_specific_http_errors(app_client):  # Changed from client to app_client
    """Test handling of specific HTTP error cases"""
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/c-422"

    # Create mock request and response for HTTPStatusError
    mock_request = httpx.Request("GET", url)
    mock_response = httpx.Response(500, request=mock_request)

    test_cases = [
        {
            "error": httpx.TimeoutException("Connection timeout"),
            "expected_message": "Processing failed: Connection timeout",
        },
        {
            "error": httpx.ConnectError("Connection failed"),
            "expected_message": "Processing failed: Connection failed",
        },
        {
            "error": httpx.HTTPStatusError(
                message="500 Internal Server Error",
                request=mock_request,
                response=mock_response,
            ),
            "expected_message": "Processing failed: 500 Internal Server Error",
        },
    ]

    for case in test_cases:

        async def mock_specific_error(*args, **kwargs):
            raise case["error"]

        with patch("httpx.AsyncClient.get", side_effect=mock_specific_error):
            response = app_client.get(f"/api/bill?url={url}")
            assert response.status_code == 500
            assert case["expected_message"] in response.json()["detail"]


@pytest.mark.asyncio
async def test_xml_parsing_error(app_client):  # Changed from client to app_client
    """Test handling of XML parsing errors"""
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/c-422"

    async def mock_invalid_xml(*args, **kwargs):
        class MockResponse:
            status_code = 200
            text = "Invalid XML"

            def raise_for_status(self):
                pass

        return MockResponse()

    with patch("httpx.AsyncClient.get", side_effect=mock_invalid_xml):
        response = app_client.get(f"/api/bill?url={url}")
        assert response.status_code == 500
        assert "Invalid XML" in response.json()["detail"]
