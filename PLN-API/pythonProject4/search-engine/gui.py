from tkinter import dialog

import customtkinter

from api_requests.reddit import RedditAPI
from process_dm.get_data import RedditData
from components.table import TableFrame

from sklearn.utils import Bunch

#https://customtkinter.tomschimansky.com/documentation/widgets

class Window(customtkinter.CTk):

    def __init__(self):

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")

        customtkinter.CTk.__init__(self)

        self.geometry("1280x720")
        self.title('Search System for Sentiment Analysis')

        # VARIABLES
        self.reddits = []
        self.comments = []
        self.query = None
        self.after_value = None

        # COMPONENTS
        frame = customtkinter.CTkFrame(master=self)
        frame.pack(pady=20, padx=60, fill="both", expand=True)

        label = customtkinter.CTkLabel(master=frame, text="Loading Posts", font=("Roboto", 24))
        label.pack(pady=12, padx=10)

        self.table_frame = TableFrame(master=frame)

        menu_buttons = customtkinter.CTkFrame(master=frame)
        menu_buttons.pack(side="left", fill="y")

        btn_search_posts = customtkinter.CTkButton(master=menu_buttons, text="Search posts", command=self.search_reddit_input)
        btn_search_posts.pack(pady=12, padx=10, side="top", anchor="w", fill="x")

        btn_search_comments = customtkinter.CTkButton(master=menu_buttons, text="Search comments with id post",
                                         command=self.search_comments_input)
        btn_search_comments.pack(pady=12, padx=10, side="top", anchor="w", fill="x")

        next_button = customtkinter.CTkButton(master=frame, text="Next Page", command=self.search_reddit_page)
        next_button.pack(pady=14, padx=10, side="top", anchor="w")

        prev_button = customtkinter.CTkButton(master=frame, text="Prev Page", command="")
        prev_button.pack(pady=14, padx=10, side="top", anchor="w")

    def search_reddit_input(self):
        # INPUT DIALOG
        dialog = customtkinter.CTkInputDialog(text="Type in a search:", title="Search posts")
        self.query = dialog.get_input()
        if self.query:
            self.search_reddit(self.query)

    def search_reddit_page(self):
        self.search_reddit(self.query, self.after_value)

    def search_reddit(self, query, after=None):
        reddit_api = RedditAPI()
        response, self.after_value = reddit_api.global_search(query, self.after_value)
        if response:
            titles = []
            selftexts = []
            ids = []
            for reddit in response['data']['children']:
                titles.append(reddit['data']['title'])
                selftexts.append(reddit['data']['selftext'])
                ids.append(reddit['data']['id'])
            self.reddits = Bunch(titles=titles, selftexts=selftexts, ids=ids)

            if self.reddits:
                self.table_frame.pack(side="left", fill="both", expand="true")
                posts_read = self.table_frame.data_frame.setRedditData(self.reddits)
                self.table_frame.update_size(posts_read)
        else:
            print("ERRO")
        query = dialog.get_input()
        if query:
            service = RedditData()
            result = service.search_reddit(query)
            if result:
                self.reddits = Bunch(**result)
                if self.reddits:
                    self.table_frame.pack(side="left", fill="both", expand="true")
                    posts_read = self.table_frame.data_frame.setRedditData(self.reddits)
                    self.table_frame.update_size(posts_read)

    def search_comments_input(self):
        # INPUT DIALOG
        dialog = customtkinter.CTkInputDialog(text="Type id post in a search:", title="Search comments")
        query = dialog.get_input()
        if query:
            service = RedditData()
            result = service.search_comments(query)
            if result:
                self.comments = Bunch(**result)





