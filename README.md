# Luxury Image Search Demo

A visual search demo combining **Amazon OpenSearch** vector similarity with **Coveo** personalized search. Upload an image to find similar luxury products, or use text search with intelligent faceting.

## Features

- **Image Search:** Upload a photo to find visually similar products using Amazon Bedrock embeddings + OpenSearch k-NN
- **Text Search:** Coveo-powered search with facets (category, color, material, style, etc.)
- **AI Metadata Extraction:** Extract structured product metadata from images using Bedrock Nova Lite
- **Coveo Analytics:** Automatic search and click event tracking via Coveo Headless

## Architecture

```
User → Netlify UI → API Gateway → Lambda
                                    ├── Bedrock (embeddings)
                                    ├── OpenSearch (k-NN similarity)
                                    └── Coveo (search + facets)
```

## Quick Deploy

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your AWS and Coveo credentials

# 2. Deploy AWS stack
cd infrastructure && sam build && sam deploy --guided

# 3. Setup data pipeline
cd ../scraper
source ../venv/bin/activate && source ../.env
python setup_coveo_fields.py
python ai_metadata_pipeline.py
python coveo_indexer.py --input output/ai_enriched_products.json

# 4. Generate embeddings
cd ../backend/embedding_generator
python cleanup_and_reindex.py

# 5. Deploy UI
cd ../../ui
npm install && npm run build && netlify deploy --prod
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## Project Structure

```
├── backend/
│   ├── search_api/          # Lambda for image search
│   ├── metadata_extractor/  # Lambda for AI metadata extraction
│   ├── embedding_generator/ # Scripts for OpenSearch indexing
│   └── layer/               # Shared Python dependencies
├── infrastructure/
│   └── template.yaml        # SAM/CloudFormation template
├── scraper/
│   ├── ai_metadata_pipeline.py  # Download images + extract metadata
│   ├── coveo_indexer.py         # Index products to Coveo
│   └── setup_coveo_fields.py    # Create Coveo facet fields
├── ui/
│   └── src/
│       ├── components/      # React components
│       ├── hooks/           # Coveo Headless hooks
│       └── lib/             # Coveo engine config
└── docs/
    ├── DEPLOYMENT.md        # Full deployment guide
    ├── ARCHITECTURE.md      # System architecture
    └── SETUP.md             # Initial setup
```

## Tech Stack

- **Frontend:** React + Vite + Tailwind CSS + Coveo Headless
- **Backend:** AWS Lambda (Python 3.12)
- **Search:** Coveo Search API + Amazon OpenSearch (k-NN)
- **AI:** Amazon Bedrock (Titan Embeddings, Nova Lite)
- **Infrastructure:** AWS SAM, CloudFormation
- **Hosting:** Netlify (UI), AWS (Backend)

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `COVEO_ORGANIZATION_ID` | Coveo org ID |
| `COVEO_PUSH_API_KEY` | Coveo Push API key |
| `COVEO_SEARCH_API_KEY` | Coveo Search API key |
| `COVEO_SOURCE_ID` | Coveo source ID |
| `S3_BUCKET_NAME` | S3 bucket for images |
| `OPENSEARCH_ENDPOINT` | OpenSearch domain endpoint |

### Coveo Setup

1. Create a Push source in Coveo Admin Console
2. Create API keys with appropriate permissions:
   - Push API key (for indexing)
   - Search API key (for UI)
   - Field API key (for creating fields)
3. Create a Query Pipeline and set condition for `Search Hub = LuxuryImageSearch`

## License

MIT
