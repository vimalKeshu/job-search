import os
import google.generativeai as genai

from typing_extensions import TypedDict, List

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

def get_json_content(page_text, retry=3):
    json=None
    cnt=1
    while cnt < retry and not json:
        try:
            res = client.generate_content(prompt + page_text)
            json = res.text
        except Exception as e:
            print(str(e))
        cnt+=1
    return json 