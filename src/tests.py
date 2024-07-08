from src.schemas import CompanyWithIcon
from src.main import app, icon_cache
from fastapi.testclient import TestClient
import pytest


# Assuming TEST_COMPANIES is defined as shown previously
TEST_COMPANIES = [
    {"name": "Apple", "url": "https://www.apple.com", "icon_url": "https://www.apple.com/favicon.ico"},
    {"name": "Microsoft", "url": "https://www.microsoft.com", "icon_url": "https://www.microsoft.com/favicon.ico"},
    # Add other companies as needed
]


@pytest.mark.parametrize("company", TEST_COMPANIES)
def test_company_with_icon_model(company):
    # Given
    name = company["name"]
    url = company["url"].rstrip('/')
    icon_url = company["icon_url"]
    # When
    company_with_icon = CompanyWithIcon(name=name, url=company['url'], icon_url=icon_url)
    # Then
    assert company_with_icon.name == name
    assert str(company_with_icon.url).rstrip('/') == url  # Convert Url object to string and remove trailing slash


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_icon_cache():
    icon_cache.clear()


def test_icon_chaching():
    company_url = "https://www.apple.com"
    company_name = "Apple"
    normalized_company_url = company_url if company_url.endswith('/') else f"{company_url}/"
    # First request to populate the cache
    response = client.post("/get_icons", json={"companies": [{"name": company_name, "url": company_url}]})
    assert response.status_code == 200
    assert normalized_company_url in icon_cache

    # Second request to check cache usage
    response = client.post("/get_icons", json={"companies": [{"name": company_name, "url": company_url}]})
    assert response.status_code == 200
    # Verify that the icon URL was retrieved from the cache rather than making a new request
    # This can be inferred if the response time is significantly shorter or by mocking the network call
