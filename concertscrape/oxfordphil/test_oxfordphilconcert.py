import pytest
from datetime import datetime, date
from concertscrape.oxfordphil.oxfordphilconcert import extract_concert, clean_text, parse_date_and_time
from concertscrape.common.concert_schema import Concert, ProgrammeItem, Performer

@pytest.mark.parametrize("input_text,expected", [
    ('  Hello   World  ', 'Hello World'),
    ('Multiple     Spaces', 'Multiple Spaces'),
    ('\nNew\nLines\n', 'New Lines'),
    ('', ''),
    (None, ''),
])
def test_clean_text(input_text, expected):
    """Test the text cleaning function"""
    assert clean_text(input_text) == expected

def test_parse_date_and_time():
    """Test date and time parsing"""
    test_date = '12 Jul 2025 | 19:30'
    date_parsed, time, date_str = parse_date_and_time(test_date)
    
    assert date_parsed == date(2025, 7, 12)
    assert time == '19:30'
    assert date_str == '12 Jul 2025'
    
    # Test invalid date
    assert parse_date_and_time('invalid date') == (None, None, None)

@pytest.fixture
def opera_html():
    return """
    <div class="event-subtitle">12 Jul 2025 | 19:30 | Sheldonian Theatre</div>
    <div class="event-description">
    <p><strong>Strauss II</strong> Overture Die Fledermaus<br>
    <strong>Mascagni </strong>Prelude & Intermezzo <em>Cavalleria Rusticana</em><br>
    <strong>Puccini </strong>Preludio sinfonico<br>
    <br>
    <strong>Angela Gheorghiu </strong>soprano<br>
    <strong>Marios Papadopoulos</strong> conductor</p>
    <p>Angela Gheorghiu, one of the most glamorous and gifted opera singers of our time...</p>
    </div>
    """

def test_opera_program(opera_html):
    """Test parsing a concert with opera selections"""
    concert = extract_concert(opera_html)
    
    assert isinstance(concert, Concert)
    assert concert.venue == 'Sheldonian Theatre'
    assert len(concert.programme) == 3  # Three pieces
    assert len(concert.performers) == 2  # Two performers
    
    # Check first program item
    assert concert.programme[0].composer == 'Strauss II'
    assert concert.programme[0].piece == 'Overture Die Fledermaus'
    
    # Check performers
    assert any(p.name == 'Angela Gheorghiu' and p.role == 'soprano' for p in concert.performers)
    assert any(p.name == 'Marios Papadopoulos' and p.role == 'conductor' for p in concert.performers)

@pytest.fixture
def carols_html():
    return """
    <div class="event-subtitle">12 Jul 2025 | 19:30 | Sheldonian Theatre</div>
    <div class="event-description">
        <p><strong>Please note the change of start time </strong></p>
        <p><strong>Traditional carols:</strong><br>
        O come, all ye faithful, &nbsp;arr. David Willcocks<br>
        King Jesus hath a garden, arr. John Rutter<br>
        Quelle est cette odeur agréable, arr.&nbsp;David Willcocks<br>
        I saw three ships, arr. John Rutter
        <br><br>
        <strong>Tchaikovsky</strong> The Crown of Roses
        <br><br>
        <strong>Arensky</strong> Variations on a Theme by Tchaikovsky
        <br><br>
        The first Nowell, arr. David Willcocks
        <br><br>
        <strong>John Rutter</strong> Brother Heinrich's Christmas
        <br><br>
        <strong>Britten</strong> <em>Wolcom Yole</em> and <em>There is no rose</em> from A Ceremony of Carols
        <br><br>
        Ding dong! merrily on high, arr. John Rutter &nbsp;
        <br><br>
        <strong>Carols by Gustav Holst:</strong><br>
        In the bleak mid-winter<br>
        Lullay my liking<br>
        Personent hodie
        <br><br>
        <strong>Handel</strong> Excerpt from Messiah
        <br><br>
        <strong>John Rutter</strong> Christmas Child (Oxford première)<br>
        <strong>John Rutter</strong> Shepherd's Pipe Carol 
        <br><br>
        <strong>Carols arranged by John Rutter:</strong><br>
        The twelve days of Christmas<br>
        Still, still, still<br>
        Silent Night
        <br><br>
        Hark! the herald angels sing, arr. Willcocks
        <br><br>
        <strong>The Choir of Merton College</strong>
        <br>
        <strong>Choristers of Winchester Cathedral</strong><br>
        <strong>Sir John Rutter</strong> conductor<br>
        <strong>Simon Callow</strong> narrator</p>
        <p>Sir John Rutter returns to Oxford for another Christmas celebration in the company of the Oxford Philharmonic Orchestra, Merton College Choir and the Choristers of Winchester Cathedral. Sir John's musical fable Brother Heinrich's Christmas forms the centrepiece of a programme that features carols and Christmas music old and new including some of Sir John's own carols, and as ever the audience has the opportunity to sing along with the choir and orchestra in classic Christmas hymns.</p>
        <p>Supported by Jon &amp; Julia Aisbitt</p>
    </div>
    """

def test_carols_program(carols_html):
    """Test parsing a concert with carols and arrangements"""
    concert = extract_concert(carols_html)
    
    assert isinstance(concert, Concert)
    
    # Check programme
    assert any(p.piece == 'The Crown of Roses' and p.composer == 'Tchaikovsky' for p in concert.programme)
    assert any(p.piece == 'O come, all ye faithful, arr. David Willcocks' for p in concert.programme)

    # Check performers
    assert any(p.name == 'The Choir of Merton College' and p.role == '' for p in concert.performers)
    assert any(p.name == 'Choristers of Winchester Cathedral' and p.role == '' for p in concert.performers)
    assert any(p.name == 'Sir John Rutter' and p.role == 'conductor' for p in concert.performers)
    assert any(p.name == 'Simon Callow' and p.role == 'narrator' for p in concert.performers)

@pytest.fixture
def minimal_html():
    return """                                        
    <h2 class="event-title">
        Simple Concert
    </h2>
    <div class="event-subtitle">
        12 Jul 2025 | 19:30 | Sheldonian Theatre, Broad Street
    </div>
    <div class="event-description">
        <p>
            <strong>Handel</strong> Water Music<br>
            <br>
            <strong>Bob Smith</strong> conductor
        </p>
        <p>Experience the sounds of Baroque in a concert.</p>
        <p>The concert is in partnership with <a href="https://oxford.org/">Oxford</a>. </p>
    </div>
    """

def test_minimal_concert(minimal_html):
    """Test parsing a concert with minimal information"""
    concert = extract_concert(minimal_html)
    
    assert concert.title == 'Simple Concert'
    assert concert.date == '12 Jul 2025'
    assert concert.date_parsed == date(2025, 7, 12)
    assert concert.venue == 'Sheldonian Theatre, Broad Street'
    assert concert.programme == [ProgrammeItem(composer='Handel', piece='Water Music')]
    assert concert.performers == [Performer(role='conductor', name='Bob Smith')]

def test_missing_date():
    """Test handling of missing date information"""
    html = """
    <h1>Simple Concert</h1>
    <div class="event-description">
    <p><strong>Mozart</strong> Symphony No. 40</p>
    </div>
    """
    
    concert = extract_concert(html)
    assert concert.start_time is None
    assert concert.venue is None

def test_empty_html():
    """Test handling of empty HTML"""
    concert = extract_concert("")
    assert concert.title == ""
