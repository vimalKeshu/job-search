import os
import chromadb
import traceback
import json
import google.generativeai as genai

from chromadb.api.types import QueryResult


genai.configure(api_key=os.environ['GOOGLE_AI_API_KEY'])

# constants
EMBEDDING_MODEL = "models/text-embedding-004"
GEMINI_FLASH_MODEL_NAME = "gemini-1.5-flash"
DB_PATH = os.getenv("CHROMA_DB_PATH")
print("DB PATH: ", DB_PATH, os.path.exists(DB_PATH))

# clients
gemini_flash_model = genai.GenerativeModel(GEMINI_FLASH_MODEL_NAME)
chromadb_client = chromadb.PersistentClient(path=DB_PATH)
jobs_collection = chromadb_client.get_or_create_collection(name="job")


def get_embedding(text, model=EMBEDDING_MODEL):
    """Return the embeddings of text."""
    text = text.replace("\n", " ")
    return (genai.embed_content(
                        model=model,
                        content=text,
                        task_type="retrieval_document")['embedding'])

def query_jobs_data(embedding, size:int) -> QueryResult:
    """Query job data"""
    return jobs_collection.query(query_embeddings=[embedding],
                                 n_results=size,
                                 include=['metadatas', 'distances', 'documents'])

def query(question:str, criteria_distance:float=0.5, size:int=5):
    jobs:list = []
    if len(question.strip()) == 0:
        return jobs
    
    question_embedding = get_embedding(text=question)
    result = query_jobs_data(question_embedding, size=size)
    #print(result)

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

def query_reranking(question: str, size: int = 5):
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
    jobs: list = []
    reranked_jobs: list = []
    final_jobs:list = []
    if len(question.strip()) == 0:
        return jobs

    try:
        question_embedding = get_embedding(text=question)
        result = query_jobs_data(embedding=question_embedding, size=size)

        # print(result)
        prompt_part_2 = ""
        jobs_dict: dict = {}
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
                prompt_part_2 += str(j +
                                     1) + ". **Job Description:** " + result[
                                         'documents'][i][j] + "\n"
                jobs_dict[job['url']] = job
        try:
            #print(jobs_dict, jobs_dict)
            final_prompt = prompt_part_1 + "\n" + prompt_part_2 + "\n" + prompt_part_3
            #print(final_prompt)
            response = gemini_flash_model.generate_content(
                final_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0))
            reranked_jobs_list = json.loads(
                response.text.replace('```json', '').replace('```', ''))
            #print(reranked_jobs_list)
            for j in reranked_jobs_list:
                # print('reranked job', j)
                job = jobs_dict.get(j['url'], None)
                if job:
                    reranked_jobs.append(job)
            print('reranked jobs', reranked_jobs)
        except:
            traceback.print_exc()

        temp_jobs = reranked_jobs if len(reranked_jobs)>0 else sorted(jobs, key=lambda job: job['distance'])
        for j in temp_jobs:
            del j['distance']
            final_jobs.append(j)
    except:
        traceback.print_exc()
    return final_jobs


if __name__=='__main__':
    jobs = query(question="give me google software engineering jobs located only in india.",)
    for job in jobs:
        # print(job['title'], job['company'], job['distance'], job['url'])
        print(job)
    # print(job_collection.count())