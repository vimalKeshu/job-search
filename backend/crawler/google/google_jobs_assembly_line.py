import re
import os 
import sys
import json
import tiktoken
import openai
import pickle
import traceback
import requests
import logging

from logging import Logger
from queue import Queue
from bs4 import BeautifulSoup
from autogen import ConversableAgent

logger:Logger = logging.getLogger('google_jobs_assembly_line')

"""
Assembly line flow:
------------------
    
[seed job website] --> [crawl html page] --> [download html] --> [parse html] --> [search information]
                            |                                                             |
                            |                                                             |
                            <----[queue] <---------------[search job ids] <-------------------------------> [store job information as json]

"""

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm_config = {"model": "gpt-4o-mini"}
google_html_jobs_dir = currentdir + '/jobs/html'
google_json_jobs_dir = currentdir + '/jobs/json'
google_job_url = "https://www.google.com/about/careers/applications/jobs/results/{}"
google_job_page_url = "https://www.google.com/about/careers/applications/jobs/results?page={}"
google_job_url = "https://www.google.com/about/careers/applications/jobs/results"
google_job_id_pattern = r"\b\d{" + str(18) + r"}\b"
google_job_id_regex = re.compile(google_job_id_pattern)


if not os.path.exists(google_html_jobs_dir):
    raise Exception('Not able to find the html directory: '+google_html_jobs_dir)

if not os.path.exists(google_json_jobs_dir):
    raise Exception('Not able to find the json directory: '+google_json_jobs_dir)

def load_visited_urls(dir=google_html_jobs_dir)-> set:
    visited:set = set()
    count = 0
    for file in os.listdir(dir):
        jid = file.replace('.html','')
        visited.add(jid)
        count = count + 1

    logger.info('Total visited job ids:'+ count)

    return visited

