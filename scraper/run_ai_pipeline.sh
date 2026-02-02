#!/bin/bash

# AI Metadata Pipeline - Full Setup Script
# 
# This script:
# 1. Downloads curated images from Unsplash
# 2. Uploads to S3
# 3. Extracts metadata using Bedrock Nova Lite
# 4. Indexes to Coveo
# 5. Generates embeddings in OpenSearch

echo "========================================================================"
echo "AI Metadata Pipeline - Full Setup"
echo "========================================================================"
echo ""

cd /mnt/d/Projects/Hermes/scraper

# Step 0: Delete existing Coveo data (optional)
read -p "Delete existing Coveo data first? (y/n): " delete_existing
if [ "$delete_existing" = "y" ]; then
    echo ""
    echo "Step 0: Deleting existing Coveo data..."
    echo "----------------------------------------"
    python delete_all_coveo.py
    echo ""
    echo "⏳ Waiting 30 seconds for Coveo to process deletions..."
    sleep 30
fi

# Step 1: Run AI Metadata Pipeline
echo ""
echo "Step 1: Running AI Metadata Pipeline..."
echo "----------------------------------------"
echo "This will:"
echo "  - Download 150 curated images from Unsplash"
echo "  - Upload to S3"
echo "  - Extract metadata using Bedrock Nova Lite"
echo ""
python ai_metadata_pipeline.py --max 150 --delay 0.5

# Step 2: Index to Coveo
echo ""
echo "Step 2: Indexing to Coveo..."
echo "----------------------------------------"
python coveo_indexer.py --input ai_enriched_products.json

# Step 3: Wait for Coveo indexing
echo ""
echo "⏳ Waiting 60 seconds for Coveo to index documents..."
sleep 60

# Step 4: Verify Coveo data
echo ""
echo "Step 4: Verifying Coveo data..."
echo "----------------------------------------"
python verify_coveo_data.py

# Step 5: Generate embeddings
echo ""
echo "Step 5: Generating embeddings in OpenSearch..."
echo "----------------------------------------"
cd /mnt/d/Projects/Hermes/backend/embedding_generator
python generate_embeddings.py

# Step 6: Build and deploy UI (optional)
read -p "Build and deploy UI to Netlify? (y/n): " deploy_ui
if [ "$deploy_ui" = "y" ]; then
    echo ""
    echo "Step 6: Building and deploying UI..."
    echo "----------------------------------------"
    cd /mnt/d/Projects/Hermes/ui
    npm run build
    netlify deploy --prod
fi

echo ""
echo "========================================================================"
echo "✅ AI Metadata Pipeline Complete!"
echo "========================================================================"
echo ""
echo "Summary:"
echo "  ✓ 150 images downloaded and uploaded to S3"
echo "  ✓ Metadata extracted using Bedrock Nova Lite"
echo "  ✓ Products indexed to Coveo with accurate metadata"
echo "  ✓ Embeddings generated in OpenSearch"
echo ""
echo "Test the demo at: https://hermes-demo.netlify.app"
echo ""
echo "Features:"
echo "  - Text search with accurate product descriptions"
echo "  - Image search with visual similarity"
echo "  - Faceted filtering with correct metadata"
echo "========================================================================"
