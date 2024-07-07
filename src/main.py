from fastapi import FastAPI
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from typing import Optional
import uvicorn
from fastapi import APIRouter
import schemas, router

app = FastAPI()

router = APIRouter()

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


if __name__ == "__main__":


    uvicorn.run(app, host="0.0.0.0", port=8000)