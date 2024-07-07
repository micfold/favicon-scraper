import re
from pydantic import Optional, BaseModel
from bs4 import BeautifulSoup
import HttpUrl

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
