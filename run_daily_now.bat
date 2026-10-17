@echo off
title Internship Hunter - Daily Scan
cd /d "E:\CV hunter Webapp"
set PYTHONIOENCODING=utf-8
".\.venv\Scripts\python.exe" daily_runner.py
pause
