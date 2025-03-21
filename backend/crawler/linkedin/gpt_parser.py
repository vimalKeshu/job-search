import os

from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

prompt = '''You are a helpful linkedin html job page parser.Please extract the job related information.Do not ask for other information.
'''

class Company(BaseModel):
    name: str
    industry: str
    size: str
    location: str

class Salary(BaseModel):
    amount: str
    currency: str

class Qualifications(BaseModel):
    required: str
    preferred: str

class Job(BaseModel):
    jobTitle: str
    company: Company
    location: str
    jobType: str
    employmentType: str
    experienceLevel: str
    salary: Salary
    jobFunction: str
    industry: str
    description: str
    responsibilities: str
    qualifications: Qualifications
    skills: list[str]
    postedDate: str
    applicationDeadline: str
    benefits: str
    remoteWork: str

def get_json_content(page_text, retry=3):
    json=None
    cnt=1
    while cnt < retry and not json:
        try:
            completion = client.beta.chat.completions.parse(model=MODEL, 
                                                messages=[{"role": "system", "content": prompt},
                                                            {"role": "user", "content": 'html text:'+ page_text}],
                                                temperature=0,
                                                response_format=Job)
            job = completion.choices[0].message.parsed
            json = job.model_dump_json()
            # json = completion.choices[0].message
        except Exception as e:
            print(str(e))
        cnt+=1
    return json 