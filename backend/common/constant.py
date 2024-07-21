import os  # for environment variables
import openai
import chromadb  # vector storage

# constants
GPT_MODEL = "gpt-3.5-turbo"  # model for tokenizer to use
MAX_TOKENS = 1600
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 1000  # you can submit up to 2048 embedding inputs per request
DB_PATH = "./storage"
OPENAI_KEY_NAME = 'MY_OPENAI_API_KEY'
OPENAI_API_KEY = "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"

# check for openai key from env
if os.getenv(OPENAI_KEY_NAME) is not None:
    openai.api_key = os.getenv(OPENAI_KEY_NAME)
else:
    openai.api_key = OPENAI_API_KEY

# clients
openai_client = openai.OpenAI(api_key=openai.api_key)
chromadb_client = chromadb.PersistentClient(path=DB_PATH)
# chromadb_openai_embedding_func = embedding_functions.OpenAIEmbeddingFunction(
#     api_key=openai.api_key,
#     model_name=EMBEDDING_MODEL)
jobs_collection = chromadb_client.get_or_create_collection(
    name="jobs")