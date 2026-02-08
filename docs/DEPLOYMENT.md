# Deployment Guide

Complete step-by-step guide to deploy the Luxury Image Search demo.

## Prerequisites

- AWS CLI configured with credentials
- AWS SAM CLI installed
- Python 3.9+ with pip
- Node.js 18+
- Netlify CLI (`npm install -g netlify-cli`)
- Coveo organization with Push API access

## Quick Start (TL;DR)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 2. Deploy AWS infrastructure
cd infrastructure && sam build && sam deploy --guided

# 3. Setup Coveo fields
cd ../scraper && source ../venv/bin/activate
python setup_coveo_fields.py

# 4. Run AI pipeline (download images, extract metadata)
python ai_metadata_pipeline.py

# 5. Index to Coveo
python coveo_indexer.py --input output/ai_enriched_products.json

# 6. Generate embeddings for OpenSearch
cd ../backend/embedding_generator
python cleanup_and_reindex.py

# 7. Deploy UI
cd ../../ui && npm install && npm run build && netlify deploy --prod
```

---

## Detailed Steps

### Step 1: Configure Environment

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# AWS Configuration
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Coveo Configuration
COVEO_ORGANIZATION_ID=your-org-id
COVEO_PUSH_API_KEY=your-push-api-key
COVEO_SEARCH_API_KEY=your-search-api-key
COVEO_FIELD_API_KEY=your-field-api-key
COVEO_SOURCE_ID=your-source-id

# OpenSearch (auto-created by CloudFormation)
OPENSEARCH_PASSWORD=YourSecurePassword123!
```

### Step 2: Deploy AWS Infrastructure

```bash
cd infrastructure

# Build SAM application
sam build

# Deploy (first time - interactive)
sam deploy --guided --stack-name luxury-image-search-demo --capabilities CAPABILITY_IAM

# Or deploy with parameters directly
sam deploy --stack-name luxury-image-search-demo \
  --capabilities CAPABILITY_IAM \
  --resolve-s3 \
  --no-confirm-changeset \
  --parameter-overrides \
    S3BucketName=your-bucket-name \
    CoveoOrgId=your-org-id \
    CoveoPushApiKey=your-push-key \
    CoveoSearchApiKey=your-search-key \
    OpenSearchPassword=YourPassword123!
```

**Important:** Note the API Gateway URL from the output. Update `.env`:

```bash
# Get the new API URL
aws cloudformation describe-stacks \
  --stack-name luxury-image-search-demo \
  --query "Stacks[0].Outputs[?OutputKey=='SearchApiUrl'].OutputValue" \
  --output text
```

Update both `.env` and `ui/.env` with the new API URL.

### Step 3: Setup Python Environment

```bash
cd /path/to/project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r scraper/requirements.txt
pip install requests-aws4auth python-dotenv opensearch-py boto3
```

### Step 4: Setup Coveo Fields

This creates the facet fields in Coveo for filtering:

```bash
cd scraper
source ../venv/bin/activate
source ../.env  # Load environment variables

python setup_coveo_fields.py
```

Fields created: `category`, `subcategory`, `color`, `material`, `style`, `gender`, `pricerange`, `brand`, `imageurl`, `s3_key`, etc.

### Step 5: Run AI Metadata Pipeline

Downloads curated images from Unsplash, extracts metadata using Bedrock Nova Lite, and prepares for indexing:

```bash
cd scraper
python ai_metadata_pipeline.py
```

This creates `output/ai_enriched_products.json` with ~150 products across 6 categories:
- Shirts, Trousers, Jewelry, Watches, Shoes, Bags

**Cost:** ~$0.03 for 150 images with Nova Lite

### Step 6: Index to Coveo

```bash
cd scraper
source ../.env

# Verify source ID is correct
echo $COVEO_SOURCE_ID

# Index products
python coveo_indexer.py --input output/ai_enriched_products.json
```

Wait 1-2 minutes for Coveo to process the documents.

### Step 7: Generate Embeddings for OpenSearch

This generates vector embeddings for image similarity search:

```bash
cd backend/embedding_generator
source ../../venv/bin/activate

# Clean and re-index with fresh embeddings
python cleanup_and_reindex.py
```

Options:
- `--delete-only` - Only delete existing documents
- `--index-only` - Only index without deleting first

**Cost:** ~$0.10 for 150 images with Titan Embeddings

### Step 8: Deploy UI to Netlify

```bash
cd ui

# Install dependencies
npm install

# Update .env with correct values
cat > .env << EOF
VITE_API_URL=https://your-api-gateway.execute-api.us-east-1.amazonaws.com/prod
VITE_COVEO_ORG_ID=your-org-id
VITE_COVEO_API_KEY=your-search-api-key
VITE_COVEO_SEARCH_HUB=LuxuryImageSearch
VITE_COVEO_PIPELINE=luxury-search
VITE_ENABLE_ANALYTICS=true
EOF

# Build and deploy
npm run build
netlify deploy --prod
```

---

## Verification

1. **Text Search:** Visit your Netlify URL, search for "blue shirt" - should show results with facets
2. **Image Search:** Upload an image to find similar products
3. **AI Metadata:** Upload an image to extract metadata with Nova Lite
4. **Coveo Analytics:** Check Coveo Admin Console > Analytics for search events

---

## Troubleshooting

### CORS Errors on Image Search
- Verify API Gateway URL is correct in `ui/.env`
- Check Lambda logs: `aws logs tail /aws/lambda/luxury-image-search --since 10m`

### Coveo Source Not Found
- Verify `COVEO_SOURCE_ID` matches your Coveo source
- Check in Coveo Admin Console > Content > Sources

### OpenSearch Connection Failed
- Verify OpenSearch endpoint in `.env`
- Check OpenSearch access policy allows Lambda execution role

### Wrong Pipeline Running
- Set `VITE_COVEO_PIPELINE=your-pipeline-name` in `ui/.env`
- Or configure Search Hub condition in Coveo Query Pipeline

### Environment Variables Not Loading
```bash
# Always source .env before running scripts
source /path/to/project/.env
echo $COVEO_SOURCE_ID  # Verify it's set
```

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Netlify   │────▶│ API Gateway │────▶│   Lambda    │
│     UI      │     │             │     │  (Search)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
            ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
            │   Bedrock   │           │ OpenSearch  │           │    Coveo    │
            │   (Embed)   │           │   (k-NN)    │           │  (Search)   │
            └─────────────┘           └─────────────┘           └─────────────┘
```

**Flow:**
1. User uploads image → Lambda generates embedding via Bedrock
2. Embedding searches OpenSearch for similar images (k-NN)
3. Asset IDs from OpenSearch query Coveo for full product data
4. Results returned to UI with facets and metadata

---

## Costs (Estimated)

| Service | Usage | Cost |
|---------|-------|------|
| Bedrock Nova Lite | 150 images metadata | ~$0.03 |
| Bedrock Titan Embed | 150 embeddings | ~$0.10 |
| OpenSearch t3.small | Per hour | ~$0.036 |
| Lambda | Per 1M requests | ~$0.20 |
| S3 | 150 images (~50MB) | ~$0.001 |

**Total for demo setup:** ~$0.15 + OpenSearch hourly cost
