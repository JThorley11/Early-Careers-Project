import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# RAG
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

import asyncio
import json

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS so React frontend can access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------
# LLM
# ---------------------------------------
if OPENAI_API_KEY:
    llm = ChatOpenAI(
        model_name="gpt-5-nano",
        temperature=1,
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
prompt = ChatPromptTemplate.from_template("""
Use ONLY the following context to answer the question.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question: {question}
""")

qa_chain = (
    {
        # RAG: retrieve docs and pass them into {context}
        "context": lambda inp: retriever.get_relevant_documents(inp["question"]),
        "question": lambda inp: inp["question"],
    }
    | prompt
    | llm
    | StrOutputParser()
)

# ---------------------------------------
# Request Model
# ---------------------------------------
class Query(BaseModel):
    question: str

# ---------------------------------------
# FastAPI Endpoint
# ---------------------------------------
@app.post("/query")
async def query_endpoint(request: Query):
    question = request.question

    if not llm:
        return JSONResponse(content={"text": "Cheese"})

    try:
        answer = qa_chain.invoke({"question": question})
    except Exception as e:
        answer = f"Error: {str(e)}"

    return JSONResponse(content={"text": answer})