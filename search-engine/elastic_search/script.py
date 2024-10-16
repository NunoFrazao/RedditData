from elastic_search.elastichsearch import index_posts
import time
from web_services.RedditService import result_to_json, reddit_data
import threading

# Variável para controlar se o script de indexação está ativo
indexing_active = False
indexing_thread = None
search_queries = [
    "Python programming",
    "Data science",
    "Machine learning",
    "Artificial intelligence"

]
def run_indexing(i):

    data, count = reddit_data.search_reddit(query=search_queries[i], pages=10)
    result = result_to_json(data)
    # indexar o result
    index_posts(result)

    return count # numero de requests à api reddit


def start():
    global indexing_active, indexing_thread
    if not indexing_active:
        indexing_active = True
        indexing_thread = threading.Thread(target=loop)
        indexing_thread.start()
        print("Indexação iniciada.")

def stop():
    global indexing_active, indexing_thread
    if indexing_active:
        indexing_active = False
        if indexing_thread:
            indexing_thread.join()  # Aguarda a thread de indexação finalizar
        print("Indexação parada.")

def loop():
    count = 0
    i = 0

    # Loop principal para executar o agendamento
    while i < len(search_queries):
        i += 1
        count += run_indexing(i-1)
        if(count == 100): # se houver mais de 100requests à api do reddit fazer uma pausa de 60sec
            time.sleep(60)
