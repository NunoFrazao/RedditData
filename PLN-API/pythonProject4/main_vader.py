"""
Author: José Parreira & Nuno Frazão
Module: 1
"""

import warnings
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import os

# Suppress specific warnings that are irrelevant or deprecated.
# This helps keep the console output clean and focused on important messages.
warnings.filterwarnings('ignore', message='`resume_download` is deprecated')
warnings.filterwarnings('ignore', message='`huggingface_hub` cache-system uses symlinks')

# Set environment variable to disable symlink warnings from Huggingface.
# This prevents repetitive and unnecessary warnings during execution.
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Define file paths for input data, analyzed output, and cache.
# These paths are used throughout the script for reading and writing data.
file_path = 'data.txt'
analyzed_data_path = 'analyzed_data.txt'
cache_file_path = 'analyzed_data_cache.txt'

# Attempt to load raw JSON data from the specified file path.
# Proper error handling ensures the script exits gracefully if the file is unreadable.
print(f"Loading data from {file_path}")
try:
    with open(file_path, 'r') as file:
        json_data = file.read()
except Exception as e:
    print(f"Error reading data file: {e}")
    exit(1)

# Parse the JSON data into a Python dictionary for processing.
# Exits the script with an error message if the JSON is improperly formatted.
try:
    data = json.loads(json_data)
except json.JSONDecodeError as e:
    print(f"Error parsing JSON data: {e}")
    exit(1)

# Initialize the VADER sentiment analyzer.
# VADER is a lexicon and rule-based sentiment analysis tool specifically attuned to sentiments expressed in social media.
analyzer = SentimentIntensityAnalyzer()

# Initialize an empty dictionary to store previously analyzed data from cache.
# Loading cached results helps in avoiding redundant computations for already processed tweets.
analyzed_cache = {}
if os.path.exists(cache_file_path):
    print(f"Loading analyzed data from {cache_file_path}")
    try:
        with open(cache_file_path, 'r') as file:
            analyzed_cache = {item["id"]: item for item in json.load(file)}
    except Exception as e:
        print(f"Error reading analyzed data file: {e}")

# Prepare a list to hold the results of the analyzed data.
# This will be populated with new analyses or retrieved from the cache.
analyzed_data = []

# Iterate through each item in the JSON data and process it for sentiment analysis.
# Cached results are used if available, and new results are computed if not.
for item in data["data"]:
    tweet_id = item["id"]
    tweet = item["title"]

    # Use cached result if available to save computation time.
    if tweet_id in analyzed_cache:
        print(f"Using cached result for Tweet ID {tweet_id}")
        analyzed_data.append(analyzed_cache[tweet_id])
        continue

    print(f"Processing Tweet ID {tweet_id}:")

    # Preprocess the tweet text by replacing user mentions and URLs with placeholders.
    # This standardization helps the sentiment analyzer focus on the core content of the tweet.
    tweet_words = []
    for word in tweet.split(' '):
        if word.startswith('@') and len(word) > 1:
            word = '@user'
        elif word.startswith('http'):
            word = "http"
        tweet_words.append(word)
    tweet_proc = " ".join(tweet_words)

    # Analyze the sentiment of the processed tweet using VADER.
    # VADER provides a compound score and scores for positive, neutral, and negative sentiments.
    vs = analyzer.polarity_scores(tweet_proc)

    # Convert VADER sentiment scores into labeled categories.
    # This mapping makes the results more interpretable by associating scores with sentiments.
    scores = {
        'Negativo': vs['neg'],
        'Neutro': vs['neu'],
        'Positivo': vs['pos']
    }

    # Collect the analysis results into a dictionary.
    # The result includes metadata from the original tweet and the sentiment scores.
    result = {
        "id": tweet_id,
        "thumbnail": item.get("thumbnail", ""),
        "selftext": item.get("selftext", ""),
        "title": item["title"],
        "permalink": item.get("permalink", ""),
        "scores": scores
    }

    # Store the result in the cache for future use and append it to the analyzed data list.
    # Caching allows the script to skip reprocessing the same tweet in future runs.
    analyzed_cache[tweet_id] = result
    analyzed_data.append(result)

# Save the updated analyzed data to the cache file for future reuse.
# Storing results in a cache avoids redundant processing in subsequent runs.
print(f"Saving cache data to {cache_file_path}")
try:
    with open(cache_file_path, 'w') as file:
        file.write(json.dumps(list(analyzed_cache.values()), indent=4))
    print("Cache data saved.")
except Exception as e:
    print(f"Error saving cache data: {e}")

# Save the current session's analyzed data to the designated output file.
# This output can be used for reporting, visualization, or further analysis.
print(f"Saving analyzed data to {analyzed_data_path}")
try:
    with open(analyzed_data_path, 'w') as file:
        file.write(json.dumps(analyzed_data, indent=4))
    print("Analysis complete. Analyzed data saved.")
except Exception as e:
    print(f"Error saving analyzed data: {e}")
    exit(1)
