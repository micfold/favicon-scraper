import asyncio
import aiohttp
from typing import List, Dict

CHUNK_SIZE = 10
TEST_COMPANIES = [
        {"name": "Apple", "url": "https://www.apple.com"},
        {"name": "Microsoft", "url": "https://www.microsoft.com"},
        {"name": "Google", "url": "https://abc.xyz/"},
        {"name": "American Express", "url": "https://americanexpress.com"},
        {"name": "US Steel", "url": "https://www.ussteel.com"},
        {"name": "Raiffeisen Bank Internatiol", "url": "https://www.rbinternational.com"},
    ]


async def process_companies(companies: List[Dict[str, str]]):
    async with aiohttp.ClientSession() as session:
        chunk_size = CHUNK_SIZE
        for i in range(0, len(companies), chunk_size):
            chunk = companies[i:i + chunk_size]
            payload = {
                "companies": [{"name": company["name"], "url": company["url"]} for company in chunk]
            }

            try:
                async with session.post('http://localhost:8000/get_icons', json=payload) as response:
                    if response.status == 200:
                        results = await response.json()
                        for result, original in zip(results, chunk):
                            original["icon_url"] = result["icon_url"]
                    else:
                        print(f"Error processing chunk {i // chunk_size + 1}: Status {response.status}")
                        print(f"Response: {await response.text()}")
            except aiohttp.ClientError as e:
                print(f"Connection error: {e}")

        return companies


async def main():
    companies = TEST_COMPANIES

    processed_companies = await process_companies(companies)

    for company in processed_companies:
        print(f"Company: {company['name']}")
        print(f"URL: {company['url']}")
        print(f"Icon URL: {company.get('icon_url', 'Not found')}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())