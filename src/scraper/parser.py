import httpx
import xml.etree.ElementTree as ET
from fastapi import HTTPException
import logging
from typing import Optional
from src.config.settings import settings
from src.models.bill import BillInfo

logger = logging.getLogger(__name__)


def safe_xml_text(element: Optional[ET.Element], default: str = "Unknown") -> str:
    """Safely extract text from XML element"""
    if element is not None and element.text:
        return str(element.text).strip()
    return default


async def scrape_bill_info(url: str) -> BillInfo:
    """
    Scrape information from a Parliament bill using the XML endpoint
    """
    try:
        # Convert HTML URL to XML URL
        xml_url = f"{url}/xml"

        headers = {"User-Agent": settings.USER_AGENT}

        timeout = httpx.Timeout(settings.REQUEST_TIMEOUT)

        async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
            response = await client.get(xml_url)
            response.raise_for_status()

            # Parse XML
            try:
                root = ET.fromstring(response.text)
                bill = root.find("Bill")
            except ET.ParseError as e:
                logger.error(f"Failed to parse XML: {e}")
                raise HTTPException(status_code=500, detail="Invalid XML response")

            if bill is None:
                raise HTTPException(
                    status_code=404, detail="Bill information not found"
                )

            # Extract all fields with safe handling
            bill_type_text = safe_xml_text(bill.find("BillDocumentTypeName"))
            status_text = safe_xml_text(bill.find("StatusName"))
            sponsor_name_text = safe_xml_text(bill.find("SponsorPersonName"))
            last_updated_text = safe_xml_text(bill.find("LatestBillEventDateTime"))
            bill_number_text = safe_xml_text(bill.find("NumberCode"))

            if bill_number_text != "Unknown":
                bill_number_text = bill_number_text.lower()

            # Validate bill number
            if not bill_number_text or bill_number_text == "unknown":
                raise HTTPException(
                    status_code=400, detail="Could not extract bill number from XML"
                )

            # Handle dropped bills
            is_dropped_elem = bill.find("IsDroppedFromSenateOrderPaper")
            if (
                is_dropped_elem is not None
                and is_dropped_elem.text is not None
                and is_dropped_elem.text.lower() == "true"
            ):
                status_text = "Dropped from Senate Order Paper"

            # Log the extracted data
            logger.info(f"""
            Extracted from XML:
            Bill Number: {bill_number_text}
            Bill Type: {bill_type_text}
            Status: {status_text}
            Sponsor Name: {sponsor_name_text}
            Last Updated: {last_updated_text}
            """)

            # Create BillInfo with guaranteed string values
            return BillInfo(
                bill_number=bill_number_text,
                bill_type=bill_type_text,
                status=status_text,
                sponsor_name=sponsor_name_text,
                sponsor_party="Government Representative",
                last_updated=last_updated_text,
            )

    except httpx.RequestError as e:
        logger.error(f"XML fetch error for {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch XML: {str(e)}")
    except ET.ParseError as e:
        logger.error(f"XML parsing error for {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to parse XML: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error for {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
