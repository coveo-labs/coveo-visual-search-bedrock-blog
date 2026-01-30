#!/bin/bash

# Update OpenSearch Access Policy to allow your IAM role
# This grants your current IAM user/role access to OpenSearch

DOMAIN_NAME="luxury-image-search-demo-os"
REGION="us-east-1"

echo "Getting your current IAM identity..."
CALLER_IDENTITY=$(aws sts get-caller-identity)
ACCOUNT_ID=$(echo $CALLER_IDENTITY | jq -r '.Account')
USER_ARN=$(echo $CALLER_IDENTITY | jq -r '.Arn')

echo "Account ID: $ACCOUNT_ID"
echo "Your ARN: $USER_ARN"
echo ""

# Extract the role ARN (remove the assumed-role session part if present)
if [[ $USER_ARN == *"assumed-role"* ]]; then
    # Extract role name from assumed-role ARN
    ROLE_NAME=$(echo $USER_ARN | cut -d'/' -f2)
    ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/aws-reserved/sso.amazonaws.com/${ROLE_NAME}"
    echo "Detected SSO Role: $ROLE_ARN"
else
    ROLE_ARN=$USER_ARN
fi

echo ""
echo "Updating OpenSearch access policy..."

aws opensearch update-domain-config \
  --domain-name "$DOMAIN_NAME" \
  --region "$REGION" \
  --access-policies "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [
      {
        \"Effect\": \"Allow\",
        \"Principal\": {
          \"AWS\": \"*\"
        },
        \"Action\": \"es:*\",
        \"Resource\": \"arn:aws:es:${REGION}:${ACCOUNT_ID}:domain/${DOMAIN_NAME}/*\"
      }
    ]
  }"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Access policy update initiated!"
    echo ""
    echo "⏳ The update will take 5-10 minutes to complete."
    echo ""
    echo "📝 Note: With fine-grained access control enabled, you also need to"
    echo "   map your IAM role in OpenSearch Dashboards:"
    echo ""
    echo "   1. Go to: https://search-${DOMAIN_NAME}-*.${REGION}.es.amazonaws.com/_dashboards"
    echo "   2. Login with admin / CoveoDemo2026!"
    echo "   3. Go to: Security → Roles → all_access → Mapped users"
    echo "   4. Add backend role: ${ROLE_ARN}"
    echo ""
else
    echo ""
    echo "❌ Failed to update access policy"
fi
