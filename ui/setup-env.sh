#!/bin/bash

set -e

echo "========================================"
echo "UI Environment Setup"
echo "========================================"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    echo ""
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Keeping existing .env file."
        exit 0
    fi
fi

echo "Creating .env file..."
echo ""

# Prompt for API Gateway URL
read -p "Enter your API Gateway URL (e.g., https://abc123.execute-api.us-east-1.amazonaws.com/prod): " api_url

# Validate URL
if [ -z "$api_url" ]; then
    echo "❌ Error: API URL cannot be empty!"
    exit 1
fi

# Create .env file
cat > .env << EOF
VITE_API_URL=$api_url
VITE_ENABLE_ANALYTICS=true
EOF

echo ""
echo "========================================"
echo "✅ .env file created successfully!"
echo "========================================"
echo ""
echo "Contents:"
cat .env
echo ""
echo ""
echo "Next steps:"
echo "  1. Verify the API URL is correct"
echo "  2. Run: npm install"
echo "  3. Run: npm run dev (for local testing)"
echo "  4. Run: ./deploy-netlify.sh (to deploy)"
echo ""
