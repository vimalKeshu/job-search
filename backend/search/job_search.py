import os 
import sys
import time
import openai
import chromadb
import logging

from chromadb.api.types import GetResult, QueryResult

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.append(parentdir)

GPT_MODEL = "gpt-4o-mini"  # model for tokenizer to use
EMBEDDING_MODEL = "text-embedding-3-large"
DB_PATH = parentdir + "/storage/prod/chromadb"

logging.basicConfig(
    level=logging.DEBUG,  # Set logging level to DEBUG
    format='%(asctime)s %(levelname)s: %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format for the timestamp
)

# clients
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai.api_key)
chromadb_client = chromadb.PersistentClient(path=DB_PATH)
jobs_collection = chromadb_client.get_or_create_collection(name="jobs")
resume_collection = chromadb_client.get_or_create_collection(name="resume")
resume_detail_collection = chromadb_client.get_or_create_collection(name="resume_detail")


def query_jobs_data(embedding) -> QueryResult:
    """Query job data"""
    return jobs_collection.query(query_embeddings=[embedding],
                                 n_results=2,
                                 include=['metadatas', 'documents', 'embeddings'])


if __name__ == '__main__':
    cnt:int =  resume_detail_collection.count()
    logging.debug('count: ',cnt)
    resumes: GetResult = resume_detail_collection.get(
        limit=cnt, include=['metadatas', 'documents', 'embeddings'])
    
    if cnt > 0:
        for i in range(0, cnt):
            person:dict = resumes['metadatas'][i]
            if person:
                logging.debug(person['name'], person['email'], '\n')
                jobs = query_jobs_data(resumes['embeddings'][i])
                receiver = person['name'] + ' <'+ person['email'] + '>'
                postings=''
                for j in range(0, len(jobs['metadatas'][0])):
                    #print('id: ', resumes['embeddings'][i])
                    logging.debug(jobs['metadatas'][0][j])
                    logging.debug(jobs['metadatas'][0][j]['company'].replace("\n", ""))
                    postings += """<li><a href={} style="color: #007bff; text-decoration: none;">{}</a></li>""".format(jobs['metadatas'][0][j]['url'], jobs['metadatas'][0][j]['company'].replace("\n", ""))
                #print(test_email_template.format(postings))
                #send_email(receiver=receiver, html=build_template(job_html=postings))
    