# Architecture Documentation

Detailed technical architecture for the Luxury Image Search solution.

## System Overview

The solution combines three main platforms:

1. **Amazon Web Services** - Image processing, embeddings, vector search
2. **Coveo** - Metadata indexing, personalization, search API
3. **Netlify** - UI hosting (or AWS App Runner as alternative)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           User Interface                         │
│                    (React + Netlify/App Runner)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                               │
│                     (REST API + CORS)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Invoke
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Search Lambda Function                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Receive image (base64)                                │  │
│  │ 2. Call Bedrock for embedding                            │  │
│  │ 3. Query OpenSearch k-NN                                 │  │
│  │ 4. Extract asset IDs                                     │  │
│  │ 5. Query Coveo Search API                                │  │
│  │ 6. Return merged results                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└───┬─────────────────────┬──────────────────────┬───────────────┘
    │                     │                      │
    │                     │                      │
    ▼                     ▼                      ▼
┌─────────┐      ┌──────────────┐      ┌─────────────────┐
│ Bedrock │      │  OpenSearch  │      │  Coveo Search   │
│  Titan  │      │   (k-NN)     │      │      API        │
│Embedding│      │              │      │                 │
└─────────┘      └──────────────┘      └─────────────────┘


                    Indexing Pipeline
                    ─────────────────

┌─────────────────────────────────────────────────────────────────┐
│                      S3 Bucket (Images)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Read
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Embedding Generator (Python Script)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. List images in S3                                     │  │
│  │ 2. Download each image                                   │  │
│  │ 3. Generate embedding via Bedrock                        │  │
│  │ 4. Index to OpenSearch                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└───┬─────────────────────────────────────────────────────────────┘
    │
    │ Index
    ▼
┌──────────────┐
│  OpenSearch  │
│   (k-NN)     │
└──────────────┘


                    Live Indexing (IPE)
                    ───────────────────

┌─────────────────────────────────────────────────────────────────┐
│                    Coveo Push API / Connector                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Document
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Coveo Indexing Pipeline                         │
│                  (with IPE Extension)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP POST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   IPE Extension Lambda                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Receive document from Coveo                          │  │
│  │ 2. Extract image URL/S3 key                             │  │
│  │ 3. Download image                                        │  │
│  │ 4. Generate embedding via Bedrock                        │  │
│  │ 5. Index to OpenSearch                                   │  │
│  │ 6. Return to Coveo                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└───┬─────────────────────────────────────────────────────────────┘
    │
    │ Index
    ▼
┌──────────────┐
│  OpenSearch  │
│   (k-NN)     │
└──────────────┘
```

## Component Details

### 1. Frontend (React UI)

**Technology:**
- React 18
- Vite (build tool)
- TailwindCSS (styling)
- Framer Motion (animations)

**Responsibilities:**
- Image upload interface
- Display search results
- Show OpenSearch debug log
- Handle loading/error states

**Key Files:**
- `App.jsx` - Main application logic
- `ImageUpload.jsx` - Drag & drop upload
- `SearchResults.jsx` - Result display
- `OpenSearchLog.jsx` - Debug viewer

**Deployment:**
- Netlify (primary)
- AWS App Runner (alternative)

### 2. API Gateway

**Configuration:**
- REST API
- CORS enabled for all origins
- POST /search endpoint
- Lambda proxy integration

**Security:**
- Public endpoint (for demo)
- Can add API key authentication
- Rate limiting available

### 3. Search Lambda Function

**Runtime:** Python 3.11
**Memory:** 512 MB
**Timeout:** 300 seconds

**Dependencies:**
- boto3 (AWS SDK)
- opensearch-py (OpenSearch client)
- requests (HTTP client)

**Environment Variables:**
- OPENSEARCH_ENDPOINT
- OPENSEARCH_USERNAME
- OPENSEARCH_PASSWORD
- OPENSEARCH_INDEX_NAME
- COVEO_ORGANIZATION_ID
- COVEO_SEARCH_API_KEY
- BEDROCK_MODEL_ID
- MAX_OPENSEARCH_RESULTS

**Flow:**
1. Receive base64 image from API Gateway
2. Decode image
3. Call Bedrock Titan Embeddings
4. Query OpenSearch k-NN index
5. Extract top N asset IDs
6. Build Coveo advanced query
7. Call Coveo Search API
8. Merge and return results

**Error Handling:**
- Try/catch for each external call
- Graceful degradation
- Detailed logging to CloudWatch

### 4. IPE Extension Lambda

**Runtime:** Python 3.11
**Memory:** 512 MB
**Timeout:** 300 seconds

**Trigger:** Lambda Function URL (public)

**Flow:**
1. Receive document from Coveo IPE
2. Extract asset_id and image source
3. Check if already indexed (skip if exists)
4. Download image from S3 or URL
5. Generate embedding via Bedrock
6. Index to OpenSearch with asset_id
7. Return success to Coveo

**Idempotency:**
- Checks if embedding exists before generating
- Uses asset_id as document ID
- Safe to retry

### 5. Amazon Bedrock

**Model:** amazon.titan-embed-image-v1

**Input:** Base64 encoded image
**Output:** 1024-dimensional vector

**Characteristics:**
- Multimodal (images and text)
- Pre-trained on billions of images
- No fine-tuning required
- Serverless, pay-per-use

**API Call:**
```python
response = bedrock_runtime.invoke_model(
    modelId='amazon.titan-embed-image-v1',
    body=json.dumps({
        "inputImage": base64_image
    }),
    contentType='application/json',
    accept='application/json'
)
```

**Pricing:**
- $0.00006 per image (as of 2024)
- 1000 images = $0.06

### 6. Amazon OpenSearch Service

**Version:** OpenSearch 2.11+
**Instance:** t3.small.search (demo)
**Storage:** 20 GB EBS (gp3)

**Index Configuration:**
```json
{
  "settings": {
    "index": {
      "knn": true,
      "knn.algo_param.ef_search": 512
    }
  },
  "mappings": {
    "properties": {
      "asset_id": {"type": "keyword"},
      "embedding_vector": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "space_type": "l2",
          "engine": "nmslib"
        }
      },
      "image_url": {"type": "keyword"},
      "metadata": {"type": "object"},
      "indexed_at": {"type": "date"}
    }
  }
}
```

**k-NN Algorithm:**
- HNSW (Hierarchical Navigable Small World)
- L2 distance (Euclidean)
- ef_construction: 512
- m: 16

**Query:**
```json
{
  "size": 10,
  "query": {
    "knn": {
      "embedding_vector": {
        "vector": [0.1, 0.2, ...],
        "k": 10
      }
    }
  }
}
```

**Performance:**
- Query latency: 50-200ms
- Scales to millions of vectors
- Approximate nearest neighbor (ANN)

### 7. Coveo Platform

**Components Used:**
- Push API (indexing)
- Search API (queries)
- Indexing Pipeline Extensions (IPE)
- Usage Analytics (tracking)

**Index Structure:**
```json
{
  "documentId": "product-12345",
  "assetid": "product-12345",
  "title": "Luxury Handbag",
  "description": "Premium leather handbag",
  "category": "Handbags",
  "price": "$2,500",
  "imageurl": "https://...",
  "producturl": "https://...",
  "s3_key": "product-images/product-12345.jpg"
}
```

**Search Query:**
```json
{
  "aq": "@assetid==product-001 OR @assetid==product-002 OR ...",
  "numberOfResults": 10,
  "fieldsToInclude": [
    "assetid", "title", "description",
    "price", "category", "imageurl", "producturl"
  ]
}
```

**IPE Configuration:**
- Condition: `@imageurl IS NOT NULL OR @s3_key IS NOT NULL`
- URL: Lambda Function URL
- Method: POST
- Timeout: 60 seconds

### 8. Embedding Generator

**Type:** Python script (run manually or scheduled)

**Purpose:**
- Pre-compute embeddings for existing images
- Bulk indexing to OpenSearch
- Initial setup

**Process:**
1. Create OpenSearch index (if not exists)
2. List all images in S3 bucket
3. For each image:
   - Check if already indexed
   - Download from S3
   - Generate embedding
   - Index to OpenSearch
4. Report summary

**Execution Time:**
- ~2-3 seconds per image
- 100 images = ~5 minutes
- Can be parallelized

## Data Flow

### Search Flow (Query Time)

```
User uploads image
    ↓
UI converts to base64
    ↓
POST to API Gateway
    ↓
Lambda receives request
    ↓
Bedrock generates embedding (800ms)
    ↓
OpenSearch k-NN search (100ms)
    ↓
Returns top 10 asset IDs
    ↓
Coveo Search API query (300ms)
    ↓
Coveo applies personalization
    ↓
Returns ranked results
    ↓
Lambda merges data
    ↓
API Gateway returns to UI
    ↓
UI displays results
```

**Total Latency:** 1.5-2.5 seconds

### Indexing Flow (Batch)

```
Images in S3 bucket
    ↓
Run embedding_generator.py
    ↓
For each image:
    ↓
    Download from S3
    ↓
    Bedrock generates embedding
    ↓
    Index to OpenSearch
    ↓
Separately: Push to Coveo
    ↓
Both systems indexed
```

### Indexing Flow (Real-time via IPE)

```
New product data
    ↓
Coveo Push API
    ↓
Coveo Indexing Pipeline
    ↓
IPE Extension triggers
    ↓
Lambda receives document
    ↓
Download image (S3 or URL)
    ↓
Bedrock generates embedding
    ↓
Index to OpenSearch
    ↓
Return to Coveo
    ↓
Coveo completes indexing
    ↓
Product searchable in both systems
```

## Security

### Authentication & Authorization

**AWS:**
- IAM roles for Lambda functions
- Least privilege permissions
- No hardcoded credentials

**OpenSearch:**
- HTTP Basic Auth
- Credentials in environment variables
- VPC isolation (optional)

**Coveo:**
- API keys with specific permissions
- Separate keys for Push, Search, Admin
- Keys in environment variables

**UI:**
- Public access (demo)
- Can add authentication layer
- HTTPS only

### Data Protection

**In Transit:**
- HTTPS for all API calls
- TLS 1.2+ for OpenSearch
- Encrypted Lambda environment variables

**At Rest:**
- S3 bucket encryption (optional)
- OpenSearch encryption at rest
- EBS volume encryption

**Sensitive Data:**
- No PII in logs
- Image data not persisted in Lambda
- Credentials in AWS Secrets Manager (production)

## Scalability

### Current Limits

- **Lambda:** 1000 concurrent executions (default)
- **API Gateway:** 10,000 requests/second
- **Bedrock:** 100 TPS (can request increase)
- **OpenSearch:** Depends on instance size
- **Coveo:** Based on plan

### Scaling Strategies

**Horizontal Scaling:**
- Lambda auto-scales
- Add OpenSearch nodes
- Use CloudFront for UI

**Vertical Scaling:**
- Increase Lambda memory
- Larger OpenSearch instances
- Optimize embedding dimension

**Caching:**
- CloudFront for static assets
- ElastiCache for frequent queries
- Cache embeddings for common images

**Optimization:**
- Batch Bedrock requests
- Async processing for IPE
- Connection pooling for OpenSearch

## Monitoring & Observability

### CloudWatch Metrics

**Lambda:**
- Invocations
- Duration
- Errors
- Throttles
- Concurrent executions

**API Gateway:**
- Request count
- Latency
- 4xx/5xx errors
- Integration latency

**Custom Metrics:**
- OpenSearch query time
- Bedrock API latency
- Coveo API latency
- End-to-end search time

### Logging

**Lambda Logs:**
- Request/response
- Error stack traces
- OpenSearch results (debug)
- Timing information

**Log Retention:**
- 7 days (demo)
- 30+ days (production)

**Log Analysis:**
- CloudWatch Insights
- Search for errors
- Performance analysis

### Alarms

**Critical:**
- Lambda error rate > 5%
- API Gateway 5xx > 10
- OpenSearch cluster red

**Warning:**
- Lambda duration > 10s
- API Gateway latency > 3s
- Bedrock throttling

## Cost Optimization

### Current Costs (Monthly)

**Fixed:**
- OpenSearch t3.small: ~$50
- EBS 20GB: ~$2

**Variable:**
- Lambda: $0.20 per 1M requests
- API Gateway: $3.50 per 1M requests
- Bedrock: $0.06 per 1000 images
- S3: $0.023 per GB
- Data transfer: $0.09 per GB

**Total for 100K searches/month:** ~$60-70

### Optimization Tips

1. **Use Reserved Instances** for OpenSearch
2. **Batch Bedrock calls** where possible
3. **Cache frequent queries** with ElastiCache
4. **Optimize Lambda memory** (cost vs performance)
5. **Use S3 Intelligent-Tiering** for images
6. **Enable CloudFront** to reduce API calls
7. **Delete old CloudWatch logs**

## Disaster Recovery

### Backup Strategy

**OpenSearch:**
- Automated snapshots to S3
- Daily backups
- 7-day retention

**S3:**
- Versioning enabled
- Cross-region replication (optional)

**Coveo:**
- Managed by Coveo
- Built-in redundancy

**Infrastructure:**
- CloudFormation templates in Git
- Reproducible deployments

### Recovery Procedures

**OpenSearch Failure:**
1. Restore from snapshot
2. Re-run embedding generator
3. Verify index

**Lambda Failure:**
1. Check CloudWatch logs
2. Redeploy from CloudFormation
3. Test with sample request

**Complete Disaster:**
1. Deploy CloudFormation stack
2. Restore OpenSearch snapshot
3. Re-run embedding generator
4. Verify end-to-end flow

**RTO:** 2-4 hours
**RPO:** 24 hours (daily snapshots)

## Future Enhancements

### Short Term

1. **Caching layer** - ElastiCache for Redis
2. **Batch API** - Process multiple images
3. **Image preprocessing** - Resize, optimize
4. **Better error handling** - Retry logic
5. **Monitoring dashboard** - CloudWatch

### Medium Term

1. **Multi-modal search** - Text + image
2. **Fine-tuned embeddings** - Domain-specific
3. **A/B testing** - Compare algorithms
4. **Analytics integration** - Track conversions
5. **Admin UI** - Manage products

### Long Term

1. **Real-time indexing** - S3 event triggers
2. **Federated search** - Multiple sources
3. **Recommendation engine** - ML-based
4. **Mobile app** - Native iOS/Android
5. **Multi-region** - Global deployment

## Troubleshooting Guide

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed troubleshooting steps.

## References

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [OpenSearch k-NN Plugin](https://opensearch.org/docs/latest/search-plugins/knn/)
- [Coveo Platform Documentation](https://docs.coveo.com/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [React Documentation](https://react.dev/)
