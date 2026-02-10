# RAG Chatbot with Groq & HuggingFace

A free, production-ready RAG (Retrieval-Augmented Generation) chatbot using:
- **Groq** for LLM (Llama 3.1 70B) - 14,400 free requests/day
- **HuggingFace** for embeddings (all-MiniLM-L6-v2) - 100% free, runs locally
- **LangChain** for orchestration
- **Chroma** for vector storage

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install langchain langchain-groq langchain-huggingface langchain-core langchain_community langchain_chroma docx2txt pypdf sentence_transformers
```

### 2. Set Up API Keys

Your Groq API key is already configured in the notebook. For production use:

```python
import os
os.environ["GROQ_API_KEY"] = "your-groq-api-key"
```

### 3. Run the Notebook

Open `LangChain_Conversational_RAG_Crash_Course_From_Basics_to_Production_Part_1.ipynb` and run all cells.

## 📊 API Keys

### Groq (Required)
- **Key**: `your_groq_api_key_here`
- **Free Tier**: 14,400 requests/day, 7,000 requests/minute
- **Model**: Llama 3.1 70B Versatile

### LangSmith (Optional - for debugging)
- **Key**: `your_langsmith_api_key_here`
- **Status**: Disabled by default (paid service)
- **Enable**: Set `LANGCHAIN_TRACING_V2=true` in environment

## 🧪 Testing

Run the test script to verify everything works:

```bash
python test_groq_migration.py
```

Expected output:
```
✅ Groq LLM: Working (Llama 3.1 70B)
✅ HuggingFace Embeddings: Working (384 dimensions)
```

## 📁 Project Structure

```
RAG langchain chatbot/
├── LangChain_Conversational_RAG_Crash_Course_From_Basics_to_Production_Part_1.ipynb  # Main notebook
├── migrate_to_groq.py           # Migration script
├── test_groq_migration.py       # Test script
├── .env.example                 # API keys template
└── README.md                    # This file
```

## 💡 Features

- ✅ **100% Free**: No API costs with Groq free tier
- ✅ **Fast**: Groq provides ~500 tokens/second
- ✅ **Local Embeddings**: HuggingFace runs on your machine
- ✅ **Production Ready**: Full RAG pipeline with vector storage
- ✅ **Conversational**: Handles follow-up questions with context

## 🔧 Configuration

### Enable LangSmith Monitoring (Optional)

If you want to monitor your LLM calls for debugging:

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_api_key_here"
os.environ["LANGCHAIN_PROJECT"] = "rag-chatbot-dev"
```

**Note**: LangSmith is a paid service. Only enable if needed for development.

## 📚 Documentation

See `walkthrough.md` in the artifacts folder for detailed migration documentation.

## 🎯 Next Steps

1. **Add Your Documents**: Place PDF/DOCX files in a `docs/` folder
2. **Customize Prompts**: Modify the system prompts in the notebook
3. **Deploy**: Use FastAPI to create a REST API (see Part 2 of the course)
4. **Build UI**: Create a Streamlit interface for end users

## 🆘 Troubleshooting

### "Module not found" errors
```bash
pip install langchain-groq langchain-huggingface sentence-transformers
```

### Slow first run
HuggingFace downloads the embedding model (~80MB) on first run. Subsequent runs are fast.

### Rate limits
Groq free tier: 14,400 requests/day. If exceeded, wait 24 hours or upgrade.

## 📝 License

This project uses:
- Groq API (free tier)
- HuggingFace models (Apache 2.0)
- LangChain (MIT)
