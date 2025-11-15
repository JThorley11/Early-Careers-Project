# backend/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage

# Uncomment for RAG
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

import asyncio
import json

load_dotenv()

try:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
except:
    OPENAI_API_KEY = None

app = FastAPI()

# CORS so React frontend can access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM setup
if OPENAI_API_KEY:
    llm = ChatOpenAI(
        model_name="gpt-5-nano",
        temperature=1,
        streaming=False,
        verbose=True,
        openai_api_key=OPENAI_API_KEY
    )
else:
    llm = None

# Uncomment for RAG
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectordb = Chroma(persist_directory="db", embedding_function=embedding)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})
qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, return_source_documents=True)

class Query(BaseModel):
    question: str

@app.post("/query")
async def query_endpoint(request: Query):
    question = request.question

    if llm:
        try:
            # Use RAG
            result = qa_chain.run(question)
            answer = result
        except Exception as e:
            answer = f"Error: {str(e)}"
    else:
        answer = "Cheese"

    return JSONResponse(content={"text": answer})