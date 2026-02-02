"""
Coveo Indexer

Creates Coveo-compatible JSON payload and pushes products to Coveo using Push API
Supports both scraped products and AI-enriched products.
"""

import requests
import json
import os
import argparse
from datetime import datetime, timezone
import config


class CoveoIndexer:
    def __init__(self):
        self.org_id = config.COVEO_ORGANIZATION_ID
        self.api_key = config.COVEO_PUSH_API_KEY
        self.source_id = config.COVEO_SOURCE_ID
        
        self.base_url = f"https://api.cloud.coveo.com/push/v1/organizations/{self.org_id}/sources/{self.source_id}"
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def load_products(self, input_file=None):
        """Load product data from JSON file"""
        if input_file is None:
            input_file = os.path.join(config.OUTPUT_DIR, config.SCRAPED_DATA_FILE)
        # Don't prepend OUTPUT_DIR if the file already exists at the given path
        elif not os.path.isabs(input_file) and not os.path.exists(input_file):
            input_file = os.path.join(config.OUTPUT_DIR, input_file)
        
        if not os.path.exists(input_file):
            print(f"❌ Error: {input_file} not found")
            return []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"✓ Loaded {len(products)} products from {input_file}")
        return products
    
    def create_coveo_document(self, product):
        """Create Coveo document structure from product data"""
        # Use the image URL for clickableuri (for display)
        image_url = product.get('image_url', '')
        
        # Create valid URI for document ID (must be unique)
        asset_id = product.get('asset_id', '')
        product_url = product.get('product_url', '')
        
        # Use product URL as document ID for uniqueness
        if product_url:
            document_id = product_url
        else:
            document_id = f"https://hermes.com/product/{asset_id}"
        
        # Get product attributes
        product_attrs = product.get('product_attributes', {})
        product_details = product.get('product_details', {})
        
        # Build description from multiple sources
        description = product.get('description', '')
        long_description = product.get('long_description', description)
        
        # Build tags string for searchability
        tags = product.get('tags', [])
        features = product.get('features', [])
        tags_str = ', '.join(tags) if tags else ''
        features_str = ', '.join(features) if features else ''
        
        document = {
            # Required fields - documentId must be a valid URI
            'documentId': document_id,
            
            # Standard fields
            'title': product.get('title', 'Hermès Product'),
            'assetid': asset_id,
            'description': description,
            'longdescription': long_description,
            
            # Category fields for faceting
            'category': product.get('category', 'Uncategorized'),
            'subcategory': product.get('subcategory', ''),
            
            # Product attributes for faceting
            'color': product.get('color', ''),
            'material': product.get('material', ''),
            'style': product.get('style', ''),
            'size': product.get('size', 'One Size'),
            'gender': product.get('gender', 'Unisex'),
            
            # Price fields
            'price': product.get('price', ''),
            'pricerange': product.get('price_range', ''),
            
            # Brand
            'brand': product.get('brand', 'Hermès'),
            
            # URLs - Use image_url for display
            'imageurl': image_url,
            'thumbnailurl': image_url,
            'clickableuri': image_url,  # This is what users click - should be the image
            'producturl': product_url or document_id,
            
            # S3 information (for backend reference)
            's3_key': product.get('s3_key', ''),
            's3_bucket': config.S3_BUCKET_NAME,
            
            # Materials as multi-value field
            'materials': product.get('materials', []),
            
            # Tags and features for search
            'tags': tags_str,
            'features': features_str,
            
            # Product Details (as JSON string for Coveo)
            'productdetails': json.dumps(product_details) if product_details else '',
            
            # Metadata
            'source': 'ai_pipeline' if product.get('ai_extracted') else 'hermes_scraper',
            'indexed_at': datetime.now(timezone.utc).isoformat(),
            'created_at': product.get('created_at', ''),
            
            # Date for Coveo
            'date': int(datetime.now(timezone.utc).timestamp() * 1000),
        }
        
        # Add individual product details as separate fields for better searchability
        for key, value in product_details.items():
            # Create safe field name (lowercase, no spaces)
            field_name = key.lower().replace(' ', '_').replace('-', '_')
            if field_name and len(field_name) < 50:  # Reasonable field name length
                document[f'detail_{field_name}'] = str(value)
        
        return document
    
    def push_document(self, document):
        """Push a single document to Coveo"""
        try:
            url = f"{self.base_url}/documents"
            params = {'documentId': document['documentId']}
            
            response = requests.put(
                url,
                params=params,
                headers=self.headers,
                json=document,
                timeout=30
            )
            
            if response.status_code in [200, 202]:
                return True, None
            else:
                return False, f"Status {response.status_code}: {response.text}"
        
        except Exception as e:
            return False, str(e)
    
    def push_all_documents(self, products):
        """Push all products to Coveo"""
        print("\n" + "="*60)
        print("Pushing Products to Coveo")
        print("="*60)
        print(f"Organization ID: {self.org_id}")
        print(f"Source ID: {self.source_id}")
        print(f"Total products: {len(products)}")
        print("="*60 + "\n")
        
        self.stats['total'] = len(products)
        coveo_documents = []
        
        for idx, product in enumerate(products, 1):
            asset_id = product.get('asset_id')
            title = product.get('title', 'Unknown')[:50]
            
            print(f"[{idx}/{len(products)}] Pushing: {title}...")
            print(f"  Asset ID: {asset_id}")
            
            # Create Coveo document
            document = self.create_coveo_document(product)
            coveo_documents.append(document)
            
            # Push to Coveo
            success, error = self.push_document(document)
            
            if success:
                print(f"  ✓ Success")
                self.stats['success'] += 1
            else:
                print(f"  ✗ Failed: {error}")
                self.stats['failed'] += 1
            
            print()
        
        return coveo_documents
    
    def save_coveo_payload(self, documents):
        """Save Coveo payload to JSON file for reference"""
        output_file = os.path.join(config.OUTPUT_DIR, config.COVEO_PAYLOAD_FILE)
        
        payload = {
            'metadata': {
                'organization_id': self.org_id,
                'source_id': self.source_id,
                'total_documents': len(documents),
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            'documents': documents
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Coveo payload saved to: {output_file}")
    
    def print_summary(self):
        """Print indexing summary"""
        print("\n" + "="*60)
        print("Coveo Indexing Summary")
        print("="*60)
        print(f"Total products: {self.stats['total']}")
        print(f"Successfully pushed: {self.stats['success']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Success rate: {(self.stats['success']/self.stats['total']*100):.1f}%")
        print("="*60)


def main(input_file=None):
    """Main function"""
    # Check configuration
    if not all([config.COVEO_ORGANIZATION_ID, config.COVEO_PUSH_API_KEY, config.COVEO_SOURCE_ID]):
        print("❌ Error: Coveo configuration missing in .env")
        print("Required variables:")
        print("  - COVEO_ORGANIZATION_ID")
        print("  - COVEO_PUSH_API_KEY")
        print("  - COVEO_SOURCE_ID")
        return
    
    indexer = CoveoIndexer()
    
    # Load product data
    products = indexer.load_products(input_file)
    if not products:
        return
    
    # Push all documents to Coveo
    coveo_documents = indexer.push_all_documents(products)
    
    # Save Coveo payload for reference
    indexer.save_coveo_payload(coveo_documents)
    
    # Print summary
    indexer.print_summary()
    
    print("\n✅ Indexing complete!")
    print("\nNext steps:")
    print("  1. Wait 1-2 minutes for Coveo to index the documents")
    print("  2. Verify in Coveo Content Browser")
    print("  3. Run: cd ../backend/embedding_generator && python generate_embeddings.py")
    print("  4. Test the search UI")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Index products to Coveo")
    parser.add_argument("--input", "-i", type=str, default=None,
                        help="Input JSON file (default: scraped_products.json)")
    
    args = parser.parse_args()
    main(input_file=args.input)
