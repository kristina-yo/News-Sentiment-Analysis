import os
import json
import pandas as pd
from datetime import datetime
from app.config.settings import OUTPUT_DIR_RAW, OUTPUT_DIR_PROCESSED
from app.config.logger import logger

TIMESTAMP_FILE = os.path.join(OUTPUT_DIR_RAW, 'scraping_timestamp.txt')
PROCESSED_FILES_LOG = os.path.join(OUTPUT_DIR_PROCESSED, 'processed_files.log')

def is_scraping_completed():
    if not os.path.exists(TIMESTAMP_FILE):
        return False
    with open(TIMESTAMP_FILE, 'r') as f:
        timestamp = f.read().strip()
    scraping_time = datetime.fromisoformat(timestamp)
    now = datetime.now()
    return (now - scraping_time).total_seconds() < 24 * 3600

def load_processed_files(log_path):
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            return set(f.read().splitlines())
    return set()

def update_processed_files(log_path, file_path):
    # Store relative path instead of absolute path
    relative_path = os.path.relpath(file_path, OUTPUT_DIR_RAW)
    with open(log_path, 'a') as f:
        f.write(os.path.dirname(relative_path) + '\n')

def process_file(input_path, output_path):
    with open(input_path, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=['title', 'description'])
    logger.info('Transformation completed')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

def process_directory(raw_dir, processed_dir, processed_files):
    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            if file.endswith(".json"):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(input_path, raw_dir)
                if relative_path in processed_files:
                    continue
                new_path = os.path.dirname(relative_path)
                output_path = os.path.join(processed_dir, new_path, 'transformed_data.csv')
                process_file(input_path, output_path)
                update_processed_files(PROCESSED_FILES_LOG, input_path)

def process_headlines_data():
    if not is_scraping_completed():
        logger.info("Scraping not completed yet. Exiting data processing.")
        exit(1)

    processed_files = load_processed_files(PROCESSED_FILES_LOG)
    process_directory(OUTPUT_DIR_RAW, OUTPUT_DIR_PROCESSED, processed_files)
