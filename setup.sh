#!/bin/bash
echo "========================================="
echo "SO Descentralizado - Setup Script"
echo "========================================="

echo "[1/3] Updating system..."
sudo apt-get update -y

echo "[2/3] Installing dependencies..."
sudo apt-get install -y build-essential python3-pip net-tools htop

echo "[3/3] Installing Python libraries..."
pip3 install numpy psutil

echo ""
echo "Setup completed successfully!"
