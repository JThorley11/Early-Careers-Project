import os
import json
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings

# Directories
DATA_DIR = "data"
DB_DIR = "db"

# Initialize embeddings
embeddings = OllamaEmbeddings(
    model="all-minilm",
    base_url="http://localhost:11434"
)

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
                    page_content = item.get("description", "")
                    page_content += "\nCurrent Issues: " + ", ".join(item.get("currentIssues", []))
                    page_content += "\nSuitable Solutions: " + ", ".join(item.get("suitableSolutions", []))
                    page_content += "\nTags: " + ", ".join(item.get("tags", []))

                    metadata = {}
                    for key, value in item.items():
                        if key in ["description", "currentIssues", "suitableSolutions"]:
                            continue
                        if isinstance(value, list):
                            metadata[key] = ", ".join(map(str, value))
                        else:
                            metadata[key] = value

                    documents.append(
                        Document(page_content=page_content, metadata=metadata)
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

# 🔹 Split documents BEFORE embedding
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

split_documents = text_splitter.split_documents(documents)

# Build the ChromaDB
vectordb = Chroma.from_documents(
    documents=split_documents,
    embedding=embeddings,
    persist_directory=DB_DIR
)

vectordb.persist()

print(f"Successfully built Chroma DB with {len(split_documents)} chunks!")
print(f"Database stored in: {DB_DIR}/")