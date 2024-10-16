"""
Author: José Parreira & Nuno Frazão
Module: 1
"""

import warnings
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import json
import os
import torch
from torch.utils.data import DataLoader, Dataset
from concurrent.futures import ThreadPoolExecutor

# Suppress specific warnings that are irrelevant or deprecated.
# This helps in keeping the console output clean and focused on important messages.
warnings.filterwarnings('ignore', message='`resume_download` is deprecated')
warnings.filterwarnings('ignore', message='`huggingface_hub` cache-system uses symlinks')

# Set environment variable to disable symlink warnings from Huggingface.
# This prevents repetitive and unnecessary warnings during model loading.
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

# Verify that the key 'data' exists in the parsed JSON dictionary.
# This check ensures that the expected data structure is present before proceeding.
if 'data' not in data:
    print(f"Key 'data' not found in loaded JSON data")
    exit(1)

# Load the pre-trained sentiment analysis model and tokenizer from Huggingface.
# The model is specifically trained for Twitter data, making it suitable for tweet analysis.
roberta = "cardiffnlp/twitter-roberta-base-sentiment"
model = AutoModelForSequenceClassification.from_pretrained(roberta)
tokenizer = AutoTokenizer.from_pretrained(roberta)

# Define sentiment labels corresponding to the model's output classes.
# These labels are used later to map predicted scores to human-readable sentiments.
labels = ['Negativo', 'Neutro', 'Positivo']

# Determine if a GPU is available and move the model to the appropriate device.
# Utilizing GPU acceleration can significantly speed up the inference process.
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

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

# Prepare lists to hold tweets and their corresponding IDs for processing.
# This setup facilitates batch processing and efficient management of data.
analyzed_data = []
tweets = []
tweet_ids = []

# Iterate through each item in the data and prepare it for analysis.
# Checks for cached results and preprocesses tweets by sanitizing mentions and URLs.
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
    # This standardization helps the model focus on the core content of the tweet.
    tweet_words = []
    for word in tweet.split(' '):
        if word.startswith('@') and len(word) > 1:
            word = '@user'
        elif word.startswith('http'):
            word = "http"
        tweet_words.append(word)
    tweet_proc = " ".join(tweet_words)

    # Append the processed tweet and its ID to their respective lists for batching.
    tweets.append(tweet_proc)
    tweet_ids.append(tweet_id)

# Define a custom Dataset class to facilitate efficient data loading and batching.
# This structure is compatible with PyTorch's DataLoader for streamlined processing.
class TweetDataset(Dataset):
    def __init__(self, tweets, tweet_ids):
        self.tweets = tweets
        self.tweet_ids = tweet_ids

    def __len__(self):
        return len(self.tweets)

    def __getitem__(self, idx):
        return self.tweets[idx], self.tweet_ids[idx]

# Create a DataLoader instance to manage batch processing of the tweet data.
# Batching improves processing speed and resource utilization during inference.
dataset = TweetDataset(tweets, tweet_ids)
dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

# Define a function to analyze a single batch of tweets.
# Processes the batch through the model and formats the output with relevant information.
def analyze_batch(batch):
    batch_tweets, batch_ids = batch

    # Tokenize the batch of tweets and move them to the appropriate device.
    # The tokenizer converts text into input IDs and attention masks suitable for the model.
    encoded_tweets = tokenizer(batch_tweets, return_tensors='pt', padding=True, truncation=True).to(device)
    with torch.no_grad():
        outputs = model(**encoded_tweets)

    batch_results = []

    # Iterate through each tweet in the batch and compute sentiment scores.
    # Applies softmax to logits to obtain probability distributions over sentiment classes.
    for j, tweet_id in enumerate(batch_ids):
        scores = outputs.logits[j].cpu().detach().numpy()
        scores = softmax(scores)
        scores = [float(score) for score in scores]

        # Retrieve original tweet information and construct a result dictionary.
        # Includes tweet metadata and computed sentiment scores for comprehensive output.
        item = next(item for item in data["data"] if item["id"] == tweet_id)
        result = {
            "id": tweet_id,
            "thumbnail": item.get("thumbnail", ""),
            "selftext": item.get("selftext", ""),
            "title": item["title"],
            "permalink": item.get("permalink", ""),
            "scores": {label: scores[k] for k, label in enumerate(labels)}
        }

        # Update the cache with the new result and append it to batch results.
        analyzed_cache[tweet_id] = result
        batch_results.append(result)

    return batch_results

# Utilize ThreadPoolExecutor to process multiple batches in parallel.
# Parallel processing significantly reduces total computation time for large datasets.
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(analyze_batch, batch) for batch in dataloader]

    # Collect results from all futures and extend the analyzed data list.
    for future in futures:
        analyzed_data.extend(future.result())

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
