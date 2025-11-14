# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# Uncomment for RAG
# from langchain.vectorstores import Chroma
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.chains import RetrievalQA

import asyncio
import json

app = FastAPI()

# CORS so React frontend can access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# LLM setup
#llm = ChatOpenAI(model_name="gpt-4", temperature=0, streaming=True, verbose=True)

# Uncomment for RAG
# embedding = OpenAIEmbeddings()
# vectordb = Chroma(persist_directory="db", embedding_function=embedding)
# retriever = vectordb.as_retriever(search_kwargs={"k": 3})
# qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever, return_source_documents=True)

class Query(BaseModel):
    question: str

''' Endpoint for querying the LLM with optional RAG support
@app.post("/query")
async def query_endpoint(query: Query):
    async def event_stream():
        # Without RAG: simple LLM response
        messages = [HumanMessage(content=query.question)]
        response = llm.stream(messages)
        
        async for chunk in response:
            yield f"data:{json.dumps({'text': chunk.delta})}\n\n"
            await asyncio.sleep(0)  # yield control

        # Uncomment for RAG:
        # result = qa_chain(query.question)
        # yield f"data:{json.dumps({'text': result['result']})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
'''

@app.post("/query")
async def query_endpoint(request: Query):
    return JSONResponse(content={"text": "Cheese"})