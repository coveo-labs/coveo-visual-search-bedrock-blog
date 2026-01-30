# Demo Guide

Complete guide for presenting the Luxury Image Search demo to customers.

## Demo Overview

**Duration:** 15-20 minutes

**Objective:** Demonstrate how Coveo's search capabilities can be enhanced with AI-powered visual similarity using Amazon Bedrock and OpenSearch.

**Key Messages:**
1. Coveo excels at personalized, metadata-rich search
2. OpenSearch provides powerful vector similarity for images
3. Combined solution offers best of both worlds
4. Easy to implement with Coveo's extensibility

## Pre-Demo Checklist

### Technical Setup

- [ ] All infrastructure deployed and tested
- [ ] UI is accessible and loading correctly
- [ ] At least 20-30 products indexed in both systems
- [ ] Test search with 2-3 sample images
- [ ] CloudWatch logs accessible for showing backend
- [ ] Coveo dashboard open for showing analytics
- [ ] OpenSearch dashboard open (optional)

### Demo Materials

- [ ] Sample luxury product images ready
- [ ] Architecture diagram prepared
- [ ] Backup screenshots in case of connectivity issues
- [ ] Customer's use case notes
- [ ] ROI/value proposition slides

### Environment Check

```bash
# Test API endpoint
curl https://your-api-gateway-url.com/prod/search -X POST \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Check UI is live
curl https://your-netlify-site.netlify.app/

# Verify OpenSearch
curl -u admin:password https://your-opensearch-endpoint.amazonaws.com/_cluster/health
```

## Demo Script

### Part 1: Introduction (2 minutes)

**What to Say:**

"Today I'll show you how we can combine Coveo's powerful personalization and search capabilities with AI-powered visual similarity to create a next-generation product discovery experience."

**What to Show:**
- Architecture diagram
- Explain the flow: Image → Bedrock → OpenSearch → Coveo → Results

**Key Points:**
- Coveo doesn't natively support reverse image search
- We leverage AWS services for visual similarity
- Coveo adds personalization, business rules, and rich metadata
- This is a production-ready pattern

### Part 2: Basic Search Demo (5 minutes)

**What to Do:**

1. Open the UI
2. Show the luxury design
3. Upload a handbag image
4. Walk through the search process

**What to Say:**

"Let me show you how this works in practice. I'll upload an image of a luxury handbag..."

[Upload image]

"Behind the scenes, several things are happening:
1. The image is sent to Amazon Bedrock's Titan model
2. Bedrock generates a 1024-dimensional embedding vector
3. OpenSearch performs k-NN search to find visually similar products
4. The top 10 asset IDs are sent to Coveo
5. Coveo returns personalized results based on user context"

[Results appear]

"Notice how the results aren't just visually similar - they're also ranked by Coveo's ML models based on:
- User behavior and preferences
- Product availability
- Business rules
- Merchandising priorities"

**What to Show:**
- Smooth UI interactions
- Loading states
- Result cards with rich metadata
- Price, category, descriptions

### Part 3: OpenSearch Debug Log (3 minutes)

**What to Do:**

1. Click "Show OpenSearch Debug Log"
2. Explain the similarity scores
3. Show asset IDs

**What to Say:**

"For this demo, I've enabled a debug view so you can see what OpenSearch returns..."

[Show log]

"Here you can see:
- The 10 most visually similar products
- Similarity scores (lower is better for L2 distance)
- Asset IDs that are passed to Coveo
- Metadata from OpenSearch

These results are purely based on visual similarity. Now watch what happens when Coveo processes them..."

[Scroll back to results]

"Coveo has re-ranked these results based on:
- Your personalization rules
- User context
- Business logic
- Availability and inventory

This is the power of combining both systems."

### Part 4: Live IPE Extension Demo (5 minutes)

**What to Say:**

"Now let me show you how new products are automatically indexed. This uses Coveo's Indexing Pipeline Extensions..."

**What to Do:**

1. Open Coveo Platform
2. Show the IPE configuration
3. Push a new document via API or UI

```python
# Show this code or run it live
import requests

url = f"https://api.cloud.coveo.com/push/v1/organizations/{org_id}/sources/{source_id}/documents"

document = {
    "documentId": "demo-product-new",
    "title": "New Luxury Watch",
    "assetid": "demo-product-new",
    "imageurl": "https://your-bucket.s3.amazonaws.com/demo-watch.jpg",
    "category": "Watches",
    "price": "$5,000"
}

response = requests.put(url, headers=headers, json=document)
```

4. Show CloudWatch logs for IPE Lambda
5. Query OpenSearch to show new embedding

**What to Say:**

"When a new product is indexed in Coveo:
1. The IPE extension intercepts the document
2. It calls our Lambda function
3. Lambda downloads the image
4. Generates embedding via Bedrock
5. Indexes to OpenSearch
6. Returns control to Coveo

This happens automatically for every product with an image. No manual intervention needed."

### Part 5: Architecture Deep Dive (3 minutes)

**What to Show:**
- CloudFormation template
- Lambda functions
- API Gateway
- Cost breakdown

**What to Say:**

"The entire infrastructure is deployed as code using CloudFormation. This means:
- Repeatable deployments
- Version controlled
- Easy to replicate across environments

The solution is serverless, so you only pay for what you use:
- Lambda charges per request
- Bedrock charges per embedding
- OpenSearch has a fixed cost
- Total cost for 1M searches per month: approximately $70"

### Part 6: Use Cases & Value Proposition (2 minutes)

**What to Say:**

"This pattern works for any scenario where you need visual similarity combined with business logic:

**Fashion & Luxury:**
- Find similar styles
- Personalized recommendations
- Visual merchandising

**Home Decor:**
- Room inspiration
- Style matching
- Product discovery

**Automotive:**
- Find similar vehicles
- Parts identification
- Visual search

**Real Estate:**
- Similar properties
- Style preferences
- Visual browsing

The key advantage is that you get:
1. State-of-the-art visual AI from AWS
2. Enterprise search and personalization from Coveo
3. Full control over business logic
4. Scalable, production-ready architecture"

## Handling Questions

### "Why not use Coveo's built-in image search?"

"Coveo doesn't currently offer native reverse image search. This solution leverages Coveo's strengths - personalization, analytics, business rules - while using AWS for the visual AI component. It's the best of both worlds."

### "What about latency?"

"End-to-end latency is typically 1-2 seconds:
- Bedrock embedding: 500-800ms
- OpenSearch k-NN: 100-200ms
- Coveo search: 200-400ms
- Network overhead: 200-400ms

This is acceptable for most use cases. We can optimize further with caching if needed."

### "How accurate is the visual similarity?"

"Bedrock's Titan model is trained on billions of images and provides excellent accuracy for general visual similarity. For domain-specific needs, we can fine-tune or use alternative models. The accuracy also improves as you add more products to the index."

### "Can this work with our existing Coveo setup?"

"Absolutely. This integrates seamlessly with your existing Coveo organization. We just:
1. Add an IPE extension to your source
2. Deploy the AWS infrastructure
3. Configure the search UI

Your existing Coveo configuration, ML models, and business rules all continue to work."

### "What about costs?"

"For a typical e-commerce site with 10,000 products and 100,000 searches per month:
- Initial embedding generation: ~$10 (one-time)
- OpenSearch: ~$50/month
- Lambda + API Gateway: ~$5/month
- Bedrock (for searches): ~$5/month
- Total: ~$60-70/month

This is very cost-effective compared to building a custom solution."

### "How do we handle updates to products?"

"The IPE extension automatically handles updates. When a product is updated in Coveo:
1. If the image changed, new embedding is generated
2. If only metadata changed, Coveo is updated
3. Both systems stay in sync automatically

You can also run batch updates using the embedding generator script."

## Demo Tips

### Do's

✅ Test everything 30 minutes before demo
✅ Have backup screenshots ready
✅ Prepare 3-4 diverse test images
✅ Know your customer's use case
✅ Show CloudWatch logs to prove it's real
✅ Emphasize the extensibility of Coveo
✅ Focus on business value, not just tech

### Don'ts

❌ Don't use copyrighted images without permission
❌ Don't promise features that don't exist
❌ Don't get too technical unless asked
❌ Don't skip the value proposition
❌ Don't forget to show the OpenSearch log
❌ Don't rush through the IPE extension demo

## Backup Plan

If live demo fails:

1. **Have screenshots ready** of successful searches
2. **Record a video** beforehand showing the full flow
3. **Show CloudWatch logs** from previous successful runs
4. **Walk through code** instead of live demo
5. **Focus on architecture** and value proposition

## Post-Demo Follow-Up

### Immediate Actions

1. Send architecture diagram
2. Share GitHub repository (if appropriate)
3. Provide cost calculator
4. Schedule technical deep-dive if interested

### Materials to Send

- Architecture documentation
- Deployment guide
- Cost breakdown spreadsheet
- Case studies (if available)
- ROI calculator
- Next steps proposal

## Success Metrics

Track these during/after demo:

- Customer engagement level
- Technical questions asked
- Interest in POC/pilot
- Concerns raised
- Follow-up meeting scheduled
- Decision timeline

## Customization for Customer

Before demo, customize:

1. **Industry-specific images** - Use products from their industry
2. **Brand colors** - Update UI theme to match their brand
3. **Use case focus** - Emphasize their specific needs
4. **Integration points** - Show how it fits their stack
5. **ROI calculation** - Use their numbers

## Advanced Demo Features

If time permits or customer is technical:

### Show Embedding Visualization

Use t-SNE or PCA to visualize embeddings in 2D:

```python
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# Get embeddings from OpenSearch
# Reduce to 2D
# Plot with product images
```

### Show A/B Test Results

"We can A/B test OpenSearch+Coveo vs Coveo-only to measure:
- Click-through rate improvement
- Conversion rate lift
- User engagement metrics"

### Show Analytics Integration

"All searches are tracked in Coveo Analytics, so you can:
- See which images are searched most
- Track conversion from visual search
- Optimize based on user behavior"

## Conclusion

End with:

"This solution demonstrates how Coveo's extensibility allows you to add cutting-edge AI capabilities while maintaining all the enterprise features you need - personalization, analytics, security, and scalability. 

Would you like to discuss a pilot project for your use case?"

## Appendix: Sample Images

Prepare these image types:

1. **Clear product shot** - Best case scenario
2. **Lifestyle image** - Product in context
3. **Partial view** - Test robustness
4. **Similar but different** - Show ranking
5. **Edge case** - Show limitations honestly

## Emergency Contacts

Have these ready during demo:

- AWS Support: [number]
- Coveo Support: [number]
- Your technical lead: [number]
- Backup presenter: [number]
