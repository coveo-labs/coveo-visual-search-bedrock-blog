#!/usr/bin/env python3
"""
Verify Coveo Data

Check what image URLs are actually stored in Coveo
"""

import requests
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def search_coveo(query="", num_results=10):
    """Search Coveo and return results"""
    url = f"https://{config.COVEO_ORGANIZATION_ID}.org.coveo.com/rest/search/v2"
    
    headers = {
        'Authorization': f'Bearer {config.COVEO_SEARCH_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "q": query,
        "numberOfResults": num_results,
        "fieldsToInclude": [
            "assetid",
            "title",
            "imageurl",
            "clickableuri",
            "thumbnailurl",
            "producturl"
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main function"""
    print("\n" + "="*80)
    print("Verify Coveo Data - Image URLs")
    print("="*80)
    
    # Search for all products (increased to 100)
    data = search_coveo(query="", num_results=100)
    
    if not data:
        print("❌ Failed to retrieve data from Coveo")
        return
    
    results = data.get('results', [])
    print(f"\nFound {len(results)} products in Coveo\n")
    
    s3_count = 0
    unsplash_count = 0
    hermes_count = 0
    other_count = 0
    
    print("Checking clickableUri for each product:")
    print("-" * 80)
    
    for idx, result in enumerate(results, 1):
        title = result.get('title', 'Unknown')[:40]
        asset_id = result.get('raw', {}).get('assetid', 'N/A')
        click_uri = result.get('clickUri', 'N/A')
        
        # Categorize URL
        if 'hermes-poc-170871290698-images.s3' in click_uri:
            status = "✓ S3"
            s3_count += 1
        elif 'unsplash.com' in click_uri:
            status = "✓ Unsplash"
            unsplash_count += 1
        elif 'hermes.com' in click_uri:
            status = "✗ Hermes.com"
            hermes_count += 1
        else:
            status = "? Other"
            other_count += 1
        
        print(f"{idx:2}. [{status}] {asset_id:20} {title:40}")
        if status.startswith("✗") or status.startswith("?"):
            print(f"    URL: {click_uri[:80]}...")
    
    print("\n" + "="*80)
    print("Summary:")
    print("="*80)
    print(f"Total products: {len(results)}")
    print(f"✓ Unsplash URLs (correct for demo): {unsplash_count}")
    print(f"✓ S3 URLs (also correct): {s3_count}")
    print(f"✗ Hermes.com URLs (incorrect): {hermes_count}")
    print(f"? Other URLs: {other_count}")
    print("="*80)
    
    if unsplash_count + s3_count == len(results):
        print("\n✅ All products have correct image URLs!")
        print("   (Unsplash URLs are used for demo display)")
    else:
        print(f"\n⚠ {hermes_count + other_count} products have incorrect URLs")


if __name__ == '__main__':
    main()
