from fastapi import APIRouter, HTTPException, Query
from src.scraper.parser import scrape_bill_info
from src.models.bill import BillInfo
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/bill", response_model=BillInfo, tags=["Bills"])
async def get_bill_info(
    url: str = Query(..., description="URL of the parliament bill to scrape"),
) -> BillInfo:
    """
    Get information about a specific bill from the Parliament website.

    Args:
        url: The full URL of the bill (e.g., https://www.parl.ca/legisinfo/en/bill/44-1/s-2)

    Returns:
        BillInfo: Information about the bill including type, status, sponsor, etc.

    Raises:
        HTTPException: If the URL is invalid or scraping fails
    """
    try:
        # Validate URL format (basic check)
        if not url.startswith("https://www.parl.ca/legisinfo/en/bill/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL format. URL must be from parl.ca/legisinfo",
            )

        return await scrape_bill_info(url)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process the bill URL")


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    return {"status": "healthy", "message": "Parliament bill scraper is running"}
