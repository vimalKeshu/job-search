'''
    Netflix uses eightfold.ai as its career site. 
    eightfold.ai posts more job ids on recommendations and which can be extracted using below url

    below is the canonical url to fetch the job page:
    https://netflix.eightfold.ai/careers/job/790298013725

'''
import requests
import re
import os 
import sys
import logging
import time

from queue import Queue

# Configure console logging
logging.basicConfig(
    level=logging.INFO,  # Set logging level to info
    format='%(asctime)s %(levelname)s: %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format for the timestamp
)

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


page_url = "https://netflix.eightfold.ai/api/apply/v2/jobs/{}/jobs"
job_url = "https://netflix.eightfold.ai/api/apply/v2/jobs/{}"
html_dir = parentdir + "/netflix/jobs/json"
pattern = r"\b\d{" + str(12) + r"}\b"
regex = re.compile(pattern)


def load_visited_urls(dir=html_dir)-> set:
    visited:set = set()
    for file in os.listdir(dir):
        jid = file.replace('.json','')
        visited.add(jid)
        logging.debug('->'+jid)
    return visited

def write_page(job_id:str, page_data:str, page_type=".json", dir=html_dir):
    with open(html_dir + job_id + page_type, 'w') as file:
        file.write(page_data)

def download_url(url):
    try:
        response = requests.get(url)
        # Raise an exception for bad status codes (e.g., 404, 500)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading HTML: {e}")
        return None
    
def find_matching_strings(pattern, text):
    # Find all matches in the text
    matches = regex.findall(text)
    return matches

def check_valid_job_id(job_id:str)->bool:
    for ch in job_id:
        if not ch.isdigit():
            return False
    return True

def crawl_jobs(url):
    q:Queue = Queue() 
    visited:set = load_visited_urls()    

    page_json = download_url(url=url)
    logging.debug(page_json)
    
    result:list[str] = find_matching_strings(pattern, page_json)
    for value in result:
        if check_valid_job_id(value) and not (value in visited):
            q.put(value)
            logging.debug(value)

    while not q.empty():
        jid = q.get()
        url = job_url.format(jid)
        page_json = download_url(url=url)
        if page_json and page_json.strip() != '{}':
            if not (jid in visited):
                write_page(job_id=jid, page_data=page_json)
                logging.info('visited page: '+url)

            result:list[str] = find_matching_strings(pattern, page_json)
            for value in result:
                if check_valid_job_id(value) and not (value in visited):
                    q.put(value)
                    visited.add(value)
                    logging.debug(value)

if __name__ == '__main__':

    jids:set = load_visited_urls()    
    for jid in jids:
        logging.info('url: '+page_url.format(jid))
        crawl_jobs(url=page_url.format(jid))
        time.sleep(60)
    