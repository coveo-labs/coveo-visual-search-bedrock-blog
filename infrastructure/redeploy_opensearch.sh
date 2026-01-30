#!/bin/bash

set -e

echo "🔄 Redeploying OpenSearch with simplified access control..."
echo ""
echo "⚠️  WARNING: This will delete and recreate the OpenSearch domain."
echo "   All existing data will be lost."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

STACK_NAME="luxury-image-search-demo"
REGION="us-east-1"

echo ""
echo "Step 1: Deleting existing stack..."
aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"

echo "Waiting for stack deletion to complete (this may take 10-15 minutes)..."
aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$REGION"

echo ""
echo "✅ Stack deleted successfully!"
echo ""
echo "Step 2: Redeploying with new configuration..."
./deploy.sh
