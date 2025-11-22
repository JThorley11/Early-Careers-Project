import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Literal

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# RAG
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

import asyncio
import json
import re

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

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if OPENAI_API_KEY is not None:
    llm = ChatOpenAI(
        model_name="gpt-4.1-nano",
        temperature=0.0,
        streaming=False,
        verbose=True,
        openai_api_key=OPENAI_API_KEY,
    )
else:
    llm = None

# ---------------------------------------
# RAG: Embeddings + VectorDB
# ---------------------------------------
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectordb = Chroma(persist_directory="db", embedding_function=embedding)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

# ---------------------------------------
# New Retrieval Chain (LCEL)
# ---------------------------------------
prompt = PromptTemplate.from_template("""
You are a sustainability expert at a multinational corportation with strong evironmental values. 
Summarise the following context to answer the prompt consisely, the context will be passed after you summary.

Use ONLY the following context to complete the summary.

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

    if not llm:
        return JSONResponse(content={"summary": "Cheese", "results": []})

    # Retrieve relevant documents
    docs = retriever.invoke(query)
    print(docs)

    # Convert to SearchResult list
    results = []
    for doc in docs:
        description, currentIssues, suitableSolutions, tags = parse_page_content(doc.page_content)
        meta = doc.metadata or {}

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
            relevanceScore=float(meta.get("relevanceScore", 0)),
            matchedTerms=[]
        ))

    # Generate summary using context
    context_text = "\n".join([doc.page_content for doc in docs])
    try:
        summary = summary_chain.invoke({"context": context_text, "prompt": query})
    except Exception as e:
        summary = f"Error generating summary: {str(e)}"
    if not docs:
        summary = "No relevant documents found."

    # Return everything together
    return SearchResponse(summary=summary, results=results)