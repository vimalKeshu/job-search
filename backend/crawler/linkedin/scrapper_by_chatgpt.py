import requests
import re
import os
import tiktoken

from openai import OpenAI
from pydantic import BaseModel
from bs4 import BeautifulSoup

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

prompt = '''You are a helpful linkedin html job page parser.Please extract the job related information.Do not ask for other information.
'''
MAX_TOKEN=128000
pattern = re.compile(r'\b\d{10}\b')
url = 'https://in.linkedin.com/jobs/search?keywords=&location=United%20States&geoId=103644278&f_TPR=r2592000&position=1&pageNum=0'
job_url = 'https://www.linkedin.com/jobs/view/{}'
urls=set()

def num_tokens(text: str, model: str = 'gpt-4o') -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

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

# Send a request to the LinkedIn page
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup:BeautifulSoup = BeautifulSoup(response.content, 'lxml')
    text = str(soup.find_all())
    #print(text)
    matches = pattern.findall(text)
    if matches:
        print('10-digit numbers found:')
        for match in matches:
            print(match)
            urls.add(job_url.format(match))
    else:
        print('No 10-digit numbers found.')    
    print('Total: ', len(urls))
    for url in urls:
        print(url)
        #res = requests.get(url)
        res = requests.get(job_url.format('3987630727'))

        sp:BeautifulSoup = BeautifulSoup(res.content, 'lxml')
        text = str(sp.find("div", attrs={'class':'details'}))
        # print("-----")
        # print(text)
        # print("-----")
        tokens = num_tokens(text=text)
        if tokens > MAX_TOKEN:
            raise Exception("Current token count:"+tokens
                            +". No. of token exceeded max token limit,"+MAX_TOKEN)
        completion = client.beta.chat.completions.parse(model=MODEL, 
                                               messages=[{"role": "system", "content": prompt},
                                                         {"role": "user", "content": 'html text:'+ text}],
                                               temperature=0,
                                               response_format=Job)
        job = completion.choices[0].message.parsed
        print('Tokens:'+str(tokens),job.model_dump_json())
        break
else:
    print(f'Failed to retrieve the page: {response.status_code}')

#input json token Tokens:28245
#output json token Tokens: 500
# output_json='''
# {"jobTitle":"Onboarding Specialist","company":{"name":"Eating Recovery Center","industry":"Mental Health Care","size":"51-200 employees","location":"United States"},"location":"United States","jobType":"Full-time","employmentType":"Full-time","experienceLevel":"Mid-Senior level","salary":{"amount":"$20.00 - $32.00","currency":"USD"},"jobFunction":"Human Resources","industry":"Mental Health Care","description":"ERC Pathlight is an innovative, rapidly growing clinical leader in the behavioral health sector. Founded in 2008 by pre-eminent psychiatrists and psychologists in the eating disorder space, ERC Pathlight now treats over 6,000 patients per year, operates more than 30 facilities in 9 states and delivers tele-healthcare to patients nationally. We offer the most comprehensive treatment program in the country for patients who struggle with eating disorders, mood and anxiety and trauma-related disorders.","responsibilities":"The Onboarding Specialist delivers a seamless and positive onboarding experience for the candidate/teammate. This person is key in the retention of our teammates. Onboard Specialist ensures all required pre-employment tasks are completed and the teammate is ready for Day 1. This role will partner and collaborate with cross-functional stakeholders such as Talent Acquisition, Payroll, HRIS, IT and Facilities for successful onboarding. Responsible for accurate teammate data in our HRIS system. Is an advocate for process improvement within the onboarding process, constantly seeking ways to improve to make it a better experience for candidates and teammates; increase turnover and efficiency. Supports various other people operations projects.","qualifications":{"required":"3+ years of experience in previous HR position with focus on onboarding, Exceptional attention to detail, highly organized, with the ability to prioritize, multi-task, and manage multiple deadlines, Resourceful problem-solving skills. Ability to troubleshoot issues independently and drive impactful solution, Strong Excel knowledge with ability to create reports and PowerPoint to create and present professional decks, Excellent written and verbal communication skills, Exceptional customer service skills","preferred":"Bachelors Degree, SHRM or PHR certificate"},"skills":["HRIS","Onboarding","Communication","Problem Solving","Excel"],"postedDate":"9 hours ago","applicationDeadline":"","benefits":"Competitive pay, comprehensive benefit plans, Generous Paid Time Off, 401(K) with company match and tuition reimbursement.","remoteWork":"No"}
# '''

# print('output token: ', num_tokens(text=output_json))