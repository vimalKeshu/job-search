# imports
import os 
import sys
import json
import traceback

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from chromadb.api.types import QueryResult
from common.constant import *

logging.getLogger().setLevel(logging.INFO)
logging.debug(currentdir)
logging.debug(parentdir)

def get_embedding(text, model=EMBEDDING_MODEL):
    """Return the embeddings of text."""
    text = text.replace("\n", " ")
    return (openai_client.embeddings.
            create(input=[text], model=model, encoding_format="float")
            .data[0].embedding)

def query_jobs_data(embedding) -> QueryResult:
    """Query job data"""
    return jobs_collection.query(query_embeddings=[embedding],
                                 n_results=2,
                                 include=["documents"])

def query_message(
    query: str,
    model: str,
    token_budget: int
) -> str:
    """Return a message for GPT, with relevant source texts."""
    query_embedding = get_embedding(text=query)
    jobs: QueryResult = query_jobs_data(embedding=query_embedding)
    # print('query result:', jobs)
    if 'documents' in jobs:
        introduction = '''
        Answer the subsequent question using given job description and return the answer in below parsable json array string, 
        in case of no answer please return empty json array string:
        [{"url": string,"company": string,"title": string}]
        '''
        question = f"\n\nquestion: {query}"
        message = introduction
        for job in jobs['documents']:
            job_posting = f'\n\nJob Description:\n"""\n{job}\n"""'
            # if (
            #     num_tokens(message + job_posting + question, model=model)
            #     > token_budget
            # ):
            #     break
            # else:
            message += job_posting
        return message + question
    else:
        return ''

def ask(
    query: str,
    model: str = GPT_MODEL,
    print_message: bool = False,
    token_budget: int = 4096 - 500,
) -> dict:
    """Answers a query using GPT and 
       a chroma db stored jobs data.
    """
    try:
        message = query_message(query, model=model, token_budget=token_budget)
        if len(message) != 0:
            if print_message:
                print(message)
            messages = [
                {"role": "system",
                    "content": "You answer questions about the jobs."},
                {"role": "user", "content": message},
            ]
            response = openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0
            )
            response_message = json.loads(response.choices[0].message.content)
            return response_message
        else:
            print('Not able to find any doc related to query:', query)
    except:
        traceback.print_exc()
    return {}

if __name__ == "__main__":
    print(ask(query='Suggest some software engineering jobs?'))