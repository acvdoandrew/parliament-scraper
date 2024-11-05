from urllib.parse import urlparse
import re
from typing import Optional


def validate_parliament_url(url: str) -> bool:
    """Validate if the URL is from parl.ca and has the expected format"""
    try:
        parsed = urlparse(url)
        return parsed.netloc == "www.parl.ca" and "/legisinfo/en/bill" in parsed.path
    except:
        return False


def extract_bill_number(url: str) -> Optional[str]:
    """Extract bill number from URL"""
    match = re.search(r"/bill/\d+-\d+/([a-z]-\d+)", url)
    return match.group(1) if match else None
