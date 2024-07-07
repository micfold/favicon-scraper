from typing import Optional, List
from urllib.parse import urljoin

import httpx
import uvicorn
from fastapi import FastAPI


from src.schemas import CompanyWithIcon, CompanyList

app = FastAPI()

icon_cache = {}


async def find_icon(base_url: str) -> Optional[str]:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Check common favicon locations
        common_favicon_paths = [
            '/favicon.ico',
            '/favicon.png',
            '/apple-touch-icon.png',
            '/apple-touch-icon-precomposed.png'
        ]

        for path in common_favicon_paths:
            favicon_url = urljoin(base_url, path)
            try:
                response = await client.head(favicon_url)
                if response.status_code == 200:
                    return favicon_url
            except httpx.HTTPError:
                continue

        # If no favicon found, use a favicon service
        favicon_service_url = f"https://www.google.com/s2/favicons?domain={base_url}&sz=512"

        try:
            response = await client.head(favicon_service_url)
            if response.status_code == 200:
                return favicon_service_url
        except httpx.HTTPError:
            pass

    return None


@app.post("/get_icons", response_model=List[CompanyWithIcon])
async def get_icons(company_list: CompanyList):
    results = []

    for company in company_list.companies:
        url = str(company.url)

        if url in icon_cache:
            results.append(CompanyWithIcon(name=company.name, url=url, icon_url=icon_cache[url]))
            continue

        try:
            icon_url = await find_icon(url)

            if icon_url:
                icon_cache[url] = icon_url
                results.append(CompanyWithIcon(name=company.name, url=url, icon_url=icon_url))
            else:
                results.append(CompanyWithIcon(name=company.name, url=url, icon_url=""))

        except Exception as e:
            print(f"Unexpected error processing {company.name}: {str(e)}")
            results.append(CompanyWithIcon(name=company.name, url=url, icon_url=""))

    return results


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
