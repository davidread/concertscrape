from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import datetime

class Performer(BaseModel):
    role: str
    name: str

class ProgrammeItem(BaseModel):
    composer: str
    piece: str

class Concert(BaseModel):
    title: str
    date: str
    date_parsed: Optional[datetime.date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    venue: Optional[str] = None
    venue_address: Optional[str] = None
    ticket_prices: Optional[str] = None
    performers: List[Performer] = Field(default_factory=list)
    programme: List[ProgrammeItem] = Field(default_factory=list)
    description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "International Organ Series: Bob Keys",
                "date": "2021-05-15T00:00:00",
                "start_time": "7PM",
                "venue": "Winchester College Chapel",
                "performers": [
                    {"role": "Organist", "name": "Bob Keys"}
                ]
            }
        }
    )

class ConcertScrape(BaseModel):
    url: str
    scrape_date: datetime.datetime
    last_modified: Optional[datetime.datetime] = None
    concert: Concert

# Function to print the extracted data in a readable format
def print_concert(concert):
    print(f"Title: {concert.title}")
    print(f"Date: {concert.date_parsed.strftime('%Y-%m-%d') or concert.date}")
    print(f"Time: {concert.start_time} - {concert.end_time}")
    print(f"Venue: {concert.venue}")
    print(f"Address: {concert.venue_address}")
    print(f"Tickets: {concert.ticket_prices}\n")
    
    print("Performers:")
    for performer in concert.performers:
        print(f"- {performer.role}: {performer.name}")
    
    print("\nProgramme:")
    for item in concert.programme:
        print(f"- {item.composer}: {item.piece}")
    
    print("\nDescription:")
    print(concert.description)

def print_concert_scrape(concert_scrape):
    print(f"URL: {concert_scrape.url}")
    print(f"Last modified: {concert_scrape.url}")
    print(f"Concert:")
    print_concert(concert_scrape.concert)
