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
            text = """
            <html>
                <body>
                    <div class="about-bill">
                        <span class="bill-type">Senate Public Bill</span>
                        <span class="status-label">In Progress</span>
                        <div class="sponsor-info">
                            <a href="/members/1234">John Doe</a>
                        </div>
                        <div class="last-updated">2024-01-01</div>
                    </body>
                </div>
            </html>
            """

            def raise_for_status(self):
                pass

            @property
            def ok(self):
                return True

        return MockResponse()

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await scrape_bill_info(sample_bill_url)

        # Print the actual result for debugging
        print(f"Actual bill_type: {result.bill_type}")
        print(f"Actual status: {result.status}")
        print(f"Actual sponsor_name: {result.sponsor_name}")

        # Updated assertions
        assert (
            result.bill_type == "Senate Public Bill"
        ), f"Expected 'Senate Public Bill' but got '{result.bill_type}'"
        assert (
            result.status == "In Progress"
        ), f"Expected 'In Progress' but got '{result.status}'"
        assert (
            result.sponsor_name == "John Doe"
        ), f"Expected 'John Doe' but got '{result.sponsor_name}'"


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
