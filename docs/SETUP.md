# Setup Guide

Complete setup instructions for the Luxury Image Search demo.

## Prerequisites

### Required Software

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **AWS CLI** - [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS SAM CLI** - [Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- **Git** - [Download](https://git-scm.com/)

### AWS Requirements

- AWS Account with appropriate permissions
- IAM user with permissions for:
  - Lambda
  - API Gateway
  - CloudFormation
  - S3
  - Bedrock
  - CloudWatch Logs
- AWS CLI configured with credentials

### AWS Services Setup

#### 1. Amazon OpenSearch Service

Create an OpenSearch domain:

```bash
aws opensearch create-domain \
  --domain-name luxury-image-search \
  --engine-version OpenSearch_2.11 \
  --cluster-config InstanceType=t3.small.search,InstanceCount=1 \
  --ebs-options EBSEnabled=true,VolumeType=gp3,VolumeSize=20 \
  --access-policies '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "*"},
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:ACCOUNT_ID:domain/luxury-image-search/*"
    }]
  }' \
  --region us-east-1
```

Wait for domain to be active (10-15 minutes):

```bash
aws opensearch describe-domain --domain-name luxury-image-search --region us-east-1
```

Note the endpoint from the output.

#### 2. Amazon Bedrock

Enable Bedrock Titan Embeddings model:

1. Go to AWS Console → Bedrock
2. Navigate to "Model access"
3. Click "Manage model access"
4. Enable "Titan Multimodal Embeddings G1"
5. Submit request (usually instant approval)

#### 3. S3 Bucket

Create bucket for images:

```bash
aws s3 mb s3://your-luxury-images-bucket --region us-east-1
```

Upload sample images:

```bash
aws s3 cp ./sample-images/ s3://your-luxury-images-bucket/hermes-images/ --recursive
```

### Coveo Setup

#### 1. Create Coveo Organization

If you don't have one:
1. Go to [Coveo Platform](https://platform.cloud.coveo.com/)
2. Sign up for a trial
3. Note your Organization ID

#### 2. Create API Keys

Create three API keys:

**Push API Key:**
1. Go to Organization → API Keys
2. Create new key
3. Permissions: Push, Edit
4. Note the key

**Search API Key:**
1. Create new key
2. Permissions: Search, Analytics
3. Note the key

**General API Key:**
1. Create new key
2. Permissions: Admin (for IPE)
3. Note the key

#### 3. Create Push Source

1. Go to Sources
2. Add Source → Push
3. Name: "Luxury Products"
4. Note the Source ID

#### 4. Index Sample Data

Use Coveo Push API to index products:

```python
import requests

COVEO_ORG_ID = "your-org-id"
COVEO_PUSH_API_KEY = "your-push-api-key"
COVEO_SOURCE_ID = "your-source-id"

url = f"https://api.cloud.coveo.com/push/v1/organizations/{COVEO_ORG_ID}/sources/{COVEO_SOURCE_ID}/documents"

headers = {
    "Authorization": f"Bearer {COVEO_PUSH_API_KEY}",
    "Content-Type": "application/json"
}

# Sample product
document = {
    "documentId": "product-12345",
    "title": "Luxury Handbag",
    "assetid": "product-12345",
    "description": "Premium leather handbag",
    "category": "Handbags",
    "price": "$2,500",
    "imageurl": "https://your-bucket.s3.amazonaws.com/hermes-images/product-12345.jpg",
    "producturl": "https://hermes.com/product-12345"
}

response = requests.put(url, headers=headers, json=document)
print(response.json())
```

## Project Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd luxury-image-search
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
S3_BUCKET_NAME=your-luxury-images-bucket
S3_IMAGES_PREFIX=hermes-images/

# Amazon Bedrock
BEDROCK_MODEL_ID=amazon.titan-embed-image-v1
BEDROCK_REGION=us-east-1

# Amazon OpenSearch
OPENSEARCH_ENDPOINT=search-luxury-xxxxx.us-east-1.es.amazonaws.com
OPENSEARCH_INDEX_NAME=luxury-image-embeddings
OPENSEARCH_USERNAME=admin
OPENSEARCH_PASSWORD=YourSecurePassword123!

# Coveo Configuration
COVEO_ORGANIZATION_ID=your-org-id
COVEO_API_KEY=your-api-key
COVEO_SEARCH_API_KEY=your-search-api-key
COVEO_PUSH_API_KEY=your-push-api-key
COVEO_SOURCE_ID=your-source-id
COVEO_SEARCH_HUB=LuxuryImageSearch
COVEO_PIPELINE=default

# CloudFormation Stack
STACK_NAME=luxury-image-search-demo

# Demo Configuration
MAX_OPENSEARCH_RESULTS=10
SEARCH_TIMEOUT_SECONDS=30
LOG_OPENSEARCH_RESULTS=true
```

### 3. Install Python Dependencies

```bash
cd backend/embedding_generator
pip install -r requirements.txt
cd ../..
```

### 4. Install UI Dependencies

```bash
cd ui
npm install
cd ..
```

## Verification

Verify your setup:

```bash
# Check AWS CLI
aws sts get-caller-identity

# Check Python
python --version

# Check Node.js
node --version

# Check SAM CLI
sam --version

# Test OpenSearch connection
curl -u admin:password https://your-opensearch-endpoint.amazonaws.com/
```

## Next Steps

Proceed to [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment instructions.

## Troubleshooting

### AWS CLI Not Configured

```bash
aws configure
# Enter your Access Key ID, Secret Access Key, Region
```

### Bedrock Access Denied

Ensure:
1. Model access is enabled in Bedrock console
2. IAM user has `bedrock:InvokeModel` permission
3. Using correct region (us-east-1 or us-west-2)

### OpenSearch Connection Failed

Check:
1. Domain is active
2. Access policy allows your IP
3. Credentials are correct
4. Using HTTPS endpoint

### Coveo API Errors

Verify:
1. API keys are valid
2. Organization ID is correct
3. Source exists and is active
4. API key has required permissions
