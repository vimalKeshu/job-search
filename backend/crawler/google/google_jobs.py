import requests
import re
import os 
import sys

from queue import Queue


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


page_url = "https://www.google.com/about/careers/applications/jobs/results?page="
job_url = "https://www.google.com/about/careers/applications/jobs/results/"
html_dir = parentdir + "/google/jobs/"
pattern = r"\b\d{" + str(18) + r"}\b"
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
    
def find_matching_strings(pattern, text):
    # Find all matches in the text
    matches = regex.findall(text)
    return matches

def check_valid_job_id(job_id:str)->bool:
    for ch in job_id:
        if not ch.isdigit():
            return False
    return True

def crawl_google_jobs(link:str, job_id:str=''):
    q:Queue = Queue()
    visited:set = load_visited_urls()    
    q.put(job_id)

    while not q.empty():
        jid = q.get()
        url = job_url + jid if len(jid) > 0 else link
        page = download_html(url=url)
        print('visited page: ', url)
        if page:
            if len(jid) > 0: 
                write_html_page(job_id=jid, html_page=page)
            result:list[str] = find_matching_strings(pattern, page)
            temp_job_id=None
            for value in result:
                tokens = value.split(';')
                if (len(tokens) == 3 and tokens[1]!=job_id and check_valid_job_id(tokens[1])):
                    #print("https://www.google.com/about/careers/applications/jobs/results/",tokens[1],'google')
                    temp_job_id=tokens[1]
                elif check_valid_job_id(value):
                    #print("https://www.google.com/about/careers/applications/jobs/results/",value,'google')
                    temp_job_id=value
                if temp_job_id and temp_job_id not in visited:
                    q.put(temp_job_id)
                    visited.add(temp_job_id)


if __name__ == '__main__':
    cnt=1
    while cnt < 126:
        crawl_google_jobs(link=page_url+str(cnt), job_id='')
        cnt += 1