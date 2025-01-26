from maoconcert import extract_concert, print_concert, print_concert_scrape
from concert_schema import Concert, Performer, ProgrammeItem, ConcertScrape
from concert_sheet import SheetHandler
from stats import ScrapingStats, ScrapeResult

from datetime import datetime
import logging
import os
import time
import xml.etree.ElementTree as ET

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REQUESTS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0"
}
            
class ConcertScraper:
    def __init__(self, sheet_handler):
        self.sheet_handler = sheet_handler

    def parse_sitemap(self, sitemap_content):
        root = ET.fromstring(sitemap_content)
        concerts = []
        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            lastmod = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod').text
            if '/whats-on/' in loc and loc != 'https://www.musicatoxford.com/whats-on/':
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
            # this sometimes happens
            return
        response.raise_for_status()

        concert = extract_concert(response.text)
        concert_scrape = ConcertScrape(
            scrape_date=datetime.now(),
            url=url,
            last_modified=last_modified,
            concert=concert,
        )
        print_concert_scrape(concert_scrape)
        return concert_scrape

    def process_concerts(self, sitemap_content):
        concerts = self.parse_sitemap(sitemap_content)
        sheet_data = self.sheet_handler.get_all_data()
        
        for concert in concerts:
            if self.needs_update(concert['url'], concert['lastmod'], sheet_data):
                try:
                    concert_scrape = self.scrape_concert(concert['url'], concert['lastmod'])
                except Exception as e:
                    print(f"Error scraping concert {concert['url']}: {e}")
                    stats_add_concert(ScrapeResult.ERROR)
                    continue
                if not concert_scrape:
                    continue

                self.sheet_handler.update_concert(concert_scrape)
                logger.info(f"Updated concert: {concert['url']}")
                stats_add_concert(ScrapeResult.NEW)
            else:
                stats_add_concert(ScrapeResult.EXISTING)


class RateLimitedRequestsSession(requests.Session):
    def __init__(self, rate_limit_enabled=True, delay=1.0):
        super().__init__()
        self.last_request_time = 0
        self.rate_limit_enabled = rate_limit_enabled
        self.delay = delay

    def request(self, *args, **kwargs):
        if self.rate_limit_enabled:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        
        response = super().request(*args, **kwargs)
        self.last_request_time = time.time()
        return response

requests_session = RateLimitedRequestsSession(rate_limit_enabled=not os.environ.get("DISABLE_RATELIMITING"))
stats = ScrapingStats()
stats_add_concert = lambda result: stats.add_concert('musicatoxford.com', result)

if __name__ == "__main__":
    sheet_handler = SheetHandler()
    scraper = ConcertScraper(sheet_handler)

    response = requests_session.get("https://www.musicatoxford.com/whats-on-sitemap.xml", headers=REQUESTS_HEADERS)
    response.raise_for_status()
    sitemap_content = response.text
    
    scraper.process_concerts(sitemap_content)
    stats.print_summary()
