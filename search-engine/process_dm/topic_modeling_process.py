from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Doc2Vec
from sklearn.cluster import KMeans
import numpy as np
from top2vec import Top2Vec
from gensim.models.doc2vec import TaggedDocument
from bertopic import BERTopic
from exceptions.exceptions import EmptyValueException
from process_dm.data_preparation import DataPreparation

class TopicModelProcessor:
    def __init__(self, data, topic, context=0):
        if not topic:
            raise EmptyValueException("The 'topic' is empty")
        if not data:
            raise EmptyValueException("The 'data' is empty")
        self.data = data
        self.topic = topic
        self.prepared_documents = self.prepare_documents(context)

    def choose_documents(self, context):
        if context:
            if context == 1:
                return self.data.get("titles", [])
        return self.data.get("selftexts", [])
    def prepare_documents(self, context):
        documents = self.choose_documents(context)
        prepare = DataPreparation()
        prepared_documents = prepare.prepareAll(documents=documents)
        non_empty_docs_indices = [i for i, doc in enumerate(prepared_documents) if doc.strip()]
        prepared_documents = [doc for doc in prepared_documents if doc.strip()]
        for key in self.data.keys():
            self.data[key] = [self.data[key][i] for i in non_empty_docs_indices]
        return prepared_documents

    def sort_data_by_indices(self, sorted_indices):
        for key in self.data.keys():
            self.data[key] = [self.data[key][i] for i in sorted_indices]
        return self.data

    def process(self):
        raise NotImplementedError("This method should be implemented by subclasses")

class ProcessNMF(TopicModelProcessor):
    def process(self, n_components=10):
        tfidf_vectorizer = TfidfVectorizer(tokenizer=word_tokenize, stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(self.prepared_documents)

        nmf_model = NMF(n_components=n_components)
        nmf_matrix = nmf_model.fit_transform(tfidf_matrix)

        topic_representation = tfidf_vectorizer.transform([self.topic])
        nmf_topic_representation = nmf_model.transform(topic_representation)

        similarities = cosine_similarity(nmf_matrix, nmf_topic_representation)
        sorted_indices = np.argsort(similarities[:, 0])[::-1]

        return self.sort_data_by_indices(sorted_indices)

class ProcessDoc2Vec(TopicModelProcessor):
    def process(self):
        tokenized_documents = [word_tokenize(doc.lower()) for doc in self.prepared_documents]
        tokenized_topic = word_tokenize(self.topic.lower())

        tagged_documents = [TaggedDocument(words=doc, tags=[str(i)]) for i, doc in enumerate(tokenized_documents)]

        model = Doc2Vec(vector_size=20, min_count=2, epochs=50)
        model.build_vocab(tagged_documents)
        model.train(tagged_documents, total_examples=model.corpus_count, epochs=model.epochs)

        document_vectors = [model.infer_vector(doc) for doc in tokenized_documents]
        topic_vector = model.infer_vector(tokenized_topic).reshape(1, -1)

        similarities = cosine_similarity(topic_vector, document_vectors)[0]
        sorted_indices = np.argsort(similarities)[::-1]

        return self.sort_data_by_indices(sorted_indices)

class ProcessTop2Vec(TopicModelProcessor):
    def process(self, num_topics=10):
        top2vec_model = Top2Vec(self.prepared_documents, embedding_model='doc2vec', min_count=2)
        topic_words, word_scores, topic_scores, topic_nums = top2vec_model.search_topics(keywords=[self.topic], num_topics=num_topics)
        topic_num = topic_nums[0]
        #topic_sizes, topic_nums = top2vec_model.get_topic_sizes()
        #index = np.where(topic_nums == topic_num)[0]
        #topic_size = topic_sizes[index]
        documents, document_scores, document_ids = top2vec_model.search_documents_by_topic(topic_num=topic_num, num_docs=len(self.prepared_documents))

        sorted_indices = np.argsort(document_scores)[::-1]

        return self.sort_data_by_indices(document_ids[sorted_indices])

class ProcessKMeans(TopicModelProcessor):
    def process(self, n_clusters=10):
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(self.prepared_documents)

        kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42)
        kmeans.fit(X)

        topic_vector = vectorizer.transform([self.topic])
        cluster_indices = np.where(kmeans.labels_ == kmeans.predict(topic_vector))[0]
        similarities = cosine_similarity(topic_vector, X[cluster_indices])[0]
        sorted_indices = cluster_indices[np.argsort(similarities)[::-1]]

        return self.sort_data_by_indices(sorted_indices)


class ProcessOnlyTFIDF(TopicModelProcessor):
    def process(self):
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(self.prepared_documents + [self.topic])

        topic_vector = tfidf_matrix[-1]
        cosine_similarities = cosine_similarity(topic_vector, tfidf_matrix[:-1])
        sorted_indices = np.argsort(cosine_similarities[0])[::-1]

        return self.sort_data_by_indices(sorted_indices)

class ProcessBERT(TopicModelProcessor):
    def process(self):
        topic_model = BERTopic()
        topics, probs = topic_model.fit_transform(self.prepared_documents)
        topic_indices, probabilities = topic_model.find_topics(self.topic, top_n=1)

        if not topic_indices:
            raise ValueError(f"Nenhum tópico encontrado para '{self.topic}'")

        selected_topic = topic_indices[0]
        topic_docs_indices = [i for i, t in enumerate(topics) if t == selected_topic]
        sorted_topic_docs = sorted(topic_docs_indices, key=lambda i: probs[i], reverse=True)

        return self.sort_data_by_indices(sorted_topic_docs)