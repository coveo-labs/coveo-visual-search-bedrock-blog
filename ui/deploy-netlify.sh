#!/bin/bash

set -e

echo "========================================"
echo "Netlify Deployment Script"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo ""
    echo "Please create .env file with:"
    echo "  VITE_API_URL=https://your-api-gateway-url.com/prod"
    echo "  VITE_ENABLE_ANALYTICS=true"
    echo ""
    echo "You can run: ./setup-env.sh"
    exit 1
fi

echo "Step 1: Installing dependencies..."
npm install
echo ""

echo "Step 2: Building production bundle..."
npm run build
echo ""

echo "Step 3: Checking Netlify CLI..."
if ! command -v netlify &> /dev/null; then
    echo "Netlify CLI not found. Installing..."
    npm install -g netlify-cli
fi
echo ""

echo "Step 4: Deploying to Netlify..."
echo ""
echo "Choose deployment option:"
echo "  1. Deploy draft (preview)"
echo "  2. Deploy to production"
echo "  3. Cancel"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Deploying draft..."
        netlify deploy
        ;;
    2)
        echo ""
        echo "Deploying to production..."
        netlify deploy --prod
        ;;
    3)
        echo ""
        echo "Deployment cancelled."
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid choice. Deployment cancelled."
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "✅ Deployment complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Open your Netlify dashboard"
echo "  2. Configure environment variables if needed"
echo "  3. Test your site"
echo ""
