# Sample Data

This directory contains sample data and scripts for testing the Luxury Image Search demo.

## Files

- `coveo-push-example.py` - Script to push sample products to Coveo
- `requirements.txt` - Python dependencies

## Usage

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure your `.env` file in the root directory has:
- COVEO_ORGANIZATION_ID
- COVEO_PUSH_API_KEY
- COVEO_SOURCE_ID

### 3. Push Sample Products

```bash
python coveo-push-example.py
```

This will push 5 sample luxury products to your Coveo source.

## Sample Products

The script includes:
1. Birkin 30 Handbag - $12,500
2. Kelly 28 Handbag - $11,000
3. Silk Twill Scarf - $425
4. H Belt - $850
5. Cape Cod Watch - $5,200

## Customization

Edit `coveo-push-example.py` to:
- Add more products
- Change product details
- Update image URLs
- Modify metadata fields

## Image Requirements

For each product, you need:
1. Image file in S3 bucket
2. Matching `s3_key` in product data
3. Public `imageurl` (or S3 presigned URL)

## Next Steps

After pushing to Coveo:
1. Wait 1-2 minutes for indexing
2. Verify in Coveo Content Browser
3. Run embedding generator:
   ```bash
   cd ../backend/embedding_generator
   python generate_embeddings.py
   ```
4. Test search in UI

## Troubleshooting

**401 Unauthorized:**
- Check COVEO_PUSH_API_KEY is valid
- Verify API key has Push permissions

**404 Not Found:**
- Check COVEO_SOURCE_ID is correct
- Verify source exists in Coveo

**Images not displaying:**
- Ensure S3 bucket is public or use presigned URLs
- Check imageurl is accessible
- Verify CORS settings on S3 bucket
