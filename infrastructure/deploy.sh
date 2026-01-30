#!/bin/bash

set -e

echo "🚀 Deploying Luxury Image Search Infrastructure..."

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
else
    echo "❌ Error: .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Validate required variables
required_vars=(
    "AWS_REGION"
    "S3_BUCKET_NAME"
    "OPENSEARCH_PASSWORD"
    "COVEO_ORGANIZATION_ID"
    "COVEO_PUSH_API_KEY"
    "COVEO_SEARCH_API_KEY"
    "STACK_NAME"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set in .env file"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Build Lambda layer
echo "📦 Building Lambda dependencies layer..."
cd ../backend/layer
mkdir -p python
pip install -r requirements.txt -t python/ --upgrade
cd ../../infrastructure

# Package and deploy with SAM
echo "📦 Packaging application..."
sam build --template-file template.yaml

echo "🚀 Deploying CloudFormation stack: $STACK_NAME..."
sam deploy \
    --template-file .aws-sam/build/template.yaml \
    --stack-name "$STACK_NAME" \
    --capabilities CAPABILITY_IAM \
    --region "$AWS_REGION" \
    --parameter-overrides \
        S3BucketName="$S3_BUCKET_NAME" \
        OpenSearchPassword="$OPENSEARCH_PASSWORD" \
        OpenSearchInstanceType="${OPENSEARCH_INSTANCE_TYPE:-t3.small.search}" \
        OpenSearchVolumeSize="${OPENSEARCH_VOLUME_SIZE:-10}" \
        CoveoOrgId="$COVEO_ORGANIZATION_ID" \
        CoveoPushApiKey="$COVEO_PUSH_API_KEY" \
        CoveoSearchApiKey="$COVEO_SEARCH_API_KEY" \
    --resolve-s3 \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

# Get outputs
echo "📋 Retrieving stack outputs..."
OPENSEARCH_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchEndpoint`].OutputValue' \
    --output text)

API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

IPE_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`IPEExtensionUrl`].OutputValue' \
    --output text)

OPENSEARCH_DASHBOARD=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchDashboard`].OutputValue' \
    --output text)

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📝 Stack Outputs:"
echo "  OpenSearch Endpoint: $OPENSEARCH_ENDPOINT"
echo "  OpenSearch Dashboard: $OPENSEARCH_DASHBOARD"
echo "  API Endpoint: $API_ENDPOINT"
echo "  IPE Extension URL: $IPE_URL"
echo ""
echo "🔧 Next Steps:"
echo "  1. Wait 10-15 minutes for OpenSearch domain to be ready"
echo "  2. Update .env file with:"
echo "     OPENSEARCH_ENDPOINT=$OPENSEARCH_ENDPOINT"
echo "     API_GATEWAY_URL=$API_ENDPOINT"
echo "  3. Configure Coveo IPE Extension with URL: $IPE_URL"
echo "  4. Run embedding generator: cd ../backend/embedding_generator && python generate_embeddings.py"
echo "  5. Deploy UI: cd ../ui && npm run build"
echo ""
