#!/usr/bin/env python3
"""
Setup Coveo Fields

Creates all required fields in Coveo for faceting and search
Must be run BEFORE indexing products
"""

import requests
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


# Fields to create with their configurations
FIELDS_TO_CREATE = [
    # Core fields
    {
        'name': 'assetid',
        'description': 'Unique asset identifier',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'category',
        'description': 'Product category (Shirts, Pants, Watches, etc.)',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'subcategory',
        'description': 'Product subcategory (Dress Shirt, Jeans, etc.)',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'color',
        'description': 'Product color',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'material',
        'description': 'Primary material',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'style',
        'description': 'Product style (Casual, Formal, etc.)',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'size',
        'description': 'Product size',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'gender',
        'description': 'Target gender (Men, Women, Unisex)',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'pricerange',
        'description': 'Price range bucket',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'price',
        'description': 'Product price',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'brand',
        'description': 'Product brand',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    # URL fields
    {
        'name': 'imageurl',
        'description': 'Product image URL',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': False,
        'sort': False,
        'includeInQuery': False,
        'includeInResults': True,
    },
    {
        'name': 'thumbnailurl',
        'description': 'Product thumbnail URL',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': False,
        'sort': False,
        'includeInQuery': False,
        'includeInResults': True,
    },
    {
        'name': 'producturl',
        'description': 'Product page URL',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': False,
        'sort': False,
        'includeInQuery': False,
        'includeInResults': True,
    },
    # Description fields
    {
        'name': 'longdescription',
        'description': 'Long product description',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': False,
        'sort': False,
        'includeInQuery': True,
        'includeInResults': True,
    },
    # Multi-value field
    {
        'name': 'materials',
        'description': 'List of materials',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': True,
        'sort': False,
        'includeInQuery': True,
        'includeInResults': True,
    },
]


def get_existing_fields():
    """Get list of existing fields in Coveo"""
    org_id = config.COVEO_ORGANIZATION_ID
    api_key = config.COVEO_FIELD_API_KEY
    
    if not api_key:
        print("Error: COVEO_FIELD_API_KEY not set in .env")
        return {}
    
    url = f"https://platform.cloud.coveo.com/rest/organizations/{org_id}/indexes/fields"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return {f['name'].lower(): f for f in data.get('items', [])}
        else:
            print(f"Warning: Could not fetch existing fields: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Warning: Error fetching fields: {e}")
        return {}


def create_field(field_config):
    """Create a single field in Coveo"""
    org_id = config.COVEO_ORGANIZATION_ID
    api_key = config.COVEO_FIELD_API_KEY
    
    if not api_key:
        return False, "COVEO_FIELD_API_KEY not set"
    
    url = f"https://platform.cloud.coveo.com/rest/organizations/{org_id}/indexes/fields"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.post(url, headers=headers, json=field_config, timeout=30)
        
        if response.status_code in [200, 201, 204]:
            return True, "Created"
        elif response.status_code == 409 or response.status_code == 412:
            return True, "Already exists"
        else:
            return False, f"Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)


def update_field(field_name, field_config):
    """Update an existing field in Coveo"""
    org_id = config.COVEO_ORGANIZATION_ID
    api_key = config.COVEO_FIELD_API_KEY
    
    if not api_key:
        return False, "COVEO_FIELD_API_KEY not set"
    
    url = f"https://platform.cloud.coveo.com/rest/organizations/{org_id}/indexes/fields/{field_name}"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.put(url, headers=headers, json=field_config, timeout=30)
        
        if response.status_code in [200, 201, 204]:
            return True, "Updated"
        else:
            return False, f"Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)


def main():
    """Main function"""
    print("\n" + "="*70)
    print("Setup Coveo Fields for Faceting")
    print("="*70)
    print(f"Organization ID: {config.COVEO_ORGANIZATION_ID}")
    print(f"Fields to create: {len(FIELDS_TO_CREATE)}")
    print("="*70 + "\n")
    
    # Get existing fields
    print("Fetching existing fields...")
    existing_fields = get_existing_fields()
    print(f"Found {len(existing_fields)} existing fields\n")
    
    created = 0
    updated = 0
    failed = 0
    skipped = 0
    
    for field_config in FIELDS_TO_CREATE:
        field_name = field_config['name']
        print(f"Processing: {field_name}...", end=" ")
        
        if field_name.lower() in existing_fields:
            # Field exists - check if we need to update it
            existing = existing_fields[field_name.lower()]
            needs_update = (
                existing.get('facet') != field_config.get('facet') or
                existing.get('includeInQuery') != field_config.get('includeInQuery')
            )
            
            if needs_update:
                success, message = update_field(field_name, field_config)
                if success:
                    print(f"✓ {message}")
                    updated += 1
                else:
                    print(f"✗ {message}")
                    failed += 1
            else:
                print("✓ Already configured correctly")
                skipped += 1
        else:
            # Create new field
            success, message = create_field(field_config)
            if success:
                print(f"✓ {message}")
                created += 1
            else:
                print(f"✗ {message}")
                failed += 1
        
        # Small delay to avoid rate limiting
        time.sleep(0.2)
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print(f"Created: {created}")
    print(f"Updated: {updated}")
    print(f"Skipped (already correct): {skipped}")
    print(f"Failed: {failed}")
    print("="*70)
    
    if failed == 0:
        print("\n✅ All fields configured successfully!")
        print("\nNext steps:")
        print("  1. Generate products: python enhanced_mock_generator.py")
        print("  2. Download images: python download_mock_images_to_s3.py")
        print("  3. Index to Coveo: python coveo_indexer.py")
    else:
        print(f"\n⚠️ {failed} fields failed to configure")
        print("You may need to create them manually in Coveo Admin Console")


if __name__ == '__main__':
    main()
