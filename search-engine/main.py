from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from web_services.RedditService import search_reddit, get_comments, search_topic_nmf, search_topic_doc2vec, \
    search_topic_top2vec, search_topic_kmeans, search_topic_elmo, search_topic_bert, ask_question_bert, question_processor, search_topic_tfidf, \
    semanticSearch
from web_services.ScriptService import stop_indexing, start_indexing
import nltk
from config import Config

app = Flask(__name__)
CORS(
    app,
    origins="*",
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    allow_methods=["*"]
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "50 per hour"]
)


app.register_blueprint(search_reddit)
app.register_blueprint(get_comments)
app.register_blueprint(search_topic_nmf)
app.register_blueprint(search_topic_doc2vec)
app.register_blueprint(search_topic_kmeans)
app.register_blueprint(search_topic_elmo)
app.register_blueprint(search_topic_bert)
app.register_blueprint(search_topic_top2vec)
app.register_blueprint(ask_question_bert)
app.register_blueprint(question_processor)
app.register_blueprint(search_topic_tfidf)
app.register_blueprint(start_indexing)
app.register_blueprint(stop_indexing)
app.register_blueprint(semanticSearch)

if __name__ == '__main__':

    # ASSEGURA QUE OS RECURSOS DA BIBLIOTECA NLTK ESTAO INSTALADOS
    def ensure_nltk_resources():
        resources = {
            'stopwords': 'corpora/stopwords',
            'punkt': 'tokenizers/punkt'
        }
        for resource, path in resources.items():
            try:
                nltk.data.find(path)
            except LookupError:
                nltk.download(resource)


    ensure_nltk_resources()

    app.run(debug=Config.DEBUG_MODE, host=Config.HOST, port=Config.PORT)



# from gui import Window
#
# if __name__ == '__main__':
#     gui = Window()
#     gui.mainloop()
