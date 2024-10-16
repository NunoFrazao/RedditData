from flask import Flask
from flask_cors import CORS
from web_services.RedditService import search_reddit, get_comments, search_topic_nmf, search_topic_doc2vec, \
    search_topic_top2vec, search_topic_kmeans, search_topic_elmo, search_topic_bert, ask_question_bert, ask_question
import nltk

app = Flask(__name__)
CORS(
    app,
    origins="*",
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    allow_methods=["*"]
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
app.register_blueprint(ask_question)

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

if __name__ == '__main__':
    app.run(debug=True, port=8080)



# from gui import Window
#
# if __name__ == '__main__':
#     gui = Window()
#     gui.mainloop()
