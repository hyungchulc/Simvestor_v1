#!/bin/bash

# Script to set up and run the SimVestor application

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but could not be found. Please install Python 3."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing required packages..."
pip install -r requirements.txt

# Run the Streamlit app
echo "Starting SimVestor application..."
streamlit run app.py

# Note: Ctrl+C to stop the application
