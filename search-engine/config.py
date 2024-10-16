import os
from dotenv import load_dotenv

# Carregar as variáveis do arquivo .env
load_dotenv()

class Config:
    # ROOT DIR
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    # DEBUG MODE
    DEBUG_MODE = os.getenv('DEBUG_MODE', True)

    # SEARCH ENGINE
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = os.getenv('PORT', 8080)

    # ELASTICSEARCH
    ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')

    # DATABASE
    DB_CONNECTION = os.getenv('DB_CONNECTION', 'mysql')
    DB_HOST = os.getenv('DB_HOST', 'database')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_DATABASE = os.getenv('DB_DATABASE', 'laravel_db')
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
