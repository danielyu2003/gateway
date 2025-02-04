from fastapi import FastAPI
from pydantic import BaseModel
from src.recommender.pipelines import CourseRecommender

app = FastAPI()
recommender = CourseRecommender(year=2024)

class QueryRequest(BaseModel):
    question: str

@app.post("/recommend")
def get_recommendation(request: QueryRequest):
    response = recommender.recommend(request.question)
    return {"recommendation": response}