"""
Metadata Extractor Lambda Handler

Uses Amazon Bedrock Nova Lite to extract structured metadata from product images
"""

import json
import os
import base64
import boto3

# Environment variables
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
NOVA_MODEL_ID = os.environ.get('NOVA_MODEL_ID', 'amazon.nova-lite-v1:0')

# Initialize Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)

# Metadata extraction prompt
EXTRACTION_PROMPT = """Analyze this product image and extract detailed metadata in JSON format.

Return a JSON object with the following fields:
{
  "title": "Product name/title",
  "category": "Main category (e.g., Shirts, Pants, Shoes, Watches, Bags, Accessories, Jewelry)",
  "subcategory": "Specific type (e.g., Dress Shirt, Sneakers, Handbag)",
  "color": "Primary color",
  "colors": ["List of all colors visible"],
  "material": "Primary material (e.g., Cotton, Leather, Silk)",
  "materials": ["List of all materials"],
  "style": "Style category (e.g., Casual, Formal, Sport, Luxury)",
  "gender": "Target gender (Men, Women, Unisex)",
  "pattern": "Pattern type if any (e.g., Solid, Striped, Plaid)",
  "brand_indicators": "Any visible brand elements or luxury indicators",
  "description": "Detailed description of the product",
  "features": ["List of notable features"],
  "occasion": "Suitable occasions (e.g., Business, Casual, Evening)",
  "season": "Suitable season (e.g., All Season, Summer, Winter)",
  "estimated_price_range": "Estimated price range based on quality indicators",
  "quality_indicators": ["List of quality/luxury indicators observed"],
  "tags": ["Relevant search tags for this product"]
}

Be specific and accurate. If you cannot determine a field, use "Unknown" or an empty array.
Return ONLY the JSON object, no additional text."""


def detect_image_format(image_bytes):
    """Detect image format from magic bytes"""
    if image_bytes[:3] == b'\xff\xd8\xff':
        return 'jpeg'
    elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return 'webp'
    else:
        return 'jpeg'  # Default to jpeg


def extract_metadata(image_bytes):
    """Extract metadata from image using Bedrock Nova Lite"""
    try:
        # Detect image format from magic bytes
        image_format = detect_image_format(image_bytes)
        print(f"Detected image format: {image_format}")
        
        # Prepare the message for Nova Lite - use raw bytes, not base64
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": image_format,
                            "source": {
                                "bytes": image_bytes  # Raw bytes, not base64
                            }
                        }
                    },
                    {
                        "text": EXTRACTION_PROMPT
                    }
                ]
            }
        ]
        
        # Call Bedrock Nova Lite
        response = bedrock_runtime.converse(
            modelId=NOVA_MODEL_ID,
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.1,
                "topP": 0.9
            }
        )
        
        # Extract the response text
        response_text = response['output']['message']['content'][0]['text']
        
        # Parse JSON from response
        # Try to extract JSON if wrapped in markdown code blocks
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        
        # Parse the JSON
        metadata = json.loads(response_text)
        
        return metadata
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response text: {response_text[:500]}")
        return {
            "error": "Failed to parse metadata JSON",
            "raw_response": response_text[:1000]
        }
    except Exception as e:
        print(f"Error extracting metadata: {str(e)}")
        raise


def lambda_handler(event, context):
    """Main Lambda handler for metadata extraction"""
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
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'No image provided'})
            }
        
        # Decode image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        print(f"Processing image of size: {len(image_bytes)} bytes")
        
        # Extract metadata using Nova Lite
        print("Extracting metadata with Bedrock Nova Lite...")
        metadata = extract_metadata(image_bytes)
        
        # Prepare response
        response_data = {
            'metadata': metadata,
            'model': NOVA_MODEL_ID,
            'status': 'success'
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
