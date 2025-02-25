import pytest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from typing import Any
import httpx
from src.scraper.parser import scrape_bill_info, get_sponsor_party, build_sponsor_url
from src.models.bill import BillInfo


@pytest.mark.asyncio
async def test_scrape_bill_info_success(mock_bill_xml: str, mock_mp_xml: str):
    """Test successful bill info scraping"""
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/c-422"

    async def mock_get(*args: Any, **kwargs: Any):
        class MockResponse:
            status_code = 200

            def __init__(self, url: str):
                self.url = url

            @property
            def text(self) -> str:
                if "parl.ca/legisinfo" in self.url:
                    return mock_bill_xml
                elif "ourcommons.ca/members" in self.url:
                    return mock_mp_xml
                return ""

            def raise_for_status(self) -> None:
                pass

        return MockResponse(args[0])

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await scrape_bill_info(url)
        assert isinstance(result, BillInfo)
        assert result.bill_number == "c-422"
        assert result.bill_type == "Private Member's Bill"
        assert result.sponsor_name == "Bonita Zarrillo"
        assert result.sponsor_party == "NDP"


@pytest.mark.asyncio
async def test_scrape_bill_info_missing_fields(mock_bill_xml: str):
    """Test handling of missing fields in XML response"""
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/c-422"
    modified_xml = """<?xml version="1.0" encoding="utf-8"?>
    <Bills>
        <Bill>
            <NumberCode>C-422</NumberCode>
        </Bill>
    </Bills>"""

    async def mock_get(*args: Any, **kwargs: Any):
        class MockResponse:
            status_code = 200
            text = modified_xml

            def raise_for_status(self) -> None:
                pass

        return MockResponse()

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await scrape_bill_info(url)
        assert result.sponsor_name == "Unknown"
        assert result.status == "Unknown"


@pytest.mark.asyncio
async def test_get_sponsor_party(mock_bill_element: ET.Element, mock_mp_xml: str):
    """Test extracting sponsor party information"""

    async def mock_get(*args: Any, **kwargs: Any):
        class MockResponse:
            status_code = 200
            text = mock_mp_xml

            def raise_for_status(self) -> None:
                pass

        return MockResponse()

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        party = await get_sponsor_party(mock_bill_element)
        assert party == "NDP"


@pytest.mark.asyncio
async def test_http_errors(app_client):
    """Test handling of HTTP errors"""
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/c-422"

    async def mock_error(*args: Any, **kwargs: Any):
        raise httpx.RequestError("Mocked HTTP error")

    with patch("httpx.AsyncClient.get", side_effect=mock_error):
        response = app_client.get(f"/api/bill?url={url}")
        assert response.status_code == 500
        assert "Processing failed" in response.json()["detail"]


@pytest.mark.parametrize(
    "first_name, last_name, id, expected_url",
    [
        (
            "Bonita",
            "Zarrillo",
            "105837",
            "https://www.ourcommons.ca/members/en/bonita-zarrillo(105837)/xml",
        ),
        (
            "John",
            "Doe Smith",
            "12345",
            "https://www.ourcommons.ca/members/en/john-doe-smith(12345)/xml",
        ),
    ],
)
def test_build_sponsor_url(first_name: str, last_name: str, id: str, expected_url: str):
    """Test sponsor URL building logic"""
    url = build_sponsor_url(first_name, last_name, id)
    assert url == expected_url


@pytest.mark.asyncio
async def test_specific_http_errors(app_client):
    """Test handling of specific HTTP error cases"""
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/c-422"

    test_cases = [
        (httpx.TimeoutException("Connection timeout"), "Connection timeout"),
        (httpx.ConnectError("Connection failed"), "Connection failed"),
        (
            httpx.HTTPStatusError(
                message="500 Internal Server Error",
                request=httpx.Request("GET", url),
                response=httpx.Response(500),
            ),
            "500 Internal Server Error",
        ),
    ]

    for error, expected_message in test_cases:

        async def mock_error(*args: Any, **kwargs: Any):
            raise error

        with patch("httpx.AsyncClient.get", side_effect=mock_error):
            response = app_client.get(f"/api/bill?url={url}")
            assert response.status_code == 500
            assert expected_message in response.json()["detail"]
