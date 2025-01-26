from pydantic import BaseModel, Field
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

    class Config:
        json_schema_extra = {
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

class ConcertScrape(BaseModel):
    url: str
    scrape_date: datetime.datetime
    last_modified: Optional[datetime.datetime] = None
    concert: Concert