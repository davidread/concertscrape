import pytest
from concertscrape.oxfordphil.oxfordphil import OxfordPhilConcertScraper, Concert, Performer, ProgrammeItem
from concertscrape.common.concert_sheet import SheetHandler
from datetime import datetime, timezone
import pandas as pd

@pytest.fixture
def scraper():
    return OxfordPhilConcertScraper(sheet_handler=None)

@pytest.fixture
def sitemap_content():
    return """<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="//oxfordphil.com/wp-content/plugins/wordpress-seo/css/main-sitemap.xsl"?>
<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd http://www.google.com/schemas/sitemap-image/1.1 http://www.google.com/schemas/sitemap-image/1.1/sitemap-image.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://oxfordphil.com/event/baroque-fest/</loc>
        <lastmod>2022-01-21T12:11:57+00:00</lastmod>
        <image:image>
            <image:loc>https://oxfordphil.com/wp-content/uploads/2022/01/Baroque.jpg</image:loc>
        </image:image>
    </url>
    <url>
        <loc>https://oxfordphil.com/event/sir-bob-moore-in-recital/</loc>
        <lastmod>2022-01-28T08:33:18+00:00</lastmod>
        <image:image>
            <image:loc>https://oxfordphil.com/wp-content/uploads/2022/01/Bobby.jpg</image:loc>
        </image:image>
    </url>
</urlset>
"""

@pytest.fixture
def mock_sheet_data():
    return pd.DataFrame({
        'url': ['https://oxfordphil.com/event/test-concert/'],
        'last_modified': ['2024-01-01T12:00:00+00:00']
    })

def test_parse_sitemap(scraper, sitemap_content):
    """Test that sitemap parsing works correctly"""
    concerts = scraper.parse_sitemap(sitemap_content)
    
    # Check that we got some concerts
    assert len(concerts) == 2
    
    # Check the structure of the first concert
    concert = concerts[0]
    assert concert['url'] == "https://oxfordphil.com/event/baroque-fest/"
    assert concert['lastmod'] == datetime(2022, 1, 21, 12, 11, 57, tzinfo=timezone.utc)

@pytest.mark.parametrize("test_date,url,expected", [
    # Test older modification date
    ('2023-12-31T12:00:00+00:00', 'https://oxfordphil.com/event/test-concert/', False),
    # Test newer modification date
    ('2024-01-02T12:00:00+00:00', 'https://oxfordphil.com/event/test-concert/', True),
    # Test non-existent concert
    ('2024-01-02T12:00:00+00:00', 'https://oxfordphil.com/event/new-concert/', True),
])
def test_needs_update(scraper, mock_sheet_data, test_date, url, expected):
    """Test the needs_update logic"""
    date = datetime.strptime(test_date, '%Y-%m-%dT%H:%M:%S%z')
    assert scraper.needs_update(url, date, mock_sheet_data) == expected
