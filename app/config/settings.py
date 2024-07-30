# config/settings.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEWS_SOURCES = {
    "BBC Business": {
        "url": "https://www.bbc.com/business",
        "headline": {
            "tag": "h2",
            "class": "sc-4fedabc7-3 zTZri"
        },
        "description": {
            "tag": "p",
            "class": "sc-b8778340-4 kYtujW"
        }
    },
    "BBC Earth": { 
        "url": "https://www.bbc.com/future-planet",
        "headline": {
            "tag": "h2",
            "class": "sc-4fedabc7-3"
        },
        "description": {
            "tag": "p",
            "class": "sc-ae29827d-0"
        }
     },
    "Hollywood Reporter": {
        "url": "https://www.hollywoodreporter.com/c/news/",
        "headline": {
            "tag": "a",
            "class": "c-title__link lrv-a-unstyle-link u-color-brand-primary:hover"
        },
        "description": {
            "tag": "p",
            "class": "c-dek a-font-accent-s lrv-u-margin-a-00 a-truncate-4"
        }
    },
    "TechCrunch": {
        "url": "https://techcrunch.com/",
        "headline": {
            "tag": "h2",
            "class": "wp-elements-565fa7bab0152bfdca0217543865c205",
            "sub_tag": "a"
        },
        "description": {
            "tag": "p",
            "class": "wp-block-post-excerpt__excerpt"
        }
    },
    "News AU": {
        "url": "https://www.news.com.au/sport",
         "headline": {
            "tag": "a",
            "class": "storyblock_title_link",
            "data-tgev-label": "story"
        },
        "description": {
            "tag": "p",
            "class": "storyblock_standfirst"
        }
    }
}

OUTPUT_DIR_RAW = os.path.join(BASE_DIR, 'data', 'raw')
OUTPUT_DIR_PROCESSED = os.path.join(BASE_DIR, 'data', 'processed')
DATABASE_PATH = os.path.join(OUTPUT_DIR_PROCESSED, 'news_sentiment.db')
