# Postman Collection for RAG Chatbot API Testing

## Base URL
http://localhost:8000

---

## 1. Health Check
**GET** `/`

**Response:**
```json
{
  "status": "online",
  "message": "RAG Chatbot API is running",
  "version": "1.0.0"
}
```

---

## 2. System Status
**GET** `/status`

**Response:**
```json
{
  "status": "ready",
  "document_count": 42,
  "message": "System ready with 42 document chunks"
}
```

---

## 3. Upload Documents
**POST** `/upload`

**Headers:**
- Content-Type: multipart/form-data

**Body (form-data):**
- Key: `files`
- Type: File
- Value: Select your PDF or DOCX file(s)

**Response:**
```json
{
  "status": "success",
  "message": "Processed 1 files into 20 chunks",
  "files": ["document.pdf"],
  "chunks": 20
}
```

---

## 4. Chat
**POST** `/chat`

**Headers:**
- Content-Type: application/json

**Body (raw JSON):**
```json
{
  "question": "What are the 3 apps to pin?",
  "chat_history": []
}
```

**Response:**
```json
{
  "answer": "The 3 apps that need to be pinned are: Outlook, OneDrive, and Microsoft Teams.",
  "sources": ["Site Cutover_User Toolkit -Sept 2025.docx"]
}
```

---

## 5. List Documents
**GET** `/documents`

**Response:**
```json
{
  "documents": [
    {
      "name": "document.pdf",
      "size": 1234567,
      "path": "c:\\...\\uploaded_documents\\document.pdf"
    }
  ],
  "count": 1
}
```

---

## 6. Delete Document
**DELETE** `/documents/{filename}`

**Example:** `/documents/document.pdf`

**Response:**
```json
{
  "status": "success",
  "message": "Deleted document.pdf"
}
```

---

## 7. Clear Vector Store
**DELETE** `/vectorstore`

**Response:**
```json
{
  "status": "success",
  "message": "Vector store cleared"
}
```

---

## Testing in Postman

### Import as Collection:
1. Open Postman
2. Click "Import"
3. Paste this file or create requests manually

### Quick Test Sequence:
1. **Health Check** - Verify API is running
2. **Status** - Check if documents are loaded
3. **Upload** - Upload a test document
4. **Status** - Verify document was processed
5. **Chat** - Ask a question
6. **List Documents** - See uploaded files

---

## cURL Examples

### Health Check
```bash
curl http://localhost:8000/
```

### Upload Document
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "files=@document.pdf"
```

### Chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "chat_history": []
  }'
```

### Get Status
```bash
curl http://localhost:8000/status
```

---

## Debugging Tips

### Check Backend Logs
Look at the terminal where `python main.py` is running for error messages.

### Use Swagger UI
Visit: http://localhost:8000/docs
- Interactive API testing
- See all endpoints
- Try requests directly in browser

### Common Errors

**Error: "No documents loaded"**
- Upload documents first using `/upload`

**Error: Connection refused**
- Backend not running
- Check port 8000 is not in use

**Error: 500 Internal Server Error**
- Check backend terminal for stack trace
- Verify all dependencies installed

---

## API Documentation
Full interactive docs: http://localhost:8000/docs
Alternative docs: http://localhost:8000/redoc
