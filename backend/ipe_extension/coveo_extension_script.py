"""
Coveo Index Pipeline Extension (IPE) Script

This script runs in Coveo's indexing pipeline and calls the Lambda function
to generate embeddings and index them to OpenSearch.

SETUP IN COVEO:
1. Go to Coveo Admin Console > Organization > Extensions
2. Create new extension with this script
3. Set the Lambda URL in the LAMBDA_URL variable below
4. Apply extension to your source as a Post-Conversion script

FIELDS USED:
- assetid: Unique product identifier
- imageurl: Unsplash image URL (for display)
- s3_key: S3 object key (for embedding generation)
- s3_url: Full S3 URL
- title: Product title
- description: Product description
- category: Product category (Shirts, Trousers, etc.)
- subcategory: Product subcategory
- color: Product color
- material: Product material
- style: Product style
- gender: Target gender
- pricerange: Price range bucket
- brand: Product brand
"""

import json
import http.client
import ssl

# =============================================================================
# CONFIGURATION - Update this with your Lambda Function URL
# =============================================================================
LAMBDA_URL = 'your-lambda-function-url.lambda-url.us-east-1.on.aws'
# =============================================================================


def get_safe_meta_data(document, field_name, default=''):
    """Safely get metadata field value from Coveo document"""
    try:
        values = document.get_meta_data_value(field_name)
        if values and len(values) > 0:
            return values[0]
        return default
    except:
        return default


# Get document data - core fields
asset_id = get_safe_meta_data(document, 'assetid')
image_url = get_safe_meta_data(document, 'imageurl')
s3_key = get_safe_meta_data(document, 's3_key')
s3_url = get_safe_meta_data(document, 's3_url')
title = get_safe_meta_data(document, 'title')

# Skip if no image source found
if not image_url and not s3_key and not s3_url:
    log('No image source found (imageurl, s3_key, or s3_url), skipping embedding generation')
else:
    # Prepare payload with all relevant fields
    payload = {
        'document': {
            # Core identification
            'assetid': asset_id,
            'asset_id': asset_id,  # Alternative field name
            
            # Image sources
            'imageurl': image_url,
            'image_url': image_url,  # Alternative field name
            's3_key': s3_key,
            's3_url': s3_url,
            
            # Product metadata
            'title': title,
            'description': get_safe_meta_data(document, 'description'),
            'category': get_safe_meta_data(document, 'category'),
            'subcategory': get_safe_meta_data(document, 'subcategory'),
            'color': get_safe_meta_data(document, 'color'),
            'material': get_safe_meta_data(document, 'material'),
            'style': get_safe_meta_data(document, 'style'),
            'gender': get_safe_meta_data(document, 'gender'),
            'pricerange': get_safe_meta_data(document, 'pricerange'),
            'brand': get_safe_meta_data(document, 'brand'),
            
            # URLs
            'producturl': get_safe_meta_data(document, 'producturl'),
            'thumbnailurl': get_safe_meta_data(document, 'thumbnailurl'),
        }
    }
    
    # Call Lambda function to generate embedding and index to OpenSearch
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to Lambda Function URL
        conn = http.client.HTTPSConnection(LAMBDA_URL, context=context)
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Make POST request
        conn.request('POST', '/', json.dumps(payload), headers)
        
        # Get response
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        
        if response.status == 200:
            result = json.loads(response_data)
            status = result.get('status', 'unknown')
            
            if status == 'indexed':
                log(f"Embedding generated and indexed for {asset_id}")
                # Add metadata to indicate embedding was generated
                document.add_meta_data({'embedding_indexed': 'true'})
                document.add_meta_data({'embedding_status': 'success'})
            elif status == 'already_indexed':
                log(f"Asset {asset_id} already indexed in OpenSearch")
                document.add_meta_data({'embedding_indexed': 'true'})
                document.add_meta_data({'embedding_status': 'already_exists'})
            else:
                log(f"Lambda returned status: {status} for {asset_id}")
                document.add_meta_data({'embedding_status': status})
        else:
            log(f"Lambda returned HTTP {response.status}: {response_data[:200]}")
            document.add_meta_data({'embedding_status': 'error'})
            document.add_meta_data({'embedding_error': f'HTTP {response.status}'})
        
        conn.close()
        
    except Exception as e:
        log(f"Error calling Lambda for {asset_id}: {str(e)}")
        document.add_meta_data({'embedding_status': 'error'})
        document.add_meta_data({'embedding_error': str(e)[:100]})
