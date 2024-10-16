import tkinter as tk
import requests


class Window(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Steam API")
        self.geometry("500x500")

        self.label = tk.Label(self, text="Steam API", font=('Arial', 18))
        self.label.grid(row=0, column=0, padx=20, pady=20)

        self.label_max_lenght = tk.Label(self, text="Max lenght for review")
        self.label_max_lenght.grid(row=1, column=0, sticky="w")

        self.max_lenght = tk.Text(self, wrap="word", height=1, width=30)
        self.max_lenght.grid(row=1, column=1, pady=20)

        self.label_num_per_page = tk.Label(self, text="Number of reviews:")
        self.label_num_per_page.grid(row=2, column=0, sticky="w")

        self.num_per_page = tk.Text(self, wrap="word", height=1, width=30)
        self.num_per_page.grid(row=2, column=1, pady=20)

        self.btn_search = tk.Button(self, text="Search Helldivers 2 Steam reviews", command=self.request_reviews)
        self.btn_search.grid(row=3, column=1)

        self.text_box = tk.Text(self, wrap="word", height=20, width=50)
        self.text_box.grid(row=4, column=1)

    def request_reviews(self):
        url = 'https://store.steampowered.com/appreviews/553850?json=1'
        params = {"num_per_page": self.num_per_page.get("1.0", tk.END)}
        response = requests.get(url, params)

        if response.status_code == 200:
            json_response = response.json()

            reviews = json_response.get("reviews", [])
            print(f"Number of reviews: {len(reviews)}")

            for review in reviews:
                review_text = review.get("review")
                if review_text and len(review_text) < int(self.max_lenght.get("1.0", tk.END)):
                    self.text_box.insert(tk.END, f"{review_text} \n\n")
