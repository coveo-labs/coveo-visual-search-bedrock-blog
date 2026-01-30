#!/usr/bin/env python3
"""
Fix and Re-index Products to Coveo

Ensures all products have correct S3 image URLs in clickableuri field
"""

import json
import os
import sys
import requests
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def load_products():
    """Load products from scraped data"""
    input_file = os.path.join(config.OUTPUT_DIR, config.SCRAPED_DATA_FILE)
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found")
        return []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"✓ Loaded {len(products)} products")
    return products


def create_coveo_document(product):
    """Create Coveo document with correct image URLs"""
    asset_id = product['asset_id']
    product_url = product.get('product_url', '')
    
    # Use S3 URL if available, otherwise construct it
    if product.get('s3_url'):
        image_url = product['s3_url']
    else:
        # Construct S3 URL from asset_id
        s3_key = f"{config.S3_IMAGES_PREFIX}{asset_id}.jpg"
        image_url = f"https://{config.S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com/{s3_key}"
    
    # IMPORTANT: Use image URL as documentId to ensure clickableUri is the image
    # This overrides Coveo's default behavior of using documentId as clickableUri
    document_id = image_url
    
    product_attrs = product.get('product_attributes', {})
    product_details = product.get('product_details', {})
    
    document = {
        'documentId': document_id,  # Use image URL as document ID
        'title': product.get('title', 'Hermès Product'),
        'assetid': asset_id,
        'description': product.get('description', ''),
        'longdescription': product.get('long_description', ''),
        'category': product.get('category', 'Uncategorized'),
        'price': product.get('price', ''),
        'brand': product.get('brand', 'Hermès'),
        
        # All image-related fields should point to S3
        'imageurl': image_url,
        'thumbnailurl': image_url,
        'clickableuri': image_url,  # Explicitly set to image URL
        'producturl': product_url or f"https://www.hermes.com/us/en/product/{asset_id}/",
        
        's3_key': product.get('s3_key', f"{config.S3_IMAGES_PREFIX}{asset_id}.jpg"),
        's3_bucket': config.S3_BUCKET_NAME,
        
        'colors': product_attrs.get('colors', []),
        'materials': product_attrs.get('materials', []),
        'dimensions': product_attrs.get('dimensions', ''),
        'sku': product_attrs.get('sku', ''),
        
        'productdetails': json.dumps(product_details) if product_details else '',
        
        'source': 'hermes_scraper',
        'indexed_at': datetime.now(timezone.utc).isoformat(),
        'scraped_at': product.get('scraped_at', ''),
        'enriched_at': product.get('enriched_at', ''),
        
        'date': int(datetime.now(timezone.utc).timestamp() * 1000),
        's3_uploaded': True
    }
    
    # Add product details as separate fields
    for key, value in product_details.items():
        field_name = key.lower().replace(' ', '_').replace('-', '_')
        if field_name and len(field_name) < 50:
            document[f'detail_{field_name}'] = str(value)
    
    return document


def push_document(document, org_id, source_id, api_key):
    """Push document to Coveo"""
    base_url = f"https://api.cloud.coveo.com/push/v1/organizations/{org_id}/sources/{source_id}"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        url = f"{base_url}/documents"
        params = {'documentId': document['documentId']}
        
        response = requests.put(
            url,
            params=params,
            headers=headers,
            json=document,
            timeout=30
        )
        
        if response.status_code in [200, 202]:
            return True, None
        else:
            return False, f"Status {response.status_code}: {response.text}"
    
    except Exception as e:
        return False, str(e)


def main():
    """Main function"""
    print("\n" + "="*60)
    print("Fix and Re-index Products to Coveo")
    print("="*60)
    
    # Check configuration
    if not all([config.COVEO_ORGANIZATION_ID, config.COVEO_PUSH_API_KEY, config.COVEO_SOURCE_ID]):
        print("❌ Error: Coveo configuration missing")
        return
    
    # Load products
    products = load_products()
    if not products:
        return
    
    print(f"Organization ID: {config.COVEO_ORGANIZATION_ID}")
    print(f"Source ID: {config.COVEO_SOURCE_ID}")
    print(f"Total products: {len(products)}")
    print("="*60 + "\n")
    
    success_count = 0
    failed_count = 0
    
    for idx, product in enumerate(products, 1):
        asset_id = product.get('asset_id')
        title = product.get('title', 'Unknown')[:50]
        
        print(f"[{idx}/{len(products)}] {title}...")
        
        # Create document with correct URLs
        document = create_coveo_document(product)
        
        # Verify image URL
        image_url = document['clickableuri']
        if 'hermes-poc-170871290698-images.s3' in image_url:
            print(f"  ✓ Image URL: {image_url[:60]}...")
        else:
            print(f"  ⚠ Unexpected URL: {image_url}")
        
        # Push to Coveo
        success, error = push_document(
            document,
            config.COVEO_ORGANIZATION_ID,
            config.COVEO_SOURCE_ID,
            config.COVEO_PUSH_API_KEY
        )
        
        if success:
            print(f"  ✓ Pushed successfully")
            success_count += 1
        else:
            print(f"  ✗ Failed: {error}")
            failed_count += 1
        
        print()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Total: {len(products)}")
    print(f"Success: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Success rate: {(success_count/len(products)*100):.1f}%")
    print("="*60)
    
    print("\n✅ Re-indexing complete!")
    print("\nNext steps:")
    print("  1. Wait 1-2 minutes for Coveo to process")
    print("  2. Update Lambda function: cd ../backend/search_api && ./update_lambda.sh")
    print("  3. Test the UI at https://hermes-demo.netlify.app")


if __name__ == '__main__':
    main()
