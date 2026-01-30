# Deployment Guide

Step-by-step deployment instructions for the Luxury Image Search demo.

## Prerequisites

Complete [SETUP.md](./SETUP.md) before proceeding.

## Deployment Steps

### Step 1: Deploy AWS Infrastructure

Deploy Lambda functions, API Gateway, and related resources:

```bash
cd infrastructure
chmod +x deploy.sh destroy.sh
./deploy.sh
```

The script will:
1. Validate environment variables
2. Build Lambda layer with dependencies
3. Package Lambda functions
4. Deploy CloudFormation stack
5. Output API endpoints

Expected output:
```
✅ Deployment completed successfully!

📝 Stack Outputs:
  API Endpoint: https://abc123.execute-api.us-east-1.amazonaws.com/prod
  IPE Extension URL: https://xyz789.lambda-url.us-east-1.on.aws/

🔧 Next Steps:
  1. Update .env file with API_GATEWAY_URL=...
  2. Configure Coveo IPE Extension with URL: ...
  3. Run embedding generator
  4. Deploy UI
```

### Step 2: Update Environment Variables

Update `.env` file with the API endpoint:

```bash
# Add this line to .env
API_GATEWAY_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

Update UI environment:

```bash
cd ui
cp .env.example .env
```

Edit `ui/.env`:
```
VITE_API_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod
VITE_ENABLE_ANALYTICS=true
```

### Step 3: Generate Embeddings

Pre-compute embeddings for all images in S3:

```bash
cd backend/embedding_generator
python generate_embeddings.py
```

Expected output:
```
================================================================================
Luxury Image Search - Embedding Generator
================================================================================

Configuration:
  S3 Bucket: your-luxury-images-bucket
  S3 Prefix: hermes-images/
  OpenSearch: search-luxury-xxxxx.us-east-1.es.amazonaws.com
  Index: luxury-image-embeddings
  Bedrock Model: amazon.titan-embed-image-v1

Creating OpenSearch index...
Created index: luxury-image-embeddings

Listing images from s3://your-luxury-images-bucket/hermes-images/...
Found 50 images

Processing images...

[1/50] Processing: hermes-images/product-001.jpg
  ✓ Indexed successfully
[2/50] Processing: hermes-images/product-002.jpg
  ✓ Indexed successfully
...

================================================================================
Summary:
  Total images: 50
  Successfully indexed: 50
  Failed: 0
================================================================================

✅ Embedding generation completed!
```

This process:
- Creates OpenSearch index with k-NN mapping
- Downloads each image from S3
- Generates embeddings using Bedrock
- Indexes embeddings to OpenSearch

**Time estimate:** ~2-3 seconds per image

### Step 4: Configure Coveo IPE Extension

Set up the IPE extension for live demo:

1. Go to Coveo Platform → Sources
2. Select your Push source
3. Navigate to "Extensions" tab
4. Click "Add Extension"
5. Configure:
   - **Name:** Image Embedding Generator
   - **Type:** Document Object Extension
   - **URL:** `https://xyz789.lambda-url.us-east-1.on.aws/` (from Step 1)
   - **Method:** POST
   - **Condition:** `@imageurl IS NOT NULL OR @s3_key IS NOT NULL`
6. Save

Test the extension:
1. Push a new document with image
2. Check CloudWatch Logs for IPE Lambda
3. Verify embedding in OpenSearch

### Step 5: Deploy UI to Netlify

#### Option A: Netlify CLI (Recommended)

```bash
cd ui

# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize site
netlify init

# Deploy
netlify deploy --prod
```

Follow prompts:
- Create new site or link existing
- Build command: `npm run build`
- Publish directory: `dist`

#### Option B: Netlify UI

1. Build the UI:
```bash
cd ui
npm run build
```

2. Go to [Netlify](https://app.netlify.com/)
3. Click "Add new site" → "Deploy manually"
4. Drag and drop the `dist` folder
5. Site is live!

#### Option C: GitHub Integration

1. Push code to GitHub
2. Go to Netlify → "New site from Git"
3. Select repository
4. Build settings (auto-detected from netlify.toml):
   - Build command: `npm run build`
   - Publish directory: `dist`
5. Add environment variables:
   - `VITE_API_URL`: Your API Gateway URL
   - `VITE_ENABLE_ANALYTICS`: `true`
6. Deploy

### Step 6: Alternative - Deploy UI to AWS App Runner

If Netlify is not an option:

1. Create Dockerfile in `ui/`:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

2. Create `ui/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

3. Build and push to ECR:

```bash
cd ui

# Create ECR repository
aws ecr create-repository --repository-name luxury-image-search-ui --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t luxury-image-search-ui .

# Tag image
docker tag luxury-image-search-ui:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/luxury-image-search-ui:latest

# Push image
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/luxury-image-search-ui:latest
```

4. Create App Runner service:

```bash
aws apprunner create-service \
  --service-name luxury-image-search-ui \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/luxury-image-search-ui:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "80"
      }
    },
    "AutoDeploymentsEnabled": false
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }' \
  --region us-east-1
```

5. Get service URL:

```bash
aws apprunner describe-service --service-arn <service-arn> --region us-east-1
```

## Verification

### Test the Complete Flow

1. Open UI in browser
2. Upload a test image
3. Click "Search Similar Items"
4. Verify:
   - Loading state appears
   - Results are displayed
   - OpenSearch log shows matches
   - Coveo results are personalized

### Check CloudWatch Logs

```bash
# Search Lambda logs
aws logs tail /aws/lambda/luxury-image-search --follow

# IPE Extension logs
aws logs tail /aws/lambda/coveo-ipe-extension --follow
```

### Verify OpenSearch Index

```bash
curl -u admin:password \
  "https://your-opensearch-endpoint.amazonaws.com/luxury-image-embeddings/_count"
```

Should return count of indexed documents.

### Test API Directly

```bash
# Convert image to base64
base64 -i test-image.jpg -o test-image.b64

# Test search endpoint
curl -X POST https://your-api-gateway-url.com/prod/search \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,<base64-string>"
  }'
```

## Monitoring

### CloudWatch Dashboards

Create dashboard for monitoring:

1. Go to CloudWatch → Dashboards
2. Create dashboard: "Luxury Image Search"
3. Add widgets:
   - Lambda invocations
   - Lambda errors
   - Lambda duration
   - API Gateway requests
   - API Gateway latency

### Alarms

Set up alarms for:

```bash
# Lambda errors
aws cloudwatch put-metric-alarm \
  --alarm-name luxury-search-lambda-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1

# API Gateway 5xx errors
aws cloudwatch put-metric-alarm \
  --alarm-name luxury-search-api-5xx \
  --alarm-description "Alert on API 5xx errors" \
  --metric-name 5XXError \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

## Cleanup

To remove all resources:

```bash
cd infrastructure
./destroy.sh
```

This will:
1. Delete CloudFormation stack
2. Remove Lambda functions
3. Delete API Gateway
4. Clean up CloudWatch logs

**Note:** OpenSearch domain and S3 bucket are NOT deleted automatically.

Manual cleanup:

```bash
# Delete OpenSearch domain
aws opensearch delete-domain --domain-name luxury-image-search --region us-east-1

# Empty and delete S3 bucket
aws s3 rm s3://your-luxury-images-bucket --recursive
aws s3 rb s3://your-luxury-images-bucket
```

## Troubleshooting

### Deployment Fails

Check:
- AWS credentials are valid
- SAM CLI is installed
- All environment variables are set
- IAM permissions are sufficient

### Embeddings Generation Fails

Common issues:
- Bedrock model not enabled
- S3 bucket permissions
- OpenSearch connection
- Image format not supported

### UI Not Loading Results

Verify:
- API Gateway URL is correct in `.env`
- CORS is enabled on API Gateway
- Lambda function has correct permissions
- Network connectivity

### IPE Extension Not Working

Check:
- Lambda URL is correct in Coveo
- Lambda has public URL enabled
- CloudWatch logs for errors
- Document has required fields

## Cost Estimation

Approximate costs for demo (1 month):

- **Lambda:** ~$5 (1M requests)
- **API Gateway:** ~$3.50 (1M requests)
- **OpenSearch:** ~$50 (t3.small.search)
- **Bedrock:** ~$10 (1000 images)
- **S3:** ~$1 (storage + requests)
- **CloudWatch:** ~$2 (logs)

**Total:** ~$70/month

For demo only, consider:
- Using OpenSearch free tier (if eligible)
- Deleting resources after demo
- Using smaller OpenSearch instance
