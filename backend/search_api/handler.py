import json
import os
import base64
import boto3
from datetime import datetime
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

# Environment variables
OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
OPENSEARCH_INDEX = os.environ['OPENSEARCH_INDEX_NAME']
COVEO_ORG_ID = os.environ['COVEO_ORGANIZATION_ID']
COVEO_SEARCH_API_KEY = os.environ['COVEO_SEARCH_API_KEY']
BEDROCK_MODEL_ID = os.environ['BEDROCK_MODEL_ID']
MAX_RESULTS = int(os.environ.get('MAX_OPENSEARCH_RESULTS', '10'))
LOG_RESULTS = os.environ.get('LOG_OPENSEARCH_RESULTS', 'true').lower() == 'true'
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize clients
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


def generate_embedding(image_bytes):
    """Generate embedding using Amazon Bedrock Titan"""
    try:
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Prepare request body
        body = json.dumps({
            "inputImage": image_base64
        })
        
        # Invoke Bedrock model
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        embedding = response_body.get('embedding')
        
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        raise


def search_opensearch(embedding, k=MAX_RESULTS):
    """Search OpenSearch for similar images"""
    try:
        query = {
            "size": k,
            "query": {
                "knn": {
                    "embedding_vector": {
                        "vector": embedding,
                        "k": k
                    }
                }
            },
            "_source": ["asset_id", "image_url", "metadata"]
        }
        
        response = opensearch_client.search(
            index=OPENSEARCH_INDEX,
            body=query
        )
        
        results = []
        for hit in response['hits']['hits']:
            score = hit['_score']
            # Only include results with similarity score > 0.5 (adjustable threshold)
            # Note: k-NN scores are normalized, higher is better
            results.append({
                'asset_id': hit['_source']['asset_id'],
                'score': score,
                'image_url': hit['_source'].get('image_url', ''),
                'metadata': hit['_source'].get('metadata', {})
            })
        
        return results
    except Exception as e:
        print(f"Error searching OpenSearch: {str(e)}")
        raise


def search_coveo(asset_ids, similarity_scores=None, min_score=0.5):
    """Search Coveo with asset IDs filter and similarity threshold"""
    import requests
    
    try:
        # Filter asset_ids by minimum similarity score if provided
        if similarity_scores:
            filtered_ids = [
                aid for aid, score in zip(asset_ids, similarity_scores) 
                if score >= min_score
            ]
            if not filtered_ids:
                print(f"No results above similarity threshold {min_score}")
                return []
            asset_ids = filtered_ids
        
        # Build advanced query with asset IDs
        aq_parts = [f"@assetid=={asset_id}" for asset_id in asset_ids]
        advanced_query = " OR ".join(aq_parts)
        
        print(f"Coveo advanced query: {advanced_query[:200]}...")
        
        url = f"https://{COVEO_ORG_ID}.org.coveo.com/rest/search/v2"
        
        headers = {
            'Authorization': f'Bearer {COVEO_SEARCH_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "aq": advanced_query,
            "numberOfResults": len(asset_ids),
            "fieldsToInclude": [
                "assetid",
                "title",
                "description",
                "longdescription",
                "price",
                "pricerange",
                "category",
                "subcategory",
                "color",
                "material",
                "style",
                "size",
                "gender",
                "brand",
                "imageurl",
                "thumbnailurl",
                "producturl",
                "clickableuri",
                "materials"
            ]
        }
        
        print(f"Calling Coveo API: {url}")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Coveo response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Coveo error response: {response.text}")
        
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        print(f"Coveo returned {len(results)} results")
        
        # Map clickUri to imageurl in raw for UI compatibility
        for result in results:
            if 'raw' not in result:
                result['raw'] = {}
            # Use clickUri as the image URL if imageurl is not present
            if 'imageurl' not in result['raw'] and 'clickUri' in result:
                result['raw']['imageurl'] = result['clickUri']
        
        # Log first result for debugging
        if results and LOG_RESULTS:
            print(f"Sample result: {results[0].get('title', 'N/A')}")
        
        return results
    except Exception as e:
        print(f"Error searching Coveo: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise


def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Get base64 encoded image
        image_data = body.get('image')
        if not image_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No image provided'})
            }
        
        # Decode image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Step 1: Generate embedding
        print("Generating embedding...")
        embedding = generate_embedding(image_bytes)
        
        # Step 2: Search OpenSearch
        print("Searching OpenSearch...")
        opensearch_results = search_opensearch(embedding)
        
        # Log OpenSearch results for demo
        if LOG_RESULTS:
            print("=" * 80)
            print("OPENSEARCH RESULTS (for demo logging):")
            print(json.dumps(opensearch_results, indent=2))
            print("=" * 80)
        
        # Extract asset IDs and scores
        asset_ids = [result['asset_id'] for result in opensearch_results]
        similarity_scores = [result['score'] for result in opensearch_results]
        
        if not asset_ids:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'results': [],
                    'opensearch_results': opensearch_results if LOG_RESULTS else [],
                    'message': 'No similar images found'
                })
            }
        
        # Get minimum score threshold from request (default 0.5)
        min_score = float(body.get('min_score', 0.5))
        
        # Step 3: Search Coveo with asset IDs (filtered by similarity)
        print(f"Searching Coveo with {len(asset_ids)} asset IDs (min_score: {min_score})...")
        coveo_results = search_coveo(asset_ids, similarity_scores, min_score)
        
        # Prepare response
        response_data = {
            'results': coveo_results,
            'opensearch_results': opensearch_results if LOG_RESULTS else [],
            'total_results': len(coveo_results),
            'search_timestamp': datetime.utcnow().isoformat()
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
