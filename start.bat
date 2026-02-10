@echo off
REM Start FastAPI Backend
echo Starting FastAPI Backend...
cd backend
start cmd /k "python main.py"
timeout /t 3

REM Start Streamlit Frontend
echo Starting Streamlit Frontend...
cd ..\frontend
start cmd /k "streamlit run app.py"

echo.
echo ========================================
echo   RAG Chatbot Started!
echo ========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:8501
echo   API Docs: http://localhost:8000/docs
echo ========================================
