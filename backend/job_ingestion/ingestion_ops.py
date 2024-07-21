# imports
import traceback
import tiktoken  # for computing tokens
import requests

from chromadb.api.types import GetResult
from bs4 import BeautifulSoup

from common.constant import *


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


def store_jobs_data(embedding, doc, id, metadata):
    """Store jobs data in chromadb."""
    jobs_collection.upsert(embeddings=[embedding],
                           documents=[doc],
                           ids=[id],
                           metadatas=[metadata])


def is_link_visited(link):
    """is job link visited before."""
    results: GetResult = jobs_collection.get(ids=[link], include=[])
    return len(results["ids"]) > 0


def get_gcp_job_document(job_id, link):

    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    # results = soup.find_all("div", attrs={"class": "bE3reb"})
    # for res in results:
    #     res.decompose()

    results = soup.find_all("div", attrs={'data-id': job_id})
    print("No. of results: ", len(results))
    job_element = results[0]
    print(str(job_element))
    job_description = str(job_element)
    token = num_tokens(text=job_description)
    print('no. of token:', token)
    return (job_description, token)


def ingest_gcp_jobs(file_path: str):
    with open(file_path) as file:
        i = 0
        for line in file:
            if i == 0:
                print('ignore header line:', line)
            else:
                (link, id, company) = line.split(",")
                url = link+'/'+id
                if not is_link_visited(link=url):
                    try:
                        print(link, id, company)
                        (doc, token) = get_gcp_job_document(
                            link=url, job_id=id)
                        embedding = get_embedding(text=doc)
                        store_jobs_data(embedding=embedding,
                                        doc=doc,
                                        id=url,
                                        metadata={"company": company, "job_id": id, "token": token, "url": url})
                        print('ingested job:', id)
                    except:
                        traceback.print_exc()

                else:
                    print('job already exist:', id)
            i = i+1

if __name__ == "__main__":
    ingest_gcp_jobs(file_path= './data/job_links.csv')