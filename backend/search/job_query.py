import os 
import sys
import openai
import chromadb

from chromadb.api.types import QueryResult

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.append(parentdir)

GPT_MODEL = "gpt-4o-mini"  # model for tokenizer to use
EMBEDDING_MODEL = "text-embedding-3-large"
DB_PATH = "/Users/vimal.chaudhari/Downloads/vimalKeshu/job-search/backend/storage/prod/chromadb"

# clients
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai.api_key)
chromadb_client = chromadb.PersistentClient(path=DB_PATH)
job_collection = chromadb_client.get_or_create_collection(name="job")

def get_embedding(text, model=EMBEDDING_MODEL):
    """Return the embeddings of text."""
    text = text.replace("\n", " ")
    return (openai_client.embeddings.
            create(input=[text], model=model, encoding_format="float")
            .data[0].embedding)

def query_jobs_data(embedding, size:int) -> QueryResult:
    """Query job data"""
    return job_collection.query(query_embeddings=[embedding],
                                 n_results=size,
                                 include=['metadatas', 'distances'])

def query(question:str, criteria_distance:float=0.5, size:int=10):
    jobs:list = []
    if len(question.strip()) == 0:
        return jobs
    
    question_embedding = get_embedding(text=question)
    result = query_jobs_data(question_embedding, size=size)
    # print(result)

    for i in range(len(result['ids'])):
        for j in range(len(result['metadatas'][i])):
            #print(i, result['metadatas'][i][j]['title'], result['distances'][i][j])
            print(type(result['distances'][i][j]), result['distances'][i][j])
            #if float(result['distances'][i][j]) <= criteria_distance:
            jobs.append({   
                            'id': result['ids'][i][j],
                            'title': result['metadatas'][i][j]['title'],
                            'company': result['metadatas'][i][j]['company'],
                            'url': result['metadatas'][i][j]['url'],
                            'distance': result['distances'][i][j]
                        })

    jobs = sorted(jobs, key=lambda job: job['distance'])        

    return jobs

if __name__=='__main__':
    jobs = query(question="give me google software engineering jobs located only in india.",)
    for job in jobs:
        print(job['title'], job['company'], job['distance'], job['url'])
    # print(job_collection.count())