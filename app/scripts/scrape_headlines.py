import os
import pandas as pd
import json
from app.config.logger import logger
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from app.config.settings import NEWS_SOURCES, OUTPUT_DIR_RAW

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TIMESTAMP_FILE = os.path.join(OUTPUT_DIR_RAW, 'scraping_timestamp.txt')


def update_timestamp():
    with open(TIMESTAMP_FILE, 'w') as f:
        f.write(datetime.now().isoformat())


# Function to fetch HTML content from a given URL
def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return None


# Function to parse content (title or description) based on provided tag and attributes
def parse_content(element, tag_config):
    if isinstance(tag_config["tag"], list):
        matched_element = element.find_next(tag_config["tag"], attrs=tag_config.get("attrs", {}))
    else:
        matched_element = element.find_next(tag_config["tag"], attrs=tag_config.get("attrs", {}))
    return matched_element.get_text(strip=True) if matched_element else ""


# Function to scrape headlines and descriptions from a single news source
def scrape_source(source, config):
    url = config["url"]
    html_content = fetch_html(url)
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    headlines = []
    fetched_date = datetime.now().isoformat()  # Get the current date and time in ISO format

    elements = soup.find_all(config["headline"]["tag"], attrs=config["headline"].get("attrs", {}))

    for item in elements:
        title = parse_content(item, config["headline"])
        if not title:
            continue

        next_element = item.find_next()
        while next_element:
            if next_element.name == config["headline"]["tag"] and all(next_element.get(attr) == value for attr, value in config["headline"].get("attrs", {}).items()):
                break  # Another title appeared before a description, skip this title

            if isinstance(config["description"]["tag"], list):
                description_matched = next_element.name in config["description"]["tag"] and all(next_element.get(attr) == value for attr, value in config["description"].get("attrs", {}).items())
            else:
                description_matched = next_element.name == config["description"]["tag"] and all(next_element.get(attr) == value for attr, value in config["description"].get("attrs", {}).items())

            # Valid title-description pair
            if description_matched:
                description = parse_content(next_element, config["description"])
                headlines.append({
                    'title': title,
                    'description': description,
                    'source': source,
                    'fetched_date': fetched_date  # Add the fetched date
                })
                break

            next_element = next_element.find_next()

    return headlines


# Function to save scraped headlines to JSON files
def save_headlines(headlines):
    if not headlines:
        logger.info("No headlines to save.")
        return

    # Create directory structure based on fetched date
    fetched_date = datetime.now()
    output_dir = os.path.join(OUTPUT_DIR_RAW, fetched_date.strftime('%Y/%m/%d'))
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, 'headlines.json')
    csv_output_path = os.path.join(output_dir, 'headlines.csv')
    try:
        with open(output_path, 'w') as f:
            json.dump(headlines, f, indent=4)
        with open(csv_output_path, 'w') as f:
            df = pd.DataFrame(headlines)
            df.to_csv(f, index=False)
        logger.info(f"Headlines saved to {output_path}")
    except IOError as e:
        logger.error(f"Error saving headlines: {e}")


# Main function to scrape headlines from all sources and save them to JSON files
def scrape_headlines():
    all_headlines = []
    for source, config in NEWS_SOURCES.items():
        logger.info(f"Scraping headlines from {source}")
        headlines = scrape_source(source, config)
        all_headlines.extend(headlines)
    save_headlines(all_headlines)
    update_timestamp()
    logger.info("Scraping completed and timestamp updated.")
