import requests
from bs4 import BeautifulSoup
import os
import json
import logging
from datetime import datetime
from app.config.settings import NEWS_SOURCES, OUTPUT_DIR_RAW

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to fetch HTML content from a given URL
def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None


# Function to parse the headline from a single news item
def parse_headline(item, config):
    if "sub_tag" in config["headline"]:
        title = item.find_next(config["headline"]["sub_tag"]).get_text(strip=True)
    else:
        title = item.get_text(strip=True)
    return title


# Function to parse the description from a single news item
def parse_description(item, config):
    description = ""
    description_elem = item.find_next(config["description"]["tag"], class_=config["description"]["class"])
    if description_elem:
        if "sub_tag" in config["description"]:
            description = description_elem.find_next(config["description"]["sub_tag"]).get_text(strip=True)
        else:
            description = description_elem.get_text(strip=True)
    return description


# Function to scrape headlines from a single news source
def scrape_source(source, config):
    url = config["url"]
    html_content = fetch_html(url)
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    headlines = []
    fetched_date = datetime.now().isoformat()  # Get the current date and time in ISO format

    if "data-tgev-label" in config["headline"]:
        elements = soup.find_all(config["headline"]["tag"], class_=config["headline"]["class"], attrs={"data-tgev-label": config["headline"]["data-tgev-label"]})
    else:
        elements = soup.find_all(config["headline"]["tag"], class_=config["headline"]["class"])

    for item in elements:
        title = parse_headline(item, config)
        if title:
            description = parse_description(item, config)
            headlines.append({
                'title': title,
                'description': description,
                'source': source,
                'fetched_date': fetched_date  # Add the fetched date
            })
    
    return headlines


# Function to save scraped headlines to JSON files
def save_headlines(headlines):
    if not headlines:
        logging.info("No headlines to save.")
        return

    # Create directory structure based on fetched date
    fetched_date = datetime.now()
    year = fetched_date.strftime('%Y')
    month = fetched_date.strftime('%m')
    day = fetched_date.strftime('%d')

    output_dir = os.path.join(OUTPUT_DIR_RAW, year, month, day)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, 'headlines.json')
    try:
        with open(output_path, 'w') as f:
            json.dump(headlines, f, indent=4)
        logging.info(f"Headlines saved to {output_path}")
    except IOError as e:
        logging.error(f"Error saving headlines: {e}")


# Main function to scrape headlines from all sources and save them to JSON files
def scrape_headlines():
    all_headlines = []
    for source, config in NEWS_SOURCES.items():
        logging.info(f"Scraping headlines from {source}")
        headlines = scrape_source(source, config)
        all_headlines.extend(headlines)
    save_headlines(all_headlines)

