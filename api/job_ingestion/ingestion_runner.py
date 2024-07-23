import os 
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
print(currentdir)
print(parentdir)

from ingestion_ops import *

if __name__ == "__main__":
    ingest_gcp_jobs(file_path= './api/storage/test/jobs/job_links.csv')