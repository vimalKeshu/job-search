import requests
import re
import os
import json
import sys
import time
import time
import copy

from bs4 import BeautifulSoup
from pydantic import BaseModel
from queue import Queue
from re import Pattern


class Config(BaseModel):
    main_page:str
    job_page:str
    job_id_digit:str
    company_url:list[str]
    
class LinkedinParserConfig(BaseModel):
    config:Config
    html_dir:str
    pattern:Pattern
    scrap_further:bool = False
    seed_ids:set = set()
    visited_ids:set = set()

def write_job_id_as_file(config:LinkedinParserConfig, job_id:str):
    with open(os.path.join(config.html_dir,job_id), 'w') as file:
        pass

def download_html_page(url, retry=5):
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
            text = str(sp.find_all())
        cnt+=1
    return text    

def load_visited_job_ids(config:LinkedinParserConfig):
    for file in os.listdir(config.html_dir):
        jid = file.replace('.html','')
        config.visited_ids.add(jid)
    print('Total visited ids: '+ str(len(config.visited_ids)))

def seed_job_ids(seed_url:str, config:LinkedinParserConfig):
    text = download_html_page(url=seed_url)
    if text:
        matches = config.pattern.findall(text)
        if matches:
            for match in matches:
                config.seed_ids.add(match)

def traverse_web(config:LinkedinParserConfig):
    q:Queue = Queue()
    unique:set = set()

    for __jid in config.seed_ids:
        if not (__jid in unique):
            q.put(__jid)
            unique.add(__jid)

    visited_page:dict = {}

    while not q.empty():
        job_id = q.get()
        unique.remove(job_id)

        if job_id in visited_page and visited_page[job_id] < 0:
            continue
        else:
            visited_page[job_id] = visited_page.get(job_id, 0) + 1

        html_text = download_html_page(url=config.config.job_page+'/'+job_id)
        if html_text:
            
            if not (job_id in config.visited_ids):
                write_job_id_as_file(config=config, job_id=job_id)
                config.visited_ids.add(job_id)
                print('new job id:'+job_id)
                print('count:'+str(len(config.visited_ids)))    

            if config.scrap_further:
                matches = config.pattern.findall(html_text)
                if matches:
                    for match in matches:
                        if match in visited_page and visited_page[match] > 2:
                            continue
                        if not (match in unique):
                            q.put(match)     
                            unique.add(match)
                            print('queue:',match)                       
        else:
            visited_page[job_id] = -1

if '__main__' == __name__:
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.append(parentdir)

    date='2024-08-22'
    
    config_json_path = currentdir + '/config.json'
    html_dir_path = currentdir + "/jobs/{}/html".format(date)
    logger_dir_path = currentdir + "/jobs/{}/log".format(date)
    
    if not (os.path.exists(config_json_path) and 
        os.path.exists(logger_dir_path) and 
        os.path.exists(html_dir_path)):
        raise Exception("Path not found")

    config_json=None
    with open(config_json_path, 'r') as file:
        config_json = json.load(file)

    # Todo: create html directory if not present
    config = LinkedinParserConfig(config=Config(**config_json), 
                                  pattern=re.compile(r"\b\d{" + config_json['job_id_digit'] + r"}\b"),
                                  html_dir=html_dir_path,
                                  scrap_further=True)
    try:
        load_visited_job_ids(config=config)
        for __jid in config.visited_ids:
            config.seed_ids.add(__jid)
            traverse_web(config=config) 
            config.seed_ids.clear()  
    except Exception as e:
        print("error: ", str(e))   