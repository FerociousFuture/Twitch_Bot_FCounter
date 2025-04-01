#!/bin/bash
clear

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install --user twitchio speechrecognition pyaudio configparser || {
    echo "Trying with sudo..."
    sudo pip3 install twitchio speechrecognition pyaudio configparser
}

# Run bot
python3 fuck_counter.py