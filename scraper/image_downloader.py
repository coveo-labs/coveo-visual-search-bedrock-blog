"""
Image Downloader and S3 Uploader

Downloads product images and uploads them to S3 bucket
"""

import requests
import boto3
import json
import os
from PIL import Image
from io import BytesIO
import config
from datetime import datetime, timezone


class ImageDownloader:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=config.AWS_REGION)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
        
        self.stats = {
            'total': 0,
            'downloaded': 0,
            'uploaded': 0,
            'skipped': 0,
            'failed': 0
        }
    
    def load_scraped_data(self):
        """Load scraped product data"""
        input_file = os.path.join(config.OUTPUT_DIR, config.SCRAPED_DATA_FILE)
        
        if not os.path.exists(input_file):
            print(f"❌ Error: {input_file} not found")
            print("Please run ai_metadata_pipeline.py first")
            return []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"✓ Loaded {len(products)} products from {input_file}")
        return products
    
    def download_image(self, image_url):
        """Download image from URL"""
        try:
            response = self.session.get(
                image_url,
                timeout=config.REQUEST_TIMEOUT,
                stream=True
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"  ✗ Error downloading: {str(e)}")
            return None
    
    def optimize_image(self, image_bytes):
        """Optimize image size and quality"""
        try:
            img = Image.open(BytesIO(image_bytes))
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large
            if img.size[0] > config.IMAGE_MAX_SIZE[0] or img.size[1] > config.IMAGE_MAX_SIZE[1]:
                img.thumbnail(config.IMAGE_MAX_SIZE, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = BytesIO()
            img.save(output, format='JPEG', quality=config.IMAGE_QUALITY, optimize=True)
            return output.getvalue()
        except Exception as e:
            print(f"  ✗ Error optimizing image: {str(e)}")
            return image_bytes  # Return original if optimization fails
    
    def upload_to_s3(self, image_bytes, s3_key):
        """Upload image to S3 bucket"""
        try:
            self.s3_client.put_object(
                Bucket=config.S3_BUCKET_NAME,
                Key=s3_key,
                Body=image_bytes,
                ContentType='image/jpeg',
                Metadata={
                    'uploaded_at': datetime.now(timezone.utc).isoformat()
                }
            )
            return True
        except Exception as e:
            print(f"  ✗ Error uploading to S3: {str(e)}")
            return False
    
    def check_s3_exists(self, s3_key):
        """Check if file already exists in S3"""
        try:
            self.s3_client.head_object(
                Bucket=config.S3_BUCKET_NAME,
                Key=s3_key
            )
            return True
        except:
            return False
    
    def process_product(self, product):
        """Download and upload image for a single product"""
        asset_id = product.get('asset_id')
        image_url = product.get('image_url')
        s3_key = product.get('s3_key')
        
        if not image_url or not s3_key:
            print(f"  ⊘ Skipping {asset_id}: No image URL or S3 key")
            self.stats['skipped'] += 1
            return False
        
        # Check if already uploaded
        if self.check_s3_exists(s3_key):
            print(f"  ✓ Already exists: {asset_id}")
            self.stats['skipped'] += 1
            product['s3_uploaded'] = True
            product['s3_url'] = f"https://{config.S3_BUCKET_NAME}.s3.{config.AWS_REGION}.amazonaws.com/{s3_key}"
            return True
        
        # Download image
        print(f"  ↓ Downloading: {asset_id}")
        image_bytes = self.download_image(image_url)
        
        if not image_bytes:
            self.stats['failed'] += 1
            return False
        
        self.stats['downloaded'] += 1
        
        # Optimize image
        print(f"  ⚙ Optimizing...")
        optimized_bytes = self.optimize_image(image_bytes)
        
        # Upload to S3
        print(f"  ↑ Uploading to S3...")
        if self.upload_to_s3(optimized_bytes, s3_key):
            self.stats['uploaded'] += 1
            product['s3_uploaded'] = True
            product['s3_url'] = f"https://{config.S3_BUCKET_NAME}.s3.{config.AWS_REGION}.amazonaws.com/{s3_key}"
            print(f"  ✓ Success: {asset_id}")
            return True
        else:
            self.stats['failed'] += 1
            return False
    
    def process_all_products(self, products):
        """Process all products"""
        print("\n" + "="*60)
        print("Starting Image Download and S3 Upload")
        print("="*60)
        print(f"Total products: {len(products)}")
        print(f"S3 Bucket: {config.S3_BUCKET_NAME}")
        print(f"S3 Prefix: {config.S3_IMAGES_PREFIX}")
        print("="*60 + "\n")
        
        self.stats['total'] = len(products)
        
        for idx, product in enumerate(products, 1):
            print(f"[{idx}/{len(products)}] Processing: {product.get('title', 'Unknown')[:50]}...")
            self.process_product(product)
            print()
        
        return products
    
    def save_updated_data(self, products):
        """Save updated product data with S3 information"""
        output_file = os.path.join(config.OUTPUT_DIR, config.SCRAPED_DATA_FILE)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Updated data saved to: {output_file}")
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "="*60)
        print("Image Download Summary")
        print("="*60)
        print(f"Total products: {self.stats['total']}")
        print(f"Downloaded: {self.stats['downloaded']}")
        print(f"Uploaded to S3: {self.stats['uploaded']}")
        print(f"Skipped (already exists): {self.stats['skipped']}")
        print(f"Failed: {self.stats['failed']}")
        print("="*60)


def main():
    """Main function"""
    # Check configuration
    if not config.S3_BUCKET_NAME:
        print("❌ Error: S3_BUCKET_NAME not configured in .env")
        return
    
    downloader = ImageDownloader()
    
    # Load scraped data
    products = downloader.load_scraped_data()
    if not products:
        return
    
    # Process all products
    updated_products = downloader.process_all_products(products)
    
    # Save updated data
    downloader.save_updated_data(updated_products)
    
    # Print summary
    downloader.print_summary()
    
    print("\nNext step:")
    print("  Run: python coveo_indexer.py (to push to Coveo)")


if __name__ == '__main__':
    main()
