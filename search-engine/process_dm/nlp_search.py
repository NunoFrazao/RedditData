import os
from operator import itemgetter

import gensim
import spacy as spacy
from gensim import corpora
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from elastic_search.elastichsearch import getAll

from elastic_search.elastichsearch import getInBunch
from exceptions.exceptions import EmptyValueException
from process_dm.data_preparation import DataPreparation

from config import Config

from process_dm.get_data import RedditData
class NLPSearchProcessor:
    def __init__(self, query, elasticSearch=0, limit=100, sort="relevance", pages=1):
        if not query:
            raise EmptyValueException("The 'query' is empty")
        self.query = query
        self.elasticSearch = elasticSearch
        self.limit = limit
        self.sort = sort
        self.pages = pages
        self.count_requests = 0

    def search(self, query):
        if not self.elasticSearch or self.elasticSearch == 0:
            reddit_data = RedditData()
            data, count_requests = reddit_data.search_reddit(query, limit=self.limit, sort=self.sort, pages=self.pages)
            self.count_requests = count_requests
            return data
        return getInBunch(query, self.elasticSearch)

    def process(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

class QuestionProcessor(NLPSearchProcessor):
    def process(self, num_topics=5):

        if Config.DEBUG_MODE:
            print("QUESTION", self.query)

        # Chat gpt
        vectorizer = CountVectorizer(stop_words=stopwords.words('english'), max_features=10000)
        X = vectorizer.fit_transform([self.query])
        keywords = vectorizer.get_feature_names_out()
        topics = keywords[:num_topics]
        search_query = " ".join(topics)

        if Config.DEBUG_MODE:
            print("Search Query: ", search_query)

        data = self.search(search_query)

        return data, self.count_requests

class SemanticSearch(NLPSearchProcessor):
    def process(self, num_best=5):

        data = getAll()

        nlp = spacy.load("en_core_web_sm")
        def spacy_tokenizer(text):
            prepare = DataPreparation()
            document = prepare.prepareOne(doc=text)
            doc = nlp(document)
            return [token.text for token in doc]

        reddits = []
        for doc in data['hits']['hits']:
            doc_id = doc['_id']
            source = doc['_source']
            selftext = source.get("selftext", "")
            tokenized_text = spacy_tokenizer(selftext)
            reddits.append({
                "id": source.get("id"),
                "title": source.get("title"),
                "selftext": selftext,
                "selftext_tokenized": tokenized_text,
                "thumbnail": source.get("thumbnail"),
                "permalink": source.get("permalink")
            })

        tokens = [content['selftext_tokenized'] for content in reddits]
        dictionary = corpora.Dictionary(tokens)

        corpus = [dictionary.doc2bow(desc) for desc in tokens]
        word_frequencies = [[(dictionary[id], frequency) for id, frequency in line] for line in corpus[0:3]]
        print("WORD FREQUENCIES", word_frequencies)

        # LOAD MODELS
        tfidf_model = gensim.models.TfidfModel(corpus, id2word=dictionary)
        tfidf_corpus = tfidf_model[corpus]
        lsi_model = gensim.models.LsiModel(tfidf_corpus, id2word=dictionary, num_topics=100)

        # Load the MatrixSimilarity
        from gensim.similarities import MatrixSimilarity
        reddit_index = MatrixSimilarity(tfidf_corpus, num_features=len(dictionary))

        # SEARCH SEMANTIC
        search_term = self.query
        query_bow = dictionary.doc2bow(spacy_tokenizer(search_term))
        query_tfidf = tfidf_model[query_bow]
        query_lsi = lsi_model[query_tfidf]

        reddit_index.num_best = num_best
        reddit_list = reddit_index[query_lsi]

        reddit_list.sort(key=itemgetter(1), reverse=True)
        print(reddit_list)
        reddits_clean = []
        for j, reddit in enumerate(reddit_list):
            reddits_clean.append(
                {
                    'relevance': round((reddit[1] * 100), 2),
                    'id': reddits[reddit[0]]['id'],
                    'title': reddits[reddit[0]]['title'],
                    'selftext': reddits[reddit[0]]['selftext'],
                    'thumbnail': reddits[reddit[0]]['thumbnail'],
                    'permalink': reddits[reddit[0]]['permalink'],
                }
            )
            if j == (reddit_index.num_best - 1):
                break

        return reddits_clean, self.count_requests