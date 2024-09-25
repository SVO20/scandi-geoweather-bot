#!/bin/bash

# Check Python version (must be 3.9 or higher)
REQUIRED_PYTHON_VERSION="3.9"
CURRENT_PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')

if [[ $(echo "$CURRENT_PYTHON_VERSION < $REQUIRED_PYTHON_VERSION" | bc -l) -eq 1 ]]; then
    echo "Python $REQUIRED_PYTHON_VERSION or higher is required. Current version: $CURRENT_PYTHON_VERSION"
    exit 1
else
    echo "Python version $CURRENT_PYTHON_VERSION is OK."
fi

# Upgrading pip and installing Python dependencies
echo "Upgrading pip and installing Python dependencies from requirements.txt..."
pip install --upgrade pip && pip install -r requirements.txt

# Check if pip and requirements installation was successful
if [ $? -eq 0 ]; then
    echo "Pip and requirements installed successfully."
else
    echo "Failed to install pip or requirements."
    exit 1
fi

# Updating package list and installing Cairo libraries
echo "Updating package list and installing Cairo libraries..."
sudo apt-get update
sudo apt-get install -y libcairo2 libcairo2-dev

# Check if Cairo libraries were installed successfully
if [ $? -eq 0 ]; then
    echo "Cairo libraries installed successfully."
else
    echo "Failed to install Cairo libraries."
    exit 1
fi

# Running Python setup.py
echo "Running setup.py..."
python3 setup.py

# Check if setup.py executed successfully
if [ $? -eq 0 ]; then
    echo "setup.py executed successfully."
else
    echo "setup.py execution failed."
    exit 1
fi
