from typing import Optional
import re


def extract_bill_number(url: str) -> Optional[str]:
    """
    Extract bill number from URL.
    Returns None if no match is found.
    """
    match = re.search(r"/bill/\d+-\d+/([a-z]-\d+)", url)
    return match.group(1) if match else None
