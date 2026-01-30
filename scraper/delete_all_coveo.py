#!/usr/bin/env python3
"""
Delete All Documents from Coveo Source

Clears the entire Coveo source to start fresh
"""

import requests
import sys
import os
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def delete_all_documents():
    """Delete all documents from Coveo source"""
    org_id = config.COVEO_ORGANIZATION_ID
    source_id = config.COVEO_SOURCE_ID
    api_key = config.COVEO_PUSH_API_KEY
    
    base_url = f"https://api.cloud.coveo.com/push/v1/organizations/{org_id}/sources/{source_id}"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("\n" + "="*60)
    print("Delete All Documents from Coveo")
    print("="*60)
    print(f"Organization ID: {org_id}")
    print(f"Source ID: {source_id}")
    print("="*60 + "\n")
    
    try:
        # Method 1: Delete all documents using batch delete
        print("Method 1: Batch delete all documents...")
        url = f"{base_url}/documents/batch?delete=true"
        response = requests.delete(url, headers=headers, timeout=30)
        
        if response.status_code in [200, 202, 204]:
            print("✓ Batch delete successful")
        else:
            print(f"⚠ Batch delete status: {response.status_code}")
        
        # Method 2: Delete old documents (anything older than 1 minute)
        print("\nMethod 2: Delete old documents...")
        url = f"{base_url}/documents/olderthan"
        params = {'orderingId': int((datetime.now(timezone.utc).timestamp() - 60) * 1000)}
        response = requests.delete(url, params=params, headers=headers, timeout=30)
        
        if response.status_code in [200, 202, 204]:
            print("✓ Old documents deleted")
        else:
            print(f"⚠ Delete old documents status: {response.status_code}")
        
        print("\n✅ Deletion commands sent successfully")
        print("\nNote: It may take 2-3 minutes for Coveo to fully process the deletion")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function"""
    if not all([config.COVEO_ORGANIZATION_ID, config.COVEO_PUSH_API_KEY, config.COVEO_SOURCE_ID]):
        print("❌ Error: Coveo configuration missing")
        return
    
    # Confirm deletion
    print("\n⚠️  WARNING: This will delete ALL documents from the Coveo source!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    success = delete_all_documents()
    
    if success:
        print("\n✅ Deletion complete!")
        print("\nNext steps:")
        print("  1. Wait 1-2 minutes for Coveo to process")
        print("  2. Regenerate mock data: python mock_data_generator.py")
        print("  3. Re-index: python coveo_indexer.py")


if __name__ == '__main__':
    main()
