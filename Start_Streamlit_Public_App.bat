@echo off
title AI Internship Hunter - Streamlit Public Web UI
echo =========================================================
echo   Starting AI Internship Hunter (Streamlit Web UI)...
echo   Your browser will open automatically at http://localhost:8501
echo   Press Ctrl+C or close this window to stop.
echo =========================================================
cd /d "E:\CV hunter Webapp"
set PYTHONIOENCODING=utf-8
".\.venv\Scripts\streamlit.exe" run streamlit_app.py
pause
