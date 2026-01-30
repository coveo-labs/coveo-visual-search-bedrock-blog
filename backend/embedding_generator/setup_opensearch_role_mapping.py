"""
Setup OpenSearch Role Mapping
Maps your IAM role to OpenSearch all_access role so you can access the cluster
"""

import os
import json
import boto3
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

OPENSEARCH_ENDPOINT = os.getenv('OPENSEARCH_ENDPOINT')
OPENSEARCH_PASSWORD = os.getenv('OPENSEARCH_PASSWORD', 'CoveoDemo2026!')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

print("=" * 70)
print("OpenSearch Role Mapping Setup")
print("=" * 70)

# Get current IAM identity
sts = boto3.client('sts')
identity = sts.get_caller_identity()
account_id = identity['Account']
user_arn = identity['Arn']

print(f"\nYour IAM Identity:")
print(f"  Account: {account_id}")
print(f"  ARN: {user_arn}")

# Extract role ARN for SSO users
if 'assumed-role' in user_arn:
    # For SSO: arn:aws:sts::ACCOUNT:assumed-role/ROLE_NAME/SESSION
    # We need: arn:aws:iam::ACCOUNT:role/aws-reserved/sso.amazonaws.com/ROLE_NAME
    parts = user_arn.split('/')
    role_name = parts[1]
    backend_role = f"arn:aws:iam::{account_id}:role/aws-reserved/sso.amazonaws.com/{role_name}"
    print(f"  Backend Role: {backend_role}")
else:
    backend_role = user_arn
    print(f"  Backend Role: {backend_role}")

print(f"\nOpenSearch Endpoint: {OPENSEARCH_ENDPOINT}")
print("\nAttempting to map IAM role to all_access...")

try:
    # Get current role mapping
    url = f"https://{OPENSEARCH_ENDPOINT}/_plugins/_security/api/rolesmapping/all_access"
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth('admin', OPENSEARCH_PASSWORD),
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    if response.status_code == 200:
        current_mapping = response.json()
        print("\n✅ Successfully connected to OpenSearch")
        
        # Get current backend roles
        all_access_mapping = current_mapping.get('all_access', {})
        backend_roles = all_access_mapping.get('backend_roles', [])
        
        # Add our role if not already present
        if backend_role not in backend_roles:
            backend_roles.append(backend_role)
            
            # Update the mapping
            updated_mapping = {
                'backend_roles': backend_roles,
                'hosts': all_access_mapping.get('hosts', []),
                'users': all_access_mapping.get('users', [])
            }
            
            response = requests.put(
                url,
                auth=HTTPBasicAuth('admin', OPENSEARCH_PASSWORD),
                headers={'Content-Type': 'application/json'},
                json=updated_mapping,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                print(f"\n✅ Successfully mapped IAM role to all_access!")
                print(f"\nBackend roles now include:")
                for role in backend_roles:
                    print(f"  - {role}")
                print("\n🎉 You can now access OpenSearch with your AWS credentials!")
                print("\nTest the connection:")
                print("  python test_opensearch_connection.py")
            else:
                print(f"\n❌ Failed to update role mapping: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"\n✅ IAM role already mapped to all_access!")
            print("\n🎉 You should be able to access OpenSearch with your AWS credentials!")
            print("\nTest the connection:")
            print("  python test_opensearch_connection.py")
    else:
        print(f"\n❌ Failed to connect: {response.status_code}")
        print(f"Response: {response.text}")
        print("\nMake sure:")
        print("  1. OPENSEARCH_PASSWORD in .env is correct")
        print("  2. OpenSearch domain is active (not processing)")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("  1. Verify OPENSEARCH_PASSWORD in .env")
    print("  2. Check OpenSearch domain status")
    print("  3. Try accessing OpenSearch Dashboard manually:")
    print(f"     https://{OPENSEARCH_ENDPOINT}/_dashboards")
    print("     Login: admin / <your-password>")
    print("     Go to: Security → Roles → all_access → Mapped users")
    print(f"     Add backend role: {backend_role}")
