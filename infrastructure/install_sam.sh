#!/bin/bash

echo "Installing AWS SAM CLI for WSL..."

# Download the installer
cd /tmp
wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip

# Unzip the installer
unzip aws-sam-cli-linux-x86_64.zip -d sam-installation

# Install SAM CLI
sudo ./sam-installation/install

# Verify installation
sam --version

# Clean up
rm -rf sam-installation aws-sam-cli-linux-x86_64.zip

echo "✅ AWS SAM CLI installed successfully!"
