"""
Scrape products from URLs file

Reads URLs from product_urls.txt and scrapes them
"""

from direct_product_scraper import DirectProductScraper
import os


def load_urls_from_file(filename='product_urls.txt'):
    """Load URLs from text file"""
    if not os.path.exists(filename):
        print(f"❌ Error: {filename} not found")
        return []
    
    urls = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                urls.append(line)
    
    return urls


def main():
    """Main function"""
    print("="*70)
    print("Scraping Products from URLs File")
    print("="*70)
    
    # Load URLs
    urls = load_urls_from_file('product_urls.txt')
    
    if not urls:
        print("\n⚠️  No URLs found in product_urls.txt")
        print("\nPlease add product URLs to product_urls.txt (one per line)")
        return
    
    print(f"\nFound {len(urls)} URLs to scrape")
    print("="*70)
    
    # Scrape products
    scraper = DirectProductScraper()
    products = scraper.scrape_products(urls)
    
    if products:
        scraper.save_products()
        
        print("\n" + "="*70)
        print("✅ Success!")
        print("="*70)
        print(f"Scraped {len(products)} products")
        print("\nNext steps:")
        print("  1. Run: python metadata_enricher.py (optional)")
        print("  2. Run: python image_downloader.py")
        print("  3. Run: python coveo_indexer.py")
        print("\nTo add more products:")
        print("  1. Add more URLs to product_urls.txt")
        print("  2. Run this script again")
    else:
        print("\n❌ No products were scraped")


if __name__ == '__main__':
    main()
