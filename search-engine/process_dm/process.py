import os
from operator import itemgetter

import gensim
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import spacy as spacy
from gensim import corpora
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Doc2Vec
from sklearn.cluster import KMeans
import numpy as np
from sklearn.utils import Bunch
from top2vec import Top2Vec
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models.doc2vec import TaggedDocument
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from transformers import BertForQuestionAnswering
from transformers import AutoTokenizer
from transformers import pipeline
from elastic_search.elastichsearch import getAll


from exceptions.exceptions import EmptyValueException
from process_dm.data_preparation import DataPreparation

from process_dm.get_data import RedditData


# from gensim.models import Word2Vec
# https://medium.com/blend360/topic-modelling-a-comparison-between-lda-nmf-bertopic-and-top2vec-part-i-3c16372d51f0


class DataMinerProcess:

    # Algoritmo Non-Negative Matrix Factorization (NMF)
    def processNMF(data, topic, context=0):
        if not topic:
            raise EmptyValueException("The 'topic' is empty")
        if not data:
            raise EmptyValueException("The 'data' is empty")


        print("DATA-------------------------\n\n\n\n", data)

        # Extrair os documentos do dicionário de entrada
        documents = choose_documents(data, context)

        # Preparacao
        prepare = DataPreparation()
        documents = prepare.prepareAll(documents=documents)
        non_empty_docs_indices = [i for i, doc in enumerate(documents) if doc.strip()]
        documents = [doc for doc in documents if doc.strip()]
        for key in data.keys():
            data[key] = [data[key][i] for i in non_empty_docs_indices]

        for key in data.keys():
            data[key] = [data[key][i] for i in non_empty_docs_indices]

        # Tokenização e representação TF-IDF
        tfidf_vectorizer = TfidfVectorizer(tokenizer=word_tokenize, stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

        # Aplicação do NMF
        nmf_model = NMF(n_components=10)
        nmf_matrix = nmf_model.fit_transform(tfidf_matrix)

        # Calcula a similaridade entre o tópico e os documentos
        topic_representation = tfidf_vectorizer.transform([topic])
        nmf_topic_representation = nmf_model.transform(topic_representation)

        similarities = cosine_similarity(nmf_matrix, nmf_topic_representation)

        # Identifica o cluster ao qual o tópico pertence
        best_cluster_index = np.argmax(similarities)

        print("Melhor índice de cluster:", best_cluster_index)

        # Encontra todos os documentos pertencentes ao mesmo cluster
        cluster_indices = np.where(np.argmax(nmf_matrix, axis=1) == best_cluster_index)[0]
        # Ordena o dicionario
        documentos_similares = [documents[i] for i in cluster_indices]
        for key in data.keys():
            if key != "selftexts":
                data[key] = [data[key][i] for i in cluster_indices]

        return data

    # https://medium.com/bitgrit-data-science-publication/nlp-snippets-in-python-90ac29ffaea0#4cba
    def processDoc2Vec(data, topic, context=0):
        # https://radimrehurek.com/gensim/auto_examples/tutorials/run_doc2vec_lee.html#sphx-glr-auto-examples-tutorials-run-doc2vec-lee-py

        if not topic:
            raise EmptyValueException("The 'topic' is empty")
        if not data:
            raise EmptyValueException("The 'data' is empty")

        # Extrair os documentos do dicionário de entrada
        documents = choose_documents(data, context)

        # Preparacao
        prepare = DataPreparation()
        prepared_documents = prepare.prepareAll(documents=documents)
        non_empty_docs_indices = [i for i, doc in enumerate(prepared_documents) if doc.strip()]
        prepared_documents = [doc for doc in prepared_documents if doc.strip()]
        for key in data.keys():
            data[key] = [data[key][i] for i in non_empty_docs_indices]

        # Tokenização dos documentos e do tópico
        tokenized_documents = [nltk.word_tokenize(doc) for doc in prepared_documents]
        tokenized_topic = nltk.word_tokenize(topic)

        # Tagging dos documentos
        tagged_documents = [TaggedDocument(words=doc, tags=[i]) for i, doc in enumerate(tokenized_documents)]

        print(tagged_documents)

        # train Doc2Vec model
        model = Doc2Vec(
            documents=tagged_documents,
            vector_size=10,  # Dimensionalidade dos embeddings
            window=4,  # Janela de contexto
            min_count=1,  # Número mínimo de contagens de palavras
            workers=4,  # Número de processadores (paralelização)
            epochs=10,  # Número de épocas de treinamento
        )

        # Geração de embeddings dos documentos e do tópico
        document_embeddings = np.array([model.dv[i] for i in range(len(tagged_documents))])
        topic_embedding = model.infer_vector(tokenized_topic).reshape(1, -1)

        # Calcula a similaridade entre o tópico e os documentos
        similarities = cosine_similarity(topic_embedding, document_embeddings)

        # Aplique o algoritmo K-Means
        kmeans = KMeans(n_clusters=5)
        kmeans.fit(document_embeddings)

        # Encontra o cluster ao qual o tópico pertence
        topic_cluster = kmeans.predict(topic_embedding)[0]
        cluster_indices = np.where(kmeans.labels_ == topic_cluster)[0]

        # Filtra os documentos pertencentes ao cluster correto e ordena por similaridade
        cluster_similarities = similarities[0][cluster_indices]
        sorted_cluster_indices = cluster_indices[np.argsort(cluster_similarities)[::-1]]

        # Seleciona os documentos mais similares dentro do cluster correto
        most_similar_documents = [prepared_documents[i] for i in sorted_cluster_indices]

        return most_similar_documents

    def processTop2Vec(data, topic, context=0):
        # https://top2vec.readthedocs.io/en/stable/Top2Vec.html#
        if not topic:
            raise EmptyValueException("The 'topic' is empty")
        if not data:
            raise EmptyValueException("The 'data' is empty")

        # Extrair os documentos do dicionário de entrada
        documents = choose_documents(data, context)

        # Preparacao
        prepare = DataPreparation()
        prepared_documents = prepare.prepareAll(documents=documents)
        print(prepared_documents)
        print(len(prepared_documents))
        # Remover os documentos vazios e os elementos correspondentes aos outros arrays do data
        non_empty_docs_indices = [i for i, doc in enumerate(prepared_documents) if doc.strip()]
        prepared_documents = [doc for doc in prepared_documents if doc.strip()]
        for key in data.keys():
            data[key] = [data[key][i] for i in non_empty_docs_indices]

        print(len(prepared_documents))
        # Inicializar o modelo Top2Vec
        top2vec_model = Top2Vec(prepared_documents, embedding_model='doc2vec', min_count=2)

        # Pesquisar tópicos com o número de tópicos
        topic_words, word_scores, topic_scores, topic_nums = top2vec_model.search_topics(keywords=[topic], num_topics=10)

        # Encontrar o topico mais similar
        topic_num = topic_nums[0]
        # Obtem o numero de documentos do topico
        topic_sizes, topic_nums = top2vec_model.get_topic_sizes()
        index = np.where(topic_nums == topic_num)[0]
        topic_size = topic_sizes[index]
        # Obtem todos os documentos do topico
        documents, document_scores, document_ids = top2vec_model.search_documents_by_topic(topic_num=topic_num,
                                                                                           num_docs=int(topic_size))

        # Organizar os outros arrays do dicionário na mesma ordem dos documentos processados
        for key in data.keys():
            if key != "selftexts":
                data[key] = [data[key][doc_id] for doc_id in document_ids]

        return data

    def processKMeans(data, topic, context=0):
        # https://stackoverflow.com/questions/19197715/scikit-learn-k-means-elbow-criterion
        # https://www.geeksforgeeks.org/elbow-method-for-optimal-value-of-k-in-kmeans/

        if not topic:
            raise EmptyValueException("The 'topic' is empty")
        if not data:
            raise EmptyValueException("The 'data' is empty")

        # Extrair os documentos do dicionário de entrada
        documents = choose_documents(data, context)

        # Preparação
        prepare = DataPreparation()
        documents = prepare.prepareAll(documents=documents)
        non_empty_docs_indices = [i for i, doc in enumerate(documents) if doc.strip()]
        documents = [doc for doc in documents if doc.strip()]
        for key in data.keys():
            data[key] = [data[key][i] for i in non_empty_docs_indices]

        # TF-IDF
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(documents)

        # Create a range of values for k
        # k_range = range(1, 31)

        # Initialize an empty list to store the inertia values for each k
        inertia_values = []

        # Fit the data for each k value and calculate inertia
        #for k in k_range:
        #    kmeans = KMeans(n_clusters=k, init='k-means++', random_state=42)
        #    kmeans.fit(X)
        #   inertia_values.append(kmeans.inertia_)

        # Plot the inertia values for each k
        #plt.plot(k_range, inertia_values, 'bo-')
        #plt.title('Elbow Method')
        #plt.xlabel('Number of clusters (k)')
        #plt.ylabel('Inertia')
        #plt.show()

        # Aplicação do K-Means com o número ideal de clusters
        n_clusters_ideal = 5  # Altere conforme necessário
        kmeans = KMeans(n_clusters=n_clusters_ideal, init='k-means++', random_state=42)
        kmeans.fit(X)

        # Encontrar o cluster com o maior número de documentos similares ao tópico
        topic_vector = vectorizer.transform([topic])
        cluster_indices = kmeans.predict(topic_vector)

        # Obter todos os documentos no cluster selecionado
        cluster_indices = np.where(kmeans.labels_ == cluster_indices)[0]

        # Calcular a similaridade entre o tópico e os documentos no cluster
        similaridades = cosine_similarity(topic_vector, X[cluster_indices])

        # Ordenar os documentos por similaridade
        documentos_similares = np.argsort(similaridades[0])[::-1]
        documentos_similares = [documents[i] for i in documentos_similares]

        # Atualizar os dados para conter apenas os elementos correspondentes aos documentos no cluster selecionado
        for key in data.keys():
            if key != "selftexts":
                data[key] = [data[key][i] for i in cluster_indices]

        return data

    def processOnlyTFIDF(data, topic, context=0):
        # Verificar entradas
        if not topic:
            raise ValueError("O 'topic' está vazio")
        if not data:
            raise ValueError("O 'data' está vazio")

        # Extrair os documentos do dicionário de entrada
        documents = choose_documents(data, context)  # Supomos que esta função existe e retorna os documentos

        # Preparação (presumivelmente limpeza e pré-processamento)
        prepare = DataPreparation()
        documents = prepare.prepareAll(documents=documents)

        # Remover documentos vazios e obter índices não vazios
        non_empty_docs_indices = [i for i, doc in enumerate(documents) if doc.strip()]
        documents = [doc for doc in documents if doc.strip()]

        # Filtrar `data` para manter apenas elementos não vazios
        for key in data.keys():
            data[key] = [data[key][i] for i in non_empty_docs_indices]

        # Vetorização TF-IDF
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents + [topic])  # Inclui o tópico na vetorização

        # Vetor do tópico
        topic_vector = tfidf_matrix[-1]  # O último vetor é o do tópico

        # Calcula a similaridade de cosseno entre o tópico e todos os documentos
        cosine_similarities = cosine_similarity(topic_vector, tfidf_matrix[:-1])  # Exclui o último vetor

        # Ordena os índices dos documentos pela similaridade (descendente)
        sorted_indices = np.argsort(cosine_similarities[0])[::-1]

        # Reorganiza todos os arrays no dicionário `data` de acordo com a nova ordem dos documentos
        for key in data.keys():
            data[key] = [data[key][i] for i in sorted_indices]

        return data

    def processBERT(data, topic, context=0):
        # https://maartengr.github.io/BERTopic/getting_started/representation/representation.html
        # https://github.com/MaartenGr/BERTopic
        # https://www.geeksforgeeks.org/how-to-generate-word-embedding-using-bert/
        # https://colab.research.google.com/github/tensorflow/text/blob/master/docs/tutorials/classify_text_with_bert.ipynb#scrollTo=_OoF9mebuSZc
        # https://medium.com/@monica.rotulo/tweets-sentiment-analysis-with-roberta-1f30cf4e1035
        # https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment/blob/main/.ipynb_checkpoints/README-checkpoint.md


        if not topic:
            raise EmptyValueException("The 'topic' is empty")
        if not data:
            raise EmptyValueException("The 'data' is empty")

        # Extrair os documentos do dicionário de entrada
        documents = choose_documents(data, context)

        # Preparação
        prepare = DataPreparation()
        documents = prepare.prepareAll(documents=documents)
        non_empty_docs_indices = [i for i, doc in enumerate(documents) if doc.strip()]
        documents = [doc for doc in documents if doc.strip()]
        for key in data.keys():
            data[key] = [data[key][i] for i in non_empty_docs_indices]

        # Fine-tune your topic representations
        topic_model = BERTopic()

        # Criar o modelo BERTopic
        # topic_model = BERTopic()
        topics, probs = topic_model.fit_transform(documents)

        # Encontrar o tópico correspondente ao tópico de entrada
        # Identificar os tópicos mais próximos ao tópico fornecido
        topic_indices, probabilities = topic_model.find_topics(topic, top_n=1)
        print("TOPICS BERTOPIC", topic_indices, probabilities) # Inicializar o modelo BERTopic

        # Ajustar o modelo aos documentos


        if not topic_indices:
            raise ValueError(f"Nenhum tópico encontrado para '{topic}'")

        # Obter os documentos associados ao tópico principal identificado
        selected_topic = topic_indices[0]  # Selecionar o tópico mais relevante
        topic_docs_indices = [i for i, t in enumerate(topics) if t == selected_topic]

        # Ordenar os documentos pela proximidade ao tópico (maior probabilidade primeiro)
        sorted_topic_docs = sorted(
            topic_docs_indices,
            key=lambda i: probs[i],
            reverse=True  # Maior probabilidade primeiro
        )

        # Extrair os documentos relevantes
        topic_documents = [documents[i] for i in sorted_topic_docs]
        print("BERTOPIC", topic_documents)

        sorted_data = Bunch()
        for key, value in data.items():
            sorted_data[key] = [value[i] for i in sorted_topic_docs]

        return sorted_data

    def askBERT(question):
        #INPUT VALIDATION
        if not question:
            raise EmptyValueException("The 'question' is empty")

        # PROFILER
        prepare = DataPreparation()

        # ASK QUESTION
        print("question: ",question)


        # PREPARE QUERY FROM QUESTION

        #MAKE A REQUEST
        # search
        reddit_data = RedditData()
        data = reddit_data.search_reddit(question, 1)

        # PREP DATA
        documents = choose_documents(data, context=1)
        print("BEFORE PREP: \n",documents)
        prepare = DataPreparation()
        prepare.pipeline = [prepare.lower_case, prepare.remove_url, prepare.remove_html, prepare.remove_spaces_tabs]
        documents = prepare.prepareAll(documents=documents)
        # non_empty_docs_indices = [i for i, doc in enumerate(documents) if doc.strip()]
        # documents = [doc for doc in documents if doc.strip()]
        # for key in data.keys():
        #     data[key] = [data[key][i] for i in non_empty_docs_indices]

        print("AFTER PREP: \n",documents)
        context = " ".join(documents)

        model = BertForQuestionAnswering.from_pretrained('deepset/bert-base-cased-squad2')


        tokenizer = AutoTokenizer.from_pretrained('deepset/bert-base-cased-squad2')
        tokenizer.encode(question, truncation=True, padding=True)

        nlp = pipeline('question-answering', model=model, tokenizer=tokenizer)

        answer_dict = nlp({
            'question': question,
            'context': context
        })

        print(answer_dict)

        # input_ids = tokenizer.encode(question, answer_text)
        # print('\n\nThe input has a total of {:} tokens.'.format(len(input_ids)))


        #BERT PROCESS

        #GIVE ANSWER
        return answer_dict["answer"]

    def ask(question):
        #https://www.ibm.com/reference/python/countvectorizer
        #https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
        if not question:
            raise EmptyValueException("The 'question' is empty")

        print("QUESTION", question)

        # EXTRACT TOPICS
        topics = extract_topics_from_question(question)
        search_query = " ".join(topics)
        print("Search Query: ", search_query)

        reddit_data = RedditData()
        data, count_requests = reddit_data.search_reddit(search_query, 5)

        return data


    # https://gianfree-notes.netlify.app/docs/machine-learning/unsupervised/topic-modelling/top2vec/

    # https://maartengr.github.io/BERTopic/index.html

    def semanticSearch(query):

        if not query:
            raise EmptyValueException("The 'query' is empty")

        data = getAll()

        print("DATA-------------------------\n\n\n\n", data['hits']['hits'])

        # Carregar o modelo de linguagem do spaCy
        #https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.1.0/en_core_web_sm-3.1.0.tar.gz

        nlp = spacy.load("en_core_web_sm")

        # Função para tokenização
        def spacy_tokenizer(text):
            prepare = DataPreparation()
            document = prepare.prepareOne(doc=text)
            doc = nlp(document)
            return [token.text for token in doc]

        # Extraindo os dados e armazenando em um dicionário
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

        for content in reddits:
            print(f"ID: {content['id']}")
            print(f"Title: {content['title']}")
            print(f"Selftext: {content['selftext']}")
            print(f"Tokenized Selftext: {content['selftext_tokenized']}")
            print(f"Thumbnail: {content['thumbnail']}")
            print(f"Permalink: {content['permalink']}")
            print("-" * 40)
            break
        print(data['hits']["total"]["value"], len(reddits), len(data['hits']['hits']))

        tokens = [content['selftext_tokenized'] for content in reddits]
        dictionary = corpora.Dictionary(tokens)

        corpus = [dictionary.doc2bow(desc) for desc in tokens]
        word_frequencies = [[(dictionary[id], frequency) for id, frequency in line] for line in corpus[0:3]]
        print("WORD FREQUENCIES", word_frequencies)

        #LOAD MODELS
        tfidf_model = gensim.models.TfidfModel(corpus, id2word=dictionary)
        tfidf_corpus = tfidf_model[corpus]
        lsi_model = gensim.models.LsiModel(tfidf_corpus, id2word=dictionary, num_topics=100)


        # Load the MatrixSimilarity
        from gensim.similarities import MatrixSimilarity
        reddit_index = MatrixSimilarity(tfidf_corpus, num_features=len(dictionary))

        #SEARCH SEMANTIC
        search_term = query
        query_bow = dictionary.doc2bow(spacy_tokenizer(search_term))
        query_tfidf = tfidf_model[query_bow]
        query_lsi = lsi_model[query_tfidf]

        reddit_index.num_best = 5
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

        return reddits_clean



def choose_documents(data, context):
    # Default - Analize reddit titles
    # 1 - Analize reddit text
    if context:
        if context == 1:
            return data.get("selftexts", [])
    return data.get("titles", [])

def extract_topics_from_question(question, num_topics=5):
    #Chat gpt
    vectorizer = CountVectorizer(stop_words=stopwords.words('english'), max_features=10000)
    X = vectorizer.fit_transform([question])
    keywords = vectorizer.get_feature_names_out()
    return keywords[:num_topics]



#https://youtu.be/h2kBNEShsiE?t=878
#https://medium.com/analytics-vidhya/semantic-search-engine-using-nlp-cec19e8cfa7e
