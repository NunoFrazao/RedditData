import requests

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
