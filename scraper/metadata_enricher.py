"""
Metadata Enricher

Fetches detailed product information from individual product pages
Enriches existing scraped data with:
- Product title
- Detailed description
- Product details
- Product attributes (color, material, size, etc.)
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import config
from datetime import datetime, timezone


class MetadataEnricher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        self.stats = {
            'total': 0,
            'enriched': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def load_scraped_data(self):
        """Load scraped product data"""
        input_file = os.path.join(config.OUTPUT_DIR, config.SCRAPED_DATA_FILE)
        
        if not os.path.exists(input_file):
            print(f"❌ Error: {input_file} not found")
            return []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        print(f"✓ Loaded {len(products)} products from {input_file}")
        return products
    
    def fetch_product_page(self, url):
        """Fetch product detail page"""
        try:
            print(f"  Fetching: {url}")
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            time.sleep(config.REQUEST_DELAY)
            return response.text
        except Exception as e:
            print(f"  ✗ Error fetching: {str(e)}")
            return None
    
    def extract_product_metadata(self, html, product_url):
        """Extract detailed metadata from product page"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            metadata = {
                'title': '',
                'description': '',
                'product_details': {},
                'product_attributes': {},
                'long_description': '',
                'materials': [],
                'colors': [],
                'dimensions': '',
                'sku': ''
            }
            
            # Extract title
            title_selectors = [
                'h1.product-name',
                'h1[class*="product"]',
                'h1[class*="title"]',
                '.product-title',
                'h1'
            ]
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    metadata['title'] = title_elem.get_text(strip=True)
                    break
            
            # Extract description
            desc_selectors = [
                '.product-description',
                '[class*="description"]',
                '.product-info p',
                'meta[name="description"]'
            ]
            for selector in desc_selectors:
                if selector.startswith('meta'):
                    desc_elem = soup.select_one(selector)
                    if desc_elem and desc_elem.get('content'):
                        metadata['description'] = desc_elem.get('content')
                        break
                else:
                    desc_elem = soup.select_one(selector)
                    if desc_elem:
                        metadata['description'] = desc_elem.get_text(strip=True)
                        break
            
            # Extract long description
            long_desc_elem = soup.select_one('.product-long-description, .product-details-description')
            if long_desc_elem:
                metadata['long_description'] = long_desc_elem.get_text(strip=True)
            
            # Extract product details (specifications)
            details_section = soup.select('.product-details li, .product-specs li, .specifications li')
            for detail in details_section:
                text = detail.get_text(strip=True)
                if ':' in text:
                    key, value = text.split(':', 1)
                    metadata['product_details'][key.strip()] = value.strip()
                else:
                    metadata['product_details'][text] = True
            
            # Extract attributes from data attributes or structured data
            # Look for JSON-LD structured data
            json_ld = soup.find('script', type='application/ld+json')
            if json_ld:
                try:
                    structured_data = json.loads(json_ld.string)
                    if isinstance(structured_data, dict):
                        if 'name' in structured_data and not metadata['title']:
                            metadata['title'] = structured_data['name']
                        if 'description' in structured_data and not metadata['description']:
                            metadata['description'] = structured_data['description']
                        if 'sku' in structured_data:
                            metadata['sku'] = structured_data['sku']
                        if 'color' in structured_data:
                            metadata['colors'].append(structured_data['color'])
                        if 'material' in structured_data:
                            metadata['materials'].append(structured_data['material'])
                except:
                    pass
            
            # Extract color information
            color_elems = soup.select('[class*="color"], [data-color]')
            for elem in color_elems:
                color_text = elem.get_text(strip=True)
                if color_text and len(color_text) < 50:
                    metadata['colors'].append(color_text)
                color_attr = elem.get('data-color')
                if color_attr:
                    metadata['colors'].append(color_attr)
            
            # Extract material information
            material_keywords = ['leather', 'canvas', 'silk', 'cotton', 'wool', 'cashmere']
            text_content = soup.get_text().lower()
            for keyword in material_keywords:
                if keyword in text_content:
                    metadata['materials'].append(keyword.title())
            
            # Extract dimensions
            dim_elem = soup.select_one('[class*="dimension"], [class*="size"]')
            if dim_elem:
                metadata['dimensions'] = dim_elem.get_text(strip=True)
            
            # Extract SKU from URL or page
            if '/product/' in product_url:
                sku_from_url = product_url.split('/product/')[-1].split('/')[0]
                metadata['sku'] = sku_from_url
            
            # Clean up lists
            metadata['colors'] = list(set(metadata['colors']))[:5]  # Limit to 5 unique colors
            metadata['materials'] = list(set(metadata['materials']))[:5]
            
            return metadata
            
        except Exception as e:
            print(f"  ✗ Error extracting metadata: {str(e)}")
            return None
    
    def enrich_product(self, product):
        """Enrich a single product with detailed metadata"""
        product_url = product.get('product_url')
        
        if not product_url:
            print(f"  ⊘ No product URL for {product.get('asset_id')}")
            self.stats['skipped'] += 1
            return False
        
        # Check if already enriched
        if product.get('title') and product.get('description'):
            print(f"  ✓ Already enriched: {product.get('asset_id')}")
            self.stats['skipped'] += 1
            return True
        
        # Fetch product page
        html = self.fetch_product_page(product_url)
        if not html:
            self.stats['failed'] += 1
            return False
        
        # Extract metadata
        print(f"  ⚙ Extracting metadata...")
        metadata = self.extract_product_metadata(html, product_url)
        
        if not metadata:
            self.stats['failed'] += 1
            return False
        
        # Update product with enriched data
        if metadata['title']:
            product['title'] = metadata['title']
        if metadata['description']:
            product['description'] = metadata['description']
        if metadata['long_description']:
            product['long_description'] = metadata['long_description']
        
        product['product_details'] = metadata['product_details']
        product['product_attributes'] = {
            'colors': metadata['colors'],
            'materials': metadata['materials'],
            'dimensions': metadata['dimensions'],
            'sku': metadata['sku']
        }
        
        product['enriched_at'] = datetime.now(timezone.utc).isoformat()
        
        self.stats['enriched'] += 1
        print(f"  ✓ Enriched: {metadata['title'][:50]}...")
        return True
    
    def enrich_all_products(self, products):
        """Enrich all products with metadata"""
        print("\n" + "="*60)
        print("Enriching Product Metadata")
        print("="*60)
        print(f"Total products: {len(products)}")
        print("="*60 + "\n")
        
        self.stats['total'] = len(products)
        
        for idx, product in enumerate(products, 1):
            print(f"[{idx}/{len(products)}] Processing: {product.get('asset_id')}")
            self.enrich_product(product)
            print()
        
        return products
    
    def save_enriched_data(self, products):
        """Save enriched product data"""
        output_file = os.path.join(config.OUTPUT_DIR, config.SCRAPED_DATA_FILE)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Enriched data saved to: {output_file}")
    
    def print_summary(self):
        """Print enrichment summary"""
        print("\n" + "="*60)
        print("Metadata Enrichment Summary")
        print("="*60)
        print(f"Total products: {self.stats['total']}")
        print(f"Enriched: {self.stats['enriched']}")
        print(f"Skipped (already enriched): {self.stats['skipped']}")
        print(f"Failed: {self.stats['failed']}")
        print("="*60)


def main():
    """Main function"""
    enricher = MetadataEnricher()
    
    # Load scraped data
    products = enricher.load_scraped_data()
    if not products:
        return
    
    # Enrich all products
    enriched_products = enricher.enrich_all_products(products)
    
    # Save enriched data
    enricher.save_enriched_data(enriched_products)
    
    # Print summary
    enricher.print_summary()
    
    print("\nNext steps:")
    print("  1. Review enriched data: cat output/scraped_products.json | jq '.[0]'")
    print("  2. Re-push to Coveo: python coveo_indexer.py")


if __name__ == '__main__':
    main()
