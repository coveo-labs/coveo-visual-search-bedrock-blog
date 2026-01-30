#!/bin/bash

# Fix OpenSearch Access Policy
# This updates the access policy to allow all AWS principals

DOMAIN_NAME="luxury-image-search-demo-os"
REGION="us-east-1"

echo "Updating OpenSearch access policy to allow all AWS principals..."

aws opensearch update-domain-config \
  --domain-name "$DOMAIN_NAME" \
  --region "$REGION" \
  --access-policies file://opensearch-access-policy.json

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Access policy update initiated!"
    echo ""
    echo "⏳ Wait 5-10 minutes for the update to complete, then run:"
    echo "   cd ../backend/embedding_generator"
    echo "   python test_opensearch_connection.py"
    echo ""
    echo "📝 Check update status:"
    echo "   aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION --query 'DomainStatus.Processing'"
else
    echo ""
    echo "❌ Failed to update access policy"
fi
