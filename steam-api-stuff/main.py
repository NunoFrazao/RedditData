from gui import Window
import requests
import json
import pprint

if __name__ == '__main__':
    gui = Window()
    gui.mainloop()

    # GET store.steampowered.com/appreviews/<appid>?json=1
    # url = 'https://store.steampowered.com/appreviews/553850?json=1'
    # params = {"num_per_page":"100"}
    # response = requests.get(url, params)

    # if response.status_code == 200:
    #     json_response = response.json()

    #     reviews = json_response.get("reviews", [])
    #     print(f"Number of reviews: {len(reviews)}")

    #     for review in reviews:
    #         review = review.get("review")
    #         if review and len(review) < 100:
    #             print(review + "\n")
