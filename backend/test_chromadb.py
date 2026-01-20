from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import numpy as np

DB_DIR = "db"

# Fake embedding class for testing
class FakeEmbeddings:
    def embed_documents(self, texts):
        # Return a list of vectors (dummy embeddings)
        return [np.random.rand(1536).tolist() for _ in texts]

    def embed_query(self, text):
        # Return a single vector for the query
        return np.random.rand(1536).tolist()

embeddings = FakeEmbeddings()

# Load Chroma DB with fake embeddings
vectordb = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

while True:
    query = input("Enter a query to test (or 'exit' to quit): ")
    if query.lower() == "exit":
        break

    results = vectordb.similarity_search(query, k=3)  # returns a list of Document objects

    print(f"\nTop {len(results)} documents for query: {query}")
    for i, doc in enumerate(results, 1):
        print(f"\nResult {i}:")
        print("Text:", doc.page_content)
        print("Metadata:", doc.metadata)