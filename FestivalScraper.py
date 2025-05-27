import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

BASE_URL = "https://do312.com/festivals"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get_soup(url):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def parse_event_details(event):
    title_tag = event.find('span', class_='ds-listing-event-title-text')
    title = title_tag.text.strip() if title_tag else 'Untitled Event'

    date_meta = event.find('meta', itemprop='startDate')
    start_date_str = date_meta['content'] if date_meta and 'content' in date_meta.attrs else ''
    start_date, start_time = '', ''
    end_date, end_time = '', ''

    if start_date_str:
        try:
            dt = datetime.fromisoformat(start_date_str)
            start_date = dt.strftime('%m/%d/%Y')
            start_time = dt.strftime('%I:%M %p')
            end_date = start_date
        except ValueError:
            pass

    venue_tag = event.find('div', class_='ds-venue-name')
    venue = venue_tag.text.strip() if venue_tag else 'Chicago'

    link_tag = event.find('a', class_='ds-listing-event-title url summary')
    link = "https://do312.com" + link_tag['href'] if link_tag and 'href' in link_tag.attrs else ''

    return [
        title,
        start_date,
        start_time,
        end_date,
        end_time,
        'False' if start_time else 'True',
        link,
        venue,
        'True'
    ]

def scrape_events():
    all_events = []
    page = 1
    while True:
        url = f"{BASE_URL}?page={page}"
        soup = get_soup(url)
        events = soup.find_all('div', class_='ds-listing')
        if not events:
            break
        for event in events:
            all_events.append(parse_event_details(event))
        page += 1
        time.sleep(1)  # Be polite to the server

    return all_events

def save_to_csv(events, filename='do312_festivals.csv'):
    headers = ['Subject', 'Start Date', 'Start Time', 'End Date', 'End Time', 'All Day Event', 'Description', 'Location', 'Private']
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(events)

if __name__ == '__main__':
    events = scrape_events()
    save_to_csv(events)
    print(f"Scraped and saved {len(events)} events to 'do312_festivals.csv'")
