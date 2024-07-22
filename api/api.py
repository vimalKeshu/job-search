import random
import uvicorn

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from api.common.ops import load_test_data

job_list = load_test_data()
# CORS middleware configuration
origins = [
    "http://localhost:3000",
    "http://192.168.29.102:3000"
    # Add more allowed origins as needed
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"], # In production, specify the actual domain of your frontend application (https://yourdomain.com) instead of allowing all origins (["*"]).
)


@app.get("/job/{query}")
async def search_jobs(query: str):
    try:
        jobs: list = []
        for job in job_list:
            if query.lower() in job['title'].lower():
                jobs.append(job)
        return jobs
    except:
        raise HTTPException(status_code=500, detail="Issue in request processing..")

@app.get("/job")
async def get_all_jobs():
    try:
        return job_list
    except:
        raise HTTPException(status_code=500, detail="Issue in request processing..")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)