#!/bin/bash

set -e

echo "🗑️  Destroying Luxury Image Search Infrastructure..."

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
else
    echo "❌ Error: .env file not found."
    exit 1
fi

if [ -z "$STACK_NAME" ]; then
    echo "❌ Error: STACK_NAME is not set in .env file"
    exit 1
fi

if [ -z "$AWS_REGION" ]; then
    echo "❌ Error: AWS_REGION is not set in .env file"
    exit 1
fi

echo "⚠️  WARNING: This will delete the CloudFormation stack: $STACK_NAME"
echo "⚠️  Region: $AWS_REGION"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Destruction cancelled"
    exit 0
fi

echo "🗑️  Deleting CloudFormation stack..."
aws cloudformation delete-stack \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION"

echo "⏳ Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION"

echo ""
echo "✅ Stack deleted successfully!"
echo ""
echo "🧹 Manual cleanup (if needed):"
echo "  - OpenSearch domain (not managed by this stack)"
echo "  - S3 bucket with images (not managed by this stack)"
echo "  - CloudWatch Logs (retained for 7 days)"
echo ""
