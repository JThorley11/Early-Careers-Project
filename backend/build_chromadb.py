import os
import json
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY missing from .env")


DATA_DIR = "data"
DB_DIR = "db"

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

documents = []

# Walk through the /data folder
for root, _, files in os.walk(DATA_DIR):
    for file in files:
        path = os.path.join(root, file)

        # Handle JSON files
        if file.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                items = json.load(f)
                for item in items:
                    documents.append(
                        Document(
                            page_content=item["text"],
                            metadata={
                                key: item[key]
                                for key in item
                                if key not in ["text"]
                            }
                        )
                    )

        # Handle text files
        elif file.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "filename": file,
                            "category": os.path.basename(root)
                        }
                    )
                )

# Build the ChromaDB
vectordb = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory=DB_DIR
)

vectordb.persist()
print(f"Successfully built Chroma DB with {len(documents)} documents!")
print(f"Database stored in: {DB_DIR}/")