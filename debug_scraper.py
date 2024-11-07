import asyncio
import httpx
from bs4 import BeautifulSoup
import logging
from rich import print as rprint
import json
from typing import List, Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def check_word_in_attribute(attr: Optional[str | List[str]], word: str) -> bool:
    """
    Check if a word exists in an attribute that could be a string or list of strings
    """
    if attr is None:
        return False
    if isinstance(attr, list):
        return any(word in str(item).lower() for item in attr)
    return word in str(attr).lower()


async def debug_scrape(url: str):
    """
    Debug scraper to find correct selectors and API endpoints
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(headers=headers) as client:
        # First, let's try to find any API endpoints in the page
        response = await client.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Save the initial HTML
        with open("initial_page.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        print("\n🔍 Analyzing page structure:")

        # Look for script tags that might contain data
        scripts = soup.find_all("script")
        print(f"\nFound {len(scripts)} script tags")

        # Look for links to JSON data
        print("\n📡 Looking for API endpoints:")
        bill_id = url.split("/")[-1]
        possible_api_urls = [
            f"https://www.parl.ca/legisinfo/en/bill/{bill_id}/json",
            f"https://www.parl.ca/legisinfo/api/v1/bills/{bill_id}",
            f"https://www.parl.ca/legisinfo/api/bill/{bill_id}",
        ]

        for api_url in possible_api_urls:
            try:
                api_response = await client.get(api_url)
                if api_response.status_code == 200:
                    print(f"\n✅ Found working API endpoint: {api_url}")
                    try:
                        data = api_response.json()
                        print("\n📝 Sample of API response:")
                        print(json.dumps(data, indent=2)[:500] + "...")

                        # Save the full API response
                        with open("api_response.json", "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2)
                            print("\nFull API response saved to api_response.json")
                    except json.JSONDecodeError:
                        print("Response is not JSON")
            except httpx.RequestError as e:
                print(f"❌ Failed to access {api_url}: {e}")

        # Look for common elements
        print("\n🔍 Looking for elements with common words:")
        relevant_words = ["bill", "status", "sponsor", "type", "update"]
        for word in relevant_words:
            elements = soup.find_all(
                lambda tag: (
                    check_word_in_attribute(tag.get("class"), word)
                    or check_word_in_attribute(tag.get("id"), word)
                    or check_word_in_attribute(tag.get("name"), word)
                )
            )
            if elements:
                print(f"\nFound elements containing '{word}':")
                for elem in elements[:3]:  # Show first 3 matches
                    print(f"Tag: {elem.name}")
                    print(f"Class: {elem.get('class')}")
                    print(f"ID: {elem.get('id')}")
                    print(f"Content: {elem.get_text(strip=True)[:100]}")
                    print("-" * 50)

        # Check for iframes that might contain the content
        iframes = soup.find_all("iframe")
        if iframes:
            print(f"\n🖼️ Found {len(iframes)} iframes:")
            for iframe in iframes:
                print(f"Source: {iframe.get('src')}")
                print(f"ID: {iframe.get('id')}")

        # Print all unique classes found
        print("\n📋 All unique classes found:")
        unique_classes = set()
        for tag in soup.find_all(class_=True):
            if isinstance(tag.get("class"), list):
                unique_classes.update(tag.get("class"))
        print(list(unique_classes))


if __name__ == "__main__":
    # Test with a real bill URL
    url = "https://www.parl.ca/legisinfo/en/bill/44-1/s-2"
    asyncio.run(debug_scrape(url))
