import os
import chromadb
import logging
import sys
import json
import pickle
import traceback

from chromadb.api.types import GetResult


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.append(parentdir)

# print(currentdir)
# print(parentdir)

DB_PATH = parentdir + "/storage/prod/chromadb"
company = 'meta'
json_jobs_dir = parentdir + '/crawler/' + company + '/jobs/json'
embedding_dir = parentdir + '/crawler/' + company + '/jobs/embedding/text-embedding-3-large'
chromadb_client = chromadb.PersistentClient(path=DB_PATH)
job_collection = chromadb_client.get_or_create_collection(name="job")


def store_jobs_data(embedding, doc, id, metadata):
    """Store jobs data in chromadb."""
    job_collection.upsert(embeddings=[embedding],
                           documents=[doc],
                           ids=[id],
                           metadatas=[metadata])

def is_job_stored(id):
    """is job link visited before."""
    results: GetResult = job_collection.get(ids=[id], include=[])
    return len(results["ids"]) > 0

def ingest_jobs():
    failed_insert = []
    cnt = 0
    for job_id in os.listdir(embedding_dir):
        if is_job_stored(job_id):
            continue
        try:
            embedding_file_path = os.path.join(embedding_dir, job_id)
            job_json_file_path = os.path.join(json_jobs_dir, job_id + '.json')

            job_json={}
            with open(job_json_file_path, 'r') as file:
                job_json = json.loads(file.read())
            
            job_embedding=None
            with open(embedding_file_path, 'rb') as file:
                job_embedding = pickle.loads(file.read())
            
            # print(job_json)
            # print(job_embedding)

            store_jobs_data(embedding=job_embedding,
                            doc=json.dumps(job_json),
                            id=job_id,
                            metadata={"company": job_json['company'], 
                                    "url": job_json['url'], 
                                    "title": job_json['title']})
            print('inserted: '+embedding_file_path) 
            cnt += 1           
        except:
            failed_insert.append(job_id)
            traceback.print_exc()
    
    print(cnt)

if __name__ == '__main__':
    ingest_jobs()