#!/bin/bash

# Full Setup Script for Enhanced Hermès Demo
# This script will:
# 0. Setup Coveo fields for faceting
# 1. Generate 1000 products with unique images
# 2. Download images to S3
# 3. Index to Coveo
# 4. Generate embeddings in OpenSearch
# 5. Update Lambda
# 6. Build and deploy UI

echo "========================================================================"
echo "Full Hermès Demo Setup - Enhanced Version"
echo "========================================================================"
echo ""

cd /mnt/d/Projects/Hermes/scraper

# Step 0: Setup Coveo fields
echo "Step 0: Setting up Coveo fields for faceting..."
echo "----------------------------------------"
python setup_coveo_fields.py

echo ""
echo "⏳ Waiting 10 seconds for Coveo to process field changes..."
sleep 10

# Step 1: Generate 1000 products
echo ""
echo "Step 1: Generating 1000 products with unique images..."
echo "----------------------------------------"
python enhanced_mock_generator.py

# Step 2: Download images to S3
echo ""
echo "Step 2: Downloading images to S3..."
echo "----------------------------------------"
python download_mock_images_to_s3.py

# Step 3: Index to Coveo
echo ""
echo "Step 3: Indexing to Coveo..."
echo "----------------------------------------"
python coveo_indexer.py

# Step 4: Generate embeddings
echo ""
echo "Step 4: Generating embeddings in OpenSearch..."
echo "----------------------------------------"
cd /mnt/d/Projects/Hermes/backend/embedding_generator
python generate_embeddings.py

# Step 5: Update Lambda
echo ""
echo "Step 5: Updating Lambda function..."
echo "----------------------------------------"
cd /mnt/d/Projects/Hermes/backend/search_api
chmod +x update_lambda.sh
./update_lambda.sh

# Step 6: Build UI
echo ""
echo "Step 6: Building UI..."
echo "----------------------------------------"
cd /mnt/d/Projects/Hermes/ui
npm run build

# Step 7: Deploy to Netlify
echo ""
echo "Step 7: Deploying to Netlify..."
echo "----------------------------------------"
netlify deploy --prod

echo ""
echo "========================================================================"
echo "✅ Full Setup Complete!"
echo "========================================================================"
echo ""
echo "Summary:"
echo "  ✓ Coveo fields configured for faceting"
echo "  ✓ 1000 products generated with unique images"
echo "  ✓ Images stored in S3"
echo "  ✓ Products indexed to Coveo"
echo "  ✓ Embeddings generated in OpenSearch"
echo "  ✓ Lambda function updated"
echo "  ✓ UI deployed to Netlify"
echo ""
echo "Test the demo at: https://hermes-demo.netlify.app"
echo ""
echo "Features:"
echo "  - Text search with natural language"
echo "  - Image search with similarity matching"
echo "  - Faceted filtering (Category, Color, Price, etc.)"
echo "  - OpenSearch results panel"
echo "  - AI Metadata Extraction (Bedrock Nova Lite)"
echo "========================================================================"
