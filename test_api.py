"""
Quick test script for the RAG chatbot API
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testing RAG Chatbot API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure the backend is running: cd backend && python main.py")
        return
    
    # Test 2: System status
    print("\n2️⃣ Testing system status...")
    try:
        response = requests.get(f"{API_URL}/status")
        status = response.json()
        print(f"✅ Status: {status['status']}")
        print(f"   Documents: {status['document_count']} chunks")
        print(f"   Message: {status['message']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: List documents
    print("\n3️⃣ Testing document list...")
    try:
        response = requests.get(f"{API_URL}/documents")
        docs = response.json()
        print(f"✅ Found {docs['count']} documents")
        for doc in docs['documents']:
            print(f"   📄 {doc['name']} ({doc['size']} bytes)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Chat (if documents exist)
    print("\n4️⃣ Testing chat...")
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "question": "What is this document about?",
                "chat_history": []
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat working!")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Sources: {result['sources']}")
        else:
            print(f"⚠️  Status: {response.status_code}")
            print(f"   Message: {response.json().get('detail', 'No documents uploaded')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API tests complete!")
    print("\n📖 View full API docs at: http://localhost:8000/docs")

if __name__ == "__main__":
    test_api()
