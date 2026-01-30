#!/bin/bash

set -e

echo "🔄 Recreating Stack with Simplified OpenSearch Configuration"
echo "============================================================"
echo ""
echo "This will:"
echo "  1. Delete the existing CloudFormation stack"
echo "  2. Redeploy with OpenSearch (no fine-grained access control)"
echo "  3. Use AWS IAM for authentication (simpler and more secure)"
echo ""
echo "⚠️  WARNING: All existing OpenSearch data will be lost."
echo "   (This is OK since we haven't indexed embeddings yet)"
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

echo "⏳ Waiting for stack deletion (10-15 minutes)..."
echo "   You can monitor progress in AWS Console:"
echo "   https://console.aws.amazon.com/cloudformation"
echo ""

aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$REGION" 2>/dev/null || {
    echo "Checking if stack is already deleted..."
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" 2>/dev/null; then
        echo "❌ Stack deletion failed. Check AWS Console for details."
        exit 1
    else
        echo "✅ Stack already deleted or doesn't exist"
    fi
}

echo ""
echo "✅ Stack deleted successfully!"
echo ""
echo "Step 2: Redeploying with new configuration..."
echo ""

./deploy.sh

echo ""
echo "============================================================"
echo "✅ Deployment Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Wait 2-3 minutes for OpenSearch to be fully ready"
echo "  2. Test connection: cd ../backend/embedding_generator && python test_opensearch_connection.py"
echo "  3. Generate embeddings: python generate_embeddings.py"
echo ""
