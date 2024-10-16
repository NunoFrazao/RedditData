import os
from api_requests.reddit import RedditAPI
from sklearn.utils import Bunch
from exceptions.exceptions import IllegalValueException, EmptyValueException, NotDataFoundException, \
    RequestRedditException

import cProfile
import pstats

from config import ROOT_DIR


# DATA PREPARATION
# selecionamos os dados que queremos
# e metemos numa biblioteca Bunch
class RedditData:
    def __init__(self):
        pass

    def search_reddit(self, query, pages=1, sort='relevance', limit=100):
        profiler = cProfile.Profile()
        profiler.enable()

        if not pages:
            pages = 1
        if not query:
            profiler.disable()
            raise EmptyValueException(f"The 'query' is empty")
        if pages < 1:
            profiler.disable()
            raise IllegalValueException(f"Invalid value '{pages}' for 'pages'")

        reddit_api = RedditAPI()
        list_of_responses = []
        titles = []
        selftexts = []
        ids = []
        thumbnails = []
        permalinks = []
        after = None
        for i in range(pages):
            status_code, temp_response, after = reddit_api.global_search(query,after,sort,limit)
            if status_code != 200:
                raise RequestRedditException("Reddit request exception")
            list_of_responses.append(temp_response)
            if not after: #qd isto devolve None é pq ja não ha mais reddits
                break

        if not list_of_responses:
            profiler.disable()
            raise NotDataFoundException("Reddit response is empty")

        for response in list_of_responses:
            for reddit in response['data']['children']:
                titles.append(reddit['data']['title'])
                selftexts.append(reddit['data']['selftext'])
                ids.append(reddit['data']['id'])
                thumbnails.append(reddit['data']['thumbnail'])
                permalinks.append(reddit['data']['permalink'])

        print("Number of ids: ",len(ids))
        profiler.disable()
        #print("Profiler search_reddit()")
        #profiler.print_stats(sort='tottime')
        profile_dir = os.path.join(ROOT_DIR, 'profiles')
        os.makedirs(profile_dir, exist_ok=True)
        profiler_output_path = os.path.join(profile_dir, 'search_reddit.prof')
        profiler.dump_stats(profiler_output_path)

        return Bunch(titles=titles, selftexts=selftexts, ids=ids, thumbnails = thumbnails, permalinks = permalinks)

    def search_comments(self, id):

        if not id:
            raise EmptyValueException(f"The 'id' is empty")


        reddit_api = RedditAPI()
        response = reddit_api.get_comments(id)

        if not response:
            raise NotDataFoundException(f"No data found from id '{id}'")

        print("RESPONSE", response[1]['data']['children'])
        ids = []
        text = []
        replies = []
        for comment in response[1]['data']['children']:
            if 'body' in comment['data']:
                ids.append(comment['data']['id'])
                text.append(comment['data']['body'])

                if 'replies' in comment['data'] and 'data' in comment['data']['replies']:
                    reply_ids = []
                    reply_text = []
                    for reply in comment['data']['replies']['data']['children']:
                        if 'body' in reply['data']:
                            reply_ids.append(reply['data']['id'])
                            reply_text.append(reply['data']['body'])
                    replies.append(Bunch(ids=reply_ids, text=reply_text))

        return Bunch(ids=ids, text=text, replies=replies)


    #https://gist.github.com/LowriWilliams/797b4266fcb1acca19aac600a9de1f31#file-lda-ipynb
