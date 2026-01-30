#!/bin/bash

# Update OpenSearch Master User Password
# Usage: ./update_opensearch_password.sh

DOMAIN_NAME="luxury-image-search-demo-os"
NEW_PASSWORD="CoveoDemo2026!"
REGION="us-east-1"

echo "Updating OpenSearch master user password..."
echo "Domain: $DOMAIN_NAME"
echo "Region: $REGION"

aws opensearch update-domain-config \
  --domain-name "$DOMAIN_NAME" \
  --region "$REGION" \
  --advanced-security-options '{
    "MasterUserOptions": {
      "MasterUserName": "admin",
      "MasterUserPassword": "'"$NEW_PASSWORD"'"
    }
  }'

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Password update initiated successfully!"
    echo ""
    echo "⏳ The update will take 5-10 minutes to complete."
    echo "   You can check the status with:"
    echo "   aws opensearch describe-domain --domain-name $DOMAIN_NAME --region $REGION --query 'DomainStatus.Processing'"
    echo ""
    echo "📝 Update your .env file:"
    echo "   OPENSEARCH_PASSWORD=$NEW_PASSWORD"
else
    echo ""
    echo "❌ Failed to update password"
fi
