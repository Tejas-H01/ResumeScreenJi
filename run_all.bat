@echo off
start "Resume Screening Backend" cmd /k "cd /d ""%~dp0backend"" && if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) && python -m uvicorn main:app --host 127.0.0.1 --port 8000"
start "Resume Screening Frontend" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"
