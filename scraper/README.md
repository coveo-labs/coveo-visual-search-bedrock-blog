# Hermes Product Scraper

Complete scraping and indexing solution for Hermes.com products.

## Overview

This scraper extracts product information from Hermes.com, downloads images to S3, and pushes structured data to Coveo for search indexing.

## Features

- ✅ Scrapes product information (title, price, description, images)
- ✅ Generates unique asset IDs for each product
- ✅ Downloads and optimizes product images
- ✅ Uploads images to AWS S3
- ✅ Creates Coveo-compatible JSON structure
- ✅ Pushes products to Coveo via Push API
- ✅ Respects rate limiting and robots.txt
- ✅ Complete error handling and logging

## Directory Structure

```
scraper/
├── config.py                 # Configuration settings
├── hermes_scraper.py         # Main scraping logic
├── image_downloader.py       # Image download and S3 upload
├── coveo_indexer.py          # Coveo Push API integration
├── run_pipeline.py           # Complete pipeline runner
├── run_pipeline.sh           # Shell script wrapper
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── output/                   # Output directory (created automatically)
    ├── scraped_products.json # Scraped product data
    └── coveo_payload.json    # Coveo-formatted payload
```

## Prerequisites

### 1. Python Environment

```bash
# From project root
source venv/bin/activate
cd scraper
pip install -r requirements.txt
```

### 2. AWS Configuration

Ensure `.env` file in project root has:
```env
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
S3_IMAGES_PREFIX=hermes-images/
```

### 3. Coveo Configuration

Ensure `.env` file has:
```env
COVEO_ORGANIZATION_ID=your-org-id
COVEO_PUSH_API_KEY=your-push-api-key
COVEO_SOURCE_ID=your-source-id
```

### 4. AWS S3 Bucket

Create S3 bucket:
```bash
aws s3 mb s3://your-bucket-name
```

## Usage

### Option 1: Run Complete Pipeline (Recommended)

```bash
# Activate virtual environment
source ../venv/bin/activate

# Run complete pipeline
python run_pipeline.py
```

Or use the shell script:
```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

This runs all three steps automatically:
1. Scrape products
2. Download images to S3
3. Push to Coveo

### Option 2: Run Individual Steps

#### Step 1: Scrape Products

```bash
python hermes_scraper.py
```

**Output:** `output/scraped_products.json`

**What it does:**
- Scrapes configured categories from Hermes.com
- Extracts product information
- Generates unique asset IDs
- Saves to JSON file

#### Step 2: Download Images to S3

```bash
python image_downloader.py
```

**Prerequisites:** Step 1 completed

**What it does:**
- Loads scraped products
- Downloads product images
- Optimizes images (resize, compress)
- Uploads to S3 bucket
- Updates product data with S3 URLs

#### Step 3: Push to Coveo

```bash
python coveo_indexer.py
```

**Prerequisites:** Steps 1 and 2 completed

**What it does:**
- Loads scraped products with S3 URLs
- Creates Coveo-compatible documents
- Pushes to Coveo via Push API
- Saves payload for reference

## Configuration

### Scraping Settings

Edit `config.py`:

```python
# Categories to scrape
CATEGORIES = [
    "/us/en/category/women/bags-and-small-leather-goods/bags-and-clutches/",
    "/us/en/category/women/accessories/scarves-and-silk-accessories/",
    # Add more categories...
]

# Limits (for demo)
MAX_PRODUCTS_PER_CATEGORY = 10
MAX_TOTAL_PRODUCTS = 50

# Rate limiting
REQUEST_DELAY = 2  # Seconds between requests
```

### Image Settings

```python
# Image optimization
IMAGE_MAX_SIZE = (1200, 1200)  # Max dimensions
IMAGE_QUALITY = 85  # JPEG quality (1-100)
```

## Output Files

### scraped_products.json

Contains raw scraped data:

```json
[
  {
    "asset_id": "hermes-abc12345",
    "title": "Birkin 30 Handbag",
    "description": "Iconic Hermès Birkin bag...",
    "price": "$12,500",
    "category": "bags-and-clutches",
    "product_url": "https://www.hermes.com/...",
    "image_url": "https://www.hermes.com/.../image.jpg",
    "image_filename": "hermes-abc12345.jpg",
    "s3_key": "hermes-images/hermes-abc12345.jpg",
    "s3_url": "https://bucket.s3.amazonaws.com/...",
    "s3_uploaded": true,
    "brand": "Hermès",
    "scraped_at": "2024-01-15T10:30:00"
  }
]
```

### coveo_payload.json

Contains Coveo-formatted documents:

```json
{
  "metadata": {
    "organization_id": "your-org-id",
    "source_id": "your-source-id",
    "total_documents": 50,
    "created_at": "2024-01-15T10:35:00"
  },
  "documents": [
    {
      "documentId": "hermes-abc12345",
      "title": "Birkin 30 Handbag",
      "assetid": "hermes-abc12345",
      "description": "...",
      "category": "bags-and-clutches",
      "price": "$12,500",
      "brand": "Hermès",
      "imageurl": "https://bucket.s3.amazonaws.com/...",
      "producturl": "https://www.hermes.com/...",
      "s3_key": "hermes-images/hermes-abc12345.jpg",
      "s3_bucket": "your-bucket-name",
      "clickableuri": "https://www.hermes.com/...",
      "indexed_at": "2024-01-15T10:35:00"
    }
  ]
}
```

## Asset ID Generation

Asset IDs are generated using MD5 hash of product URL:

```python
def generate_asset_id(product_url):
    url_hash = hashlib.md5(product_url.encode()).hexdigest()[:8]
    return f"hermes-{url_hash}"
```

Example: `hermes-abc12345`

This ensures:
- Unique IDs for each product
- Consistent IDs across runs
- URL-based identification

## Data Flow

```
Hermes.com
    ↓
[hermes_scraper.py]
    ↓
scraped_products.json
    ↓
[image_downloader.py]
    ↓
AWS S3 Bucket + Updated JSON
    ↓
[coveo_indexer.py]
    ↓
Coveo Index + coveo_payload.json
```

## Error Handling

All scripts include comprehensive error handling:

- **Network errors:** Retry logic and timeouts
- **Missing data:** Graceful skipping with logging
- **S3 errors:** Detailed error messages
- **Coveo errors:** Status code checking

## Rate Limiting

The scraper respects rate limits:

```python
REQUEST_DELAY = 2  # Seconds between requests
```

Adjust based on website's robots.txt and terms of service.

## Troubleshooting

### No products scraped

**Possible causes:**
- Website structure changed
- Network connectivity issues
- robots.txt restrictions

**Solution:**
- Check website HTML structure
- Update CSS selectors in `hermes_scraper.py`
- Verify network access

### S3 upload fails

**Possible causes:**
- Invalid AWS credentials
- Bucket doesn't exist
- Insufficient permissions

**Solution:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check bucket exists
aws s3 ls s3://your-bucket-name

# Check permissions
aws s3 ls s3://your-bucket-name/hermes-images/
```

### Coveo push fails

**Possible causes:**
- Invalid API key
- Wrong organization/source ID
- Network issues

**Solution:**
- Verify credentials in `.env`
- Check Coveo dashboard for source status
- Test API key with curl:

```bash
curl -X GET \
  "https://api.cloud.coveo.com/push/v1/organizations/$COVEO_ORGANIZATION_ID/sources/$COVEO_SOURCE_ID/status" \
  -H "Authorization: Bearer $COVEO_PUSH_API_KEY"
```

### Images not displaying in UI

**Possible causes:**
- S3 bucket not public
- CORS not configured
- Wrong image URLs

**Solution:**
- Make S3 bucket public or use presigned URLs
- Configure S3 CORS:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

## Best Practices

### 1. Respect robots.txt

Always check and respect the website's robots.txt:
```
https://www.hermes.com/robots.txt
```

### 2. Rate Limiting

Use appropriate delays between requests:
```python
REQUEST_DELAY = 2  # Minimum 2 seconds
```

### 3. User Agent

Use a descriptive user agent:
```python
USER_AGENT = "YourBot/1.0 (contact@example.com)"
```

### 4. Error Handling

Always handle errors gracefully and log them.

### 5. Data Validation

Validate scraped data before uploading:
- Check required fields exist
- Validate URLs
- Verify image formats

## Legal Considerations

⚠️ **Important:**

- This scraper is for **demonstration purposes only**
- Always respect website terms of service
- Check robots.txt before scraping
- Consider using official APIs when available
- Don't overload servers with requests
- Respect copyright and intellectual property

## Integration with Main Project

After running the scraper:

### 1. Generate Embeddings

```bash
cd ../backend/embedding_generator
python generate_embeddings.py
```

This creates embeddings for all images in S3.

### 2. Verify in Coveo

1. Log in to Coveo Platform
2. Go to Content Browser
3. Search for `source:your-source-id`
4. Verify products are indexed

### 3. Test Search UI

1. Deploy UI (if not already deployed)
2. Upload a product image
3. Verify results show scraped products

## Customization

### Add More Categories

Edit `config.py`:

```python
CATEGORIES = [
    "/us/en/category/women/bags/",
    "/us/en/category/men/accessories/",
    "/us/en/category/home/",
    # Add more...
]
```

### Change Scraping Limits

```python
MAX_PRODUCTS_PER_CATEGORY = 20  # Increase limit
MAX_TOTAL_PRODUCTS = 100
```

### Modify Product Structure

Edit `extract_product_info()` in `hermes_scraper.py` to extract additional fields.

### Custom Asset ID Format

Modify `generate_asset_id()` in `hermes_scraper.py`:

```python
def generate_asset_id(self, product_url):
    # Custom format
    return f"custom-prefix-{uuid.uuid4().hex[:8]}"
```

## Performance

### Scraping Speed

- ~2-3 seconds per product (with rate limiting)
- 50 products ≈ 2-3 minutes

### Image Processing

- ~1-2 seconds per image (download + optimize + upload)
- 50 images ≈ 2-3 minutes

### Coveo Indexing

- ~0.5 seconds per document
- 50 documents ≈ 30 seconds
- Plus 1-2 minutes for Coveo to process

**Total time for 50 products:** ~5-10 minutes

## Monitoring

Check progress in real-time:

```bash
# Watch output directory
watch -n 1 ls -lh output/

# Monitor S3 uploads
watch -n 5 aws s3 ls s3://your-bucket/hermes-images/

# Check Coveo indexing
# (Use Coveo dashboard)
```

## Support

For issues or questions:

1. Check this README
2. Review error messages in console
3. Check output files in `output/` directory
4. Verify configuration in `config.py`
5. Test individual components separately

## Next Steps

After successful scraping and indexing:

1. ✅ Products scraped from Hermes.com
2. ✅ Images uploaded to S3
3. ✅ Products indexed in Coveo
4. ⏭️ Generate embeddings (see main project README)
5. ⏭️ Test search UI
6. ⏭️ Configure IPE extension for live updates

See main project documentation for complete deployment guide.
