#!/usr/bin/env python3
"""
AI Metadata Pipeline

Downloads curated images, extracts metadata using Bedrock Nova Lite,
and prepares data for Coveo indexing.

Pipeline:
1. Download images from Unsplash URLs
2. Upload to S3
3. Extract metadata using Bedrock Nova Lite
4. Save enriched product data for Coveo indexing
"""

import json
import os
import sys
import time
import base64
import hashlib
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from curated_image_urls import CURATED_IMAGES

# Constants
AWS_REGION = config.AWS_REGION or 'us-east-1'
S3_BUCKET = config.S3_BUCKET_NAME
S3_PREFIX = config.S3_IMAGES_PREFIX or 'hermes-images/'
NOVA_MODEL_ID = 'amazon.nova-lite-v1:0'
OUTPUT_DIR = config.OUTPUT_DIR or 'output'

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

# Metadata extraction prompt
EXTRACTION_PROMPT = """Analyze this product image and extract detailed metadata.

Return a JSON object with these exact fields:
{
  "title": "Descriptive product title (e.g., 'Classic White Cotton Dress Shirt')",
  "category": "Main category - MUST be one of: Shirts, Trousers, Jewelry, Watches, Shoes, Bags",
  "subcategory": "Specific type (e.g., Dress Shirt, Jeans, Necklace, Chronograph, Sneakers, Handbag)",
  "color": "Primary color (e.g., White, Black, Blue, Brown, Gold, Silver)",
  "material": "Primary material (e.g., Cotton, Leather, Silk, Gold, Silver, Canvas, Denim)",
  "style": "Style category - one of: Casual, Formal, Sport, Luxury, Classic, Modern, Vintage",
  "gender": "Target gender - one of: Men, Women, Unisex",
  "description": "2-3 sentence detailed description of the product",
  "features": ["List of 3-5 notable features"],
  "tags": ["5-8 relevant search tags"],
  "estimated_price_range": "Price range (e.g., '$50-$100', '$500-$1000', '$2000+')"
}

Be accurate and specific based on what you see in the image.
Return ONLY valid JSON, no additional text."""


def generate_asset_id(url):
    """Generate unique asset ID from URL"""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    return f"prod-{url_hash}"


def download_image(url, timeout=30):
    """Download image from URL and return bytes"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"  ✗ Failed to download {url[:50]}...: {e}")
        return None


def upload_to_s3(image_bytes, asset_id):
    """Upload image to S3 and return the S3 URL"""
    try:
        s3_key = f"{S3_PREFIX}{asset_id}.jpg"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=image_bytes,
            ContentType='image/jpeg'
        )
        s3_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        return s3_url, s3_key
    except ClientError as e:
        print(f"  ✗ Failed to upload to S3: {e}")
        return None, None


def detect_image_format(image_bytes):
    """Detect image format from magic bytes"""
    if image_bytes[:3] == b'\xff\xd8\xff':
        return 'jpeg'
    elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return 'webp'
    return 'jpeg'


def extract_metadata_with_nova(image_bytes, category_hint=None):
    """Extract metadata from image using Bedrock Nova Lite via invoke_model"""
    try:
        image_format = detect_image_format(image_bytes)
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Add category hint to prompt if available
        prompt = EXTRACTION_PROMPT
        if category_hint:
            category_map = {
                'mens_shirts': 'Shirts',
                'trousers': 'Trousers', 
                'jewelry': 'Jewelry',
                'watches': 'Watches',
                'shoes': 'Shoes',
                'bags': 'Bags'
            }
            hint_category = category_map.get(category_hint, category_hint)
            prompt = f"This is a {hint_category} product.\n\n" + prompt
        
        # Nova Lite request body format for invoke_model
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "image": {
                                "format": image_format,
                                "source": {
                                    "bytes": image_b64
                                }
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "maxTokens": 1500,
                "temperature": 0.1,
                "topP": 0.9
            }
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_MODEL_ID,
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        response_text = response_body['output']['message']['content'][0]['text']
        
        # Extract JSON from response
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        
        metadata = json.loads(response_text)
        return metadata
        
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"  ✗ Nova extraction error: {e}")
        return None


def get_price_range_bucket(price_range_str):
    """Convert price range string to bucket for faceting"""
    if not price_range_str:
        return "$100-$500"
    
    price_str = price_range_str.lower().replace(',', '').replace('$', '')
    
    try:
        # Extract first number
        import re
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            price = int(numbers[0])
            if price < 100:
                return "$0-$100"
            elif price < 500:
                return "$100-$500"
            elif price < 1000:
                return "$500-$1,000"
            elif price < 2500:
                return "$1,000-$2,500"
            elif price < 5000:
                return "$2,500-$5,000"
            else:
                return "$5,000+"
    except:
        pass
    
    return "$100-$500"


def process_single_image(url, category_hint, index, total):
    """Process a single image through the pipeline"""
    asset_id = generate_asset_id(url)
    print(f"\n[{index}/{total}] Processing {asset_id}...")
    
    # Step 1: Download image
    print(f"  Downloading from Unsplash...")
    image_bytes = download_image(url)
    if not image_bytes:
        return None
    
    # Step 2: Upload to S3
    print(f"  Uploading to S3...")
    s3_url, s3_key = upload_to_s3(image_bytes, asset_id)
    if not s3_url:
        return None
    
    # Step 3: Extract metadata with Nova Lite
    print(f"  Extracting metadata with Nova Lite...")
    metadata = extract_metadata_with_nova(image_bytes, category_hint)
    if not metadata:
        # Create basic metadata if extraction fails
        metadata = {
            "title": f"Product {asset_id}",
            "category": category_hint.replace('_', ' ').title() if category_hint else "Unknown",
            "subcategory": "Unknown",
            "color": "Unknown",
            "material": "Unknown",
            "style": "Classic",
            "gender": "Unisex",
            "description": "A quality product.",
            "features": [],
            "tags": [],
            "estimated_price_range": "$100-$500"
        }
    
    # Build product document
    product = {
        "asset_id": asset_id,
        "title": metadata.get("title", f"Product {asset_id}"),
        "description": metadata.get("description", ""),
        "category": metadata.get("category", "Unknown"),
        "subcategory": metadata.get("subcategory", "Unknown"),
        "color": metadata.get("color", "Unknown"),
        "material": metadata.get("material", "Unknown"),
        "style": metadata.get("style", "Classic"),
        "gender": metadata.get("gender", "Unisex"),
        "brand": "Hermès",
        "price_range": get_price_range_bucket(metadata.get("estimated_price_range")),
        "features": metadata.get("features", []),
        "tags": metadata.get("tags", []),
        "image_url": url,  # Use original Unsplash URL for display
        "s3_url": s3_url,  # S3 URL for embedding generation
        "s3_key": s3_key,
        "original_url": url,
        "product_url": f"https://www.hermes.com/us/en/product/{asset_id}/",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ai_extracted": True,
    }
    
    print(f"  ✓ {metadata.get('title', 'Unknown')[:50]}... ({metadata.get('color')}, {metadata.get('category')})")
    
    return product


def run_pipeline(max_images=150, delay_between=0.5):
    """Run the full pipeline"""
    print("\n" + "="*70)
    print("AI Metadata Pipeline - Bedrock Nova Lite")
    print("="*70)
    print(f"S3 Bucket: {S3_BUCKET}")
    print(f"Model: {NOVA_MODEL_ID}")
    print(f"Max Images: {max_images}")
    print("="*70 + "\n")
    
    # Collect all images
    all_images = []
    for category, urls in CURATED_IMAGES.items():
        for url in urls:
            all_images.append({
                "url": url,
                "category_hint": category
            })
    
    # Limit to max_images
    all_images = all_images[:max_images]
    total = len(all_images)
    
    print(f"Processing {total} images...\n")
    
    # Process images
    products = []
    failed = 0
    
    for i, img_data in enumerate(all_images, 1):
        try:
            product = process_single_image(
                img_data["url"],
                img_data["category_hint"],
                i,
                total
            )
            
            if product:
                products.append(product)
            else:
                failed += 1
            
            # Rate limiting
            if delay_between > 0:
                time.sleep(delay_between)
                
        except Exception as e:
            print(f"  ✗ Error processing image: {e}")
            failed += 1
    
    # Save results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "ai_enriched_products.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*70)
    print("Pipeline Complete!")
    print("="*70)
    print(f"Total processed: {total}")
    print(f"Successful: {len(products)}")
    print(f"Failed: {failed}")
    print(f"Output file: {output_file}")
    
    # Category breakdown
    categories = {}
    for p in products:
        cat = p.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nCategory breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print("\n" + "="*70)
    print("Next steps:")
    print("  1. Index to Coveo: python coveo_indexer.py --input ai_enriched_products.json")
    print("  2. Generate embeddings: cd ../backend/embedding_generator && python generate_embeddings.py")
    print("="*70)
    
    return products


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Metadata Pipeline")
    parser.add_argument("--max", type=int, default=150, help="Maximum images to process")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between API calls (seconds)")
    
    args = parser.parse_args()
    
    run_pipeline(max_images=args.max, delay_between=args.delay)
