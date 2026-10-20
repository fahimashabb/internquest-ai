@echo off
title Publish to GitHub - BizIntern BD
echo ========================================================
echo   Syncing and Publishing BizIntern BD to GitHub...
echo ========================================================
cd /d "%~dp0"
git add .
git commit -m "update: refresh business internship listings and web app"
git push origin main
echo ========================================================
echo   Successfully published to GitHub Pages!
echo   Visit: https://fahimashabb.github.io/internquest-ai/
echo ========================================================
pause
