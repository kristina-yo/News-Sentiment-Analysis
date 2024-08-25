# import libraries
import pandas as pd
import os
from app.config.settings import OUTPUT_DIR_PROCESSED, OUTPUT_DIR_ANALYZED
import nltk

nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


# initialize NLTK sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    compound = sentiment_score['compound']
    if compound >= 0.25:
        return compound, 'Positive'
    elif compound <= -0.25:
        return compound, 'Negative'
    else:
        return compound, 'Neutral'


# create preprocess_text function
def preprocess_text(text):

    # Tokenize the text
    tokens = word_tokenize(text.lower())

    # Remove stop words
    filtered_tokens = [token for token in tokens if token not in stopwords.words('english')]

    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    # Join the tokens back into a string
    processed_text = ' '.join(lemmatized_tokens)

    return processed_text


# Load the amazon review dataset
def process_sentiment_analysis(input_csv, output_csv):
    # Load data
    df = pd.read_csv(input_csv)
    df['Combined Text'] = df['Title'] + ". " + df['Description']
    df['Combined Text'] = df['Combined Text'].apply(preprocess_text)

    # Apply sentiment analysis
    df['Sentiment'], df['Score'] = zip(*df['Combined Text'].apply(analyze_sentiment))
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Save the results
    df.to_csv(output_csv, index=False)
    print(f"Sentiment analysis results saved to {output_csv}")


def process_directory(processed_dir, analyzed_dir):
    for root, dirs, files in os.walk(processed_dir):
        for file in files:
            if file.endswith(".csv"):
                input_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, processed_dir)
                output_path = os.path.join(analyzed_dir, relative_path, 'headlines_with_sentiment.csv')
                process_sentiment_analysis(input_path, output_path)


def analyze_data():
    processed_dir = OUTPUT_DIR_PROCESSED
    analyzed_dir = OUTPUT_DIR_ANALYZED
    process_directory(processed_dir, analyzed_dir)