from haystack import Pipeline
from haystack.components.evaluators import DocumentMRREvaluator, DocumentRecallEvaluator, DocumentMAPEvaluator
import numpy as np

def evaluation_pipeline():
    evaluator = Pipeline()
    evaluator.add_component("mrr", DocumentMRREvaluator())
    evaluator.add_component("map", DocumentMAPEvaluator())
    evaluator.add_component("recall", DocumentRecallEvaluator(mode="multi_hit"))
    return evaluator

class SystemEvaluator:
    def __init__(self, recommender, retriever):
        self.recommender = recommender
        self.retriever = retriever
        self.eval_pipeline = evaluation_pipeline()

    def evaluate(self, queries, filters_list, debug=False):
        assert len(queries) == len(filters_list), "Each query must have a corresponding set of filters."

        metric_scores = {
            "mrr": [],
            "map": [],
            "recall": []
        }

        for query, filters in zip(queries, filters_list):
            result = self.retriever.run(filters=filters)
            ground_truth_docs = result['documents']
            predicted_docs = self.recommender.query(question=query)

            if debug:
                print(f"\nQuery: {query}")
                print("Ground truth codes:")
                for doc in ground_truth_docs:
                    print(doc.meta['code'])
                print("Predicted codes:")
                for doc in predicted_docs:
                    print(doc.meta['code'])

            evaluation_result = self.eval_pipeline.run({
                "mrr": {
                    "ground_truth_documents": [ground_truth_docs],
                    "retrieved_documents": [predicted_docs]
                },
                "map": {
                    "ground_truth_documents": [ground_truth_docs],
                    "retrieved_documents": [predicted_docs]
                },
                "recall": {
                    "ground_truth_documents": [ground_truth_docs],
                    "retrieved_documents": [predicted_docs]
                }
            })

            for metric in metric_scores:
                metric_scores[metric].append(evaluation_result[metric]['score'])

        mean_metrics = tuple(np.mean(metric_scores[metric]) for metric in ["mrr", "map", "recall"])
        return mean_metrics

if __name__ == "__main__":
    from src.recommender.pipelines import CourseRecommender
    from haystack.components.retrievers import FilterRetriever

    recommender = CourseRecommender(year=2024, k=5)
    retriever = FilterRetriever(recommender.document_store)

    evaluator = SystemEvaluator(recommender, retriever)

    queries = [
        "As a CS major, what courses should I take if I am interested in machine learning?",
        "As a CS major, what courses should I take if I am interested in systems and compilers?",
        "As a CS major, what courses should I take if I am interested in web and mobile app development?"
    ]

    filters_list = [
        {
            "operator": "OR",
            "conditions": [
                {"field": "meta.code", "operator": "==", "value": "CS 559"},
                {"field": "meta.code", "operator": "==", "value": "CS 560"},
                {"field": "meta.code", "operator": "==", "value": "CS 583"},
                {"field": "meta.code", "operator": "==", "value": "CS 541"},
                {"field": "meta.code", "operator": "==", "value": "CS 556"}
            ]
        },
        {
            "operator": "OR",
            "conditions": [
                {"field": "meta.code", "operator": "==", "value": "CS 392"},
                {"field": "meta.code", "operator": "==", "value": "CS 492"},
                {"field": "meta.code", "operator": "==", "value": "CS 511"},
                {"field": "meta.code", "operator": "==", "value": "CS 516"},
                {"field": "meta.code", "operator": "==", "value": "CS 576"}
            ]
        },
        {
            "operator": "OR",
            "conditions": [
                {"field": "meta.code", "operator": "==", "value": "CS 546"},
                {"field": "meta.code", "operator": "==", "value": "CS 522"},
                {"field": "meta.code", "operator": "==", "value": "CS 347"},
                {"field": "meta.code", "operator": "==", "value": "CS 554"},
                {"field": "meta.code", "operator": "==", "value": "CS 524"}
            ]
        },
    ]

    mean_mrr, mean_map, mean_recall = evaluator.evaluate(queries, filters_list, debug=True)

    print(f"\nMean MRR: {mean_mrr:.4f}")
    print(f"Mean MAP: {mean_map:.4f}")
    print(f"Mean Recall: {mean_recall:.4f}")
