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
google_html_jobs_dir = currentdir + '/jobs/html'
google_json_jobs_dir = currentdir + '/jobs/json'
google_job_url = "https://www.google.com/about/careers/applications/jobs/results/{}"

html_parser_prompt = '''
You are html parser. 
you here to retrieve job title, job location, job level (example Mid, Manager, Early or Advanced), job Minimum qualifications, job Preferred qualifications, about the job description, job Responsibilities text information from the given html page if present.
Provide the answer in below python parsable json string:
{"title": job title as string else empty string, "level": job level as string else empty string,"location": job location as string else empty string,"description": about job description as string else empty string,"salary": salary range as string else empty string,"key_qualifications": job Minimum qualifications as string else empty string, "preferred_qualifications": job preferred qualifications as string else empty string, "responsibilities": job Responsibilities as string else empty string}
Do not ask for other information. If you don't get information, return answer with empty json.
'''

html_parser_agent = ConversableAgent(
    name="html_parser",
    system_message=html_parser_prompt,
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1
)

def load_visited_files(dir=google_json_jobs_dir)-> set:
    visited:set = set()
    for file in os.listdir(dir):
        jid = file.replace('.json','')
        visited.add(jid)
        logging.debug('->',jid)
    return visited

def parse():
    visited:set = load_visited_files()
    failed_path:list = []
    for html_file_name in os.listdir(google_html_jobs_dir):

        file_name = html_file_name.replace('.html','')
        if file_name in visited:
            logging.info('visited: '+file_name)
            continue
        google_job_html_file_path = os.path.join(google_html_jobs_dir, html_file_name)
        page_str=''
        try:
            with open(google_job_html_file_path, 'r') as file:
                page_str = file.read()
            
            soup = BeautifulSoup(page_str, "html.parser")
            results = soup.find_all("div", attrs={'data-id': file_name})
            if not results:
                failed_path.append(google_job_html_file_path)
                continue
            html_str=str(results[0])

            reply = html_parser_agent.generate_reply(
                messages=[{"content": html_str, "role": "user"}]
            )

            logging.debug(reply)
            if reply:
                message = reply
                message = message.replace("```json",'')
                message = message.replace("```",'')
                job_json = json.loads(message)
                job_json['company'] = 'google'
                job_json['url'] = google_job_url.format(file_name)

                json_path = os.path.join(google_json_jobs_dir, file_name + '.json')
                with open(json_path, 'w') as file:
                    file.write(json.dumps(job_json))
                visited.add(file_name)
                logging.info('written: ' + json_path)
            else:
                failed_path.append(google_job_html_file_path)                
        except:
            failed_path.append(google_job_html_file_path)
            traceback.print_exc()
        
    if len(failed_path) > 0:
        logging.info('Failed path:')
        logging.info(failed_path)

if __name__ == '__main__':
    parse()