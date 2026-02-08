# Scraper Quick Start

Get the luxury product scraper running in 5 minutes.

## Prerequisites

```bash
# Activate virtual environment
source ../venv/bin/activate

# Install scraper dependencies
cd scraper
pip install -r requirements.txt
```

## Configuration

Ensure `.env` file in project root has:

```env
# AWS
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
S3_IMAGES_PREFIX=product-images/

# Coveo
COVEO_ORGANIZATION_ID=your-org-id
COVEO_PUSH_API_KEY=your-push-api-key
COVEO_SOURCE_ID=your-source-id
```

## Run Complete Pipeline

```bash
# Option 1: Python script
python run_pipeline.py

# Option 2: Shell script
chmod +x run_pipeline.sh
./run_pipeline.sh
```

This will:
1. ✅ Scrape products from curated sources
2. ✅ Download images to S3
3. ✅ Push to Coveo

## Run Individual Steps

### 1. Scrape Only

```bash
python ai_metadata_pipeline.py
```

Output: `output/scraped_products.json`

### 2. Download Images

```bash
python image_downloader.py
```

Requires: Step 1 completed

### 3. Push to Coveo

```bash
python coveo_indexer.py
```

Requires: Steps 1 & 2 completed

## Verify Results

### Check Scraped Data

```bash
cat output/scraped_products.json | jq '.[0]'
```

### Check S3 Images

```bash
aws s3 ls s3://your-bucket-name/product-images/
```

### Check Coveo

1. Go to Coveo Platform
2. Navigate to Content Browser
3. Search for your products

## Next Steps

After scraping:

```bash
# Generate embeddings
cd ../backend/embedding_generator
python generate_embeddings.py

# Test search UI
cd ../ui
npm run dev
```

## Troubleshooting

### No products scraped

Source may be unavailable or structure may have changed. Check scraping scripts and update selectors if needed.

### S3 upload fails

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check bucket exists
aws s3 ls s3://your-bucket-name
```

### Coveo push fails

```bash
# Test API key
curl -X GET \
  "https://api.cloud.coveo.com/push/v1/organizations/$COVEO_ORGANIZATION_ID/sources/$COVEO_SOURCE_ID/status" \
  -H "Authorization: Bearer $COVEO_PUSH_API_KEY"
```

## Configuration Options

Edit `config.py` to customize:

```python
# Scraping limits
MAX_PRODUCTS_PER_CATEGORY = 10
MAX_TOTAL_PRODUCTS = 50

# Rate limiting
REQUEST_DELAY = 2  # seconds

# Image settings
IMAGE_MAX_SIZE = (1200, 1200)
IMAGE_QUALITY = 85
```

## Complete Workflow

```bash
# 1. Setup
source ../venv/bin/activate
cd scraper
pip install -r requirements.txt

# 2. Configure
# Edit ../.env with your credentials

# 3. Run scraper
python run_pipeline.py

# 4. Generate embeddings
cd ../backend/embedding_generator
python generate_embeddings.py

# 5. Test UI
cd ../ui
npm run dev
```

## Support

See [README.md](README.md) for detailed documentation.
