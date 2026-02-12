"""
FastAPI Backend for RAG Chatbot
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from rag_core import RAGChatbot

# Load environment variables from parent directory (.env is in root)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Production-ready RAG chatbot with Groq and HuggingFace",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_documents")
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploaded_documents"
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize RAG chatbot
rag_chatbot = RAGChatbot(
    groq_api_key=GROQ_API_KEY,
    model_name=MODEL_NAME,
    collection_name=COLLECTION_NAME,
    chroma_persist_dir=CHROMA_DIR
)

# Initial sync on startup
print("🚀 Performing initial document sync...")
rag_chatbot.sync_folder(str(UPLOAD_DIR))

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class StatusResponse(BaseModel):
    status: str
    document_count: int
    message: str

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "RAG Chatbot API is running",
        "version": "1.0.0"
    }

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status"""
    doc_count = rag_chatbot.get_document_count()
    return StatusResponse(
        status="ready" if doc_count > 0 else "no_documents",
        document_count=doc_count,
        message=f"System ready with {doc_count} document chunks" if doc_count > 0 else "No documents uploaded yet"
    )

@app.post("/sync")
async def sync_documents():
    """Manually trigger a sync of the uploaded_documents folder"""
    try:
        chunk_count = rag_chatbot.sync_folder(str(UPLOAD_DIR))
        return {
            "status": "success",
            "message": f"Sync complete. Total document chunks: {chunk_count}",
            "chunks": chunk_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents (Kept for API compatibility)"""
    try:
        uploaded_files = []
        for file in files:
            if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}. Only PDF and DOCX are supported."
                )
            
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append(str(file_path))
        
        # Sync the entire folder after upload
        chunk_count = rag_chatbot.sync_folder(str(UPLOAD_DIR))
        
        return {
            "status": "success",
            "message": f"Processed {len(uploaded_files)} files. Total chunks: {chunk_count}",
            "files": [f.filename for f in files],
            "chunks": chunk_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the RAG system"""
    try:
        # Get response
        # Note: Chat history is handled by the rag_chatbot.chat method
        response = rag_chatbot.chat(request.question, request.chat_history)
        
        # Extract sources
        sources = []
        for doc in response.get("context", []):
            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                source = os.path.basename(doc.metadata['source'])
                if source not in sources:
                    sources.append(source)
        
        return ChatResponse(
            answer=response["answer"],
            sources=sources
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    """List uploaded documents"""
    files = []
    # Use rglob to find files in subdirectories recursively
    for file_path in UPLOAD_DIR.rglob("*"):
        if file_path.is_file() and (file_path.suffix == ".pdf" or file_path.suffix == ".docx"):
            files.append({
                "name": file_path.name,
                "rel_path": str(file_path.relative_to(UPLOAD_DIR)),
                "size": file_path.stat().st_size,
                "path": str(file_path)
            })
    return {"documents": files, "count": len(files)}

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete an uploaded document"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path.unlink()
    return {"status": "success", "message": f"Deleted {filename}"}

@app.delete("/vectorstore")
async def clear_vectorstore():
    """Clear all documents from vector store"""
    try:
        rag_chatbot.clear_vectorstore()
        return {"status": "success", "message": "Vector store cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
