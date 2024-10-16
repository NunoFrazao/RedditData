# elasticsearch_utils.py
from elasticsearch import Elasticsearch, exceptions
from sklearn.utils import Bunch
from config import Config

ELASTICSEARCH_HOST = Config.ELASTICSEARCH_HOST

def index_posts(result):
    # Configurar conexão com o Elasticsearch
    es = Elasticsearch(ELASTICSEARCH_HOST)

    # Agora indexar os documentos
    for post in result:
        post_id = post['id']

        try:
            # Verificar se o documento já existe no Elasticsearch
            es.get(index='reddit_posts', id=post_id)
            # Se o documento existe, você pode escolher atualizá-lo ou ignorá-lo
            print(f"Documento com ID {post_id} já existe. Ignorando.")
        except exceptions.NotFoundError:
            # Se o documento não existe, então indexe-o
            es.index(index='reddit_posts', id=post_id, body=post)
            print(f"Documento com ID {post_id} adicionado ao Elasticsearch.")

    # Verificar se os documentos foram indexados corretamente
    # Aqui, você pode verificar o retorno do Elasticsearch ou simplesmente assumir que funcionou se não houver erros.

def getAll(user_id):
    index = "reddit_posts_"+user_id
    es = Elasticsearch(ELASTICSEARCH_HOST)

    response = es.search(index=index, query={"match_all": {}}, size=10000)
    return response

def getAllInBunch():
    result = getAll()

    titles = []
    selftexts = []
    ids = []
    thumbnails = []
    permalinks = []

    for doc in result['hits']['hits']:
        source = doc['_source']
        titles.append(source.get("title", ""))
        selftexts.append(source.get("selftext", ""))
        ids.append(source.get("id", ""))
        thumbnails.append(source.get("thumbnail", ""))
        permalinks.append(source.get("permalink", ""))

    return Bunch(titles=titles, selftexts=selftexts, ids=ids, thumbnails=thumbnails, permalinks=permalinks)

def get(query, user_id):
    index = "reddit_posts_"+user_id
    es = Elasticsearch(ELASTICSEARCH_HOST)

    response = es.search(index=index, query={
        "match": {
            "selftext": query
        }
    }, size=10000)

    return response

def getInBunch(query, user_id):
    result = get(query, user_id)

    titles = []
    selftexts = []
    ids = []
    thumbnails = []
    permalinks = []

    for doc in result['hits']['hits']:
        source = doc['_source']
        titles.append(source.get("title", ""))
        selftexts.append(source.get("selftext", ""))
        ids.append(source.get("id", ""))
        thumbnails.append(source.get("thumbnail", ""))
        permalinks.append(source.get("permalink", ""))

    return Bunch(titles=titles, selftexts=selftexts, ids=ids, thumbnails=thumbnails, permalinks=permalinks)