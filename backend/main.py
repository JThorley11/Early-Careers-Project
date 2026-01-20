import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal

from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# RAG
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# ---------------------------
# Utility functions
# ---------------------------
def cosine_similarity(vec1, vec2):
    dot = sum(x*y for x, y in zip(vec1, vec2))
    norm1 = math.sqrt(sum(x*x for x in vec1))
    norm2 = math.sqrt(sum(y*y for y in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def parse_page_content(page_content):
    description, currentIssues, suitableSolutions, tags = "", [], [], []
    lines = page_content.split("\n")
    if lines:
        description = lines[0]
    for line in lines[1:]:
        if line.startswith("Current Issues:"):
            currentIssues = [s.strip() for s in line[len("Current Issues:"):].split(",") if s.strip()]
        elif line.startswith("Suitable Solutions:"):
            suitableSolutions = [s.strip() for s in line[len("Suitable Solutions:"):].split(",") if s.strip()]
        elif line.startswith("Tags:"):
            tags = [s.strip() for s in line[len("Tags:"):].split(",") if s.strip()]
    return description, currentIssues, suitableSolutions, tags

# ---------------------------
# FastAPI setup
# ---------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# LLM & Embeddings
# ---------------------------
llm = ChatOpenAI(
    model_name="llama3.2:latest",
    temperature=0.0,
    base_url="http://localhost:11434/v1",
    streaming=False,
    verbose=True,
    openai_api_key="unused-key",
)

embedding = OllamaEmbeddings(
    model="all-minilm:latest",
    base_url="http://localhost:11434"
)

# VectorDB
vectordb = Chroma(persist_directory="db", embedding_function=embedding)
retriever = vectordb.as_retriever(search_kwargs={"k": 5})

# ---------------------------
# Summary chain
# ---------------------------
prompt = PromptTemplate.from_template("""
You are a sustainability expert at a multinational corporation with strong environmental values. 
You have access to the knowledge provided below that has been retrieved from internal documents to answer user prompts.
Please explain briefly why each document is relevant to the user's query in the summary and why they are ordered that way.
Summarize the following context to answer the prompt concisely.
Your answer must be concise, not exceeding 100 words.
Do not use any information that is not in the context.
Please start immediately with the answer; do not preamble.

Context:
{context}

Prompt: {prompt}
""")

summary_chain = prompt | llm | StrOutputParser()

# ---------------------------
# Request & Response Models
# ---------------------------
class Query(BaseModel):
    query: str

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

# ---------------------------
# Query endpoint
# ---------------------------
@app.post("/query")
async def query_endpoint(request: Query):
    query = request.query

    # Use Chroma similarity search with precomputed embeddings
    docs_with_scores = vectordb.similarity_search_with_score(query, k=5)

    results = []
    filtered_docs = []

    for doc, distance in docs_with_scores:
        description, currentIssues, suitableSolutions, tags = parse_page_content(doc.page_content)
        meta = doc.metadata or {}

        relevance_score = 1 / (1 + distance)  # convert distance → relevance score
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

    # Sort by relevance
    results.sort(key=lambda r: r.relevanceScore, reverse=True)

    if not results:
        return SearchResponse(
            summary="No highly relevant documents found.",
            results=[]
        )

    # Generate summary only from filtered docs
    context_text = "\n".join([doc.page_content for doc in filtered_docs])
    try:
        summary = summary_chain.invoke({"context": context_text, "prompt": query})
    except Exception as e:
        summary = f"Error generating summary: {str(e)}"

    return SearchResponse(summary=summary, results=results)
