from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from exceptions.exceptions import IllegalValueException, EmptyValueException, NotDataFoundException, \
    RequestRedditException
from process_dm.get_data import RedditData
from process_dm.process import DataMinerProcess
from process_dm.topic_modeling_process import ProcessOnlyTFIDF, ProcessBERT, ProcessDoc2Vec, ProcessKMeans, ProcessTop2Vec, ProcessNMF
from process_dm.nlp_search import SemanticSearch, QuestionProcessor
import json
import cProfile
import os
from config import Config
from elastic_search.elastichsearch import getInBunch, getAllInBunch
reddit_data = RedditData()


def result_to_json(bunch):
    result = [
        {
            "id": id,
            "title": title,
            "selftext": selftext,
            "thumbnail": thumbnail,
            "permalink": permalink
        }
        for id, title, selftext, thumbnail, permalink in
        zip(bunch.ids, bunch.titles, bunch.selftexts, bunch.thumbnails, bunch.permalinks)
    ]
    return result

def bunch_to_json(bunch, requests_count):
    result = result_to_json(bunch)
    reddit_json = {
        "data": result,
        "count": len(result),
        "status_code": 200,
        "requests_count": requests_count
    }
    reddit_json = json.dumps(reddit_json, indent=2)
    return reddit_json

def list_to_json(list, requests_count):
    reddit_json = {
        "data": list,
        "count": len(list),
        "status_code": 200,
        "requests_count": requests_count
    }
    reddit_json = json.dumps(reddit_json, indent=2)
    return reddit_json


def comments_bunch_to_json(bunch):
    result = [
        {
            "id": comment_id,
            "text": comment_text,
            "replies": [
                {
                    "id": reply_id,
                    "text": reply_text
                }
                for reply_id, reply_text in zip(reply.ids, reply.text)
            ]
        }
        for comment_id, comment_text, reply in zip(bunch.ids, bunch.text, bunch.replies)
    ]
    comments_json = {
        "data": result,
        "count": len(result),
        "status_code": 200
    }
    comments_json = json.dumps(comments_json, indent=2)
    return comments_json


search_reddit = Blueprint('search_reddit', __name__)


@search_reddit.route('/search', methods=['GET'])
def search_reddit_route():
    query = request.args.get('query')  # request.json.get
    sort = request.args.get('sort', "relevance")
    limit = int(request.args.get('limit', 100))
    pages = int(request.args.get('pages', 1))
    try:
        data, count_requests = reddit_data.search_reddit(query, pages, sort, limit)
        return bunch_to_json(data, count_requests)
    except (IllegalValueException, EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except (NotDataFoundException, RequestRedditException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 503, 'message': str(error)}), 503
    except Exception as error:
        print(str(error))
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

get_comments = Blueprint('get_comments', __name__)

@get_comments.route('/comments', methods=['GET'])
def get_comments_route():
    reddit_id = request.json.get('id')
    try:
        data = reddit_data.search_comments(reddit_id)
        return comments_bunch_to_json(data)
    except (IllegalValueException, EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except (NotDataFoundException, RequestRedditException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 503, 'message': str(error)}), 503
    except Exception as error:
        print(str(error))
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

def search_topic_route(process_class):
    def route_function():
        # PARAMETROS
        query = request.args.get('query')  # request.json.get
        topic = request.args.get('topic')
        sort = request.args.get('sort', "relevance")
        limit = int(request.args.get('limit', 100))
        pages = int(request.args.get('pages', 10))
        context = request.args.get('context')
        elasticSearch = request.args.get('elastic_search')
        count_requests = 0
        
        if Config.DEBUG_MODE:
            # PROFILE
            profiler = cProfile.Profile()
            profiler.enable()

        try:
            if not elasticSearch or elasticSearch == 0:
                data, count_requests = reddit_data.search_reddit(query, pages, sort, limit)
            else:
                data = getInBunch(query, elasticSearch)
            process = process_class(data=data, topic=topic, context=context)
            data_processed = process.process()
            response = bunch_to_json(data_processed, count_requests)
        except (IllegalValueException, EmptyValueException) as error:
            response = jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
        except Exception as error:
            response = jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500
        finally:
            if Config.DEBUG_MODE:
                profiler.disable()
                profile_dir = os.path.join(Config.ROOT_DIR, 'profiles')
                os.makedirs(profile_dir, exist_ok=True)
                profiler_output_path = os.path.join(profile_dir, f'{process_class.__name__}.prof')
                profiler.dump_stats(profiler_output_path)
                print(f"Profiler output saved to {profiler_output_path}")

        return response

    return route_function

# Blueprints
search_topic_nmf = Blueprint('search_topic_nmf', __name__)
search_topic_top2vec = Blueprint('search_topic_top2vec', __name__)
search_topic_doc2vec = Blueprint('search_topic_doc2vec', __name__)
search_topic_kmeans = Blueprint('search_topic_kmeans', __name__)
search_topic_elmo = Blueprint('search_topic_elmo', __name__)
search_topic_bert = Blueprint('search_topic_bert', __name__)
search_topic_tfidf = Blueprint('search_topic_tfidf', __name__)

# CAMINHOS
search_topic_nmf.route('/search/nmf/topic', methods=['GET'])(search_topic_route(ProcessNMF))
search_topic_top2vec.route('/search/top2vec/topic', methods=['GET'])(search_topic_route(ProcessTop2Vec))
search_topic_doc2vec.route('/search/doc2vec/topic', methods=['GET'])(search_topic_route(ProcessDoc2Vec))
search_topic_kmeans.route('/search/kmeans/topic', methods=['GET'])(search_topic_route(ProcessKMeans))
search_topic_elmo.route('/search/elmo/topic', methods=['GET'])(search_topic_route(ProcessBERT))
search_topic_bert.route('/search/bert/topic', methods=['GET'])(search_topic_route(ProcessBERT))
search_topic_tfidf.route('/search/tfidf/topic', methods=['GET'])(search_topic_route(ProcessOnlyTFIDF))


ask_question_bert = Blueprint('ask_question_bert', __name__)
@ask_question_bert.route('/ask/bert', methods=['GET'])
def ask_question_bert_route():
    question = request.json.get('question')
    try:
        data_processed = DataMinerProcess.askBERT(question)
        # return bunch_to_json(data_processed)
        return data_processed
    except (EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

question_processor = Blueprint('question_processor', __name__)
@question_processor.route('/question', methods=['GET'])
def question_question_route():
    query = request.args.get('query')
    elasticSearch = request.args.get('elastic_search')
    sort = request.args.get('sort', "relevance")
    limit = int(request.args.get('limit', 100))
    pages = int(request.args.get('pages', 1))
    try:
        processor = QuestionProcessor(query, elasticSearch, sort, limit, pages)
        data_processed, count_requests = processor.process()
        return bunch_to_json(data_processed, count_requests)
    except (EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

semanticSearch = Blueprint('semanticSearch', __name__)
@semanticSearch.route('/semanticSearch', methods=['GET'])
def semanticSearch_route():
    query = request.args.get('query')
    #é sempre no elasticSearch
    top = request.args.get('top', 5)
    try:
        processor = SemanticSearch(query)
        data_processed, count_requests = processor.process(top)
        return list_to_json(data_processed, count_requests)
    except (EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500
