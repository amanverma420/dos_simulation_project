#!/bin/bash

echo "Setting up DOS Simulation Environment for Kali Linux..."

# Navigate to project root
cd ~/Desktop/ddos_simulation

# Remove old venv if exists
rm -rf venv

# Create new virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
pip install Flask==2.3.3
pip install psutil==5.9.5

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. cd ~/Desktop/ddos_simulation"
echo "2. source venv/bin/activate"
echo "3. python app.py"
echo ""
echo "Then open your browser to http://localhost:5000"
