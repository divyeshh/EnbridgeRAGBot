import os
import sys
from dotenv import load_dotenv
from backend.rag_core import RAGChatbot

# Load environment variables
load_dotenv()

def run_test(query: str = None):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found in .env file.")
        return

    print("\n--- Initializing Enbridge Bot Testing Tool ---")
    chatbot = RAGChatbot(groq_api_key=api_key)
    
    # Sync documents
    docs_path = os.path.join(os.getcwd(), "backend", "uploaded_documents")
    chatbot.sync_folder(docs_path)
    
    if query:
        test_query(chatbot, query)
    else:
        # Interactive Mode
        print("\nEntering Interactive Mode (type 'exit' to quit)")
        while True:
            user_input = input("\nUser: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            test_query(chatbot, user_input)

def test_query(chatbot, question):
    print(f"\n--- Testing Question: {question} ---")
    print("Searching for official steps...")
    
    try:
        result = chatbot.chat(question)
        
        print("\n--- RETRIEVED SOURCES ---")
        sources = set()
        for i, doc in enumerate(result.get("context", [])):
            src = os.path.basename(doc.metadata.get("source", "Unknown"))
            pg = doc.metadata.get("page", "?")
            sources.add(f"{src} (Page {pg})")
            if i < 3: # Just show snippet of first 3
                print(f"Snippet {i+1} from {src}: {doc.page_content[:150]}...")
        
        print(f"\nTotal unique sources found: {len(sources)}")
        for s in sorted(sources):
            print(f"- {s}")

        print("\n--- AI ANSWER ---")
        print(result["answer"])
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"Error during query: {e}")

if __name__ == "__main__":
    # If a query is passed as argument, run it once
    if len(sys.argv) > 1:
        single_query = " ".join(sys.argv[1:])
        run_test(single_query)
    else:
        # Otherwise start interactive mode
        run_test()
