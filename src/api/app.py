import threading
from fastapi import FastAPI
from pydantic import BaseModel
from src.recommender.pipelines import CourseRecommender

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing (change in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

recommender = CourseRecommender(year=2024)
thread = threading.Thread(target=recommender.index, daemon=True)
thread.start()

class QueryRequest(BaseModel):
    question: str

@app.post("/api/recommend/")
def get_recommendation(request: QueryRequest):
    response = recommender.recommend(request.question)
    return {"recommendation": response}
