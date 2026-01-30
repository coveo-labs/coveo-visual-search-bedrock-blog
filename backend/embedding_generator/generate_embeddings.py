"""
Pre-compute embeddings for images in S3 bucket
Run this script to generate embeddings for all images before demo
"""

import os
import json
import base64
import boto3
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
S3_BUCKET = os.getenv('S3_BUCKET_NAME')
S3_PREFIX = os.getenv('S3_IMAGES_PREFIX', 'hermes-images/')
OPENSEARCH_ENDPOINT = os.getenv('OPENSEARCH_ENDPOINT')
OPENSEARCH_INDEX = os.getenv('OPENSEARCH_INDEX_NAME', 'luxury-image-embeddings')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'amazon.titan-embed-image-v1')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Initialize clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

# Get AWS credentials for OpenSearch
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


def create_opensearch_index():
    """Create OpenSearch index with k-NN mapping"""
    index_body = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 512
            }
        },
        "mappings": {
            "properties": {
                "asset_id": {"type": "keyword"},
                "embedding_vector": {
                    "type": "knn_vector",
                    "dimension": 1024,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "nmslib",
                        "parameters": {
                            "ef_construction": 512,
                            "m": 16
                        }
                    }
                },
                "image_url": {"type": "keyword"},
                "metadata": {"type": "object"},
                "indexed_at": {"type": "date"}
            }
        }
    }
    
    try:
        if opensearch_client.indices.exists(index=OPENSEARCH_INDEX):
            print(f"Index {OPENSEARCH_INDEX} already exists")
        else:
            opensearch_client.indices.create(index=OPENSEARCH_INDEX, body=index_body)
            print(f"Created index: {OPENSEARCH_INDEX}")
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        raise


def generate_embedding(image_bytes):
    """Generate embedding using Bedrock Titan"""
    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        body = json.dumps({
            "inputImage": image_base64
        })
        
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        return response_body.get('embedding')
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None


def extract_asset_id_from_key(s3_key):
    """Extract asset ID from S3 key"""
    # Example: hermes-images/product-12345.jpg -> product-12345
    filename = s3_key.split('/')[-1]
    asset_id = filename.rsplit('.', 1)[0]
    return asset_id


def process_image(s3_key):
    """Process single image: download, generate embedding, index"""
    try:
        print(f"Processing: {s3_key}")
        
        # Extract asset ID
        asset_id = extract_asset_id_from_key(s3_key)
        
        # Check if already indexed
        try:
            existing = opensearch_client.get(index=OPENSEARCH_INDEX, id=asset_id)
            print(f"  ✓ Already indexed, skipping")
            return True
        except:
            pass
        
        # Download image from S3
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        image_bytes = response['Body'].read()
        
        # Generate embedding
        embedding = generate_embedding(image_bytes)
        if not embedding:
            print(f"  ✗ Failed to generate embedding")
            return False
        
        # Prepare document
        document = {
            'asset_id': asset_id,
            'embedding_vector': embedding,
            'image_url': f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}",
            'metadata': {
                's3_key': s3_key,
                's3_bucket': S3_BUCKET
            },
            'indexed_at': datetime.utcnow().isoformat()
        }
        
        # Index to OpenSearch
        opensearch_client.index(
            index=OPENSEARCH_INDEX,
            id=asset_id,
            body=document
        )
        
        print(f"  ✓ Indexed successfully")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


def main():
    """Main function to process all images"""
    print("=" * 80)
    print("Luxury Image Search - Embedding Generator")
    print("=" * 80)
    print()
    
    # Validate configuration
    if not all([S3_BUCKET, OPENSEARCH_ENDPOINT]):
        print("❌ Error: Missing required environment variables")
        print("   Please ensure .env file is configured with:")
        print("   - S3_BUCKET_NAME")
        print("   - OPENSEARCH_ENDPOINT")
        return
    
    print(f"Configuration:")
    print(f"  S3 Bucket: {S3_BUCKET}")
    print(f"  S3 Prefix: {S3_PREFIX}")
    print(f"  OpenSearch: {OPENSEARCH_ENDPOINT}")
    print(f"  Index: {OPENSEARCH_INDEX}")
    print(f"  Bedrock Model: {BEDROCK_MODEL_ID}")
    print()
    
    # Create index
    print("Creating OpenSearch index...")
    create_opensearch_index()
    print()
    
    # List images in S3
    print(f"Listing images from s3://{S3_BUCKET}/{S3_PREFIX}...")
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
    
    image_keys = []
    for page in pages:
        for obj in page.get('Contents', []):
            key = obj['Key']
            # Filter for image files
            if key.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                image_keys.append(key)
    
    print(f"Found {len(image_keys)} images")
    print()
    
    if not image_keys:
        print("⚠️  No images found. Please upload images to S3 bucket.")
        return
    
    # Process images
    print("Processing images...")
    print()
    
    success_count = 0
    failed_count = 0
    
    for i, key in enumerate(image_keys, 1):
        print(f"[{i}/{len(image_keys)}] ", end='')
        if process_image(key):
            success_count += 1
        else:
            failed_count += 1
    
    # Summary
    print()
    print("=" * 80)
    print("Summary:")
    print(f"  Total images: {len(image_keys)}")
    print(f"  Successfully indexed: {success_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 80)
    print()
    
    if success_count > 0:
        print("✅ Embedding generation completed!")
        print()
        print("Next steps:")
        print("  1. Verify embeddings in OpenSearch")
        print("  2. Ensure Coveo has indexed the same products")
        print("  3. Deploy the UI and test the search")
    else:
        print("❌ No embeddings were generated. Please check the errors above.")


if __name__ == '__main__':
    main()
