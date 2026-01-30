#!/bin/bash

echo "========================================"
echo "Scraper Configuration Setup"
echo "========================================"
echo ""

# Check if .env exists in parent directory
if [ ! -f ../.env ]; then
    echo "❌ Error: .env file not found in project root"
    echo ""
    echo "Please create .env file first:"
    echo "  cd .."
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

echo "✓ Found .env file"
echo ""

# Load current values
source ../.env

echo "Current Configuration:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check AWS configuration
echo "AWS Configuration:"
if [ "$S3_BUCKET_NAME" = "your-images-bucket" ] || [ -z "$S3_BUCKET_NAME" ]; then
    echo "  ❌ S3_BUCKET_NAME: Not configured"
    NEEDS_CONFIG=true
else
    echo "  ✓ S3_BUCKET_NAME: $S3_BUCKET_NAME"
fi

if [ -z "$AWS_REGION" ]; then
    echo "  ❌ AWS_REGION: Not configured"
    NEEDS_CONFIG=true
else
    echo "  ✓ AWS_REGION: $AWS_REGION"
fi

echo ""

# Check Coveo configuration
echo "Coveo Configuration:"
if [ "$COVEO_ORGANIZATION_ID" = "your-org-id" ] || [ -z "$COVEO_ORGANIZATION_ID" ]; then
    echo "  ❌ COVEO_ORGANIZATION_ID: Not configured"
    NEEDS_CONFIG=true
else
    echo "  ✓ COVEO_ORGANIZATION_ID: $COVEO_ORGANIZATION_ID"
fi

if [ "$COVEO_PUSH_API_KEY" = "your-push-api-key" ] || [ -z "$COVEO_PUSH_API_KEY" ]; then
    echo "  ❌ COVEO_PUSH_API_KEY: Not configured"
    NEEDS_CONFIG=true
else
    echo "  ✓ COVEO_PUSH_API_KEY: ${COVEO_PUSH_API_KEY:0:10}..."
fi

if [ "$COVEO_SOURCE_ID" = "your-source-id" ] || [ -z "$COVEO_SOURCE_ID" ]; then
    echo "  ❌ COVEO_SOURCE_ID: Not configured"
    NEEDS_CONFIG=true
else
    echo "  ✓ COVEO_SOURCE_ID: $COVEO_SOURCE_ID"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$NEEDS_CONFIG" = "true" ]; then
    echo "⚠️  Configuration incomplete!"
    echo ""
    echo "Please update your .env file with actual values:"
    echo ""
    echo "1. Create S3 bucket:"
    echo "   aws s3 mb s3://your-unique-bucket-name"
    echo ""
    echo "2. Update .env file:"
    echo "   nano ../.env"
    echo ""
    echo "   Required variables:"
    echo "   - S3_BUCKET_NAME=your-unique-bucket-name"
    echo "   - AWS_REGION=us-east-1"
    echo "   - COVEO_ORGANIZATION_ID=your-actual-org-id"
    echo "   - COVEO_PUSH_API_KEY=your-actual-api-key"
    echo "   - COVEO_SOURCE_ID=your-actual-source-id"
    echo ""
    echo "3. Get Coveo credentials:"
    echo "   - Log in to Coveo Platform"
    echo "   - Go to Organization → API Keys"
    echo "   - Create Push API key"
    echo "   - Go to Sources → Your Source → Copy Source ID"
    echo ""
    exit 1
else
    echo "✅ Configuration looks good!"
    echo ""
    echo "Next steps:"
    echo "  1. Verify S3 bucket exists:"
    echo "     aws s3 ls s3://$S3_BUCKET_NAME"
    echo ""
    echo "  2. Run the scraper pipeline:"
    echo "     python run_pipeline.py"
    echo ""
fi
