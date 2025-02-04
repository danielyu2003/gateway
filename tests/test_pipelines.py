from src.recommender.pipelines import CourseRecommender

recommender = CourseRecommender(2024)

# recommender.index()

text = "What course should I take if I want to learn about evolutionary algorithms?"

docs = recommender.query(text)

courses = [doc.meta['name'] for doc in docs]

print(courses)

assert any("Evolutionary Algorithm" in name for name in courses)