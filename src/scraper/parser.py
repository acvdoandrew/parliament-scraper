import httpx
from bs4 import BeautifulSoup, Tag
from fastapi import HTTPException
import logging
from urllib.parse import urljoin
from typing import Optional, Union
from src.scraper.utils import extract_bill_number
from src.config.settings import settings
from src.models.bill import BillInfo

logger = logging.getLogger(__name__)


def safe_text_extract(element: Optional[Tag]) -> str:
    """Safely extract text from a BeautifulSoup element"""
    if element is None:
        return "Unknown"
    return element.text.strip() or "Unknown"


def build_sponsor_url(href: Union[str, list[str]]) -> str:
    """
    Safely build sponsor URL handling various href types.
    """
    base_url = "https://www.parl.ca"

    # If href is a list, take the first item
    if isinstance(href, list):
        href = href[0] if href else ""

    # If href is empty or not a string, raise error
    if not isinstance(href, str) or not href:
        raise ValueError("Invalid href value")

    return urljoin(base_url, href)


async def scrape_bill_info(url: str) -> BillInfo:
    """
    Scrape information from a Parliament bill page.
    """
    try:
        headers = {"User-Agent": settings.USER_AGENT}
        timeout = httpx.Timeout(settings.REQUEST_TIMEOUT)

        async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
            # Fetch main bill page
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract Bill Type
            bill_type: str = safe_text_extract(soup.select_one(".bill-type"))

            # Extract status
            status: str = safe_text_extract(soup.select_one(".status-label"))

            # Extract sponsor information
            sponsor_elem = soup.select_one(".sponsor-info a")
            sponsor_name: str = "Unknown"
            sponsor_party: str = "Unknown"

            if sponsor_elem:
                sponsor_name = safe_text_extract(sponsor_elem)
                href = sponsor_elem.get("href")

                if href:
                    try:
                        # Use the new build_sponsor_url function
                        sponsor_url = build_sponsor_url(href)
                        sponsor_response = await client.get(sponsor_url)
                        if sponsor_response.status_code == 200:
                            sponsor_soup = BeautifulSoup(
                                sponsor_response.text, "html.parser"
                            )
                            party_elem = sponsor_soup.select_one(".party-affiliation")
                            if party_elem:
                                sponsor_party = safe_text_extract(party_elem)
                    except (ValueError, httpx.HTTPError) as e:
                        logger.warning(f"Failed to fetch sponsor details: {e}")

            # Extract last updated date
            last_updated: str = safe_text_extract(soup.select_one(".last-updated"))

            # Get bill number with default
            bill_number = extract_bill_number(url)
            if bill_number is None:
                raise HTTPException(
                    status_code=400, detail="Could not extract bill number from URL"
                )

            return BillInfo(
                bill_number=bill_number,
                bill_type=bill_type,
                status=status,
                sponsor_name=sponsor_name,
                sponsor_party=sponsor_party,
                last_updated=last_updated,
            )

    except httpx.RequestError as e:
        logger.error(f"Scraping error for {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error for {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
