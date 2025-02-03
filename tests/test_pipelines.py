from src.recommender.pipelines import CourseRecommender

recommender = CourseRecommender(2024, k=1)
recommender.index(2024, debug=True)

text = "What should I take if I want to learn about evolutionary algorithms?"

docs = recommender.query(text, debug=True)

courses = [doc.meta['name'] for doc in docs]

assert any("Evolutionary Algorithm" in name for name in courses)