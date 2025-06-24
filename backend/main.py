from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from routers import chat
from dotenv import load_dotenv
from containers import Container

# 環境変数の読み込み
load_dotenv()

# DIコンテナの初期化と設定の読み込み
container = Container()
container.load_config()

app = FastAPI(
    title="LocalRAG API",
    description="A local RAG (Retrieval-Augmented Generation) API using LangChain and Ollama",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=True
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

class FolderPath(BaseModel):
    path: str

class Response(BaseModel):
    answer: str
    sources: List[str]


# ルーターのインクルード
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to LocalRAG API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)