@echo off
setlocal
echo ======================================================
echo  GitHub Deploy Script (Nuclear Reset Version)
echo ======================================================

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] git is not installed or not in PATH.
    pause
    exit /b 1
)

set /p repo_url="Enter GitHub Repo URL: "

echo [INFO] Hard resetting git history to remove large files...
rd /s /q .git >nul 2>nul

echo [INFO] Initializing fresh git...
git init

REM Set identity
git config --local user.email "owner@example.com"
git config --local user.name "Project Owner"

echo [INFO] Adding files (clean list)...
git add .

echo [INFO] Committing fresh start...
git commit -m "Initial commit: Lightweight 24/7 Machine"

echo [INFO] Setting branch to main...
git branch -M main

echo [INFO] Setting remote origin...
git remote add origin %repo_url%

echo [INFO] Pushing to GitHub (Force Clean)...
git push -u origin main --force

if %ERRORLEVEL% neq 0 (
    echo.
    echo [FAILED] Push failed. Check the error message above.
) else (
    echo.
    echo [SUCCESS] Upload completed successfully!
)

pause
