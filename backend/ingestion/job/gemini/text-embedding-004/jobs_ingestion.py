import os
import chromadb
import logging
import sys
import json
import pickle
import traceback
import tiktoken

from chromadb.api.types import GetResult
import google.generativeai as genai
from chromadb.api.types import QueryResult

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
parentdir = os.path.dirname(parentdir)
parentdir = os.path.dirname(parentdir)
parentdir = os.path.dirname(parentdir)
sys.path.append(parentdir)

print(currentdir)
print(parentdir)

DB_PATH = parentdir + "/storage/gemini/text-embedding-004/prod/chromadb"
if not os.path.exists(DB_PATH):
    raise Exception("Not able to find the path: "+DB_PATH)

print(DB_PATH)
company = ''

MAX_TOKENS = 8191
genai.configure(api_key=os.environ['GOOGLE_AI_API_KEY'])
TEXT_EMBEDDING_MODEL_NAME = "models/text-embedding-004"
GEMINI_FLASH_MODEL_NAME = "gemini-1.5-flash"
gemini_flash_model = genai.GenerativeModel(GEMINI_FLASH_MODEL_NAME)
chromadb_client = chromadb.PersistentClient(path=DB_PATH)
job_collection = chromadb_client.get_or_create_collection(name="job")


def num_tokens(text: str, model: str = TEXT_EMBEDDING_MODEL_NAME) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def get_embedding(text, model=TEXT_EMBEDDING_MODEL_NAME):
    """Return the embeddings of text."""
    text = text.replace("\n", " ")
    return (genai.embed_content(
                        model=model,
                        content=text,
                        task_type="retrieval_document")['embedding'])

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

def get_netflix_job_text(job_json:dict):
    text=""
    text+= 'title: ' + job_json['name']

    if 'locations' in job_json and len(job_json['locations']) > 1:
        text+= 'location: ' + (' and '.join(job_json['locations']))
    elif 'locations' in job_json and len(job_json['locations']) == 1 :
        text+= 'location: ' + job_json['location']

    if 'department' in job_json and len(job_json['department']) > 0:
        text+= 'department: ' + job_json['department']

    if 'work_type' in job_json:
        text+= 'work_type: ' + (', '.join(job_json.get['work_type']))    

    if 'business_unit' in job_json and len(job_json['business_unit']) > 0:
        text+= 'business_unit: ' + job_json['business_unit']

    text+= 'description: ' + job_json['job_description']
    text+= 'company: netflix'
    text+= 'url:' + job_json['canonicalPositionUrl']

    return text

def ingest_jobs(json_jobs_dirs):
    for json_jobs_dir in json_jobs_dirs:        
        try:
            if not os.path.exists(json_jobs_dir):
                raise Exception("Not able to find the path: "+json_jobs_dir)
            cnt = 0
            for file_name in os.listdir(json_jobs_dir):
                job_id = file_name.replace('.json', '')
                if is_job_stored(job_id):
                    continue
                job_json_file_path = os.path.join(json_jobs_dir, job_id + '.json')
                try:
                    job_json={}
                    with open(job_json_file_path, 'r') as file:
                        job_json = json.loads(file.read())

                    job_text=""
                    if not 'netflix' in job_json_file_path:
                        for key in job_json:
                            job_text+=key+":"+job_json[key]+" "
                    else:
                        job_text=get_netflix_job_text(job_json=job_json)
                        job_json['company'] = 'netflix'
                        job_json['url'] = job_json.get('canonicalPositionUrl', 
                                                       "https://netflix.eightfold.ai/api/apply/v2/jobs/{}".format(job_id))    
                        job_json['title'] = job_json['name']

                    job_embedding=get_embedding(job_text)
                    print(job_embedding)
                    store_jobs_data(embedding=job_embedding,
                                    doc=json.dumps(job_json),
                                    id=job_id,
                                    metadata={"company": job_json['company'], 
                                            "url": job_json['url'], 
                                            "title": job_json['title']})
                    print('count: ',cnt,',inserted: ',job_json_file_path) 
                    cnt = cnt + 1         
                except:
                    print('failed at json path: ', job_json_file_path)
                    traceback.print_exc()
                    break
            print(cnt)            
        except:
            traceback.print_exc()


def query(question:str, size:int=10):
    jobs:list = []
    if len(question.strip()) == 0:
        return jobs
    
    question_embedding = get_embedding(text=question)
    result = job_collection.query(query_embeddings=[question_embedding],
                                 n_results=size,
                                 include=['metadatas', 'distances'])
    # print(result)

    for i in range(len(result['ids'])):
        for j in range(len(result['metadatas'][i])):
            jobs.append({   
                            'id': result['ids'][i][j],
                            'title': result['metadatas'][i][j]['title'],
                            'company': result['metadatas'][i][j]['company'],
                            'url': result['metadatas'][i][j]['url'],
                            'distance': result['distances'][i][j]
                        })

    jobs = sorted(jobs, key=lambda job: job['distance'])        

    return jobs

def query_reranking(question:str, size:int=10):
    prompt_part_1 = '''I have a list of job description. I want you to rerank this list based on the user's query, taking into account everything mentioned in job description. Prioritize results that closely match the user's query, considering keywords, skills, experience, salary and location requirements.
    **User Query:** {}
    **Job List:**

    '''.format(question)
    prompt_part_3 = ''' **Rerank this list according to the user's query, providing the new order from most relevant to least relevant. 
    Output the reranked list as a RFC8259 compliant JSON format which should follow below json schema without deviation:
    {"url": job url as string}
    Dont include any other text in the response other than json.
    **
    '''
    jobs:list = []
    if len(question.strip()) == 0:
        return jobs
    
    try:
        question_embedding = get_embedding(text=question)
        result = job_collection.query(query_embeddings=[question_embedding],
                                    n_results=size,
                                    include=['metadatas', 'distances', 'documents'])
        # print(result)
        prompt_part_2=""
        jobs_dict:dict = {}
        for i in range(len(result['ids'])):
            for j in range(len(result['metadatas'][i])):
                job = ({   
                                'id': result['ids'][i][j],
                                'title': result['metadatas'][i][j]['title'],
                                'company': result['metadatas'][i][j]['company'],
                                'url': result['metadatas'][i][j]['url'],
                                'distance': result['distances'][i][j]
                    })
                jobs.append(job)
                prompt_part_2 += str(j+1) + ". **Job Description:** " + result['documents'][i][j] + "\n"
                jobs_dict[job['url']] = job        
        try:
            #print(jobs_dict, jobs_dict)
            final_prompt = prompt_part_1 + "\n" + prompt_part_2+ "\n" + prompt_part_3
            #print(final_prompt)
            response = gemini_flash_model.generate_content(final_prompt,generation_config=genai.types.GenerationConfig(temperature=0.0))
            print(response.text)
            reranked_jobs_list = json.loads(response.text.replace('```json','').replace('```',''))
            print(reranked_jobs_list)    
            reranked_jobs = []
            for j in reranked_jobs_list:
                print('reranked job', j)
                job = jobs_dict.get(j['url'], None)
                if job:
                    reranked_jobs.append(job)
            print('reranked jobs', reranked_jobs)
            return reranked_jobs
        except:
            traceback.print_exc()
        jobs = sorted(jobs, key=lambda job: job['distance'])
    except:
        traceback.print_exc()
    return jobs

if __name__ == '__main__':
    # ingest_jobs()
    print(job_collection.count())
    jobs = query_reranking(question="give me devops platform engineering jobs located only in london.", size=5)
    for job in jobs:
        print(job)
    #     print(job['title'], job['company'], job['url'])
        # print(job['distance'], job['url'])