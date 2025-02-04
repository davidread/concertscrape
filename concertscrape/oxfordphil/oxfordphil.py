from oxfordphilconcert import extract_concert
from concertscrape.common.concert_schema import Concert, Performer, ProgrammeItem, ConcertScrape, print_concert_scrape
from concertscrape.common.concert_sheet import SheetHandler
from concertscrape.common.stats import ScrapingStats, ScrapeResult
from concertscrape.common.requests_session import RateLimitedRequestsSession, REQUESTS_HEADERS
from datetime import datetime
import logging
import os
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OxfordPhilConcertScraper:
    def __init__(self, sheet_handler):
        self.sheet_handler = sheet_handler

    def parse_sitemap(self, sitemap_content):
        root = ET.fromstring(sitemap_content)
        concerts = []
        
        # Remove the XML stylesheet processing instruction if present
        if sitemap_content.startswith('<?xml'):
            clean_content = sitemap_content[sitemap_content.find('<urlset'):]
            root = ET.fromstring(clean_content)

        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            lastmod = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text
            
            # Only process event URLs
            if '/event/' in loc:
                concerts.append({
                    'url': loc,
                    'lastmod': datetime.strptime(lastmod, '%Y-%m-%dT%H:%M:%S%z')
                })
        return concerts

    def needs_update(self, concert_url, lastmod, sheet_data):
        for _, row in sheet_data.iterrows():
            if row.url == concert_url:
                sheet_lastmod = datetime.strptime(row['last_modified'], '%Y-%m-%dT%H:%M:%S%z')
                return lastmod > sheet_lastmod
        return True

    def scrape_concert(self, url, last_modified):
        response = requests_session.get(url, headers=REQUESTS_HEADERS)
        if response.status_code == 404:
            logger.warning(f"Concert page not found: {url}")
            return None
            
        response.raise_for_status()
        concert = extract_concert(response.text)
        concert_scrape = ConcertScrape(
            scrape_date=datetime.now(),
            url=url,
            last_modified=last_modified,
            concert=concert,
        )
        return concert_scrape

    def process_concerts(self, sitemap_content):
        concerts = self.parse_sitemap(sitemap_content)
        sheet_data = self.sheet_handler.get_all_data()
        
        for concert in concerts:
            if self.needs_update(concert['url'], concert['lastmod'], sheet_data):
                try:
                    concert_scrape = self.scrape_concert(concert['url'], concert['lastmod'])
                except Exception as e:
                    logger.error(f"Error scraping concert {concert['url']}: {e}")
                    stats_add_concert(ScrapeResult.ERROR)
                    continue

                if not concert_scrape:
                    continue

                self.sheet_handler.update_concert(concert_scrape)
                logger.info(f"Updated concert: {concert['url']}")
                stats_add_concert(ScrapeResult.NEW)
            else:
                stats_add_concert(ScrapeResult.EXISTING)

requests_session = RateLimitedRequestsSession(
    rate_limit_enabled=not os.environ.get("DISABLE_RATELIMITING")
)

stats = ScrapingStats()
stats_add_concert = lambda result: stats.add_concert('oxfordphil.com', result)

def scrape():
    sheet_handler = SheetHandler()
    scraper = OxfordPhilConcertScraper(sheet_handler)
    
    response = requests_session.get(
        "https://oxfordphil.com/event-sitemap.xml", 
        headers=REQUESTS_HEADERS
    )
    response.raise_for_status()
    sitemap_content = response.text
    
    scraper.process_concerts(sitemap_content)
    stats.print_summary()

if __name__ == "__main__":
    scrape()