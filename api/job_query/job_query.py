# imports
from chromadb.api.types import QueryResult
from api.common.constant import *

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
        introduction = 'Use the below jobs description to answer the subsequent question. If the answer cannot be found in the articles, write "I could not find an answer."'
        question = f"\n\nQuestion: {query}"
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
) -> str:
    """Answers a query using GPT and 
       a chroma db stored jobs data.
    """
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
        response_message = response.choices[0].message.content
        return response_message
    else:
        print('Not able to find any doc related to query:', query)


if __name__ == "__main__":
    print(ask(query='Is there any google job in india country?'))