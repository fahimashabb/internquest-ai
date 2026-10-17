@echo off
setlocal enabledelayedexpansion
title Push to GitHub - fahimashabb

echo ========================================================
echo   Pushing InternQuest AI to GitHub Profile:
echo   https://github.com/fahimashabb
echo ========================================================
echo.

set GIT_EXE="%LOCALAPPDATA%\Programs\MinGit\cmd\git.exe"
if not exist %GIT_EXE% (
    set GIT_EXE=git
)

echo [1/3] Checking Git Status...
cd /d "E:\CV hunter Webapp"
%GIT_EXE% status --short

echo.
echo [2/3] Configuring Remote Origin for https://github.com/fahimashabb/internquest-ai.git ...
%GIT_EXE% remote remove origin >nul 2>&1
%GIT_EXE% remote add origin https://github.com/fahimashabb/internquest-ai.git
%GIT_EXE% branch -M main

echo.
echo [3/3] Pushing to GitHub (origin main)...
echo If a GitHub login window appears, please authorize your account.
echo.

%GIT_EXE% push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo   SUCCESS! Your repository is live at:
    echo   https://github.com/fahimashabb/internquest-ai
    echo ========================================================
    echo.
    echo Next step: Deploy free on Streamlit Cloud:
    echo 1. Open https://share.streamlit.io
    echo 2. Select repository: fahimashabb/internquest-ai
    echo 3. Set file to: streamlit_app.py
    echo 4. Click Deploy!
    echo.
) else (
    echo.
    echo [NOTE] Push failed. Make sure you created an EMPTY repository named
    echo        'internquest-ai' at https://github.com/new first!
    echo.
)

pause
