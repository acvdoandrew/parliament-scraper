from src.scraper.utils import extract_bill_number


def test_extract_bill_number():
    """
    Test bill number extraction from URLs
    """
    # Test valid URL
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/s-2"
    assert extract_bill_number(url) == "s-2"

    # Test invalid URL
    invalid_url = "https://invalid-url.com"
    assert extract_bill_number(invalid_url) is None

    # Test malformed URL
    malformed_url = "https://www.parl.ca/legisinfo/en/bill/invalid"
    assert extract_bill_number(malformed_url) is None
