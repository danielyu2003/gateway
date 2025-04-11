from haystack import Pipeline
from haystack.components.evaluators import SASEvaluator, DocumentMRREvaluator, DocumentRecallEvaluator, DocumentMAPEvaluator

def evaluation_pipeline(flag_fail=False):
    evaluator = Pipeline()
    evaluator.add_component("sas", SASEvaluator())
    evaluator.add_component("mrr", DocumentMRREvaluator())
    evaluator.add_component("map", DocumentMAPEvaluator())
    evaluator.add_component("recall", DocumentRecallEvaluator())
    return evaluator

class SystemEvaluator:
    def __init__(self, model, store):
        self.model = model
        self.store = store

if __name__ == "__main__":
    from src.recommender.pipelines import CourseRecommender
    from haystack.components.retrievers import FilterRetriever

    recommender = CourseRecommender(year=2024, k=5)
    retriever = FilterRetriever(recommender.document_store)

    test_q = "As a CS major, what courses should I take if I am interested in machine learning?"

    result = retriever.run(filters={
        "operator": "OR",
        "conditions": [
            {"field": "meta.code", "operator": "==", "value": "CS 559"},
            {"field": "meta.code", "operator": "==", "value": "CS 560"},
            {"field": "meta.code", "operator": "==", "value": "CS 583"},
            {"field": "meta.code", "operator": "==", "value": "CS 541"},
            {"field": "meta.code", "operator": "==", "value": "CS 556"}
        ]
    })

    docs = result['documents']
    test_y = '\n'.join([f"{doc.meta['name']}:\n{doc.meta['desc']}\nCode: {doc.meta['code']}\nLink: {doc.meta['link']}\n" for doc in docs])

    model_docs, model_response = recommender.recommend(test_q)

    print(model_response)

    for doc in docs:
        print(doc.meta['code'])
    print()
    for doc in model_docs:
        print(doc.meta['code'])

    eval_pipe = evaluation_pipeline()

    evals = eval_pipe.run({
        "sas": {"ground_truth_answers": [test_y], "predicted_answers": [model_response]},
        "mrr": {"ground_truth_documents": [docs], "retrieved_documents": [model_docs]},
        "map": {"ground_truth_documents": [docs], "retrieved_documents": [model_docs]},
        "recall": {"ground_truth_documents": [docs], "retrieved_documents": [model_docs]}
    })

    for metric in evals:
        print(f"{metric}: {evals[metric]['score']}")
