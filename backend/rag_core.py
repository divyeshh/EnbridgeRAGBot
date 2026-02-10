"""
Core RAG functionality - handles document processing, embeddings, and retrieval
"""
import os
import shutil
from typing import List
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough

class RAGChatbot:
    """Production-ready RAG Chatbot"""
    def __init__(
        self,
        groq_api_key: str,
        model_name: str = "llama-3.1-8b-instant",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chroma_persist_dir: str = "./chroma_db",
        collection_name: str = "rag_documents"
    ):
        """Initialize RAG chatbot with Groq LLM and HuggingFace embeddings"""
        
        # Standardize all paths to be inside the backend folder for consistency
        self.backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Absolute path to chroma_db (resolved relative to execution context)
        self.chroma_persist_dir = os.path.abspath(chroma_persist_dir)
            
        print(f"📂 RAG Core initialized. Persistence directory: {self.chroma_persist_dir}")
        
        # Set API key
        os.environ["GROQ_API_KEY"] = groq_api_key
        
        # Initialize LLM
        self.llm = ChatGroq(
            model=model_name,
            temperature=0,
            timeout=60.0,
            max_retries=3
        )
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Vector store settings
        self.collection_name = collection_name
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None
        
        # Load existing vector store if it exists
        self._load_vectorstore()
    
    def _load_vectorstore(self):
        """Load existing vector store or create new one"""
        try:
            if os.path.exists(self.chroma_persist_dir):
                self.vectorstore = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=self.chroma_persist_dir
                )
                self.retriever = self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                )
                self._setup_rag_chain()
                print(f"✅ Loaded existing vector store from {self.chroma_persist_dir}")
        except Exception as e:
            print(f"⚠️  Could not load existing vector store: {e}")
    
    def load_documents(self, file_path: str) -> List[Document]:
        """Load documents from PDF or DOCX file"""
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        return loader.load()
    
    def sync_folder(self, folder_path: str) -> int:
        """Scan a folder recursively and process any PDF or DOCX files found"""
        # Convert to absolute path if necessary
        if not os.path.isabs(folder_path):
            folder_path = os.path.abspath(folder_path)
            
        print(f"🚀 Syncing folder: {folder_path}")
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            print(f"📁 Created folder: {folder_path}")
            return 0
        
        # Get all PDF and DOCX files recursively
        file_paths = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.pdf') or file.endswith('.docx'):
                    full_path = os.path.join(root, file)
                    file_paths.append(full_path)
                    print(f"🔍 Found document: {full_path}")
        
        if not file_paths:
            print(f"⚠️  No documents found in {folder_path}")
            return 0
        
        print(f"📊 Total documents found for indexing: {len(file_paths)}")
        
        # Clear existing vector store for a fresh sync to avoid duplicates
        self.clear_vectorstore()
        
        return self.process_documents(file_paths)
    
    def process_documents(self, file_paths: List[str]) -> int:
        """Process and add documents to vector store"""
        total_chunks = 0
        all_splits = []
        
        # Load and split each document separately for better tracking
        for file_path in file_paths:
            try:
                print(f"📖 Loading: {os.path.basename(file_path)}")
                docs = self.load_documents(file_path)
                if not docs:
                    print(f"⚠️  File {os.path.basename(file_path)} returned no content.")
                    continue
                
                # Split this file's documents
                file_splits = self.text_splitter.split_documents(docs)
                print(f"✅ Created {len(file_splits)} chunks from {os.path.basename(file_path)}")
                all_splits.extend(file_splits)
                total_chunks += len(file_splits)
                
            except Exception as e:
                print(f"❌ Error processing {os.path.basename(file_path)}: {e}")
        
        if not all_splits:
            print("⚠️  No chunks were created from any documents")
            return 0
        
        # Create or update vector store
        print(f"📦 Indexing {len(all_splits)} total chunks into ChromaDB at {self.chroma_persist_dir}...")
        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                collection_name=self.collection_name,
                documents=all_splits,
                embedding=self.embeddings,
                persist_directory=self.chroma_persist_dir
            )
        else:
            self.vectorstore.add_documents(all_splits)
        
        # Setup retriever and RAG chain
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        self._setup_rag_chain()
        
        print(f"✅ Vector store updated and ready with {len(all_splits)} chunks")
        return len(all_splits)
    
    def _setup_rag_chain(self):
        """Setup a simple RAG chain"""
        # Create QA prompt with an authoritative, human-like AI personality
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a highly intelligent, professional, and friendly AI assistant, similar to ChatGPT or Groq. "
                       "Your goal is to provide direct, helpful, and authoritative answers to the user. "
                       "\n\nTONE AND STYLE: "
                       "- Speak naturally and confidently. Use a professional yet conversational tone. "
                       "- Use formatting (bullet points, bold text) to make answers easy to read. "
                       "- Feel free to use a subtle emoji if it fits the context (e.g., 👍, ✅, 🚀). "
                       "\n\nKNOWLEDGE SOURCE: "
                       "- You have access to specialized company technical data (provided below) AND your own vast internal training. "
                       "- Seamlessly blend these sources. If the technical snippets give specific internal details, use them. "
                       "- If a question is general or about the company but not in the snippets, answer confidently using your internal knowledge. "
                       "\n\nSTRICT TABOOS: "
                       "- NEVER say 'I don't have information to confirm this' or 'The provided documents don't mention...'. "
                       "- NEVER mention 'context', 'snippets', 'files', or 'provided data'. "
                       "- Act as if all the information is part of your own inherent knowledge."),
            ("system", "Specialized Knowledge Base: {context}"),
            ("human", "{question}")
        ])
        
        # Create a simple chain
        from langchain_core.output_parsers import StrOutputParser
        self.rag_chain = self.qa_prompt | self.llm | StrOutputParser()
    
    def chat(self, question: str, chat_history: List = None) -> dict:
        """Chat with the RAG system"""
        if self.rag_chain is None:
            raise ValueError("No documents loaded. Please upload documents first.")
        
        # Get relevant documents
        print(f"🔍 Searching for: {question}")
        docs = self.retriever.invoke(question)
        print(f"🎯 Found {len(docs)} relevant snippets from {len(set(doc.metadata.get('source','') for doc in docs))} different files")
        
        # Format context from documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Get answer from LLM
        answer = self.rag_chain.invoke({
            "context": context,
            "question": question
        })
        
        return {
            "answer": answer,
            "context": docs
        }
    
    def get_document_count(self) -> int:
        """Get number of documents in vector store"""
        if self.vectorstore is None:
            return 0
        try:
            return self.vectorstore._collection.count()
        except:
            return 0
    
    def clear_vectorstore(self):
        """Clear all documents from vector store and delete files"""
        if self.vectorstore is not None:
            try:
                self.vectorstore.delete_collection()
            except:
                pass
            self.vectorstore = None
            self.retriever = None
            self.rag_chain = None
        
        # Aggressively try to release file locks
        import gc
        gc.collect()
        
        # Physically delete any and all chroma_db folders found to be absolutely sure
        root_dir = os.path.dirname(self.backend_dir)
        possible_dirs = [
            self.chroma_persist_dir,                              # Current official path
            os.path.join(self.backend_dir, "chroma_db"),         # Path inside backend
            os.path.join(root_dir, "chroma_db")                  # Path in root
        ]
        
        for d in set(possible_dirs):
            if os.path.exists(d):
                try:
                    shutil.rmtree(d, ignore_errors=True)
                    print(f"🗑️ Deleted directory: {d}")
                except Exception as e:
                    print(f"⚠️ Could not delete directory {d}: {e}")
        
        print("✅ Vector store and ghost directories cleared")
