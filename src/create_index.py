import os
from langchain_community.vectorstores import FAISS
import nltk

from src.helper import load_data, text_split, load_hf_embeddings
from config import *


DATA_PATH = os.path.join(ROOT_DIR, 'data', 'MedQuAD-master')


def fix_nltk():
	# If you get error from nltk package, add the required downloads here
	#nltk.download('all')
	nltk.download('punkt_tab')
	nltk.download('averaged_perceptron_tagger_eng')

def create_index(data_path, save_path, chunk_size, chunk_overlap):
	print("Creating index...")
	fix_nltk()
	print("Loading data...")
	data = load_data(data_path)
	print("Data loaded...")
	text_chunks = text_split(data, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
	print("Loading embeddings...")
	embeddings = load_hf_embeddings()
	print("Creating vector store...")
	vectorstore_from_docs = FAISS.from_documents(text_chunks, embedding=embeddings)
	vectorstore_from_docs.save_local(save_path)
	print("Done!")
	return vectorstore_from_docs

if __name__ == '__main__':
	_ = create_index(DATA_PATH, INDEX_PATH, CHUNK_SIZE, CHUNK_OVERLAP)