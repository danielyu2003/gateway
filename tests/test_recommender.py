from src.recommender.pipelines import CourseRecommender

recommender = CourseRecommender(2024)
# recommender.index()

text = "Can you recommend me some cool courses involving machine learning?"

recommendation = recommender.recommend(text)

answer = recommendation

print(answer)