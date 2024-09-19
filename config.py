import os

# Application parameters
USER_NAME = 'Martini'
HOST = '127.0.0.1'
PORT = 8080

# File paths
ROOT_DIR = os.path.dirname(__file__)
ASSETS_FOLDER = os.path.join(ROOT_DIR, 'assets')
DB_ROOT = os.path.join(ASSETS_FOLDER, 'database')
DB_NAME = 'medassist'
DB_PATH = os.path.join(DB_ROOT, DB_NAME + '.db')
INDEX_ROOT = os.path.join(ASSETS_FOLDER, 'index')
INDEX_NAME = 'medassist'
INDEX_PATH = os.path.join(INDEX_ROOT, INDEX_NAME + '.faiss')
CHAT_HISTORY_FOLDER = os.path.join(ASSETS_FOLDER, 'chat_history')

# Parameters for creating vector index
CHUNK_SIZE = 500
CHUNK_OVERLAP = 20

# Parameters for LLM initialization
CHAT_BUFFER = 5
K=2
T=0.1
MAX_TOKENS = 500

