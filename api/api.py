import uvicorn
import traceback
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from job_query import query_reranking

# CORS middleware configuration
origins = [
    # "http://localhost:3000",
    # "http://192.168.29.102:3000"
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


@app.get("/job/{q}")
async def search_jobs(q: str):
    try:
        response = query_reranking(question=q)
        #print(q + "=" + response)
        time.sleep(5)
        return response
    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Issue in request processing..")

@app.get("/job")
async def get_all_jobs():
    try:
        return []
    except:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Issue in request processing..")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)