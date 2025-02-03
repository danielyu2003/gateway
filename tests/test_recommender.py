from src.recommender.pipelines import CourseRecommender

recommender = CourseRecommender(2024, k=5)
recommender.index(debug=True)

text = "Can you recommend me some cool courses involving machine learning?"

recommendation = recommender.recommend(text)

answer = recommendation["llm"]["replies"][0]

print(answer)