import requests
import os
import time
import sys
import json
import traceback
import tiktoken
import copy
import google.generativeai as genai

from typing_extensions import TypedDict, List
from bs4 import BeautifulSoup
from pydantic import BaseModel
from queue import Queue
from multiprocessing import Process

genai.configure(api_key=os.environ['GOOGLE_AI_API_KEY'])
MODEL = "gemini-1.5-flash"

prompt = '''You are a helpful linkedin html job page parser.
Please extract the job related information from given html string.
Do not ask for other information.
***
Example json output:
{
    "jobTitle": "Onboarding Specialist",
    "company": {
      "name": "Eating Recovery Center",
      "industry": "Mental Health Care",
      "size": "51-200 employees",
      "location": "United States"
    },
    "location": "United States",
    "jobType": "Full-time",
    "employmentType": "Full-time",
    "experienceLevel": "Mid-Senior level",
    "salary": {
      "amount": "$20.00 - $32.00",
      "currency": "USD"
    },
    "jobFunction": "Human Resources",
    "industry": "Mental Health Care",
    "description": "ERC Pathlight is an innovative, rapidly growing clinical leader in the behavioral health sector. Founded in 2008 by pre-eminent psychiatrists and psychologists in the eating disorder space, ERC Pathlight now treats over 6,000 patients per year, operates more than 30 facilities in 9 states and delivers tele-healthcare to patients nationally. We offer the most comprehensive treatment program in the country for patients who struggle with eating disorders, mood and anxiety and trauma-related disorders.",
    "responsibilities": "The Onboarding Specialist delivers a seamless and positive onboarding experience for the candidate/teammate. This person is key in the retention of our teammates. Onboard Specialist ensures all required pre-employment tasks are completed and the teammate is ready for Day 1. This role will partner and collaborate with cross-functional stakeholders such as Talent Acquisition, Payroll, HRIS, IT and Facilities for successful onboarding. Responsible for accurate teammate data in our HRIS system. Is an advocate for process improvement within the onboarding process, constantly seeking ways to improve to make it a better experience for candidates and teammates; increase turnover and efficiency. Supports various other people operations projects.",
    "qualifications": {
      "required": "3+ years of experience in previous HR position with focus on onboarding, Exceptional attention to detail, highly organized, with the ability to prioritize, multi-task, and manage multiple deadlines, Resourceful problem-solving skills. Ability to troubleshoot issues independently and drive impactful solution, Strong Excel knowledge with ability to create reports and PowerPoint to create and present professional decks, Excellent written and verbal communication skills, Exceptional customer service skills",
      "preferred": "Bachelors Degree, SHRM or PHR certificate"
    },
    "skills": [
      "HRIS",
      "Onboarding",
      "Communication",
      "Problem Solving",
      "Excel"
    ],
    "postedDate": "9 hours ago",
    "applicationDeadline": "",
    "benefits": "Competitive pay, comprehensive benefit plans, Generous Paid Time Off, 401(K) with company match and tuition reimbursement.",
    "remoteWork": "No"
}
***
html string:
'''

class Company(TypedDict):
    name: str
    industry: str
    size: str
    location: str

class Salary(TypedDict):
    amount: str
    currency: str

class Qualifications(TypedDict):
    required: str
    preferred: str

class Job(TypedDict):
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
    skills: List[str]
    postedDate: str
    applicationDeadline: str
    benefits: str
    remoteWork: str

client = genai.GenerativeModel(MODEL, 
                               generation_config={"response_mime_type": "application/json", 
                                                  "response_schema": Job,
                                                  "temperature":0.0})
class Config(BaseModel):
    main_page:str
    job_page:str
    job_id_digit:str
    
class LinkedinParserConfig(BaseModel):
    config:Config
    html_dir:str
    json_dir:str
    visited_ids:set = set()
    non_visited_ids:set = set()

def num_tokens(text: str, model: str = 'gpt-4o') -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def download_job_tag(url, retry=5):
    text=None
    cnt=0
    while cnt < retry and not text:
        res = requests.get(url=url)
        if res.status_code == 404:
            break
        elif res.status_code == 429:
            time.sleep(1)
        elif res.status_code != 200:
            print(url +" ->  "+ str(res.status_code))
        else:
            sp:BeautifulSoup = BeautifulSoup(res.content, 'lxml')
            text = str(sp.find("div", attrs={'class':'details'}))
        cnt+=1
    return text

def load_visited_job_ids(config:LinkedinParserConfig):
    for file in os.listdir(config.json_dir):
        jid = file.replace('.json','')
        config.visited_ids.add(jid)
    print('Total visited ids: '+ str(len(config.visited_ids)))

def load_non_visited_job_ids(config:LinkedinParserConfig):
    config.non_visited_ids.clear()
    for file in os.listdir(config.html_dir):
        jid = file.replace('.html','')
        if not (jid in config.visited_ids):
            config.non_visited_ids.add(jid)
    print('Total non visited ids: '+ str(len(config.non_visited_ids)))

def write_job_data(path:str, data:dict):
    with open(path, 'w') as file:
        file.write(json.dumps(data))

def get_json_content(page_text, retry=3):
    json=None
    cnt=1
    while cnt < retry and not json:
        try:
            res = client.generate_content(prompt + page_text)
            json = res.text
        except:
            traceback.print_exec()
        cnt+=1
    return json          

def traverse_web(config:LinkedinParserConfig, id=1):
    q:Queue = Queue()
    for __jid in config.non_visited_ids:
        q.put(__jid)
    
    max_input_token= 0
    max_output_token= 0

    while not q.empty():
        job_id = q.get()

        page_text = download_job_tag(url=config.config.job_page+'/'+job_id)

        if page_text:
            data = get_json_content(page_text=page_text)
            if data:
                try:
                    job_json = json.loads(data)
                    job_json['url'] = config.config.job_page + '/' + job_id
                    job_json_path = os.path.join(config.json_dir, job_id + '.json')
                    write_job_data(path=job_json_path, data=job_json)

                    max_input_token = max(max_input_token, num_tokens(text=page_text))
                    max_output_token = max(max_output_token, num_tokens(text=json.dumps(job_json)))

                    print('worker:' + str(id), 
                          job_json_path, 'Total downloaded ids: '+ str(len(config.visited_ids)))
                    print('input tokens: '+ str(max_input_token),
                          'output tokens: '+ str(max_output_token))
                    config.visited_ids.add(job_id)
                except Exception as e:
                    print('worker:' + str(id), config.config.job_page+'/'+job_id)
                    print('worker:' + str(id), str(e))
            else:
                print('worker:' + str(id), 'Not able to parse json data for url:'+ (config.config.job_page+'/'+job_id))
        else:
            print('worker:' + str(id), 'Not able to download html for url:'+ (config.config.job_page+'/'+job_id))

        if q.qsize() < 2:
            load_non_visited_job_ids(config=config)
            for __jid in config.non_visited_ids:
                q.put(__jid)


if '__main__' == __name__:
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

    config_json_path = currentdir + '/config.json'
    json_dir_path = currentdir + "/jobs/2024-08-22/json"
    html_dir_path = currentdir + "/jobs/2024-08-22/html"

    print(config_json_path)
    print(json_dir_path)
    print(html_dir_path)

    if not (os.path.exists(config_json_path) and 
        os.path.exists(json_dir_path) and 
        os.path.exists(html_dir_path)):
        raise Exception("Path not found")

    config_json=None
    with open(config_json_path, 'r') as file:
        config_json = json.load(file)
    
    if not config_json:
        raise Exception('Not able to load the config json from given path: '+config_json_path)
    
    # Todo: create html directory if not present
    config = LinkedinParserConfig(config=Config(**config_json), 
                                  html_dir=html_dir_path,
                                  json_dir=json_dir_path)

    # while True:
    try:
        load_visited_job_ids(config=config)
        load_non_visited_job_ids(config=config)
        traverse_web(config=config)
        time.sleep(60*5)
    except Exception as e:
        print("error: ", str(e))
    # try:
    #     load_non_visited_job_ids(config=config)
    #     non_visited_ids_list = list(config.non_visited_ids)
    #     lists:list=[]
    #     processes:list = []
    #     d = int(len(non_visited_ids_list)/4)
    #     cnt=0

    #     for i in range(1,4):
    #         print(cnt, cnt+d)
    #         lists.append(non_visited_ids_list[cnt:cnt+d])
    #         cnt += d + 1
    #     print(cnt, len(non_visited_ids_list))
    #     lists.append(non_visited_ids_list[cnt:])

    #     i=1
    #     for list in lists:
    #         cc:LinkedinParserConfig = copy.deepcopy(config)
    #         cc.non_visited_ids.update(list)
            
    #         process = Process(target=traverse_web, args=(cc, i))
    #         processes.append(process)
    #         process.start()
    #         i+=1

    #     # for __jid in config.visited_ids:
    #     #     config.seed_ids.add(__jid)
    #     #     traverse_web(config=config) 
    #     #     config.seed_ids.clear()  

    #     # Wait for all processes to finish
    #     for process in processes:
    #         process.join()
    
    #     print('All processes finished')
    # except Exception as e:
    #     print("error: ", str(e))   
