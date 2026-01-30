"""
Test OpenSearch Connection
Quick script to verify OpenSearch credentials and connectivity
"""

import os
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENSEARCH_ENDPOINT = os.getenv('OPENSEARCH_ENDPOINT')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

print("Testing OpenSearch Connection")
print("=" * 60)
print(f"Endpoint: {OPENSEARCH_ENDPOINT}")
print(f"Region: {AWS_REGION}")
print(f"Auth: AWS Signature V4 (using your AWS credentials)")
print("=" * 60)

try:
    # Get AWS credentials
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, AWS_REGION, 'es')
    
    # Create client
    client = OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30
    )
    
    # Test connection
    print("\nTesting connection...")
    info = client.info()
    print("✅ Connection successful!")
    print(f"\nCluster info:")
    print(f"  Name: {info.get('cluster_name')}")
    print(f"  Version: {info.get('version', {}).get('number')}")
    
    # List indices
    print("\nListing indices...")
    indices = client.cat.indices(format='json')
    if indices:
        print(f"Found {len(indices)} indices:")
        for idx in indices:
            print(f"  - {idx['index']}")
    else:
        print("  No indices found")
    
except Exception as e:
    print(f"❌ Connection failed!")
    print(f"Error: {str(e)}")
    print("\nTroubleshooting:")
    print("  1. Verify your AWS credentials are valid (run: aws sts get-caller-identity)")
    print("  2. Check if OpenSearch domain is active (not in processing state)")
    print("  3. Verify endpoint URL is correct")
    print("  4. Ensure your AWS IAM user/role has OpenSearch permissions")
    print("  5. Try accessing OpenSearch Dashboard in browser:")
    print(f"     https://{OPENSEARCH_ENDPOINT}/_dashboards")
