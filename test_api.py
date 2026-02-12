import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("--- 🤖 Enbridge Bot API Local Test ---")
    
    # 1. Root Check
    print("\n1. Checking API Root...")
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. System Status
    print("\n2. Checking System Status...")
    r = requests.get(f"{BASE_URL}/status")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")

    # 3. List Documents
    print("\n3. Listing Documents...")
    r = requests.get(f"{BASE_URL}/documents")
    print(f"Status: {r.status_code}")
    docs = r.json().get("documents", [])
    print(f"Found {len(docs)} documents.")

    # 4. Manual Sync
    print("\n4. Triggering Manual Sync...")
    r = requests.post(f"{BASE_URL}/sync")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")

    # 5. Test Chat (Laptop)
    print("\n5. Testing Chat (Laptop Setup)...")
    payload = {
        "question": "how do I setup my enbridge laptop?",
        "chat_history": []
    }
    r = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print("\nAnswer Summary:")
        print(result["answer"][:300] + "...")
        print("\nSources Found:")
        print(result["sources"])
    
    # 6. Test Ambiguity
    print("\n6. Testing Ambiguity Rule...")
    payload = {"question": "setup my device", "chat_history": []}
    r = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(f"Response: {r.json()['answer']}")

if __name__ == "__main__":
    test_api()
