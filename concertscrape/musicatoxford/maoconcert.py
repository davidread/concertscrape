from common.concert_schema import Concert, Performer, ProgrammeItem

from bs4 import BeautifulSoup
import re
from datetime import datetime


def extract_concert(html_content: str) -> Concert:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title
    title_elem = soup.find('h1', class_='blue')
    concert_data = {
        'title': title_elem.text.strip() if title_elem else '',
        'performers': [],
        'programme': []
    }

    # Extract date
    date_span = soup.find('span', class_='event-description__date')
    if date_span:
        date_str = date_span.text.strip()
        concert_data['date'] = date_str
        try:
            date_obj = datetime.strptime(date_str, '%A %d %B %Y')
            concert_data['date_parsed'] = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    # Extract times
    event_info = soup.find_all('div', class_='event-information__single')
    for info in event_info:
        heading = info.find('h3')
        if heading:
            if heading.text == 'Start Time':
                concert_data['start_time'] = info.find('p').text.strip()
            elif heading.text == 'End Time':
                concert_data['end_time'] = info.find('p').text.strip()
            elif heading.text == 'Tickets':
                concert_data['ticket_prices'] = info.find('p').text.strip()
    
    # Extract venue
    venue_link = soup.find('a', class_='event-description__venue')
    if venue_link:
        concert_data['venue'] = venue_link.text.strip()
    
    # Extract venue address
    venue_info = soup.find('div', class_='programme-listing__venue')
    if venue_info:
        address_paragraphs = venue_info.find_all('p')
        if address_paragraphs:
            concert_data['venue_address'] = address_paragraphs[0].text.strip()

    listing_wrapper = soup.find_all('div', class_='programme-listing__wrapper')
    for section in listing_wrapper:
        title = section.find('h2')
        if not title:
            continue

        # Extract programme
        if title.text.strip() == 'Programme':
            programme_items = section.find_all('div', class_='programme-listing__single')
            for item in programme_items:
                composer = item.find('h3')
                piece = item.find('p')
                if composer and piece:
                    concert_data['programme'].append({
                        'composer': composer.text.strip(),
                        'piece': piece.text.strip()
                    })


        # Extract performers
        elif title.text.strip() == 'Performers':
            performer_items = section.find_all('div', class_='programme-listing__single')
            for item in performer_items:
                role = item.find('h3')
                name = item.find('p')
                if role and name:
                    concert_data['performers'].append({
                        'role': role.text.strip(),
                        'name': name.text.strip()
                    })

        elif title.text.strip() == 'Venue Information':
            # extracted elsewhere
            continue
    
        else:
            print(f'unparsed section: {title}')
    
    # Extract description
    description = soup.find('div', class_='event-description')
    if description:
        # Get all paragraphs but exclude the ones containing date, venue and title
        paragraphs = [p.text.strip() for p in description.find_all('p') if not any(c in p.get('class', []) for c in ['event-description__date', 'event-description__venue'])]
        concert_data['description'] = '\n'.join(paragraphs)
    
    return Concert(**concert_data)

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
