#!/usr/bin/env python3
"""
OpenSearch Cleanup and Re-index Script

This script:
1. Deletes all documents from the OpenSearch index
2. Re-generates embeddings from S3 images
3. Indexes fresh data with correct URLs

Usage:
  python cleanup_and_reindex.py [--delete-only] [--index-only]
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Load environment from project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'scraper'))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

# Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
OPENSEARCH_ENDPOINT = os.getenv('OPENSEARCH_ENDPOINT')
OPENSEARCH_INDEX = os.getenv('OPENSEARCH_INDEX_NAME', 'luxury-image-embeddings')
S3_BUCKET = os.getenv('S3_BUCKET_NAME')
S3_PREFIX = os.getenv('S3_IMAGES_PREFIX', 'hermes-images/')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'amazon.titan-embed-image-v1')

# Product data file (from AI pipeline)
PRODUCTS_FILE = project_root / 'scraper' / 'output' / 'ai_enriched_products.json'

# Initialize AWS clients
session = boto3.Session(region_name=AWS_REGION)
credentials = session.get_credentials()
s3_client = session.client('s3')
bedrock_runtime = session.client('bedrock-runtime')

# OpenSearch auth
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    AWS_REGION,
    'es',
    session_token=credentials.token
)

# Initialize OpenSearch client
opensearch_client = OpenSearch(
    hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


def delete_all_documents():
    """Delete all documents from the OpenSearch index"""
    print("\n" + "="*60)
    print("Deleting all documents from OpenSearch")
    print("="*60)
    print(f"Index: {OPENSEARCH_INDEX}")
    print(f"Endpoint: {OPENSEARCH_ENDPOINT}")
    
    try:
        # Check if index exists
        if not opensearch_client.indices.exists(index=OPENSEARCH_INDEX):
            print(f"Index '{OPENSEARCH_INDEX}' does not exist. Nothing to delete.")
            return True
        
        # Get document count
        count_response = opensearch_client.count(index=OPENSEARCH_INDEX)
        doc_count = count_response.get('count', 0)
        print(f"Current document count: {doc_count}")
        
        if doc_count == 0:
            print("Index is already empty.")
            return True
        
        # Delete by query (all documents)
        print("Deleting all documents...")
        response = opensearch_client.delete_by_query(
            index=OPENSEARCH_INDEX,
            body={"query": {"match_all": {}}},
            refresh=True
        )
        
        deleted = response.get('deleted', 0)
        print(f"✓ Deleted {deleted} documents")
        
        # Verify
        count_response = opensearch_client.count(index=OPENSEARCH_INDEX)
        remaining = count_response.get('count', 0)
        print(f"Remaining documents: {remaining}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error deleting documents: {e}")
        return False


def generate_embedding(image_bytes):
    """Generate embedding using Amazon Bedrock Titan"""
    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        body = json.dumps({"inputImage": image_base64})
        
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body.get('embedding')
        
    except Exception as e:
        print(f"  ✗ Embedding error: {e}")
        return None


def get_image_from_s3(s3_key):
    """Download image from S3"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        return response['Body'].read()
    except Exception as e:
        print(f"  ✗ S3 error for {s3_key}: {e}")
        return None


def index_document(asset_id, embedding, image_url, metadata=None):
    """Index a document in OpenSearch"""
    try:
        doc = {
            'asset_id': asset_id,
            'embedding_vector': embedding,
            'image_url': image_url,
            'metadata': metadata or {}
        }
        
        response = opensearch_client.index(
            index=OPENSEARCH_INDEX,
            id=asset_id,
            body=doc,
            refresh=False
        )
        
        return response.get('result') in ['created', 'updated']
        
    except Exception as e:
        print(f"  ✗ Index error: {e}")
        return False


def ensure_index_exists():
    """Create the index if it doesn't exist"""
    if opensearch_client.indices.exists(index=OPENSEARCH_INDEX):
        print(f"Index '{OPENSEARCH_INDEX}' already exists")
        return True
    
    print(f"Creating index '{OPENSEARCH_INDEX}'...")
    
    # Index mapping with k-NN vector field
    mapping = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 100
            }
        },
        "mappings": {
            "properties": {
                "asset_id": {"type": "keyword"},
                "embedding_vector": {
                    "type": "knn_vector",
                    "dimension": 1024,  # Titan embedding dimension
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib",
                        "parameters": {
                            "ef_construction": 128,
                            "m": 24
                        }
                    }
                },
                "image_url": {"type": "keyword"},
                "metadata": {"type": "object", "enabled": True}
            }
        }
    }
    
    try:
        opensearch_client.indices.create(index=OPENSEARCH_INDEX, body=mapping)
        print(f"✓ Index created")
        return True
    except Exception as e:
        print(f"✗ Error creating index: {e}")
        return False


def reindex_from_products():
    """Re-index all products with fresh embeddings"""
    print("\n" + "="*60)
    print("Re-indexing products with embeddings")
    print("="*60)
    print(f"Products file: {PRODUCTS_FILE}")
    print(f"S3 Bucket: {S3_BUCKET}")
    print(f"Bedrock Model: {BEDROCK_MODEL_ID}")
    
    # Load products
    if not PRODUCTS_FILE.exists():
        print(f"✗ Products file not found: {PRODUCTS_FILE}")
        return False
    
    with open(PRODUCTS_FILE, 'r') as f:
        products = json.load(f)
    
    print(f"Loaded {len(products)} products")
    
    # Ensure index exists
    if not ensure_index_exists():
        return False
    
    success = 0
    failed = 0
    
    for i, product in enumerate(products, 1):
        asset_id = product.get('asset_id')
        s3_key = product.get('s3_key')
        image_url = product.get('image_url')  # Unsplash URL
        
        print(f"\n[{i}/{len(products)}] Processing {asset_id}...")
        
        if not s3_key:
            print(f"  ✗ No S3 key for {asset_id}")
            failed += 1
            continue
        
        # Get image from S3
        print(f"  Downloading from S3: {s3_key}")
        image_bytes = get_image_from_s3(s3_key)
        if not image_bytes:
            failed += 1
            continue
        
        # Generate embedding
        print(f"  Generating embedding...")
        embedding = generate_embedding(image_bytes)
        if not embedding:
            failed += 1
            continue
        
        # Prepare metadata
        metadata = {
            'title': product.get('title', ''),
            'category': product.get('category', ''),
            'subcategory': product.get('subcategory', ''),
            'color': product.get('color', ''),
            'material': product.get('material', ''),
            'style': product.get('style', ''),
            'gender': product.get('gender', ''),
            'brand': product.get('brand', 'Hermès'),
        }
        
        # Index document with Unsplash URL
        print(f"  Indexing with URL: {image_url[:50]}...")
        if index_document(asset_id, embedding, image_url, metadata):
            print(f"  ✓ Indexed successfully")
            success += 1
        else:
            failed += 1
    
    # Refresh index
    print("\nRefreshing index...")
    opensearch_client.indices.refresh(index=OPENSEARCH_INDEX)
    
    # Print summary
    print("\n" + "="*60)
    print("Re-indexing Complete")
    print("="*60)
    print(f"Total products: {len(products)}")
    print(f"Successfully indexed: {success}")
    print(f"Failed: {failed}")
    print("="*60)
    
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="OpenSearch Cleanup and Re-index")
    parser.add_argument("--delete-only", action="store_true", help="Only delete documents, don't re-index")
    parser.add_argument("--index-only", action="store_true", help="Only re-index, don't delete first")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("OpenSearch Cleanup and Re-index")
    print("="*60)
    print(f"OpenSearch Endpoint: {OPENSEARCH_ENDPOINT}")
    print(f"Index: {OPENSEARCH_INDEX}")
    print(f"S3 Bucket: {S3_BUCKET}")
    print("="*60)
    
    if not OPENSEARCH_ENDPOINT:
        print("✗ OPENSEARCH_ENDPOINT not set in .env")
        return 1
    
    if not args.index_only:
        if not delete_all_documents():
            print("Failed to delete documents")
            return 1
    
    if not args.delete_only:
        if not reindex_from_products():
            print("Failed to re-index products")
            return 1
    
    print("\n✅ Done!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
