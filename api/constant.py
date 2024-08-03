import os
import openai
import chromadb
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
#parentdir = os.path.dirname(parentdir)

# constants
GPT_MODEL = "gpt-4o-mini"  # model for tokenizer to use
MAX_TOKENS = 1600
EMBEDDING_MODEL = "text-embedding-3-large"
BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request
DB_PATH = parentdir + "/storage/prod/chromadb"
print("DB PATH: ", DB_PATH, os.path.exists(DB_PATH))

# clients
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai.api_key)
chromadb_client = chromadb.PersistentClient(path=DB_PATH)
jobs_collection = chromadb_client.get_or_create_collection(name="job")
resume_collection = chromadb_client.get_or_create_collection(name="resume")
resume_detail_collection = chromadb_client.get_or_create_collection(name="resume_detail")