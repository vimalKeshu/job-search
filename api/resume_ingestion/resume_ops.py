# imports
import openai  # for generating embeddings
import json

from common.constant import *
from chromadb.api.types import GetResult


def get_embedding(text, model=EMBEDDING_MODEL):
    """Return the embeddings of text."""
    try:
        # text = text.replace("\n", " ")
        return (openai_client.embeddings.
                create(input=[text], model=model).data[0].embedding)
    except openai.BadRequestError as e:
        print(e)

def store_resume_data(embedding, doc, id, metadata):
    """Store resume data in chromadb."""
    resume_collection.upsert(embeddings=[embedding],
                             documents=[doc],
                             ids=[id],
                             metadatas=[metadata])

def store_resume_detail_data(embedding, doc, id, metadata):
    """Store resume detail data in chromadb."""
    resume_detail_collection.upsert(embeddings=[embedding],
                                    documents=[doc],
                                    ids=[id],
                                    metadatas=[metadata])


def query_message(resume) -> str:
    """Return a message for GPT, with relevant source texts."""
    message = """Extract below json information from resume text and only reply the below json in response.
        json: {'name': 'resume owner name', 'e-mail':'email id', 'resume_detail': 'write paragraph which include resume summary, skills and tools'} 
        resume:"""
    return message + resume


def ask(
    query: str,
    model: str = GPT_MODEL,
    print_message: bool = True,
    token_budget: int = 4096 - 500,
) -> str:
    """Answers a query using GPT and 
       a chroma db stored jobs data.
    """
    message = query_message(query)
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

def extract_and_store_resume_metadata():
        resumes: GetResult = resume_collection.get(limit=resume_collection.count())
        all_resumes = set()
        # get all unique resumes from collection
        for i in range(0, len(resumes['documents'])):
            all_resumes.add((resumes['metadatas'][i]['name'],
                            resumes['metadatas'][i]['pages']))
            print('name: ', resumes['metadatas'][i]['name'])

        results = {}
        # Iterate each resume by page
        for rs, pages in all_resumes:
            results[rs] = ''
            for i in range(0, pages):
                id = rs+'_'+str(i)
                print('file name: ', id)
                user_resume: GetResult = resume_collection.get(
                    limit=1, ids=[id])
                # print(user_resume['metadatas'][0]['name'])
                # print(len(user_resume['metadatas']))
                results[rs] = results[rs] + ' ' + (user_resume['documents'][0])
        for rs in results:
            print(rs, results[rs])
            print('-----------------------------')
            json_res = ask(query=results[rs])
            json_res = json.loads(json_res)
            print(json_res['resume_detail'])
            embedding = get_embedding(
                text=json_res['resume_detail'], model=EMBEDDING_MODEL)
            print('---->', embedding)
            store_resume_detail_data(id=rs,
                                    embedding=embedding,
                                    doc=json_res['resume_detail'],
                                    metadata={'name': json_res['name'], 'email': json_res['e-mail']})
