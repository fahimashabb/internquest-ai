@echo off
title Fahim's AI Internship Assistant
echo =========================================================
echo   Starting Fahim's AI Internship Assistant...
echo   Your browser will open automatically.
echo   Keep this window open while using the dashboard.
echo   Press Ctrl+C or close this window to stop.
echo =========================================================
cd /d "E:\CV hunter Webapp"
set PYTHONIOENCODING=utf-8
".\.venv\Scripts\python.exe" web_server.py
pause
