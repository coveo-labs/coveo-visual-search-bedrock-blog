"""
Coveo Index Pipeline Extension (IPE) Script - ASYNCHRONOUS VERSION

This script runs in Coveo's indexing pipeline and triggers the Lambda function
asynchronously to generate embeddings and index them to OpenSearch.

ARCHITECTURE:
- IPE sends fire-and-forget request to Lambda (non-blocking)
- IPE returns immediately with embedding_status: pending
- Lambda processes asynchronously in background
- Lambda updates Coveo metadata via Push API when complete

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

METADATA FIELDS SET BY IPE:
- embedding_status: 'pending' (will be updated to 'indexed' by Lambda)
- embedding_trigger_sent: 'true'
- embedding_triggered_at: ISO timestamp
"""

import json
import requests
from datetime import datetime

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


def trigger_lambda_async(lambda_url, payload, asset_id):
    """
    Fire-and-forget asynchronous trigger to Lambda.
    
    Uses a very short timeout (1ms) to ensure the request is sent but
    the IPE doesn't wait for the response. This allows the IPE to return
    immediately while Lambda processes in the background.
    
    Args:
        lambda_url: Lambda Function URL
        payload: JSON payload to send
        asset_id: Asset ID for logging
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Fire-and-forget: send request with 1ms timeout
        # This ensures request is sent but IPE doesn't wait for response
        requests.post(
            f'https://{lambda_url}/',
            json=payload,
            timeout=0.001,  # 1 millisecond - request sent but not waited for
            stream=True
        )
    except requests.exceptions.ReadTimeout:
        # EXPECTED: Request was sent, but we didn't wait for response
        # This is the desired behavior for fire-and-forget
        return True, f"Asynchronous trigger sent for {asset_id}"
    except requests.exceptions.ConnectionError as e:
        # REAL ERROR: Request couldn't be sent (network issue)
        return False, f"Connection error triggering Lambda: {str(e)}"
    except requests.exceptions.Timeout as e:
        # Other timeout errors
        return False, f"Timeout error: {str(e)}"
    except Exception as e:
        # Unexpected error
        return False, f"Unexpected error: {str(e)}"


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
    # Prepare minimal payload for asynchronous processing
    # Only include essential fields needed by Lambda
    payload = {
        'document': {
            # Core identification
            'assetid': asset_id,
            'asset_id': asset_id,
            
            # Image sources
            'imageurl': image_url,
            'image_url': image_url,
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
    
    # Trigger Lambda asynchronously (fire-and-forget)
    success, message = trigger_lambda_async(LAMBDA_URL, payload, asset_id)
    
    if success:
        log(message)
        # Set metadata flags to track asynchronous processing
        document.add_meta_data({'embedding_status': 'pending'})
        document.add_meta_data({'embedding_trigger_sent': 'true'})
        document.add_meta_data({'embedding_triggered_at': datetime.utcnow().isoformat()})
    else:
        log(f"ERROR: {message}")
        document.add_meta_data({'embedding_status': 'trigger_failed'})
        document.add_meta_data({'embedding_error': message[:100]})
    
    # CRITICAL: Return document immediately
    # IPE does not wait for Lambda to complete
    # Lambda will update metadata via Coveo Push API when embedding is ready
