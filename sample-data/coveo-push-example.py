"""
Example script to push sample products to Coveo
Run this to populate Coveo with test data
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

COVEO_ORG_ID = os.getenv('COVEO_ORGANIZATION_ID')
COVEO_PUSH_API_KEY = os.getenv('COVEO_PUSH_API_KEY')
COVEO_SOURCE_ID = os.getenv('COVEO_SOURCE_ID')

# Sample luxury products
SAMPLE_PRODUCTS = [
    {
        "documentId": "hermes-bag-001",
        "assetid": "hermes-bag-001",
        "title": "Birkin 30 Togo Leather Handbag",
        "description": "Iconic Hermès Birkin bag in supple Togo leather. Features palladium hardware and signature lock and key.",
        "category": "Handbags",
        "price": "$12,500",
        "imageurl": "https://your-bucket.s3.amazonaws.com/hermes-images/hermes-bag-001.jpg",
        "producturl": "https://www.hermes.com/us/en/product/birkin-30-togo-leather-handbag",
        "s3_key": "hermes-images/hermes-bag-001.jpg",
        "brand": "Hermès",
        "material": "Togo Leather",
        "color": "Gold"
    },
    {
        "documentId": "hermes-bag-002",
        "assetid": "hermes-bag-002",
        "title": "Kelly 28 Epsom Leather Handbag",
        "description": "Elegant Kelly bag in structured Epsom leather. Classic design with top handle and detachable shoulder strap.",
        "category": "Handbags",
        "price": "$11,000",
        "imageurl": "https://your-bucket.s3.amazonaws.com/hermes-images/hermes-bag-002.jpg",
        "producturl": "https://www.hermes.com/us/en/product/kelly-28-epsom-leather-handbag",
        "s3_key": "hermes-images/hermes-bag-002.jpg",
        "brand": "Hermès",
        "material": "Epsom Leather",
        "color": "Black"
    },
    {
        "documentId": "hermes-scarf-001",
        "assetid": "hermes-scarf-001",
        "title": "Silk Twill Scarf 90",
        "description": "Luxurious silk twill scarf with hand-rolled edges. Features iconic Hermès print.",
        "category": "Accessories",
        "price": "$425",
        "imageurl": "https://your-bucket.s3.amazonaws.com/hermes-images/hermes-scarf-001.jpg",
        "producturl": "https://www.hermes.com/us/en/product/silk-twill-scarf-90",
        "s3_key": "hermes-images/hermes-scarf-001.jpg",
        "brand": "Hermès",
        "material": "Silk",
        "color": "Multi"
    },
    {
        "documentId": "hermes-belt-001",
        "assetid": "hermes-belt-001",
        "title": "H Belt Buckle & Reversible Leather Strap",
        "description": "Iconic H belt buckle with reversible leather strap. Timeless accessory for any wardrobe.",
        "category": "Accessories",
        "price": "$850",
        "imageurl": "https://your-bucket.s3.amazonaws.com/hermes-images/hermes-belt-001.jpg",
        "producturl": "https://www.hermes.com/us/en/product/h-belt-buckle-reversible-leather-strap",
        "s3_key": "hermes-images/hermes-belt-001.jpg",
        "brand": "Hermès",
        "material": "Leather",
        "color": "Brown/Black"
    },
    {
        "documentId": "hermes-watch-001",
        "assetid": "hermes-watch-001",
        "title": "Cape Cod Watch, Large Model",
        "description": "Elegant timepiece with distinctive anchor chain-inspired case. Swiss automatic movement.",
        "category": "Watches",
        "price": "$5,200",
        "imageurl": "https://your-bucket.s3.amazonaws.com/hermes-images/hermes-watch-001.jpg",
        "producturl": "https://www.hermes.com/us/en/product/cape-cod-watch-large-model",
        "s3_key": "hermes-images/hermes-watch-001.jpg",
        "brand": "Hermès",
        "material": "Stainless Steel",
        "color": "Silver"
    }
]


def push_document(document):
    """Push a single document to Coveo"""
    url = f"https://api.cloud.coveo.com/push/v1/organizations/{COVEO_ORG_ID}/sources/{COVEO_SOURCE_ID}/documents"
    
    headers = {
        "Authorization": f"Bearer {COVEO_PUSH_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Add document to Coveo
    response = requests.put(
        f"{url}?documentId={document['documentId']}",
        headers=headers,
        json=document
    )
    
    return response


def main():
    """Push all sample products to Coveo"""
    print("=" * 80)
    print("Pushing Sample Products to Coveo")
    print("=" * 80)
    print()
    
    if not all([COVEO_ORG_ID, COVEO_PUSH_API_KEY, COVEO_SOURCE_ID]):
        print("❌ Error: Missing Coveo credentials in .env file")
        return
    
    print(f"Organization ID: {COVEO_ORG_ID}")
    print(f"Source ID: {COVEO_SOURCE_ID}")
    print(f"Products to push: {len(SAMPLE_PRODUCTS)}")
    print()
    
    success_count = 0
    failed_count = 0
    
    for i, product in enumerate(SAMPLE_PRODUCTS, 1):
        print(f"[{i}/{len(SAMPLE_PRODUCTS)}] Pushing: {product['title']}")
        
        try:
            response = push_document(product)
            
            if response.status_code in [200, 202]:
                print(f"  ✓ Success")
                success_count += 1
            else:
                print(f"  ✗ Failed: {response.status_code} - {response.text}")
                failed_count += 1
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            failed_count += 1
    
    print()
    print("=" * 80)
    print("Summary:")
    print(f"  Successfully pushed: {success_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 80)
    print()
    
    if success_count > 0:
        print("✅ Products pushed to Coveo!")
        print()
        print("Next steps:")
        print("  1. Wait for Coveo to index the documents (~1-2 minutes)")
        print("  2. Verify in Coveo Content Browser")
        print("  3. Run embedding generator to index to OpenSearch")
        print("  4. Test the search UI")


if __name__ == '__main__':
    main()
