import requests
from bs4 import BeautifulSoup
from app.config.logger import logger
import os
import json
from datetime import datetime
from app.config.settings import NEWS_SOURCES, OUTPUT_DIR_RAW, TIMESTAMP_FILE


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


# Function to parse content from a BeautifulSoup element based on the given tag and attributes
def parse_content(element, tag_config):
    if "sub_tag" in tag_config:
        content = element.find_next(tag_config["sub_tag"]).get_text(strip=True)
    else:
        content = element.get_text(strip=True)
    return content


# Function to scrape headlines from a single news source
def scrape_source(source, config):
    url = config["url"]
    html_content = fetch_html(url)
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    headlines = []
    fetched_date = datetime.now().isoformat()  # Get the current date and time in ISO format

    elements = soup.find_all(config["headline"]["tag"], attrs=config["headline"]["attrs"])

    for item in elements:
        title = parse_content(item, config["headline"])
        if title:
            next_element = item.find_next()

            # Ensure that the next description comes before another title
            while next_element:
                if next_element.name == config["headline"]["tag"] and (next_element.get(attr) == value for attr, value in config["headline"]["attrs"]):
                    # Another title appeared before a description, skip this title
                    break
                description_matched = False
                if isinstance(config["description"]["tag"], list):
                    description_matched = next_element.name in config["description"]["tag"] and (next_element.get(attr) == value for attr, value in config["headline"]["attrs"])
                else:
                    description_matched = next_element.name == config["description"]["tag"] and (next_element.get(attr) == value for attr, value in config["headline"]["attrs"])
                
                if description_matched:
                    # Valid title-description pair found
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
    try:
        with open(output_path, 'w') as f:
            json.dump(headlines, f, indent=4)            
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