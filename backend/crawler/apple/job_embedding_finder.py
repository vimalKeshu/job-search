import os
import json
import sys
import logging
import tiktoken
import openai
import pickle
import traceback


# Configure console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai.api_key)
GPT_MODEL = "gpt-4o-mini"
llm_config = {"model": GPT_MODEL}

MAX_TOKENS = 8191
EMBEDDING_MODEL = "text-embedding-3-large"
apple_json_jobs_dir = currentdir + '/jobs/json'
apple_embedding_dir = currentdir + '/jobs/embedding/text-embedding-3-large'


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def get_embedding(text, model=EMBEDDING_MODEL):
    """Return the embeddings of text."""
    text = text.replace("\n", " ")
    return (openai_client.embeddings.
            create(input=[text], model=model, encoding_format="float")
            .data[0].embedding)

def load_visited_files(dir=apple_embedding_dir)-> set:
    visited:set = set()
    for file_name in os.listdir(dir):
        visited.add(file_name)
        #print('->',file_name)
    return visited

def find():
    visited:set = load_visited_files()
    failed_path_list = []
    for json_file_name in os.listdir(apple_json_jobs_dir):
        json_file_path = os.path.join(apple_json_jobs_dir, json_file_name)
        if json_file_name.replace('.json','') in visited:
            print('visited:',json_file_name)
            continue           
        try:
            with open(json_file_path, 'r') as file:
                page_str = file.read()

            job_json = json.loads(page_str)
            #print(job_json)
            job_text=""
            for key in job_json:
                job_text+=key+":"+job_json[key]+" "
            
            token_count = num_tokens(job_text)
            if token_count > MAX_TOKENS:
                raise Exception('Token count exceeded.token count'+token_count)

            # print(job_json)
            # print(job_text)

            job_embedding = get_embedding(job_text)
            # print(job_embedding)
            embedding_file_path = os.path.join(apple_embedding_dir, json_file_name.replace('.json',''))
            with open(embedding_file_path, 'wb') as embedding_file:
                pickle.dump(job_embedding, embedding_file)            
        except:
            failed_path_list.append(json_file_path)
            traceback.print_exc()

    if len(failed_path_list) > 0:
        print(failed_path_list)

if __name__ == '__main__':
    find()