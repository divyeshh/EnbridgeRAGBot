import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from rag_core import RAGChatbot

def debug():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
    
    print("=== RAG INDEXING DEBUGGER ===")
    bot = RAGChatbot(groq_api_key=api_key)
    
    upload_dir = os.path.join(os.getcwd(), "backend", "uploaded_documents")
    print(f"📂 Checking upload directory: {upload_dir}")
    
    if not os.path.exists(upload_dir):
        print(f"❌ Upload directory NOT FOUND at {upload_dir}")
        return

    files = bot.sync_folder(upload_dir)
    print(f"\n✅ Sync result: {files} chunks indexed.")
    
    count = bot.get_document_count()
    print(f"📊 Vector Store reported count: {count} chunks.")
    
    if count > 0:
        print("\n🔍 Testing a generic retrieval...")
        results = bot.retriever.invoke("toolkit")
        print(f"🎯 Found {len(results)} snippets.")
        for i, res in enumerate(results):
            source = os.path.basename(res.metadata.get('source', 'unknown'))
            print(f"   [{i+1}] Source: {source} | Content preview: {res.page_content[:100]}...")
    else:
        print("\n❌ NO CHUNKS IN DATABASE. Something is wrong with the loader or the files.")

if __name__ == "__main__":
    debug()
