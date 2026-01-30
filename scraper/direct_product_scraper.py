"""
Direct Product Scraper

Scrapes specific product URLs directly
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import hashlib
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
import config


class DirectProductScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.products = []
    
    def generate_asset_id(self, product_url):
        """Generate unique asset ID from product URL"""
        url_hash = hashlib.md5(product_url.encode()).hexdigest()[:8]
        return f"hermes-{url_hash}"
    
    def fetch_product_page(self, url):
        """Fetch a product page"""
        try:
            print(f"  Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            time.sleep(2)  # Be respectful
            return response.text
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return None
    
    def extract_product_data(self, html, product_url):
        """Extract product data from product page"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            product = {
                'asset_id': self.generate_asset_id(product_url),
                'product_url': product_url,
                'brand': 'Hermès',
                'scraped_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Extract title
            title_selectors = [
                'h1.product-name',
                'h1[class*="product"]',
                'h1',
                'meta[property="og:title"]',
                'title'
            ]
            for selector in title_selectors:
                if selector.startswith('meta'):
                    elem = soup.find('meta', property='og:title')
                    if elem and elem.get('content'):
                        product['title'] = elem['content'].replace(' | Hermès USA', '').strip()
                        break
                elif selector == 'title':
                    elem = soup.find('title')
                    if elem:
                        product['title'] = elem.get_text().replace(' | Hermès USA', '').strip()
                        break
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        product['title'] = elem.get_text(strip=True)
                        break
            
            # Extract description
            desc_selectors = [
                'meta[property="og:description"]',
                'meta[name="description"]',
                '.product-description',
                '[class*="description"]'
            ]
            for selector in desc_selectors:
                if selector.startswith('meta'):
                    if 'og:description' in selector:
                        elem = soup.find('meta', property='og:description')
                    else:
                        elem = soup.find('meta', attrs={'name': 'description'})
                    if elem and elem.get('content'):
                        product['description'] = elem['content']
                        break
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        product['description'] = elem.get_text(strip=True)
                        break
            
            # Extract price
            price_selectors = [
                '[class*="price"]',
                '[data-price]',
                'span.price',
                'div.price'
            ]
            for selector in price_selectors:
                elem = soup.select_one(selector)
                if elem:
                    price_text = elem.get_text(strip=True)
                    if '$' in price_text or '€' in price_text:
                        product['price'] = price_text
                        break
            
            # Extract main image
            image_selectors = [
                'meta[property="og:image"]',
                'img[class*="product"]',
                'img[class*="main"]',
                '.product-image img',
                'picture img',
                'img[src*="hermesproduct"]'
            ]
            for selector in image_selectors:
                if selector.startswith('meta'):
                    elem = soup.find('meta', property='og:image')
                    if elem and elem.get('content'):
                        product['image_url'] = elem['content']
                        break
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        # Try different attributes
                        for attr in ['src', 'data-src', 'data-lazy-src']:
                            if elem.get(attr):
                                img_url = elem[attr]
                                if 'http' in img_url and 'placeholder' not in img_url.lower():
                                    product['image_url'] = img_url
                                    break
                        if product.get('image_url'):
                            break
            
            # Extract category from URL
            url_parts = product_url.split('/')
            if 'product' in url_parts:
                idx = url_parts.index('product')
                if idx > 0:
                    product['category'] = url_parts[idx - 1]
            
            # Extract SKU from URL
            if '/product/' in product_url:
                sku = product_url.split('/product/')[-1].rstrip('/')
                product['sku'] = sku
            
            # Set defaults for missing fields
            if 'title' not in product:
                product['title'] = f"Hermès Product {product['asset_id']}"
            if 'description' not in product:
                product['description'] = ''
            if 'price' not in product:
                product['price'] = ''
            if 'category' not in product:
                product['category'] = 'products'
            if 'image_url' not in product:
                print(f"  ⚠️  No image found for {product_url}")
                return None
            
            # Generate S3 key
            ext = os.path.splitext(urlparse(product['image_url']).path)[1] or '.jpg'
            product['image_filename'] = f"{product['asset_id']}{ext}"
            product['s3_key'] = f"{config.S3_IMAGES_PREFIX}{product['image_filename']}"
            
            return product
            
        except Exception as e:
            print(f"  ✗ Error extracting data: {str(e)}")
            return None
    
    def scrape_product(self, url):
        """Scrape a single product"""
        print(f"\n[{len(self.products) + 1}] Scraping: {url}")
        
        html = self.fetch_product_page(url)
        if not html:
            return False
        
        product = self.extract_product_data(html, url)
        if product:
            self.products.append(product)
            print(f"  ✓ {product['title'][:60]}...")
            print(f"  Price: {product.get('price', 'N/A')}")
            print(f"  Image: {'✓' if product.get('image_url') else '✗'}")
            return True
        else:
            print(f"  ✗ Failed to extract product data")
            return False
    
    def scrape_products(self, urls):
        """Scrape multiple products"""
        print("\n" + "="*70)
        print("Direct Product Scraper")
        print("="*70)
        print(f"Products to scrape: {len(urls)}")
        print("="*70)
        
        success = 0
        failed = 0
        
        for url in urls:
            if self.scrape_product(url):
                success += 1
            else:
                failed += 1
        
        print("\n" + "="*70)
        print("Scraping Complete")
        print("="*70)
        print(f"Success: {success}")
        print(f"Failed: {failed}")
        print(f"Total: {len(self.products)}")
        print("="*70)
        
        return self.products
    
    def save_products(self):
        """Save scraped products"""
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(config.OUTPUT_DIR, config.SCRAPED_DATA_FILE)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved {len(self.products)} products to: {output_file}")
        return output_file


def main():
    """Main function"""
    # Product URLs to scrape
    product_urls = [
        'https://www.hermes.com/us/en/product/master-sneaker-H261881ZH01390/',
        'https://www.hermes.com/us/en/product/master-sneaker-H261881ZH20400/',
        'https://www.hermes.com/us/en/product/jet-sneaker-H242925ZHGT390/',
        'https://www.hermes.com/us/en/product/match-sneaker-H261863ZH01390/',
        'https://www.hermes.com/us/en/product/trail-sneaker-H242848ZH90415/',
        'https://www.hermes.com/us/en/product/day-sneaker-H252883ZH90410/',
        'https://www.hermes.com/us/en/product/fitted-shirt-H566000H20237/',
        'https://www.hermes.com/us/en/product/fitted-shirt-H566000H29037/',
        'https://www.hermes.com/us/en/product/h-straight-cut-embroidered-denim-shirt-H566060HA6041/',
        'https://www.hermes.com/us/en/product/h-straight-cut-embroidered-denim-shirt-H566060HA5037/',
        'https://www.hermes.com/us/en/product/metal-au-carre-straight-cut-shirt-H656500HH6639/',
        'https://www.hermes.com/us/en/product/rayures-de-laine-et-papier-reversible-straight-cut-jacket-H562340HD0148/',
        'https://www.hermes.com/us/en/product/straight-cut-denim-jacket-H562480HN6046/',
        'https://www.hermes.com/us/en/product/straight-cut-jacket-H562400HE1W52/',
        'https://www.hermes.com/us/en/product/cavalcadour-esquisse-swim-trunks-H568101H463SM/',
        'https://www.hermes.com/us/en/product/echappee-hermes-earrings-medium-model-H219597Bv00/',
        'https://www.hermes.com/us/en/product/chaine-d-ancre-enchainee-ring-small-model-H120647Bv00051/',
    ]
    
    scraper = DirectProductScraper()
    products = scraper.scrape_products(product_urls)
    
    if products:
        scraper.save_products()
        
        print("\nNext steps:")
        print("  1. Run: python metadata_enricher.py (optional, for more details)")
        print("  2. Run: python image_downloader.py (to download images to S3)")
        print("  3. Run: python coveo_indexer.py (to push to Coveo)")
    else:
        print("\n⚠️  No products were scraped successfully")


if __name__ == '__main__':
    main()
