import traceback
import requests
import re
import logging
import os 
import sys

from queue import Queue
from bs4 import BeautifulSoup


currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)


page_url = "https://jobs.apple.com/en-in/search?page={}"
job_url = "https://jobs.apple.com/en-in/details/{}"
html_dir = parentdir + "/apple/jobs/"
pattern = r"\b\d{" + str(9) + r"}\b"
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

def crawl_jobs(link:str, job_id:str=''):
    q:Queue = Queue()
    visited:set = load_visited_urls()    
    q.put(job_id)

    while not q.empty():
        jid = q.get()
        url = job_url.format(jid) if len(jid) > 0 else link
        page = download_html(url=url)
        if page:
            if len(jid) > 0: 
                write_html_page(job_id=jid, html_page=page)
                print('visited page: ', url)
            result:list[str] = find_matching_strings(page)
            for value in result:
                if check_valid_job_id(value) and not (value in visited):
                    q.put(value)
                    visited.add(value)
                    print('==>', value)


if __name__ == '__main__':
    cnt=1
    while cnt < 213:
        print("url:",page_url.format(cnt))
        crawl_jobs(link=page_url.format(cnt), job_id='')
        cnt += 1