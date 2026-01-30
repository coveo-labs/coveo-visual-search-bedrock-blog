import json
import os
import base64
import boto3
import requests
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

# Environment variables
OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
OPENSEARCH_INDEX = os.environ['OPENSEARCH_INDEX_NAME']
S3_BUCKET = os.environ['S3_BUCKET_NAME']
BEDROCK_MODEL_ID = os.environ['BEDROCK_MODEL_ID']
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize clients
s3_client = boto3.client('s3')
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

# Get AWS credentials for OpenSearch
credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, AWS_REGION, 'es')

opensearch_client = OpenSearch(
    hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


def download_image_from_s3(s3_key):
    """Download image from S3"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        return response['Body'].read()
    except Exception as e:
        print(f"Error downloading from S3: {str(e)}")
        raise


def download_image_from_url(url):
    """Download image from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error downloading from URL: {str(e)}")
        raise


def generate_embedding(image_bytes):
    """Generate embedding using Amazon Bedrock Titan"""
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
        raise


def index_to_opensearch(asset_id, embedding, metadata):
    """Index embedding to OpenSearch"""
    try:
        document = {
            'asset_id': asset_id,
            'embedding_vector': embedding,
            'image_url': metadata.get('image_url', ''),
            'metadata': metadata,
            'indexed_at': datetime.utcnow().isoformat()
        }
        
        response = opensearch_client.index(
            index=OPENSEARCH_INDEX,
            id=asset_id,
            body=document
        )
        
        return response['result'] in ['created', 'updated']
    except Exception as e:
        print(f"Error indexing to OpenSearch: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    Coveo IPE Extension Handler
    Receives document from Coveo, generates embedding, indexes to OpenSearch
    """
    try:
        # Parse Coveo IPE request
        body = json.loads(event.get('body', '{}'))
        
        # Extract document data
        document = body.get('document', {})
        asset_id = document.get('assetid') or document.get('asset_id')
        image_url = document.get('imageurl') or document.get('image_url')
        s3_key = document.get('s3_key')
        
        if not asset_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing asset_id in document'
                })
            }
        
        print(f"Processing document: {asset_id}")
        
        # Check if already indexed
        try:
            existing = opensearch_client.get(index=OPENSEARCH_INDEX, id=asset_id)
            print(f"Asset {asset_id} already indexed, skipping...")
            
            # Return success to Coveo
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'document': document,
                    'status': 'already_indexed',
                    'asset_id': asset_id
                })
            }
        except:
            # Not found, proceed with indexing
            pass
        
        # Download image
        image_bytes = None
        if s3_key:
            print(f"Downloading from S3: {s3_key}")
            image_bytes = download_image_from_s3(s3_key)
        elif image_url:
            print(f"Downloading from URL: {image_url}")
            image_bytes = download_image_from_url(image_url)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No image source provided (s3_key or image_url)'
                })
            }
        
        # Generate embedding
        print("Generating embedding...")
        embedding = generate_embedding(image_bytes)
        
        # Prepare metadata
        metadata = {
            'title': document.get('title', ''),
            'description': document.get('description', ''),
            'category': document.get('category', ''),
            'price': document.get('price', ''),
            'image_url': image_url or f"s3://{S3_BUCKET}/{s3_key}",
            'product_url': document.get('producturl', '')
        }
        
        # Index to OpenSearch
        print("Indexing to OpenSearch...")
        success = index_to_opensearch(asset_id, embedding, metadata)
        
        if success:
            print(f"Successfully indexed {asset_id}")
            
            # Add metadata to document for Coveo
            document['embedding_indexed'] = True
            document['embedding_indexed_at'] = datetime.utcnow().isoformat()
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'document': document,
                    'status': 'indexed',
                    'asset_id': asset_id
                })
            }
        else:
            raise Exception("Failed to index to OpenSearch")
        
    except Exception as e:
        print(f"Error in IPE extension: {str(e)}")
        
        # Return error but don't fail Coveo indexing
        return {
            'statusCode': 200,
            'body': json.dumps({
                'document': body.get('document', {}),
                'status': 'error',
                'error': str(e)
            })
        }
