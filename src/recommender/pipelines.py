import re
from dotenv import load_dotenv
from haystack import Document, Pipeline
from haystack.components.preprocessors import DocumentCleaner
from haystack.utils import Secret
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.writers import DocumentWriter
from haystack.components.generators import AzureOpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore
from haystack_integrations.components.retrievers.pgvector import PgvectorEmbeddingRetriever

from src.crawler.scraper import CatalogScraper

import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ Pipeline Builders ------------------ #

def indexing_pipeline(document_store):
    indexer = Pipeline()
    indexer.add_component("cleaner", DocumentCleaner())
    indexer.add_component("embedder", SentenceTransformersDocumentEmbedder())
    indexer.add_component("writer", DocumentWriter(document_store, policy=DuplicatePolicy.SKIP))
    indexer.connect("cleaner", "embedder")
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
You are a handy assistant named Attila who recommends courses for students at Stevens Institute of Technology.
Given the following courses from the fall of {year} to the spring of {year+1}, answer the question at the end.
Include the name, code, description, and link (in that order) of each course in your response.
Order courses by relevancy, if applicable, and omit courses that are irrelevant to the question.
If there are no relevant courses, or if the question is irrelevant or tangential to course recommendations, tell the user to meet their academic advisor.
Otherwise, do not prompt the user to follow up.

Courses:
\u007b% for doc in documents %\u007d
    \u007b\u007b loop.index \u007d\u007d. \u007b\u007b doc.meta['name'] \u007d\u007d
    \u007b\u007b doc.meta['desc'] \u007d\u007d
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

# ------------------ Main Class ------------------ #

class Preprocessor:
    """
    Class encapsulating logic for text preprocessing.
    """
    def __init__(self):
        self.isNotAlpha = re.compile(r"[^a-z\s]+")  # Remove non-alphabetic characters
        self.isUrl = re.compile(r"(https?://|www\.)\S+")  # Remove URLs
        self.isStopword = re.compile(r"\b(i|me|my|...|now)\b")  # Remove common stopwords
        self.isSuffix = re.compile(r"\B(ings?|e[sdr]|st?|ly|ment|ness|ion)\b")  # Remove common suffixes for stemming

    def pipeline(self, text):
        """
        Apply text cleaning steps sequentially.

        Args:
            text (str): Raw text input.

        Returns:
            list of str: Processed word tokens.
        """
        line = text.lower() # first ensure that all text is lowercase
        line = self.isUrl.sub('', line)
        line = self.isNotAlpha.sub('', line)
        line = self.isStopword.sub('', line)
        line = self.isSuffix.sub('', line)
        return line

class CourseRecommender:
    def __init__(self, year, k=3):
        load_dotenv()
        azure_api_key = Secret.from_env_var("API_TOKEN")
        if not azure_api_key:
            raise EnvironmentError("Missing API_TOKEN in environment variables.")
        client = AzureOpenAIGenerator(
            azure_endpoint="https://models.inference.ai.azure.com",
            api_key=azure_api_key,
            azure_deployment="gpt-4o"
        )
        self.year = year
        self.document_store = PgvectorDocumentStore(
            table_name=f"f{year}_s{year+1}",
            keyword_index_name=f"f{year}_s{year+1}_index",
            embedding_dimension=768,
            recreate_table=False,
            vector_function="cosine_similarity",
            search_strategy="exact_nearest_neighbor"
        )
        self.indexer = indexing_pipeline(self.document_store)
        self.querier = querying_pipeline(self.document_store, k)
        self.recommender = recommendation_pipeline(client, year)

    def index(self, batch_size=10):
        preprocessing = Preprocessor()
        scraper = CatalogScraper(self.year)
        course_generator = scraper.get_courses()
        batch = []
        for course in course_generator:
            desc, code, name, link = course
            text = preprocessing.pipeline(desc)
            doc = Document(content=text, meta={"code": code, "name": name, "link": link, "desc": desc})
            batch.append(doc)
            if len(batch) >= batch_size:
                logger.info(f"Indexing batch of size {batch_size}")
                self.indexer.run({"cleaner": {"documents": batch}})
                batch.clear()
        if batch:
            self.indexer.run({"cleaner": {"documents": batch}})

    def query(self, question):
        logger.info(f"Querying for: {question}")
        results = self.querier.run({"embedder": {"text": question}})
        docs = results["retriever"]["documents"]
        return docs

    def recommend(self, question):
        docs = self.query(question)
        response = self.recommender.run({'prompt_builder': {"documents": docs, "query": question}})
        return docs, response['llm']['replies'][0]
