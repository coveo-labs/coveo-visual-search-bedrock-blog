"""
Hermes Product Scraper

This scraper extracts product information from Hermes.com including:
- Product images
- Product titles
- Descriptions
- Prices
- Categories
- Product URLs

Note: This is for demonstration purposes only. Always respect robots.txt
and terms of service. Consider using official APIs when available.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os
import hashlib
from urllib.parse import urljoin, urlparse
from datetime import datetime
import config


class HermesScraper:
    def __init__(self):
        self.session = requests.Session()
        
        # Rotate through multiple user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        self.current_ua_index = 0
        
        self.update_headers()
        self.products = []
        self.seen_urls = set()  # Track seen product URLs to avoid duplicates
        
        # Create output directory
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    def update_headers(self):
        """Update session headers with rotating user agent"""
        self.session.headers.update({
            'User-Agent': self.user_agents[self.current_ua_index],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
    
    def generate_asset_id(self, product_url):
        """Generate unique asset ID from product URL"""
        # Use hash of URL for consistent IDs
        url_hash = hashlib.md5(product_url.encode()).hexdigest()[:8]
        return f"hermes-{url_hash}"
    
    def fetch_page(self, url, retry_count=0):
        """Fetch a page with error handling, rate limiting, and retries"""
        try:
            # Rotate user agent on retries
            if retry_count > 0:
                self.update_headers()
                print(f"  Retry {retry_count}/{config.MAX_RETRIES} with different user agent...")
                time.sleep(config.RETRY_DELAY)
            
            print(f"  Fetching: {url}")
            response = self.session.get(
                url,
                timeout=config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            
            # Check for rate limiting or blocking
            if response.status_code == 403:
                if retry_count < config.MAX_RETRIES:
                    print(f"  ⚠️  403 Forbidden - Retrying with different approach...")
                    return self.fetch_page(url, retry_count + 1)
                else:
                    print(f"  ✗ 403 Forbidden after {config.MAX_RETRIES} retries")
                    return None
            
            response.raise_for_status()
            time.sleep(config.REQUEST_DELAY)  # Be respectful
            return response.text
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403 and retry_count < config.MAX_RETRIES:
                return self.fetch_page(url, retry_count + 1)
            print(f"  ✗ HTTP Error: {str(e)}")
            return None
        except Exception as e:
            if retry_count < config.MAX_RETRIES:
                print(f"  ⚠️  Error: {str(e)} - Retrying...")
                return self.fetch_page(url, retry_count + 1)
            print(f"  ✗ Error after retries: {str(e)}")
            return None
    
    def extract_product_info(self, product_element, category):
        """Extract product information from HTML element"""
        try:
            product_data = {
                'asset_id': '',
                'title': '',
                'description': '',
                'price': '',
                'category': category,
                'product_url': '',
                'image_url': '',
                'image_filename': '',
                's3_key': '',
                'brand': 'Hermès',
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            # Extract product URL first (most important)
            link_elem = product_element.find('a', href=True)
            if link_elem:
                product_url = urljoin(config.BASE_URL, link_elem['href'])
                
                # Skip if we've already seen this product
                if product_url in self.seen_urls:
                    return None
                
                product_data['product_url'] = product_url
                product_data['asset_id'] = self.generate_asset_id(product_url)
                self.seen_urls.add(product_url)
            else:
                return None
            
            # Extract title - try multiple selectors
            title_selectors = [
                'h2', 'h3', 'h4',
                '.product-title', '.product-name',
                '[class*="title"]', '[class*="name"]',
                'a[title]'
            ]
            for selector in title_selectors:
                if selector == 'a[title]':
                    title_elem = product_element.find('a', title=True)
                    if title_elem and title_elem.get('title'):
                        product_data['title'] = title_elem['title'].strip()
                        break
                else:
                    title_elem = product_element.find(selector)
                    if title_elem:
                        product_data['title'] = title_elem.get_text(strip=True)
                        if product_data['title']:
                            break
            
            # Extract image URL - try multiple sources
            img_elem = product_element.find('img')
            if img_elem:
                # Try different image attributes
                for attr in ['src', 'data-src', 'data-lazy-src', 'data-original']:
                    if img_elem.get(attr):
                        image_url = img_elem[attr]
                        # Skip placeholder images
                        if 'placeholder' not in image_url.lower() and 'data:image' not in image_url:
                            product_data['image_url'] = urljoin(config.BASE_URL, image_url)
                            break
                
                # Generate filename from asset_id
                if product_data['image_url']:
                    ext = os.path.splitext(urlparse(product_data['image_url']).path)[1] or '.jpg'
                    product_data['image_filename'] = f"{product_data['asset_id']}{ext}"
                    product_data['s3_key'] = f"{config.S3_IMAGES_PREFIX}{product_data['image_filename']}"
            
            # Extract price - try multiple selectors
            price_selectors = [
                '.price', '.product-price', '[class*="price"]',
                '[data-price]', 'span.price', 'div.price'
            ]
            for selector in price_selectors:
                if selector == '[data-price]':
                    price_elem = product_element.find(attrs={'data-price': True})
                    if price_elem:
                        product_data['price'] = price_elem['data-price']
                        break
                else:
                    price_elem = product_element.find(class_=selector.replace('.', ''))
                    if not price_elem:
                        price_elem = product_element.select_one(selector)
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        if price_text and ('$' in price_text or '€' in price_text or price_text.replace(',', '').replace('.', '').isdigit()):
                            product_data['price'] = price_text
                            break
            
            # Extract description
            desc_elem = product_element.find(['p', 'div'], class_=['description', 'product-description'])
            if desc_elem:
                product_data['description'] = desc_elem.get_text(strip=True)
            
            # Only return if we have at least URL and image
            if product_data['product_url'] and product_data['image_url']:
                return product_data
            
            return None
            
        except Exception as e:
            print(f"  ✗ Error extracting product info: {str(e)}")
            return None
    
    def scrape_category(self, category_url):
        """Scrape products from a category page"""
        print(f"\n{'='*60}")
        print(f"Scraping category: {category_url}")
        print(f"{'='*60}")
        
        full_url = urljoin(config.BASE_URL, category_url)
        html = self.fetch_page(full_url)
        
        if not html:
            print(f"  ⊘ Skipping category (fetch failed)")
            return []
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Try multiple selector strategies
        product_elements = []
        
        # Strategy 1: Common product container classes
        selectors = [
            'div.product-item',
            'div.product-card',
            'article.product',
            'div.product',
            'li.product-item',
            'div[class*="product"]',
            'article[class*="product"]',
            'div.grid-item',
            'div[data-product-id]',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  ✓ Found {len(elements)} products using selector: {selector}")
                product_elements = elements
                break
        
        # Strategy 2: Find all links to product pages
        if not product_elements:
            print(f"  Trying alternative: finding product links...")
            product_links = soup.find_all('a', href=lambda x: x and '/product/' in x)
            if product_links:
                print(f"  ✓ Found {len(product_links)} product links")
                # Wrap links in a container for consistent processing
                product_elements = [link.parent for link in product_links if link.parent]
        
        # Strategy 3: Look for image containers
        if not product_elements:
            print(f"  Trying alternative: finding image containers...")
            img_containers = soup.find_all('div', class_=lambda x: x and ('image' in x.lower() or 'img' in x.lower()))
            if img_containers:
                print(f"  ✓ Found {len(img_containers)} image containers")
                product_elements = img_containers
        
        if not product_elements:
            print(f"  ⊘ No products found in this category")
            return []
        
        category_name = category_url.split('/')[-2] if category_url.endswith('/') else category_url.split('/')[-1]
        
        products = []
        processed = 0
        for idx, element in enumerate(product_elements):
            if processed >= config.MAX_PRODUCTS_PER_CATEGORY:
                break
            
            if len(self.products) >= config.MAX_TOTAL_PRODUCTS:
                print(f"  ⚠️  Reached maximum total products ({config.MAX_TOTAL_PRODUCTS})")
                break
            
            print(f"  [{processed + 1}/{min(len(product_elements), config.MAX_PRODUCTS_PER_CATEGORY)}] Extracting product...")
            
            product = self.extract_product_info(element, category_name)
            if product and product['asset_id']:
                products.append(product)
                processed += 1
                title_preview = product.get('title', 'No title')[:50] or 'No title'
                print(f"    ✓ {title_preview}...")
            else:
                print(f"    ⊘ Skipped (incomplete data or duplicate)")
        
        print(f"\n  Extracted {len(products)} unique products from this category")
        return products
    
    def scrape_all_categories(self):
        """Scrape all configured categories"""
        print("\n" + "="*60)
        print("Starting Hermes Product Scraper")
        print("="*60)
        print(f"Categories to scrape: {len(config.CATEGORIES)}")
        print(f"Max products per category: {config.MAX_PRODUCTS_PER_CATEGORY}")
        print(f"Max total products: {config.MAX_TOTAL_PRODUCTS}")
        print("="*60)
        
        all_products = []
        
        for category_url in config.CATEGORIES:
            if len(all_products) >= config.MAX_TOTAL_PRODUCTS:
                print(f"\nReached maximum of {config.MAX_TOTAL_PRODUCTS} products. Stopping.")
                break
            
            products = self.scrape_category(category_url)
            all_products.extend(products)
        
        self.products = all_products[:config.MAX_TOTAL_PRODUCTS]
        
        print("\n" + "="*60)
        print(f"Scraping Complete!")
        print(f"Total products scraped: {len(self.products)}")
        print("="*60)
        
        return self.products
    
    def save_scraped_data(self):
        """Save scraped data to JSON file"""
        output_file = os.path.join(config.OUTPUT_DIR, config.SCRAPED_DATA_FILE)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Scraped data saved to: {output_file}")
        return output_file
    
    def get_summary(self):
        """Get summary statistics"""
        if not self.products:
            return {}
        
        categories = {}
        for product in self.products:
            cat = product.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_products': len(self.products),
            'categories': categories,
            'products_with_images': sum(1 for p in self.products if p.get('image_url')),
            'products_with_prices': sum(1 for p in self.products if p.get('price')),
        }


def main():
    """Main scraping function"""
    scraper = HermesScraper()
    
    # Scrape products
    products = scraper.scrape_all_categories()
    
    if not products:
        print("\n⚠️  No products were scraped. Please check:")
        print("  1. Website structure may have changed")
        print("  2. Network connectivity")
        print("  3. robots.txt restrictions")
        return
    
    # Save scraped data
    scraper.save_scraped_data()
    
    # Print summary
    summary = scraper.get_summary()
    print("\n" + "="*60)
    print("Scraping Summary:")
    print("="*60)
    print(f"Total products: {summary['total_products']}")
    print(f"Products with images: {summary['products_with_images']}")
    print(f"Products with prices: {summary['products_with_prices']}")
    print("\nProducts by category:")
    for cat, count in summary['categories'].items():
        print(f"  {cat}: {count}")
    print("="*60)
    
    print("\nNext steps:")
    print("  1. Run: python image_downloader.py (to download images to S3)")
    print("  2. Run: python coveo_indexer.py (to push to Coveo)")


if __name__ == '__main__':
    main()
