import unittest
from oxfordphil import OxfordPhilConcertScraper, Concert, Performer, ProgrammeItem
from concertscrape.common.concert_sheet import SheetHandler
from datetime import datetime, timezone
import os

class TestOxfordPhilConcertScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = OxfordPhilConcertScraper(sheet_handler=None)
        
        # Load test sitemap data based on https://oxfordphil.com/event-sitemap.xml
        self.sitemap_content = """<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="//oxfordphil.com/wp-content/plugins/wordpress-seo/css/main-sitemap.xsl"?>
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

    def test_parse_sitemap(self):
        """Test that sitemap parsing works correctly"""
        concerts = self.scraper.parse_sitemap(self.sitemap_content)
        
        # Check that we got some concerts
        self.assertTrue(len(concerts) == 2)
        
        # Check the structure of the first concert
        concert = concerts[0]
        self.assertEqual(concert['url'], "https://oxfordphil.com/event/baroque-fest/")
        self.assertEqual(concert['lastmod'], datetime(2022, 1, 21, 12, 11, 57, tzinfo=timezone.utc))
        
    def test_needs_update(self):
        """Test the needs_update logic"""
        # Create a mock sheet data with one concert
        import pandas as pd
        mock_data = pd.DataFrame({
            'url': ['https://oxfordphil.com/event/test-concert/'],
            'last_modified': ['2024-01-01T12:00:00+00:00']
        })
        
        # Test older modification date
        older_date = datetime.strptime('2023-12-31T12:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z')
        self.assertFalse(self.scraper.needs_update(
            'https://oxfordphil.com/event/test-concert/',
            older_date,
            mock_data
        ))
        
        # Test newer modification date
        newer_date = datetime.strptime('2024-01-02T12:00:00+00:00', '%Y-%m-%dT%H:%M:%S%z')
        self.assertTrue(self.scraper.needs_update(
            'https://oxfordphil.com/event/test-concert/',
            newer_date,
            mock_data
        ))
        
        # Test non-existent concert
        self.assertTrue(self.scraper.needs_update(
            'https://oxfordphil.com/event/new-concert/',
            newer_date,
            mock_data
        ))

if __name__ == '__main__':
    unittest.main()