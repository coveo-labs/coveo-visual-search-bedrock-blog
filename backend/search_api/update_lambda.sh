#!/bin/bash

# Update Search API Lambda Function
echo "📦 Updating Search API Lambda..."

cd /mnt/d/Projects/Hermes/backend/search_api

# Create deployment package
zip -r function.zip handler.py

# Lambda function name from CloudFormation template
FUNCTION_NAME="luxury-image-search"

echo "🔄 Updating function: $FUNCTION_NAME"

# Update Lambda function code
aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --zip-file fileb://function.zip

echo "✅ Lambda function updated successfully!"

# Clean up
rm function.zip
