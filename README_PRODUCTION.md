# Production RAG Chatbot - FastAPI + Streamlit

A production-ready RAG (Retrieval-Augmented Generation) chatbot with FastAPI backend and Streamlit frontend.

## 🚀 Features

- ✅ **Free LLM**: Groq (Llama 3.1 8B) - 14,400 requests/day
- ✅ **Free Embeddings**: HuggingFace (sentence-transformers)
- ✅ **Document Upload**: PDF and DOCX support
- ✅ **Conversational**: Maintains chat history
- ✅ **REST API**: FastAPI backend with Swagger docs
- ✅ **Modern UI**: Streamlit frontend
- ✅ **Production Ready**: Modular architecture

## 📁 Project Structure

```
RAG langchain chatbot/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── rag_core.py          # Core RAG functionality
│   └── uploaded_documents/  # Uploaded files
├── frontend/
│   └── app.py               # Streamlit UI
├── chroma_db/               # Vector database
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🔧 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file is already configured with your Groq API key.

## 🚀 Running the Application

### Option 1: Run Both (Recommended)

**Terminal 1 - Start Backend:**
```bash
cd backend
python main.py
```
Backend will run at: `http://localhost:8000`

**Terminal 2 - Start Frontend:**
```bash
cd frontend
streamlit run app.py
```
Frontend will open automatically in your browser

### Option 2: Run Separately

**Backend Only:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Only:**
```bash
cd frontend
streamlit run app.py
```

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/status` | GET | System status |
| `/upload` | POST | Upload documents |
| `/chat` | POST | Chat with RAG |
| `/documents` | GET | List documents |
| `/documents/{filename}` | DELETE | Delete document |
| `/vectorstore` | DELETE | Clear all data |

### Example API Usage

**Upload Document:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "files=@document.pdf"
```

**Chat:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "chat_history": []
  }'
```

## 🎨 Using the Streamlit UI

1. **Upload Documents**:
   - Click "Browse files" in the sidebar
   - Select PDF or DOCX files
   - Click "Process Documents"

2. **Chat**:
   - Type your question in the chat input
   - View AI responses with source citations
   - Chat history is maintained automatically

3. **Manage Documents**:
   - View uploaded documents in sidebar
   - Delete individual documents
   - Clear all data with one click

## 🔑 Configuration

Edit `.env` to customize:

```env
# Change LLM model
LLM_MODEL=llama-3.1-8b-instant

# Change embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Change API port
API_PORT=8000
```

## 🧪 Testing

**Test Backend:**
```bash
# Health check
curl http://localhost:8000/

# Check status
curl http://localhost:8000/status
```

**Test with Python:**
```python
import requests

# Upload document
files = {"files": open("document.pdf", "rb")}
response = requests.post("http://localhost:8000/upload", files=files)
print(response.json())

# Chat
response = requests.post(
    "http://localhost:8000/chat",
    json={"question": "What is this about?", "chat_history": []}
)
print(response.json())
```

## 📊 Architecture

```
┌─────────────┐      HTTP      ┌──────────────┐
│  Streamlit  │ ────────────▶  │   FastAPI    │
│   Frontend  │                │   Backend    │
└─────────────┘                └──────┬───────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │  RAG Core    │
                               │  - Groq LLM  │
                               │  - HF Embed  │
                               │  - ChromaDB  │
                               └──────────────┘
```

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Change port in .env or run with different port
uvicorn main:app --port 8001
```

**Cannot connect to API:**
- Ensure backend is running
- Check `API_URL` in frontend matches backend URL

**Module not found:**
```bash
pip install -r requirements.txt
```

**Groq API errors:**
- Check your API key in `.env`
- Verify you haven't exceeded rate limits (14,400/day)

## 🚀 Deployment

### Deploy Backend (FastAPI)

**Using Docker:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Using Railway/Render:**
- Deploy `backend/` directory
- Set environment variables from `.env`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Deploy Frontend (Streamlit)

**Streamlit Cloud:**
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Set `API_URL` to your backend URL

## 📝 License

This project uses:
- Groq API (free tier)
- HuggingFace models (Apache 2.0)
- LangChain (MIT)

## 🆘 Support

- **Backend Issues**: Check `http://localhost:8000/docs`
- **Frontend Issues**: Check Streamlit terminal output
- **API Errors**: Enable LangSmith tracing in `.env`

---

**Built with ❤️ using Groq, HuggingFace, FastAPI, and Streamlit**
