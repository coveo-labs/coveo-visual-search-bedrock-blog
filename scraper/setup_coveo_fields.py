#!/usr/bin/env python3
"""
Setup Coveo Fields

Creates all required fields in Coveo for faceting and search.
Must be run BEFORE indexing products.

Usage:
  python setup_coveo_fields.py

Requires COVEO_FIELD_API_KEY in .env (needs Field API permissions)
"""

import requests
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


# Fields to create with their configurations
# These match the AI pipeline output and UI facets
FIELDS_TO_CREATE = [
    # === Core Identification Fields ===
    {
        'name': 'assetid',
        'description': 'Unique asset identifier',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    
    # === Facet Fields (used in UI sidebar) ===
    {
        'name': 'category',
        'description': 'Product category (Shirts, Trousers, Jewelry, Watches, Shoes, Bags)',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'subcategory',
        'description': 'Product subcategory (Dress Shirt, Jeans, Necklace, etc.)',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'color',
        'description': 'Product color (White, Black, Blue, Brown, Gold, etc.)',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'material',
        'description': 'Primary material (Cotton, Leather, Silk, Gold, etc.)',
        'type': 'STRING',
        'facet': True,
        'multiValueFacet': False,
        'sort': True,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'style',
        'description': 'Product style (Casual, Formal, Sport, Luxury, Classic, Modern)',
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
        'description': 'Price range bucket ($0-$100, $100-$500, etc.)',
        'type': 'STRING',
        'facet': True,
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
    
    # === URL Fields ===
    {
        'name': 'imageurl',
        'description': 'Product image URL (S3)',
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
    
    # === S3/Storage Fields ===
    {
        'name': 's3_key',
        'description': 'S3 object key for the image',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': False,
        'sort': False,
        'includeInQuery': False,
        'includeInResults': True,
    },
    
    # === Description Fields ===
    {
        'name': 'description',
        'description': 'Product description',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': False,
        'sort': False,
        'includeInQuery': True,
        'includeInResults': True,
    },
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
    
    # === Multi-value Fields (from AI extraction) ===
    {
        'name': 'features',
        'description': 'Product features list',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': True,
        'sort': False,
        'includeInQuery': True,
        'includeInResults': True,
    },
    {
        'name': 'tags',
        'description': 'Search tags for the product',
        'type': 'STRING',
        'facet': False,
        'multiValueFacet': True,
        'sort': False,
        'includeInQuery': True,
        'includeInResults': True,
    },
    
    # === Legacy Fields (for backward compatibility) ===
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
        'name': 'materials',
        'description': 'List of materials (multi-value)',
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
        print("You need an API key with 'Edit fields' permission")
        return None
    
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
        elif response.status_code == 401:
            print("Error: Invalid API key or insufficient permissions")
            print("Make sure your API key has 'Edit fields' permission")
            return None
        else:
            print(f"Warning: Could not fetch existing fields: {response.status_code}")
            print(response.text[:200])
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
    print("Setup Coveo Fields for Faceting & Search")
    print("="*70)
    print(f"Organization ID: {config.COVEO_ORGANIZATION_ID}")
    print(f"Fields to configure: {len(FIELDS_TO_CREATE)}")
    print("="*70 + "\n")
    
    # Get existing fields
    print("Fetching existing fields...")
    existing_fields = get_existing_fields()
    
    if existing_fields is None:
        print("\n❌ Cannot proceed without API access")
        print("\nTo fix this:")
        print("  1. Go to Coveo Admin Console > API Keys")
        print("  2. Create a key with 'Edit fields' permission")
        print("  3. Add COVEO_FIELD_API_KEY=your-key to .env")
        return 1
    
    print(f"Found {len(existing_fields)} existing fields\n")
    
    created = 0
    updated = 0
    failed = 0
    skipped = 0
    
    for field_config in FIELDS_TO_CREATE:
        field_name = field_config['name']
        print(f"  {field_name}...", end=" ")
        
        if field_name.lower() in existing_fields:
            # Field exists - check if we need to update facet setting
            existing = existing_fields[field_name.lower()]
            needs_update = (
                existing.get('facet') != field_config.get('facet') or
                existing.get('includeInQuery') != field_config.get('includeInQuery') or
                existing.get('includeInResults') != field_config.get('includeInResults')
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
                print("✓ OK")
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
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Already OK: {skipped}")
    print(f"  Failed: {failed}")
    print("="*70)
    
    if failed == 0:
        print("\n✅ All fields configured successfully!")
        print("\nFacet fields enabled:")
        facet_fields = [f['name'] for f in FIELDS_TO_CREATE if f.get('facet')]
        for f in facet_fields:
            print(f"  • {f}")
        print("\nNext steps:")
        print("  1. Run AI pipeline: python ai_metadata_pipeline.py")
        print("  2. Index to Coveo: python coveo_indexer.py --input output/ai_enriched_products.json")
        return 0
    else:
        print(f"\n⚠️ {failed} fields failed to configure")
        print("You may need to create them manually in Coveo Admin Console")
        return 1


if __name__ == '__main__':
    sys.exit(main())
