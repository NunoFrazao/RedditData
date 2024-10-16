from flask import Blueprint, request, jsonify

from exceptions.exceptions import IllegalValueException, EmptyValueException, NotDataFoundException, \
    RequestRedditException
from process_dm.get_data import RedditData
from process_dm.process import DataMinerProcess
import json

reddit_data = RedditData()

def bunch_to_json(bunch):
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
    reddit_json = {
        "data": result,
        "count": len(result),
        "status_code": 200
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
    query = request.json.get('query')
    pages = request.json.get('pages')
    sort = request.json.get('sort')
    limit = request.json.get('limit')
    try:
        data = reddit_data.search_reddit(query, pages, sort, limit)
        return bunch_to_json(data)
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


search_topic_nmf = Blueprint('search_topic_nmf', __name__)
@search_topic_nmf.route('/search/nmf/topic', methods=['GET'])
def search_topic_nmf_route():
    query = request.json.get('query')
    topic = request.json.get('topic')
    sort = request.json.get('sort')
    limit = request.json.get('limit')
    pages = request.json.get('pages')
    analysis_mode = request.json.get('analysis_mode')
    try:
        data = reddit_data.search_reddit(query, pages, sort, limit)
        data_processed = DataMinerProcess.processNMF(data, topic, analyze=analysis_mode)
        return bunch_to_json(data_processed)
    except (IllegalValueException, EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

search_topic_top2vec = Blueprint('search_topic_top2vec', __name__)

@search_topic_top2vec.route('/search/top2vec/topic', methods=['GET'])
def search_topic_top2vec_route():
    query = request.json.get('query')
    topic = request.json.get('topic')
    sort = request.json.get('sort')
    limit = request.json.get('limit')
    pages = request.json.get('pages')
    type = request.json.get('type')
    try:
        data = reddit_data.search_reddit(query, pages, sort, limit)
        data_processed = DataMinerProcess.processTop2Vec(data, topic, analyze=type)
        return bunch_to_json(data_processed)
    except (IllegalValueException, EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

search_topic_doc2vec = Blueprint('search_topic_doc2vec', __name__)
@search_topic_doc2vec.route('/search/doc2vec/topic', methods=['GET'])
def search_topic_word2vec_route():
    query = request.json.get('query')
    topic = request.json.get('topic')
    sort = request.json.get('sort')
    limit = request.json.get('limit')
    pages = request.json.get('pages')
    type = request.json.get('type')
    try:
        data = reddit_data.search_reddit(query, pages, sort, limit)
        data_processed = DataMinerProcess.processDoc2Vec(data, topic, analyze=type)
        return bunch_to_json(data_processed)
    except (IllegalValueException, EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

search_topic_kmeans = Blueprint('search_topic_kmeans', __name__)
@search_topic_kmeans.route('/search/kmeans/topic', methods=['GET'])
def search_topic_kmeans_route():
    query = request.json.get('query')
    topic = request.json.get('topic')
    sort = request.json.get('sort')
    limit = request.json.get('limit')
    pages = request.json.get('pages')
    type = request.json.get('type')
    try:
        data = reddit_data.search_reddit(query, pages, sort, limit)
        data_processed = DataMinerProcess.processKMeans(data, topic, analyze=type)
        return bunch_to_json(data_processed)
    except (IllegalValueException, EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

search_topic_elmo = Blueprint('search_topic_elmo', __name__)
@search_topic_elmo.route('/search/elmo/topic', methods=['GET'])
def search_topic_elmo_route():
    query = request.json.get('query')
    topic = request.json.get('topic')
    sort = request.json.get('sort')
    limit = request.json.get('limit')
    pages = request.json.get('pages')
    try:
        data = reddit_data.search_reddit(query, pages, sort, limit)
        data_processed = DataMinerProcess.processBERT(data, topic)
        return bunch_to_json(data_processed)
    except (IllegalValueException, EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify(
            {'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

search_topic_bert = Blueprint('search_topic_bert', __name__)
@search_topic_bert.route('/search/bert/topic', methods=['GET'])
def search_topic_bert_route():
    query = request.json.get('query')
    topic = request.json.get('topic')
    sort = request.json.get('sort')
    limit = request.json.get('limit')
    pages = request.json.get('pages')
    type = request.json.get('type')
    try:
        data = reddit_data.search_reddit(query, pages, sort, limit)
        data_processed = DataMinerProcess.processBERT(data, topic, analyze=type)
        return bunch_to_json(data_processed)
    except (IllegalValueException, EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500

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

ask_question = Blueprint('ask_question', __name__)
@ask_question.route('/ask', methods=['GET'])
def ask_question_route():
    question = request.json.get('question')
    try:
        data_processed = DataMinerProcess.ask(question)
        return bunch_to_json(data_processed)
    except (EmptyValueException) as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 400, 'message': str(error)}), 400
    except Exception as error:
        return jsonify({'error': error.__class__.__name__, 'status_code': 500, 'message': str(error)}), 500
