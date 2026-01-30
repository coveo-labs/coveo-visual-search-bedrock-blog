"""
Check what fields exist in Coveo documents
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

COVEO_ORG_ID = os.getenv('COVEO_ORGANIZATION_ID')
COVEO_SEARCH_API_KEY = os.getenv('COVEO_SEARCH_API_KEY')

print("=" * 70)
print("Checking Coveo Documents")
print("=" * 70)

try:
    url = f"https://{COVEO_ORG_ID}.org.coveo.com/rest/search/v2"
    headers = {
        'Authorization': f'Bearer {COVEO_SEARCH_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Search for all documents, get all fields
    payload = {
        "q": "",
        "numberOfResults": 5
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    total = data.get('totalCount', 0)
    results = data.get('results', [])
    
    print(f"\nTotal documents in Coveo: {total}")
    print(f"Retrieved: {len(results)}")
    
    if results:
        print("\n" + "=" * 70)
        print("Sample Document Fields:")
        print("=" * 70)
        
        for i, result in enumerate(results[:2]):
            print(f"\n--- Document {i+1} ---")
            print(f"Title: {result.get('title', 'N/A')}")
            print(f"URI: {result.get('uri', 'N/A')}")
            print(f"ClickableUri: {result.get('clickableUri', 'N/A')}")
            
            raw = result.get('raw', {})
            print(f"\nRaw fields ({len(raw)} total):")
            for key, value in sorted(raw.items()):
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"  {key}: {value}")
    else:
        print("\n❌ No documents found in Coveo!")
        print("   You need to re-push documents to Coveo.")
        print("   Run: cd ../../scraper && python coveo_indexer.py")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
