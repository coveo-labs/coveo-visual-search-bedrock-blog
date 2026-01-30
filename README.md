# Luxury Reverse Image Search Demo
## Coveo + Amazon OpenSearch + Bedrock Integration

A sophisticated reverse image search solution combining Amazon OpenSearch's vector similarity with Coveo's personalized search capabilities, plus AI-powered metadata extraction.

## Features

- 🔍 **Text Search** - Natural language search powered by Coveo
- 🖼️ **Image Search** - Upload an image to find visually similar products
- 🤖 **AI Metadata Extraction** - Extract structured product metadata using Amazon Bedrock Nova Lite
- 📊 **Faceted Filtering** - Filter by category, color, price, style, material, etc.
- ⚡ **Real-time IPE** - Coveo Index Pipeline Extension for automatic embedding generation

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              User Interface                              │
│                    (React + TailwindCSS + Netlify)                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │   Text    │   │   Image   │   │ Metadata  │
            │  Search   │   │  Search   │   │ Extractor │
            └───────────┘   └───────────┘   └───────────┘
                    │               │               │
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │   Coveo   │   │ OpenSearch│   │  Bedrock  │
            │ Search API│   │   k-NN    │   │ Nova Lite │
            └───────────┘   └───────────┘   └───────────┘
                    │               │
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │    Coveo      │
                    │  (Results +   │
                    │   Facets)     │
                    └───────────────┘
```

## Project Structure

```
├── backend/
│   ├── embedding_generator/   # Offline embedding generation
│   ├── ipe_extension/         # Coveo IPE Lambda
│   ├── metadata_extractor/    # AI metadata extraction Lambda
│   ├── search_api/            # Search API Lambda
│   └── layer/                 # Shared Lambda layer
├── infrastructure/
│   └── template.yaml          # AWS SAM template
├── scraper/
│   ├── enhanced_mock_generator.py  # Generate mock product data
│   ├── coveo_indexer.py            # Index to Coveo
│   ├── setup_coveo_fields.py       # Create Coveo fields
│   └── full_setup.sh               # Complete setup script
├── ui/
│   └── src/
│       ├── App.jsx
│       └── components/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEMO_GUIDE.md
│   ├── DEPLOYMENT.md
│   └── SETUP.md
└── .env.example
```

## Quick Start

### Prerequisites

- AWS Account with Bedrock access enabled
- Python 3.11+ with pip
- Node.js 18+ with npm
- AWS CLI configured
- Coveo organization with Push API access

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 2. Deploy AWS Infrastructure

```bash
cd infrastructure
sam build
sam deploy --guided
```

### 3. Setup Coveo Fields & Index Data

```bash
cd scraper
pip install -r requirements.txt
./full_setup.sh
```

### 4. Deploy UI

```bash
cd ui
npm install
npm run build
netlify deploy --prod
```

## Environment Variables

See `.env.example` for all required variables:

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | AWS region (default: us-east-1) |
| `S3_BUCKET_NAME` | S3 bucket for images |
| `OPENSEARCH_ENDPOINT` | OpenSearch domain endpoint |
| `COVEO_ORGANIZATION_ID` | Coveo org ID |
| `COVEO_PUSH_API_KEY` | Coveo Push API key |
| `COVEO_SEARCH_API_KEY` | Coveo Search API key |
| `COVEO_FIELD_API_KEY` | Coveo Field API key |

## Tech Stack

**Backend:** Python 3.12, AWS Lambda, Amazon Bedrock, Amazon OpenSearch

**Frontend:** React 18, Vite, TailwindCSS, Framer Motion

**Infrastructure:** AWS SAM, CloudFormation, Netlify

## Documentation

- [Setup Guide](docs/SETUP.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Demo Guide](docs/DEMO_GUIDE.md)

## License

Demo/POC - Not for production use
