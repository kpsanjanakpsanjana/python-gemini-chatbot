@echo off
REM Launcher script for Gemini AI Conversational Chatbot
if exist "C:\Users\K.P Sanjana\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    "C:\Users\K.P Sanjana\AppData\Local\Python\pythoncore-3.14-64\python.exe" "%~dp0BOT.py"
) else if exist "C:\Users\K.P Sanjana\AppData\Local\Python\bin\python.exe" (
    "C:\Users\K.P Sanjana\AppData\Local\Python\bin\python.exe" "%~dp0BOT.py"
) else (
    "C:\Users\K.P Sanjana\AppData\Local\Programs\Python\Python313\python.exe" "%~dp0BOT.py"
)
pause
