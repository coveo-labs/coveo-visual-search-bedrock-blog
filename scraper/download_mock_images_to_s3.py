"""
Download Mock Images to S3

Downloads images from Unsplash URLs in mock data and uploads to S3
This prepares the images for embedding generation
"""

import json
import os
import requests
import boto3
from datetime import datetime, timezone
import config


class MockImageDownloader:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=config.AWS_REGION)
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"  ✗ Download failed: {str(e)}")
            return None
    
    def upload_to_s3(self, image_bytes, s3_key):
        """Upload image to S3"""
        try:
            self.s3_client.put_object(
                Bucket=config.S3_BUCKET_NAME,
                Key=s3_key,
                Body=image_bytes,
                ContentType='image/jpeg',
                Metadata={
                    'uploaded_at': datetime.now(timezone.utc).isoformat(),
                    'source': 'mock_data_unsplash'
                }
            )
            return True
        except Exception as e:
            print(f"  ✗ Upload failed: {str(e)}")
            return False
    
    def check_s3_exists(self, s3_key):
        """Check if file already exists in S3"""
        try:
            self.s3_client.head_object(Bucket=config.S3_BUCKET_NAME, Key=s3_key)
            return True
        except:
            return False
    
    def process_product(self, product):
        """Download and upload image for a product"""
        asset_id = product['asset_id']
        image_url = product['image_url']
        s3_key = product['s3_key']
        title = product['title'][:50]
        
        print(f"  Asset ID: {asset_id}")
        print(f"  Title: {title}")
        
        # Check if already exists
        if self.check_s3_exists(s3_key):
            print(f"  ✓ Already exists in S3, skipping")
            self.stats['skipped'] += 1
            return True
        
        # Download from Unsplash
        print(f"  ↓ Downloading from Unsplash...")
        image_bytes = self.download_image(image_url)
        if not image_bytes:
            self.stats['failed'] += 1
            return False
        
        # Upload to S3
        print(f"  ↑ Uploading to S3...")
        if self.upload_to_s3(image_bytes, s3_key):
            print(f"  ✓ Success")
            self.stats['success'] += 1
            
            # Update product with S3 URL
            product['s3_url'] = f"https://{config.S3_BUCKET_NAME}.s3.{config.AWS_REGION}.amazonaws.com/{s3_key}"
            product['s3_uploaded'] = True
            return True
        else:
            self.stats['failed'] += 1
            return False
    
    def process_all_products(self):
        """Process all products from scraped data"""
        # Load products
        input_file = os.path.join(config.OUTPUT_DIR, config.SCRAPED_DATA_FILE)
        
        if not os.path.exists(input_file):
            print(f"❌ Error: {input_file} not found")
            print("Please run mock_data_generator.py first")
            return
        
        with open(input_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print("\n" + "="*60)
        print("Downloading Mock Images to S3")
        print("="*60)
        print(f"Total products: {len(products)}")
        print(f"S3 Bucket: {config.S3_BUCKET_NAME}")
        print(f"S3 Prefix: {config.S3_IMAGES_PREFIX}")
        print("="*60 + "\n")
        
        self.stats['total'] = len(products)
        
        # Process each product
        for idx, product in enumerate(products, 1):
            print(f"[{idx}/{len(products)}] Processing...")
            self.process_product(product)
            print()
        
        # Save updated products
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print("✓ Updated product data saved")
        
        # Print summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Total products: {self.stats['total']}")
        print(f"Successfully uploaded: {self.stats['success']}")
        print(f"Already existed: {self.stats['skipped']}")
        print(f"Failed: {self.stats['failed']}")
        print("="*60)


def main():
    """Main function"""
    # Check configuration
    if not all([config.S3_BUCKET_NAME, config.AWS_REGION]):
        print("❌ Error: Missing configuration")
        print("Required in .env:")
        print("  - S3_BUCKET_NAME")
        print("  - AWS_REGION")
        return
    
    downloader = MockImageDownloader()
    downloader.process_all_products()
    
    print("\n✅ Image download complete!")
    print("\nNext steps:")
    print("  1. Verify images in S3 bucket")
    print("  2. Re-push to Coveo: python coveo_indexer.py")
    print("  3. Generate embeddings: cd ../backend/embedding_generator && python generate_embeddings.py")


if __name__ == '__main__':
    main()
