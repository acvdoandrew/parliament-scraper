import pytest
import httpx
from src.scraper.parser import scrape_bill_info, build_sponsor_url
from unittest.mock import patch


@pytest.mark.asyncio
async def test_scrape_bill_info(sample_bill_url, mock_bill_html):
    """
    Test the bill scraping functionality
    """

    # Mock the HTTP client responses
    async def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200
            text = mock_bill_html

            def raise_for_status(self):
                pass

        return MockResponse()

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await scrape_bill_info(sample_bill_url)

        assert result.bill_type == "Senate Public Bill"
        assert result.status == "In Progress"
        assert result.sponsor_name == "John Doe"


@pytest.mark.asyncio
async def test_scrape_bill_info_http_error(sample_bill_url):
    """
    Test handling of HTTP errors
    """
    with patch("httpx.AsyncClient.get", side_effect=httpx.HTTPError("Mocked error")):
        with pytest.raises(Exception):
            await scrape_bill_info(sample_bill_url)


def test_build_sponsor_url():
    """
    Test URL building functionality
    """
    # Test with string
    href = "/members/1234"
    url = build_sponsor_url(href)
    assert url == "https://www.parl.ca/members/1234"

    # Test with list
    href_list = ["/members/1234"]
    url = build_sponsor_url(href_list)
    assert url == "https://www.parl.ca/members/1234"

    # Test with invalid input
    with pytest.raises(ValueError):
        build_sponsor_url("")
