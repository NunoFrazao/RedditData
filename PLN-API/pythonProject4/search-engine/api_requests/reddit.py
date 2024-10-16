import argparse
import requests
import json

class RedditAPI:
    def __init__(self):
        self.base_url = 'https://www.reddit.com'
        self.headers = {
            'User-Agent': 'Your bot 0.1'
        }

    def global_search(self, query, after=None, sort='relevance', limit=100):
        url = f'{self.base_url}/search.json'
        params = {
            'q': query,
            'sort': sort,
            'limit': limit,
            'after': after
        }
        response = requests.get(url, params=params, headers=self.headers)
        response_json = response.json()
        after_value = response_json["data"]["after"]

        if response.status_code == 200:
            return response.status_code, response.json(), after_value
        else:
            return response.status_code, None, None

    def get_comments(self, post_id):
        review_url = f"{self.base_url}/comments/{post_id}.json"
        response = requests.get(review_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro no post ID: {post_id}")

def fetch_reddit_data(search_term, quantity, order):
    reddit_api = RedditAPI()
    status_code, data, after_value = reddit_api.global_search(query=search_term, sort=order, limit=quantity)
    
    if status_code == 200:
        return data
    else:
        print(f"Error fetching data from Reddit. Status code: {status_code}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch data from Reddit.')
    parser.add_argument('--searchTerm', required=True, help='Search term for Reddit')
    parser.add_argument('--quantity', required=True, type=int, help='Number of posts to fetch')
    parser.add_argument('--order', required=True, help='Order of posts')

    args = parser.parse_args()
    
    data = fetch_reddit_data(args.searchTerm, args.quantity, args.order)
    
    # Save data to file
    if data:
        with open('data.txt', 'w') as f:
            json.dump(data, f)
