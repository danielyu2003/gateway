import os
from dotenv import load_dotenv
from haystack import Document, Pipeline
from haystack.utils import Secret
from haystack.components.writers import DocumentWriter
from haystack.components.generators import AzureOpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever

from src.crawler.scraper import CatalogScraper

def indexing_pipeline(document_store):
    indexer = Pipeline()
    indexer.add_component("embedder", SentenceTransformersDocumentEmbedder())
    indexer.add_component("writer", DocumentWriter(document_store))
    indexer.connect("embedder", "writer")
    return indexer

def querying_pipeline(document_store, k):
    querier = Pipeline()
    querier.add_component("embedder", SentenceTransformersTextEmbedder())
    querier.add_component("retriever", PgvectorEmbeddingRetriever(document_store=document_store, top_k=k))
    querier.connect("embedder", "retriever")
    return querier

def recommendation_pipeline(client, year):
    template = f"""\
Given the following information about courses from the fall semester of {year} to the spring semester of {year+1} at Stevens Institute of Technology, provide a descriptive answer to the question. The courses are ordered from most relevant to least relevant. Please include the course code and the link to the course catalog page in your answer.

Courses: 
\u007b% for doc in documents %\u007d
    \u007b\u007b loop.index \u007d\u007d. \u007b\u007b doc.meta['name'] \u007d\u007d
    \u007b\u007b doc.content \u007d\u007d
    Course code: \u007b\u007b doc.meta['code'] \u007d\u007d
    Link to catalog page: \u007b\u007b doc.meta['link'] \u007d\u007d
\u007b% endfor %\u007d

Question: \u007b\u007b query \u007d\u007d?\
"""
    recommender = Pipeline()
    recommender.add_component("prompt_builder", PromptBuilder(template=template))
    recommender.add_component("llm", client)
    recommender.connect("prompt_builder", "llm")
    return recommender

class CourseRecommender:
    def __init__(self, year, k=3, model_name="gpt-4o"):
        load_dotenv()
        self.year = year
        self.document_store = PgvectorDocumentStore(
            embedding_dimension=768,
            vector_function="cosine_similarity",
            recreate_table=True,
            search_strategy="hnsw",
        )
        self.indexer = indexing_pipeline(self.document_store)
        self.querier = querying_pipeline(self.document_store, k)

        endpoint = "https://models.inference.ai.azure.com"
        model_name = model_name

        client = AzureOpenAIGenerator(azure_endpoint=endpoint, 
                                      api_key=Secret.from_env_var("GITHUB_TOKEN"), 
                                      azure_deployment=model_name)

        self.recommender = recommendation_pipeline(client, year)
    
    def index(self, batch_size=10, debug=False):
        scraper = CatalogScraper(self.year)
        course_generator = scraper.get_courses(debug=debug)
        batch = []
        for course in course_generator:
            desc, code, name, link = course
            doc = Document(content=desc,
                           meta={"code": code, "name": name, "link": link})
            batch.append(doc)
            if len(batch) >= batch_size:
                self.indexer.run({"embedder": {"documents": batch}})
                batch = []
        if batch:
            self.indexer.run({"embedder": {"documents": batch}})
        if debug:
            print(f"Total documents indexed: {self.document_store.count_documents()}")

    def query(self, question, debug=False):
        results = self.querier.run({"embedder": {"text": question}})
        docs = results["retriever"]["documents"]
        if debug:
            print("Top Courses:\n" + "-" * 12)
            for rank, doc in enumerate(docs, start=1):
                print(f"{rank}: {doc.meta['name']}")
        return docs

    def recommend(self, question):
        docs = self.query(question)
        response = self.recommender.run({'prompt_builder': {"documents": docs, "query": question}})
        
        return response 
        
