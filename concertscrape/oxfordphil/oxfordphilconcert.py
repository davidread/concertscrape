from concertscrape.common.concert_schema import Concert, Performer, ProgrammeItem
from bs4 import BeautifulSoup, Tag
from datetime import datetime
import re

def parse_date_and_time(date_str: str) -> tuple:
    """Parse the date string in format '12 Jul 2025 | 19:30'"""
    try:
        date_part, time_part = date_str.split('|')
        date_obj = datetime.strptime(date_part.strip(), '%d %b %Y')
        start_time = time_part.strip()
        return date_obj.date(), start_time, date_part.strip()
    except (ValueError, AttributeError):
        return None, None, None

def clean_text(text: str) -> str:
    """Clean up text by removing extra whitespace"""
    if not text:
        return ''
    return ' '.join(text.strip().split())

def extract_program_and_performers_and_description(desc_elem: Tag):
    """Extract program items and performers from the event-description"""
    program = []
    performers = []
    description_lines = []
    
    paras = desc_elem.find_all('p')
    for para in paras:

        # Split into blocks based on double <br> tags
        blocks = re.split(r'<br\s*/?>\s*<br\s*/?>', str(para))
        
        for block in blocks:
            # Skip empty blocks
            if not clean_text(BeautifulSoup(block, 'html.parser').get_text()):
                continue
                
            # Determine if this block is performers
            has_strong = re.search(r'<strong>([^<]+)</strong>', block)
            has_performer_role = has_strong and any(role in block.lower() for role in [
                'conductor', 'soprano', 'piano', 'violin', 'viola', 'cello', 
                'tenor', 'bass', 'baritone', 'mezzo-soprano', 'alto', 'narrator',
                'choir', 'choristers'
            ])
            # Determine if this block is programme
            is_programme = has_strong and not has_performer_role
            
            # Split block into lines
            lines = block.split('<br/>')
            if len(lines) <= 1:  # If no <br/> found, try <br>
                lines = block.split('<br>')
                
            # If a single line, make it a list
            if len(lines) <= 1:
                lines = [block]
                
            # Process each line based on block type
            for line in lines:
                if has_performer_role:
                    # Process as performer
                    strong_match = re.search(r'<strong>([^<]+)</strong>', line)
                    if strong_match:
                        name = clean_text(strong_match.group(1))
                        # Get text after strong tag for role
                        rest = clean_text(re.sub(r'<[^>]+>', '', line.replace(strong_match.group(0), '')))
                        if rest:
                            role = rest
                        else:
                            # If no role specified, the block might be a choir or ensemble
                            role = ''
                        performers.append(Performer(name=name, role=role))
                elif is_programme:
                    # Process as programme
                    strong_match = re.search(r'<strong>([^<]+)</strong>', line)
                    if strong_match:
                        composer = clean_text(strong_match.group(1))
                        piece = clean_text(re.sub(r'<[^>]+>', '', line.replace(strong_match.group(0), '')))
                    else:
                        piece = clean_text(line)
                    program.append(ProgrammeItem(composer=composer, piece=piece))
                else:
                    # Process as description
                    description_lines.append(line)

    return program, performers, "\n".join(description_lines)

def extract_concert(html_content: str) -> Concert:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initial data with required fields
    concert_data = {
        'title': '',
        'date': '',
        'performers': [],
        'programme': [],
    }
    
    # Extract title
    title_elem = soup.find('h2', class_='event-title')
    if title_elem:
        concert_data['title'] = clean_text(title_elem.text)
    
    # Extract date, time and venue
    subtitle = soup.find('div', class_='event-subtitle')
    if subtitle:
        parts = subtitle.text.split('|')
        if len(parts) >= 3:
            date_time = ' | '.join(parts[:2])
            date_parsed, start_time, date_str = parse_date_and_time(date_time)
            concert_data['date'] = date_str
            concert_data['date_parsed'] = date_parsed
            concert_data['start_time'] = start_time
            concert_data['venue'] = clean_text(parts[2])
    
    # Extract ticket prices
    price_box = soup.find('div', class_='event-info-box')
    if price_box:
        ticket_prices = []
        for line in price_box.text.split('\n'):
            if 'Tickets:' in line:
                ticket_prices.append(clean_text(line.replace('Tickets:', '').strip()))
            elif 'Students' in line:
                ticket_prices.append(clean_text(line.strip()))
        concert_data['ticket_prices'] = ' '.join(ticket_prices)

    # Extract description and program/performers
    desc_elem = soup.find('div', class_='event-description')
    if desc_elem:
        # Extract program, performers and description
        program, performers, description = extract_program_and_performers_and_description(desc_elem)
        concert_data['programme'] = program
        concert_data['performers'] = performers
        concert_data['description'] = description

    return Concert(**concert_data)
