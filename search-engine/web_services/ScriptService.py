from flask import Blueprint, jsonify
from elastic_search.script import start, stop


start_indexing = Blueprint('start_indexing', __name__)
stop_indexing = Blueprint('stop_indexing', __name__)
@start_indexing.route('/start_indexing', methods=['GET'])
def start_indexing_route():
    start()  # Chama a função para iniciar a indexação
    return jsonify({'message': 'Indexação iniciada.'})

@stop_indexing.route('/stop_indexing', methods=['GET'])
def stop_indexing_route():
    stop()  # Chama a função para parar a indexação
    return jsonify({'message': 'Indexação parada.'})