"""
Configuration for Hermes scraper
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (parent of scraper directory)
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_IMAGES_PREFIX = os.getenv('S3_IMAGES_PREFIX', 'hermes-images/')

# Coveo Configuration
COVEO_ORGANIZATION_ID = os.getenv('COVEO_ORGANIZATION_ID')
COVEO_PUSH_API_KEY = os.getenv('COVEO_PUSH_API_KEY')
COVEO_SEARCH_API_KEY = os.getenv('COVEO_SEARCH_API_KEY')
COVEO_FIELD_API_KEY = os.getenv('COVEO_FIELD_API_KEY')
COVEO_SOURCE_ID = os.getenv('COVEO_SOURCE_ID')

# Scraping Configuration
BASE_URL = "https://www.hermes.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Categories to scrape - comprehensive list trying different URL patterns
CATEGORIES = [
    # Women's Bags - Different subcategories
    "/us/en/category/women/bags-and-small-leather-goods/bags-and-clutches/",
    "/us/en/category/women/bags-and-small-leather-goods/handbags/",
    "/us/en/category/women/bags-and-small-leather-goods/shoulder-bags/",
    "/us/en/category/women/bags-and-small-leather-goods/crossbody-bags/",
    "/us/en/category/women/bags-and-small-leather-goods/tote-bags/",
    "/us/en/category/women/bags-and-small-leather-goods/clutches/",
    "/us/en/category/women/bags-and-small-leather-goods/backpacks/",
    "/us/en/category/women/bags-and-small-leather-goods/",
    
    # Women's Accessories
    "/us/en/category/women/accessories/",
    "/us/en/category/women/accessories/scarves-and-silk-accessories/",
    "/us/en/category/women/accessories/belts/",
    "/us/en/category/women/accessories/hats-and-gloves/",
    "/us/en/category/women/accessories/small-leather-goods/",
    
    # Women's Jewelry
    "/us/en/category/women/jewelry/",
    "/us/en/category/women/jewelry/bracelets/",
    "/us/en/category/women/jewelry/necklaces/",
    "/us/en/category/women/jewelry/rings/",
    "/us/en/category/women/jewelry/earrings/",
    
    # Women's Shoes
    "/us/en/category/women/shoes/",
    "/us/en/category/women/shoes/sandals/",
    "/us/en/category/women/shoes/pumps/",
    "/us/en/category/women/shoes/sneakers/",
    
    # Men's Bags
    "/us/en/category/men/bags-and-small-leather-goods/",
    "/us/en/category/men/bags-and-small-leather-goods/briefcases/",
    "/us/en/category/men/bags-and-small-leather-goods/messenger-bags/",
    "/us/en/category/men/bags-and-small-leather-goods/backpacks/",
    "/us/en/category/men/bags-and-small-leather-goods/travel-bags/",
    
    # Men's Accessories
    "/us/en/category/men/accessories/",
    "/us/en/category/men/accessories/belts/",
    "/us/en/category/men/accessories/ties/",
    "/us/en/category/men/accessories/small-leather-goods/",
    
    # Men's Shoes
    "/us/en/category/men/shoes/",
    "/us/en/category/men/shoes/sneakers/",
    "/us/en/category/men/shoes/loafers/",
    
    # Home
    "/us/en/category/home/",
    "/us/en/category/home/decorative-objects/",
    "/us/en/category/home/tableware/",
    "/us/en/category/home/textiles/",
    
    # Watches
    "/us/en/category/women/watches/",
    "/us/en/category/men/watches/",
    
    # Try story/collection pages
    "/us/en/story/women/bags/",
    "/us/en/story/men/bags/",
]

# Scraping limits
MAX_PRODUCTS_PER_CATEGORY = 15  # Increased to get more per category
MAX_TOTAL_PRODUCTS = 50
MAX_RETRIES = 3  # Retry failed requests

# Request settings
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 3  # Increased delay to be more respectful
RETRY_DELAY = 5  # Delay between retries

# Image settings
IMAGE_MAX_SIZE = (1200, 1200)  # Max dimensions for images
IMAGE_QUALITY = 85  # JPEG quality

# Output
OUTPUT_DIR = "output"
SCRAPED_DATA_FILE = "scraped_products.json"
COVEO_PAYLOAD_FILE = "coveo_payload.json"
