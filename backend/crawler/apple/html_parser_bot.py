import os
import json
import sys
import logging
import traceback

from autogen import ConversableAgent
from bs4 import BeautifulSoup

# Configure console logging
logging.basicConfig(
    level=logging.INFO,  # Set logging level to DEBUG
    format='%(asctime)s %(levelname)s: %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format for the timestamp
)

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# llm_config = {"model": "gpt-3.5-turbo"}
llm_config = {"model": "gpt-4o-mini"}
apple_html_jobs_dir = currentdir + '/jobs/html'
apple_json_jobs_dir = currentdir + '/jobs/json'
apple_job_url = "https://jobs.apple.com/en-in/details/{}"

html_parser_prompt = '''
You are html parser. 
you here to retrieve job title, job Summary, job Description, job Key Qualifications, job Preferred Qualifications, job Education & Experience, job Additional Requirements, job Pay & Benefits information from the given html page if present.
Provide the answer in below python parsable json string:
{"title": job title as string else empty string, "summary": job summary as string else empty string, "description", job description as string else empty string, "key_qualifications": job Key Qualifications as string else empty string, "preferred_qualifications": job preferred qualifications as string else empty string, "education_experience": job Education & Experience as string else empty string, "additional_requirements": job Additional Requirements as string else empty string, "pay_benefits":job Pay and Benefits as string else empty string}
Do not ask for other information. If you don't get information, return answer with empty json.
'''

html_parser_agent = ConversableAgent(
    name="html_parser",
    system_message=html_parser_prompt,
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER"
)

def load_visited_files(dir=apple_json_jobs_dir)-> set:
    visited:set = set()
    for file in os.listdir(dir):
        jid = file.replace('.json','')
        visited.add(jid)
        #print('->',jid)
    return visited

def parse():
    visited:set = load_visited_files()
    failed_path:list = []
    for html_file_name in os.listdir(apple_html_jobs_dir):

        #print(file)
        file_name = html_file_name.replace('.html','')
        if file_name in visited:
            print('visited:',file_name)
            continue
        apple_job_html_file_path = os.path.join(apple_html_jobs_dir, html_file_name)
        page_str=''
        try:
            with open(apple_job_html_file_path, 'r') as file:
                page_str = file.read()
            #print(html_str)
            
            soup = BeautifulSoup(page_str, "html.parser")
            results = soup.find_all("section", attrs={'id': 'app'})
            #print(str(results[0]))
            html_str=str(results[0])

            reply = html_parser_agent.generate_reply(
                messages=[{"content": html_str, "role": "user"}]
            )

            message = reply.replace("```json",'')
            message = message.replace("```",'')
            #print(message)
            job_json = json.loads(message)
            #job_json = reply
            job_json['company'] = 'apple'
            job_json['url'] = apple_job_url.format(file_name)

            json_path = os.path.join(apple_json_jobs_dir, file_name + '.json')
            with open(json_path, 'w') as file:
                file.write(json.dumps(job_json))
            visited.add(file_name)
            print('written:', json_path)            
        except:
            failed_path.append(apple_job_html_file_path)
            traceback.print_exc()
        
    if len(apple_job_html_file_path) > 0:
        print('Failed path:')
        print(failed_path)

if __name__ == '__main__':
    parse()