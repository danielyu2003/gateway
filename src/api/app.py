import threading
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.recommender.pipelines import CourseRecommender

class QueryRequest(BaseModel):
    question: str

def createApp(year=2024, k=7, startIndexing=False):

    recommender = CourseRecommender(year=year, k=k)

    if startIndexing:
        thread = threading.Thread(target=recommender.index, daemon=True)
        thread.start()

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/api/recommend/")
    def get_recommendation(request: QueryRequest):
        _, response = recommender.recommend(request.question)
        return {"recommendation": response}

    return app

app = createApp()
