# backend/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# Uncomment for RAG
# from langchain.vectorstores import Chroma
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.chains import RetrievalQA

import asyncio
import json

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY in your .env file")

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
# embedding = OpenAIEmbeddings()
# vectordb = Chroma(persist_directory="db", embedding_function=embedding)
# retriever = vectordb.as_retriever(search_kwargs={"k": 3})
# qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, return_source_documents=True)

class Query(BaseModel):
    question: str

#@app.post("/query")
#async def query_endpoint(query: Query):
#    async def event_stream():
#        # Without RAG: simple LLM response
#        messages = [HumanMessage(content=query.question)]
#        response = llm.stream(messages)
#        
#        async for chunk in response:
#            yield f"data:{json.dumps({'text': chunk.delta})}\n\n"
#            await asyncio.sleep(0)  # yield control#

        # Uncomment for RAG:
        # result = qa_chain(query.question)
        # yield f"data:{json.dumps({'text': result['result']})}\n\n"

#    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/query")
async def query_endpoint(request: Query):
    question = request.question

    if llm:
        # Call LLM
        messages = [HumanMessage(content=question)]
        # For static/simple call, use generate() or call() instead of streaming
        try:
            response = llm(messages)  # returns a message object
            answer = response.content
        except Exception as e:
            answer = f"Error: {str(e)}"
    else:
        # Fallback if LLM not available
        answer = "Cheese"

    return JSONResponse(content={"text": answer})