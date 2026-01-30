"""
Check Asset IDs in OpenSearch vs Coveo
Diagnose why search results don't match
"""

import os
import json
import boto3
import requests
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENSEARCH_ENDPOINT = os.getenv('OPENSEARCH_ENDPOINT')
OPENSEARCH_INDEX = os.getenv('OPENSEARCH_INDEX_NAME', 'luxury-image-embeddings')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
COVEO_ORG_ID = os.getenv('COVEO_ORGANIZATION_ID')
COVEO_SEARCH_API_KEY = os.getenv('COVEO_SEARCH_API_KEY')

print("=" * 70)
print("Asset ID Comparison: OpenSearch vs Coveo")
print("=" * 70)

# Get OpenSearch asset IDs
print("\n1. Getting asset IDs from OpenSearch...")
try:
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, AWS_REGION, 'es')
    
    opensearch_client = OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30
    )
    
    # Get all documents
    response = opensearch_client.search(
        index=OPENSEARCH_INDEX,
        body={
            "size": 100,
            "query": {"match_all": {}},
            "_source": ["asset_id"]
        }
    )
    
    opensearch_ids = set()
    for hit in response['hits']['hits']:
        opensearch_ids.add(hit['_source']['asset_id'])
    
    print(f"   Found {len(opensearch_ids)} asset IDs in OpenSearch")
    print(f"   Sample: {list(opensearch_ids)[:5]}")
    
except Exception as e:
    print(f"   Error: {str(e)}")
    opensearch_ids = set()

# Get Coveo asset IDs
print("\n2. Getting asset IDs from Coveo...")
try:
    url = f"https://{COVEO_ORG_ID}.org.coveo.com/rest/search/v2"
    headers = {
        'Authorization': f'Bearer {COVEO_SEARCH_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "q": "",
        "numberOfResults": 100,
        "fieldsToInclude": ["assetid", "title"]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    coveo_ids = set()
    for result in data.get('results', []):
        asset_id = result.get('raw', {}).get('assetid')
        if asset_id:
            coveo_ids.add(asset_id)
    
    print(f"   Found {len(coveo_ids)} asset IDs in Coveo")
    print(f"   Sample: {list(coveo_ids)[:5]}")
    
except Exception as e:
    print(f"   Error: {str(e)}")
    coveo_ids = set()

# Compare
print("\n3. Comparison:")
print("=" * 70)

matching = opensearch_ids & coveo_ids
only_opensearch = opensearch_ids - coveo_ids
only_coveo = coveo_ids - opensearch_ids

print(f"   Matching IDs: {len(matching)}")
print(f"   Only in OpenSearch: {len(only_opensearch)}")
print(f"   Only in Coveo: {len(only_coveo)}")

if matching:
    print(f"\n   ✅ Matching IDs: {list(matching)[:5]}...")
if only_opensearch:
    print(f"\n   ⚠️  Only in OpenSearch: {list(only_opensearch)[:5]}...")
if only_coveo:
    print(f"\n   ⚠️  Only in Coveo: {list(only_coveo)[:5]}...")

print("\n" + "=" * 70)
if len(matching) == 0:
    print("❌ NO MATCHING ASSET IDs!")
    print("   This is why Coveo returns no results.")
    print("\n   Solution: Re-index Coveo with the same data that's in OpenSearch,")
    print("   OR delete OpenSearch index and regenerate embeddings from Coveo data.")
elif len(matching) < len(opensearch_ids):
    print(f"⚠️  Only {len(matching)} of {len(opensearch_ids)} OpenSearch IDs match Coveo")
else:
    print("✅ All OpenSearch asset IDs have matching Coveo documents!")
print("=" * 70)
