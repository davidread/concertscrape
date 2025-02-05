from concertscrape.musicatoxford.maoconcert import extract_concert
from concertscrape.common.concert_schema import ProgrammeItem, Performer
import datetime
import pytest

@pytest.fixture
def test_html():
    return """
    <div class="event-description">
        <span class="event-description__date blue">Thursday 15 May 2020</span>
        <a href="/venues/Winchester-college-chapel/" class="event-description__venue blue">Winchester College Chapel</a>
        <h1 class="blue">International Organ Series: Bob Keys</h1>
    </div>
    <div class="event-information__single">
        <h3>Start Time</h3>
        <p>7PM</p>
    </div>
    <div class="event-information__single">
        <h3>Tickets</h3>
        <p>£15 Full price | £7.50 Standard concession</p>
    </div>
    <div class="programme-listing__wrapper">
        <h2>Programme</h2>
        <div class="programme-listing__single">
            <h3>Jeanne Demessieux</h3>
            <p>Te Deum, Op. 11</p>
        </div>
        <div class="programme-listing__single">
            <h3>George Baker</h3>
            <p>Deux Evocations</p>
        </div>
    </div>
    <div class="programme-listing__wrapper">
        <h2>Performers</h2>
        <div class="programme-listing__single">
            <h3>Organist</h3>
            <p>Bob Keys</p>
        </div>
    </div>
    """

@pytest.fixture
def concert(test_html):
    return extract_concert(test_html)

def test_extract_title(concert):
    assert concert.title == 'International Organ Series: Bob Keys'

def test_extract_date(concert):
    assert concert.date == "Thursday 15 May 2020"
    assert concert.date_parsed == datetime.date(2020, 5, 15)

def test_extract_time(concert):
    assert concert.start_time == '7PM'

def test_extract_venue(concert):
    assert concert.venue == 'Winchester College Chapel'

def test_extract_tickets(concert):
    assert concert.ticket_prices == '£15 Full price | £7.50 Standard concession'

def test_extract_programme(concert):
    expected = [
        ProgrammeItem(composer='Jeanne Demessieux', piece='Te Deum, Op. 11'),
        ProgrammeItem(composer='George Baker', piece='Deux Evocations')
    ]
    assert concert.programme == expected

def test_extract_performers(concert):
    expected = [Performer(role='Organist', name='Bob Keys')]
    assert concert.performers == expected