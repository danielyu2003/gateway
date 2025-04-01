from haystack import Document, Pipeline
from haystack.components.evaluators import SASEvaluator, DocumentMRREvaluator, DocumentRecallEvaluator, DocumentMAPEvaluator

def evaluation_pipeline(flag_fail=False):
    evaluator = Pipeline()
    evaluator.add_component("sas", SASEvaluator())
    evaluator.add_component("mrr", DocumentMRREvaluator())
    evaluator.add_component("map", DocumentMAPEvaluator())
    evaluator.add_component("recall", DocumentRecallEvaluator())
    return evaluator

class SystemEvaluator:
    def __init__(self):
        pass

if __name__ == "__main__":
    pass

    # from haystack import Document
    # from haystack.components.retrievers import FilterRetriever
    # from haystack.document_stores.in_memory import InMemoryDocumentStore

    # docs = [
    # 	Document(content="Python is a popular programming language", meta={"lang": "en"}),
    # 	Document(content="python ist eine beliebte Programmiersprache", meta={"lang": "de"}),
    # ]

    # doc_store = InMemoryDocumentStore()
    # doc_store.write_documents(docs)
    # retriever = FilterRetriever(doc_store)
    # result = retriever.run(filters={"field": "lang", "operator": "==", "value": "en"})

    # assert "documents" in result
    # assert len(result["documents"]) == 1
    # assert result["documents"][0].content == "Python is a popular programming language"
