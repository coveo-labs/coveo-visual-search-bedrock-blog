import json
import os
import base64
import boto3
import requests
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from opensearchpy.exceptions import NotFoundError

# Environment variables
OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
OPENSEARCH_INDEX = os.environ['OPENSEARCH_INDEX_NAME']
S3_BUCKET = os.environ['S3_BUCKET_NAME']
BEDROCK_MODEL_ID = os.environ['BEDROCK_MODEL_ID']
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Coveo Push API credentials
COVEO_ORG_ID = os.environ.get('COVEO_ORGANIZATION_ID')
COVEO_SOURCE_ID = os.environ.get('COVEO_SOURCE_ID')
COVEO_PUSH_API_KEY = os.environ.get('COVEO_PUSH_API_KEY')

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
            'image_url': metadata.get('image_url', ''),  # Unsplash URL for display
            'metadata': metadata,
            'indexed_at': datetime.utcnow().isoformat()
        }
        
        response = opensearch_client.index(
            index=OPENSEARCH_INDEX,
            id=asset_id,
            body=document,
            refresh=True  # Make immediately searchable
        )
        
        return response['result'] in ['created', 'updated']
    except Exception as e:
        print(f"Error indexing to OpenSearch: {str(e)}")
        raise


def update_coveo_document_metadata(asset_id, metadata_updates):
    """
    Update Coveo document metadata via Push API after embedding is complete.
    
    This closes the asynchronous loop by notifying Coveo that the embedding
    has been generated and indexed to OpenSearch.
    
    Args:
        asset_id: Product asset ID
        metadata_updates: Dictionary of metadata fields to update
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not COVEO_ORG_ID or not COVEO_SOURCE_ID or not COVEO_PUSH_API_KEY:
        print("WARNING: Coveo Push API credentials not configured, skipping metadata update")
        return False
    
    try:
        # Build Coveo Push API URL
        push_url = (
            f"https://api.cloud.coveo.com/push/v1/organizations/{COVEO_ORG_ID}/"
            f"sources/{COVEO_SOURCE_ID}/documents"
        )
        
        headers = {
            'Authorization': f'Bearer {COVEO_PUSH_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Build document update payload
        document_update = {
            'documentId': f'https://luxury-catalog.com/product/{asset_id}',
            'metadata': metadata_updates
        }
        
        # Push update to Coveo
        response = requests.put(
            f"{push_url}?documentId={document_update['documentId']}",
            headers=headers,
            json=document_update,
            timeout=30
        )
        
        if response.status_code in [200, 201, 202]:
            print(f"Successfully updated Coveo metadata for {asset_id}")
            return True
        else:
            print(f"Failed to update Coveo metadata: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Error updating Coveo metadata: {str(e)}")
        return False


def lambda_handler(event, context):
    """
    Coveo IPE Extension Handler - ASYNCHRONOUS VERSION
    
    Receives document from Coveo IPE, generates embedding, indexes to OpenSearch,
    and updates Coveo metadata via Push API to close the asynchronous loop.
    
    Flow:
    1. IPE sends fire-and-forget request (doesn't wait for response)
    2. Lambda processes: download image → generate embedding → index to OpenSearch
    3. Lambda updates Coveo metadata via Push API (embedding_status: indexed)
    4. Coveo document is updated with embedding metadata
    """
    try:
        # Parse Coveo IPE request
        body = json.loads(event.get('body', '{}'))
        
        # Extract document data
        document = body.get('document', {})
        asset_id = document.get('assetid') or document.get('asset_id')
        
        # Image sources - prefer S3 for embedding, but store Unsplash URL for display
        s3_key = document.get('s3_key')
        s3_url = document.get('s3_url')
        image_url = document.get('imageurl') or document.get('image_url')  # Unsplash URL
        
        if not asset_id:
            print("ERROR: Missing asset_id in document")
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
            
            # Update Coveo to indicate already indexed
            update_coveo_document_metadata(asset_id, {
                'embedding_indexed': 'true',
                'embedding_status': 'already_indexed',
                'embedding_indexed_at': datetime.utcnow().isoformat()
            })
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'already_indexed',
                    'asset_id': asset_id
                })
            }
        except NotFoundError:
            # Document not found, proceed with indexing
            print(f"Asset {asset_id} not found in OpenSearch, proceeding with indexing...")
        except Exception as e:
            # Real error (network, auth, etc.) - log and fail
            print(f"ERROR: Failed to check OpenSearch for {asset_id}: {str(e)}")
            
            # Attempt to notify Coveo of the error
            try:
                update_coveo_document_metadata(asset_id, {
                    'embedding_status': 'error',
                    'embedding_error': f'OpenSearch check failed: {str(e)[:80]}'
                })
            except:
                pass
            
            # Return error to Lambda (will be retried)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'status': 'error',
                    'asset_id': asset_id,
                    'error': f'Failed to check OpenSearch: {str(e)}'
                })
            }
        
        # Download image - prefer S3 for better quality embeddings
        image_bytes = None
        if s3_key:
            print(f"Downloading from S3: {s3_key}")
            image_bytes = download_image_from_s3(s3_key)
        elif s3_url and s3_url.startswith('http'):
            print(f"Downloading from S3 URL: {s3_url}")
            image_bytes = download_image_from_url(s3_url)
        elif image_url:
            print(f"Downloading from URL: {image_url}")
            image_bytes = download_image_from_url(image_url)
        else:
            print(f"ERROR: No image source provided for {asset_id}")
            
            # Update Coveo with error status
            update_coveo_document_metadata(asset_id, {
                'embedding_status': 'error',
                'embedding_error': 'No image source provided'
            })
            
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No image source provided (s3_key, s3_url, or imageurl)'
                })
            }
        
        # Generate embedding
        print("Generating embedding...")
        embedding = generate_embedding(image_bytes)
        
        # Prepare metadata - store Unsplash URL for display
        metadata = {
            'title': document.get('title', ''),
            'description': document.get('description', ''),
            'category': document.get('category', ''),
            'subcategory': document.get('subcategory', ''),
            'color': document.get('color', ''),
            'material': document.get('material', ''),
            'style': document.get('style', ''),
            'gender': document.get('gender', ''),
            'pricerange': document.get('pricerange', ''),
            'brand': document.get('brand', 'Hermès'),
            'image_url': image_url,  # Store Unsplash URL for display
            'product_url': document.get('producturl', ''),
            's3_key': s3_key,
        }
        
        # Index to OpenSearch with Unsplash URL
        print("Indexing to OpenSearch...")
        success = index_to_opensearch(asset_id, embedding, metadata)
        
        if success:
            print(f"Successfully indexed {asset_id}")
            
            # Update Coveo metadata to signal completion (closes async loop)
            metadata_updates = {
                'embedding_indexed': 'true',
                'embedding_indexed_at': datetime.utcnow().isoformat(),
                'embedding_status': 'indexed',
                'opensearch_indexed': 'true'
            }
            
            coveo_updated = update_coveo_document_metadata(asset_id, metadata_updates)
            
            if coveo_updated:
                print(f"Asynchronous loop closed for {asset_id}")
            else:
                print(f"WARNING: Failed to update Coveo for {asset_id}, but embedding is indexed in OpenSearch")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'indexed',
                    'asset_id': asset_id,
                    'coveo_updated': coveo_updated
                })
            }
        else:
            raise Exception("Failed to index to OpenSearch")
        
    except Exception as e:
        print(f"Error in IPE extension: {str(e)}")
        
        # Attempt to notify Coveo of failure
        try:
            asset_id = body.get('document', {}).get('assetid') or body.get('document', {}).get('asset_id')
            if asset_id:
                update_coveo_document_metadata(asset_id, {
                    'embedding_status': 'error',
                    'embedding_error': str(e)[:100]
                })
        except:
            pass
        
        # Return success to Coveo (don't fail indexing)
        # Error is logged and Coveo is notified via metadata
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'error',
                'asset_id': asset_id if 'asset_id' in locals() else 'unknown',
                'error': str(e)
            })
        }
