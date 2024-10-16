"""
Author: José Parreira & Nuno Frazão
Module: 1
"""

import warnings
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
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
file_path = 'comments_data.txt'
analyzed_data_path = 'analyzed_comments_data.txt'
cache_file_path = 'analyzed_comments_cache.txt'

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

# Load a pre-trained sentiment analysis model and tokenizer from Huggingface.
# The model is specifically trained for Twitter data, making it suitable for analyzing social media comments.
roberta = "cardiffnlp/twitter-roberta-base-sentiment"
model = AutoModelForSequenceClassification.from_pretrained(roberta)
tokenizer = AutoTokenizer.from_pretrained(roberta)

# Define sentiment labels corresponding to the model's output classes.
# These labels are used later to map predicted scores to human-readable sentiments.
labels = ['Negativo', 'Neutro', 'Positivo']

# Initialize an empty dictionary to store previously analyzed data from cache.
# Loading cached results helps in avoiding redundant computations for already processed comments.
analyzed_cache = {}
if os.path.exists(cache_file_path):
    print(f"Loading analyzed data from {cache_file_path}")
    try:
        with open(cache_file_path, 'r') as file:
            analyzed_cache = {comment["id"]: comment for comment in json.load(file)}
    except Exception as e:
        print(f"Error reading analyzed data file: {e}")

# Prepare a list to hold the results of the analyzed comments.
# This will be populated with new analyses or retrieved from the cache.
analyzed_comments = []

# Iterate through each comment in the JSON data and process it for sentiment analysis.
# Cached results are used if available, and new results are computed if not.
for comment in data:
    comment_id = comment["id"]
    comment_text = comment["body"]

    # Use cached result if available to save computation time.
    if comment_id in analyzed_cache:
        print(f"Using cached result for Comment ID {comment_id}")
        analyzed_comments.append(analyzed_cache[comment_id])
        continue

    print(f"Processing Comment ID {comment_id}:")

    # Preprocess the comment text by replacing user mentions and URLs with placeholders.
    # This standardization helps the sentiment analyzer focus on the core content of the comment.
    comment_words = []
    for word in comment_text.split(' '):
        if word.startswith('@') and len(word) > 1:
            word = '@user'
        elif word.startswith('http'):
            word = "http"
        comment_words.append(word)
    comment_proc = " ".join(comment_words)

    # Encode the processed comment and analyze its sentiment using the model.
    # The tokenizer converts text into input IDs and attention masks suitable for the model.
    encoded_comment = tokenizer(comment_proc, return_tensors='pt')
    output = model(**encoded_comment)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)  # Convert logits to probabilities using softmax.

    # Convert float32 to float for better compatibility in JSON serialization.
    scores = [float(score) for score in scores]

    # Collect the analysis results into a dictionary.
    # The result includes the original comment text and the sentiment scores.
    comment_result = {
        "id": comment_id,
        "body": comment["body"],
        "scores": {label: scores[i] for i, label in enumerate(labels)}
    }

    # Store the result in the cache for future use and append it to the analyzed data list.
    # Caching allows the script to skip reprocessing the same comment in future runs.
    analyzed_cache[comment_id] = comment_result
    analyzed_comments.append(comment_result)

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
        file.write(json.dumps(analyzed_comments, indent=4))
    print("Analysis complete. Analyzed comments data saved.")
except Exception as e:
    print(f"Error saving analyzed comments data: {e}")
    exit(1)
