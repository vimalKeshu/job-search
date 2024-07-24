import traceback
import requests
import re
import logging

from bs4 import BeautifulSoup

base_url = "https://www.google.com/about/careers/applications/jobs/results/"
pattern = r"\b\d{" + str(18) + r"}\b"
regex = re.compile(pattern)

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

def crawl_google_jobs(link:str, job_id:str):
    url = link + job_id.strip()
    page = download_html(url)
    #print(page)
    if page:
        result:list[str] = find_matching_strings(pattern, page)
        for value in result:
            print(value)
            tokens = value.split(';')
            if (len(tokens) == 3 and tokens[1]!=job_id and check_valid_job_id(tokens[1])):
                print("https://www.google.com/about/careers/applications/jobs/results/",tokens[1],'google')
            elif check_valid_job_id(value):
                print("https://www.google.com/about/careers/applications/jobs/results/",value,'google')                

if __name__ == '__main__':
    crawl_google_jobs(link='https://www.google.com/about/careers/applications/jobs/results/', 
                      job_id='136449007806227142')