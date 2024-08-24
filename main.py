from app.scripts.scrape_headlines import scrape_headlines
from app.scripts.process_headlines import process_headlines_data
from app.scripts.sentiment_analysis import analyze_data


if __name__ == "__main__":
    scrape_headlines()
    process_headlines_data()
    analyze_data()