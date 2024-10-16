from flask import Flask, request, jsonify
import json
import os
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
from torch.utils.data import DataLoader, Dataset
from concurrent.futures import ThreadPoolExecutor
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# Load model and tokenizer
roberta = "cardiffnlp/twitter-roberta-base-sentiment"
model = AutoModelForSequenceClassification.from_pretrained(roberta)
tokenizer = AutoTokenizer.from_pretrained(roberta)
labels = ['Negativo', 'Neutro', 'Positivo']

# Check for GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


# Initialize VADER sentiment analyzer
vader_analyzer = SentimentIntensityAnalyzer()

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
 
    if 'data' not in data:
        return jsonify({'error': 'Missing "data" key in request body'}), 400

    # Load data from request
    tweets = np.array([item.get("title", "") for item in data['data']])
    tweet_ids = np.array([item.get("id") for item in data['data']])
    
    # Prepare DataLoader
    dataset = TweetDataset(tweets, tweet_ids)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

    def analyze_batch(batch):
        batch_tweets, batch_ids = batch
        encoded_tweets = tokenizer(batch_tweets, return_tensors='pt', padding=True, truncation=True).to(device)
        with torch.no_grad():
            outputs = model(**encoded_tweets)

        batch_results = []
        for j, tweet_id in enumerate(batch_ids):
            scores = outputs.logits[j].cpu().detach().numpy()
            scores = softmax(scores)
            scores = [float(score) for score in scores]

            item = next(item for item in data["data"] if item.get("id") == tweet_id)
            result = {
                "id": tweet_id,
                "thumbnail": item.get("thumbnail", ""),
                "selftext": item.get("selftext", ""),
                "title": item["title"],
                "permalink": item.get("permalink", ""),
                "scores": {label: scores[k] for k, label in enumerate(labels)}
            }

            batch_results.append(result)
        
        return batch_results

    # Analyze data in parallel
    analyzed_data = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(analyze_batch, batch) for batch in dataloader]
        for future in futures:
            analyzed_data.extend(future.result())

    return jsonify(analyzed_data)

@app.route('/analyze/vader', methods=['POST'])
def analyzeVader():
    data = request.json

    if 'data' not in data:
        return jsonify({'error': 'Missing "data" key in request body'}), 400

    # Load data from request
    tweets = [item.get("title", "") for item in data['data']]
    tweet_ids = [item.get("id") for item in data['data']]

    analyzed_data = []
    # Process each item in the JSON dataset
    for item in data["data"]:
        tweet_id = item["id"]
        tweet = item["title"]
        # Pre-process tweet
        tweet_words = []
        for word in tweet.split(' '):
            if word.startswith('@') and len(word) > 1:
                word = '@user'
            elif word.startswith('http'):
                word = "http"
            tweet_words.append(word)
        tweet_proc = " ".join(tweet_words)

        # Analyze sentiment using VADER
        vs = vader_analyzer.polarity_scores(tweet_proc)
        scores = {
            'Negativo': vs['neg'],
            'Neutro': vs['neu'],
            'Positivo': vs['pos']
        }

         # Collect results
        result = {
            "id": tweet_id,
            "thumbnail": item.get("thumbnail", ""),
            "selftext": item.get("selftext", ""),
            "title": item["title"],
            "permalink": item.get("permalink", ""),
            "scores": scores
        }

        analyzed_data.append(result)

    return jsonify(analyzed_data)

# Define a Dataset class
class TweetDataset(Dataset):
    def __init__(self, tweets, tweet_ids):
        self.tweets = tweets
        self.tweet_ids = tweet_ids

    def __len__(self):
        return len(self.tweets)

    def __getitem__(self, idx):
        return self.tweets[idx], self.tweet_ids[idx]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)