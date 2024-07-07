from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from typing import Optional, List

app = FastAPI()

icon_cache = {}

class Company(BaseModel):
    name: str
    url: HttpUrl

class CompanyList(BaseModel):
    companies: list[Company]

class CompanyWithIcon(BaseModel):
    name: str
    url: HttpUrl
    icon_url: str

class IconRequest(BaseModel):
    url: HttpUrl


class IconFinder:
    @staticmethod
    async def find(soup: BeautifulSoup, base_url: str) -> Optional[str]:
        raise NotImplementedError


class FaviconFinder(IconFinder):
    @staticmethod
    async def find(soup: BeautifulSoup, base_url: str) -> Optional[str]:
        favicon = soup.find('link', rel=re.compile(r'(shortcut )?icon', re.I))
        return favicon['href'] if favicon else None


class AppleTouchIconFinder(IconFinder):
    @staticmethod
    async def find(soup: BeautifulSoup, base_url: str) -> Optional[str]:
        apple_touch_icon = soup.find('link', rel='apple-touch-icon')
        return apple_touch_icon['href'] if apple_touch_icon else None


class OpenGraphImageFinder(IconFinder):
    @staticmethod
    async def find(soup: BeautifulSoup, base_url: str) -> Optional[str]:
        og_image = soup.find('meta', property='og:image')
        return og_image['content'] if og_image else None


class HeaderLogoFinder(IconFinder):
    @staticmethod
    async def find(soup: BeautifulSoup, base_url: str) -> Optional[str]:
        header_logo = soup.select_one('header img, #header img, .logo img')
        return header_logo['src'] if header_logo else None


class SvgLogoFinder(IconFinder):
    @staticmethod
    async def find(soup: BeautifulSoup, base_url: str) -> Optional[str]:
        svg_logo = soup.select_one('header svg, #header svg, .logo svg')
        return str(svg_logo) if svg_logo else None


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
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)