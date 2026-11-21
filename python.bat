@echo off
if exist "C:\Users\K.P Sanjana\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    "C:\Users\K.P Sanjana\AppData\Local\Python\pythoncore-3.14-64\python.exe" %*
) else if exist "C:\Users\K.P Sanjana\AppData\Local\Python\bin\python.exe" (
    "C:\Users\K.P Sanjana\AppData\Local\Python\bin\python.exe" %*
) else (
    "C:\Users\K.P Sanjana\AppData\Local\Programs\Python\Python313\python.exe" %*
)
