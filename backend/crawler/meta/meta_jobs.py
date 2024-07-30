'''
    Meta uses graphql for loading the list of jobs.
    As there were only 1K jobs, it loaded entire jobs thumpnail in single request as json.
    I downloaded json manually and extracted the job ids from it.
    Now, process will crawl for each job page html source.
'''
import requests
import re
import os 
import sys

from queue import Queue


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


page_url = "https://www.metacareers.com/jobs"
job_url = "https://www.metacareers.com/jobs/{}"
html_dir = parentdir + "/meta/jobs/"
pattern = r"\b\d{" + str(15) + r"}\b"
regex = re.compile(pattern)


def load_visited_urls(dir=html_dir)-> set:
    visited:set = set()
    for file in os.listdir(dir):
        jid = file.replace('.html','')
        visited.add(jid)
        print('->',jid)
    return visited

def write_html_page(job_id:str, html_page:str, dir=html_dir):
    with open(html_dir + job_id + ".html", 'w') as file:
        file.write(html_page)

def download_html(url):
    try:
        response = requests.get(url)
        # Raise an exception for bad status codes (e.g., 404, 500)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading HTML: {e}")
        return None
    
def find_matching_strings(text):
    # Find all matches in the text
    matches = regex.findall(text)
    return matches

def check_valid_job_id(job_id:str)->bool:
    for ch in job_id:
        if not ch.isdigit():
            return False
    return True

def crawl_jobs(jobid_json_filepath):
    q:Queue = Queue() 
    visited:set = load_visited_urls()    

    job_str = ""
    with open(jobid_json_filepath, 'r') as file:
         job_str = file.read()

    result:list[str] = find_matching_strings(job_str)

    for value in result:
        if check_valid_job_id(value):
            q.put(value)

    while not q.empty():
        jid = q.get()
        url = job_url.format(jid)
        page = download_html(url=url)
        if page:
            write_html_page(job_id=jid, html_page=page)
            print('visited page: ', url)
            result:list[str] = find_matching_strings(page)
            for value in result:
                if check_valid_job_id(value) and not (value in visited):
                    q.put(value)
                    visited.add(value)
                    print('==>', value)

if __name__ == '__main__':
    jobid_json_filepath = currentdir + "/jobids.json"
    if os.path.exists(jobid_json_filepath):
        crawl_jobs(jobid_json_filepath=jobid_json_filepath)
    