import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Literal

from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# RAG
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
import math

def cosine_similarity(vec1, vec2):
    dot = sum(x*y for x, y in zip(vec1, vec2))
    norm1 = math.sqrt(sum(x*x for x in vec1))
    norm2 = math.sqrt(sum(y*y for y in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def parse_page_content(page_content):
    # Default values
    description, currentIssues, suitableSolutions, tags = "", [], [], []

    # Split by lines
    lines = page_content.split("\n")
    if lines:
        description = lines[0]

    # Extract lists
    for line in lines[1:]:
        if line.startswith("Current Issues:"):
            currentIssues = [s.strip() for s in line[len("Current Issues:"):].split(",") if s.strip()]
        elif line.startswith("Suitable Solutions:"):
            suitableSolutions = [s.strip() for s in line[len("Suitable Solutions:"):].split(",") if s.strip()]
        elif line.startswith("Tags:"):
            tags = [s.strip() for s in line[len("Tags:"):].split(",") if s.strip()]

    return description, currentIssues, suitableSolutions, tags

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(
    model_name="llama3.2",
    temperature=0.0,
    base_url="http://localhost:11434/v1",
    streaming=False,
    verbose=True,
    openai_api_key="unused-key",
)

# ---------------------------------------
# RAG: Embeddings + VectorDB
# ---------------------------------------
embedding = OllamaEmbeddings(
    model="all-minilm",
    base_url="http://localhost:11434"
)
vectordb = Chroma(persist_directory="db", embedding_function=embedding)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})

# ---------------------------------------
# New Retrieval Chain (LCEL)
# ---------------------------------------
prompt = PromptTemplate.from_template("""
You are a sustainability expert at a multinational corportation with strong evironmental values. 
You have access to the knowledge provided below that has been retrieved from internal documents to answer user prompts.
Please explain breifly why each document is relevant to the user's query in the summary. And why they are ordered that way.
Summarise the following context to answer the prompt consisely.
Your answer must be consise not exceeding 100 words.

Context:
{context}

Prompt: {prompt}
""")

summary_chain = prompt | llm | StrOutputParser()    

# ---------------------------------------
# Request Model
# ---------------------------------------
class Query(BaseModel):
    query: str

# ---------------------------------------
# Response Models
# ---------------------------------------
class SearchResult(BaseModel):
    id: str
    name: str
    location: str
    description: str
    currentIssues: List[str]
    suitableSolutions: List[str]
    priority: Literal["high", "medium", "low"]
    area: float
    tags: List[str]
    relevanceScore: float
    matchedTerms: List[str]

class SearchResponse(BaseModel):
    summary: str
    results: List[SearchResult]
# ---------------------------------------
# FastAPI Endpoint
# ---------------------------------------
@app.post("/query")
async def query_endpoint(request: Query):
    query = request.query

    # Retrieve relevant documents
    docs = retriever.invoke(query)

    # Compute query embedding
    query_vector = embedding.embed_query(query)

    results = []
    filtered_docs = []  # we need this to generate a correct summary

    for doc in docs:
        description, currentIssues, suitableSolutions, tags = parse_page_content(doc.page_content)
        meta = doc.metadata or {}

        # Compute relevance score
        doc_vector = embedding.embed_query(doc.page_content)
        relevance_score = cosine_similarity(query_vector, doc_vector)

        # Only include if cosine similarity >= 0.8
        #if relevance_score < 0.8:
        #    continue  # skip weak matches

        filtered_docs.append(doc)

        results.append(SearchResult(
            id=str(meta.get("id", "")),
            name=meta.get("name", ""),
            location=meta.get("location", ""),
            description=description,
            currentIssues=currentIssues,
            suitableSolutions=suitableSolutions,
            priority=str(meta.get("priority", "low")),
            area=float(meta.get("area", 0)),
            tags=tags,
            relevanceScore=relevance_score,
            matchedTerms=[]
        ))

    # Sort strong results
    results.sort(key=lambda r: r.relevanceScore, reverse=True)

    # If nothing passes the threshold
    if not results:
        return SearchResponse(
            summary="No highly relevant documents found.",
            results=[]
        )

    # Generate summary ONLY from filtered docs
    context_text = "\n".join([doc.page_content for doc in filtered_docs])
    try:
        summary = summary_chain.invoke({"context": context_text, "prompt": query})
    except Exception as e:
        summary = f"Error generating summary: {str(e)}"

    return SearchResponse(summary=summary, results=results)