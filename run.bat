@echo off
title Fuck Counter Bot Installer

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python 3.9...
    curl -o %temp%\python-installer.exe https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe
    start /wait %temp%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del %temp%\python-installer.exe
)

:: Install dependencies
echo Installing required packages...
pip install twitchio speechrecognition pyaudio configparser

:: Run bot
python fuck_counter.py
pause