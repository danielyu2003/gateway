from dotenv import load_dotenv
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

load_dotenv()

document_store = PgvectorDocumentStore(
    embedding_dimension=768,
    vector_function="cosine_similarity",
    recreate_table=True,
    search_strategy="hnsw",
)

print(document_store.count_documents())