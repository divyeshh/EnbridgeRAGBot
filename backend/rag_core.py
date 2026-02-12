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
        
        # Persistence directory (None for in-memory mode)
        if chroma_persist_dir:
            self.chroma_persist_dir = os.path.abspath(chroma_persist_dir)
        else:
            self.chroma_persist_dir = None
            
        print(f"RAG Core initialized. Mode: {'Persistent' if self.chroma_persist_dir else 'In-Memory'}")
        
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
        
        # Initialize text splitter (Title-aware chunks)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=400,
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
                print(f"Loaded existing vector store from {self.chroma_persist_dir}")
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
            
        print(f"Syncing folder: {folder_path}")
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder_path}")
            return 0
        
        # Get all PDF and DOCX files recursively
        file_paths = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.pdf') or file.endswith('.docx'):
                    full_path = os.path.join(root, file)
                    file_paths.append(full_path)
                    print(f"Found document: {full_path}")
        
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
                print(f"Loading: {os.path.basename(file_path)}")
                docs = self.load_documents(file_path)
                if not docs:
                    print(f"⚠️  File {os.path.basename(file_path)} returned no content.")
                    continue
                
                # Split this file's documents
                file_splits = self.text_splitter.split_documents(docs)
                
                # Prepend Title to every chunk for better retrieval hits
                doc_title = os.path.basename(file_path).replace(".pdf", "").replace("Job Aid_", "")
                for split in file_splits:
                    split.page_content = f"[Manual: {doc_title}] Page {split.metadata.get('page', '?')}\n{split.page_content}"
                
                print(f"Created {len(file_splits)} title-aware chunks from {os.path.basename(file_path)}")
                all_splits.extend(file_splits)
                total_chunks += len(file_splits)
                
            except Exception as e:
                print(f"❌ Error processing {os.path.basename(file_path)}: {e}")
        
        if not all_splits:
            print("⚠️  No chunks were created from any documents")
            return 0
        
        # Create or update vector store
        print(f"Indexing {len(all_splits)} total chunks into ChromaDB...")
        if self.vectorstore is None:
            kwargs = {
                "collection_name": self.collection_name,
                "documents": all_splits,
                "embedding": self.embeddings
            }
            # Only add persist_directory if we have a path
            if self.chroma_persist_dir:
                kwargs["persist_directory"] = self.chroma_persist_dir
                
            self.vectorstore = Chroma.from_documents(**kwargs)
        else:
            self.vectorstore.add_documents(all_splits)
        
        # Setup retriever and RAG chain (High-depth for reranking)
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 40}
        )
        self._setup_rag_chain()
        
        print(f"Vector store updated and ready with {len(all_splits)} chunks")
        return len(all_splits)
    
    def _setup_rag_chain(self):
        """Setup a simple RAG chain"""
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a warm internal IT support assistant. "
                       "\n\nAMBIGUITY RULE: "
                       "- If query is 'setup device' without 'Laptop' or 'Mobile', ask: 'Are you setting up your Enbridge Laptop or your Mobile device?' "
                       "\n\nGROUNDING & 'HYPER-DETAIL' RULES: "
                       "- **NEVER SUMMARIZE**: You must reproduce the steps EXACTLY. If the manual has i, ii, iii or a, b, c, you MUST include every one of them in a nested list. "
                       "- **LAPTOP MASTER SEQUENCE**: "
                       "  1. Power & Connect (Plug in, login). "
                       "  2. VPN (Global Protect & Secure Connect). "
                       "  3. Pinning Apps (Outlook/OneDrive/Teams). "
                       "  4. **Rule Import (Page 6/7)**: Include ALL sub-steps (Navigate to ELink, Download rule file, Right-click Inbox -> New Folder 'Inbox External', Manage Rules -> Options -> Import). Then include **Step 5: Verify Folder** (Choose 'Inbox' then 'Inbox External', click OK) and **Step 6: Finalize Rule** (Select 'Apply' then 'OK'). "
                       "  5. DE VDI/VDI (VMware Horizon). "
                       "  6. Printer (Windows+R, \\\\enbpazcwldd001). "
                       "  7. Gnetwork. 8. Software Center. "
                       "- **MOBILE MASTER SEQUENCE**: "
                       "  1. Power & Language/Country. 2. 'Set Up Without Another Device'. 3. Wi-Fi. 4. 'Don't Transfer Apps'. 5. Sign in with Enbridge ID. 6. Okta Authenticate. 7. Company Portal Setup. "
                       "- **UNIVERSAL INQUIRY RULE**: Use provided knowledge for ANY inquiry (backups, resets, apps, etc.). Always prioritize manuals. "
                       "- **SMART FALLBACK**: If information is NOT in the manuals, provide general IT guidance but prefix with: 'Note: This specific information is not in our official manuals, but here is some general IT guidance...' "
                       "\n\nVDI NOTE: Skip 'Citrix' for laptops; focus on 'VMware Horizon'. "
                       "\n\nSTYLE: Simple English, friendly. No mentions of 'context' or 'snippets'. Do not summarize procedures."),
            ("system", "Internal Support Knowledge: {context}"),
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
        print(f"Searching for: {question}")
        raw_docs = self.retriever.invoke(question)
        
        # DEEP RERANKING: Boost by filename OR sequence (Page 0/1)
        q_lower = question.lower()
        scored_docs = []
        for doc in raw_docs:
            source = os.path.basename(doc.metadata.get("source", "")).lower()
            page = doc.metadata.get("page", 0)
            score = 0
            
            # FILENAME & KEYWORD BOOST
            if "setup" in q_lower and "set-up" in source: score += 10
            
            # LAPTOP TOOLKIT SUPER-BOOST: If query is about laptop, give ALL toolkit pages huge priority
            if "laptop" in q_lower:
                if "toolkit" in source or "productivity" in source or "cutover" in source:
                    score += 100 # This ensures toolkit chunks rank first
                elif "mobile" in source or "set-up" in source or "job aid" in source:
                    score -= 50  # Deprioritize mobile if laptop is requested
            
            if "mobile" in q_lower or "iphone" in q_lower:
                if "mobile" in source or "set-up" in source or "job aid" in source:
                    score += 60
                elif "toolkit" in source or "laptop" in source:
                    score -= 50 # Deprioritize laptop if mobile is requested

            if "backup" in q_lower and "backup" in source: score += 20
            if "reset" in q_lower and "reset" in source: score += 20
            
            # Sequence Boost: Page 0/1 is the start of the procedure
            if page <= 1: score += 20
            elif page <= 3: score += 10
            
            scored_docs.append((score, doc))
        
        # Sort by boosted score
        reranked_docs = [d[1] for d in sorted(scored_docs, key=lambda x: x[0], reverse=True)]
        
        # OPTIMIZED CONTEXT: 18 snippets to cover 16-page manuals while staying under 6000 tokens
        final_docs = reranked_docs[:18]
        
        # SORT DOCS: Group by source and sort by page number
        def sort_key(doc):
            source = doc.metadata.get("source", "")
            page = doc.metadata.get("page", 0)
            return (source, page)
        
        docs = sorted(final_docs, key=sort_key)
        
        print(f"Found {len(docs)} deep-matched snippets from {len(set(doc.metadata.get('source','') for doc in docs))} different files")
        
        # Format context from documents
        context = ""
        for i, doc in enumerate(docs):
            source_name = os.path.basename(doc.metadata.get('source', 'Manual'))
            page_num = doc.metadata.get('page', '?')
            context += f"--- Source: {source_name} (Page {page_num}) ---\n"
            context += doc.page_content + "\n\n"
        
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
        """Clear all documents from vector store"""
        if self.vectorstore is not None:
            try:
                # Soft reset the vectorstore if possible
                if hasattr(self.vectorstore, 'delete_collection'):
                    self.vectorstore.delete_collection()
            except:
                pass
            self.vectorstore = None
            self.retriever = None
            self.rag_chain = None
        
        # Aggressively try to release file locks
        import gc
        gc.collect()
        
        # Physically delete the directory ONLY if we are in persistence mode
        if self.chroma_persist_dir and os.path.exists(self.chroma_persist_dir):
            try:
                shutil.rmtree(self.chroma_persist_dir, ignore_errors=True)
                print(f"🗑️ Deleted directory: {self.chroma_persist_dir}")
            except Exception as e:
                print(f"⚠️ Could not delete directory {self.chroma_persist_dir}: {e}")
        
        print(f"✅ Vector store cleared (Mode: {'Persistent' if self.chroma_persist_dir else 'In-Memory'})")
