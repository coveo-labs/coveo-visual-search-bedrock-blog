/**
 * Coveo Headless Engine Configuration
 * 
 * This module sets up the Coveo Headless search engine with:
 * - Search functionality
 * - Analytics (Coveo UA protocol for non-commerce)
 * - Facets for filtering
 * - Result list management
 */

import {
  buildSearchEngine,
  buildSearchBox,
  buildResultList,
  buildFacet,
  buildQuerySummary,
  buildPager,
  buildInteractiveResult,
  loadSearchActions,
} from '@coveo/headless';

// Configuration from environment variables
const COVEO_ORG_ID = import.meta.env.VITE_COVEO_ORG_ID;
const COVEO_API_KEY = import.meta.env.VITE_COVEO_API_KEY;
const COVEO_SEARCH_HUB = import.meta.env.VITE_COVEO_SEARCH_HUB || 'LuxuryImageSearch';
const COVEO_PIPELINE = import.meta.env.VITE_COVEO_PIPELINE || 'hermes';

/**
 * Create and configure the Coveo Search Engine
 */
export function createSearchEngine() {
  if (!COVEO_API_KEY) {
    console.error('VITE_COVEO_API_KEY is not set');
    return null;
  }

  const engine = buildSearchEngine({
    configuration: {
      organizationId: COVEO_ORG_ID,
      accessToken: COVEO_API_KEY,
      search: {
        searchHub: COVEO_SEARCH_HUB,
        pipeline: COVEO_PIPELINE,
      },
      analytics: {
        enabled: true,
        originLevel2: COVEO_SEARCH_HUB,
        originLevel3: 'default',
      },
    },
  });

  return engine;
}

/**
 * Create SearchBox controller
 * Automatically logs search events
 */
export function createSearchBox(engine) {
  return buildSearchBox(engine, {
    options: {
      numberOfSuggestions: 5,
      highlightOptions: {
        notMatchDelimiters: {
          open: '<strong>',
          close: '</strong>',
        },
      },
    },
  });
}

/**
 * Create ResultList controller
 */
export function createResultList(engine) {
  return buildResultList(engine, {
    options: {
      fieldsToInclude: [
        'title',
        'description',
        'category',
        'subcategory',
        'color',
        'material',
        'style',
        'gender',
        'pricerange',
        'brand',
        'imageurl',
        'thumbnailurl',
        'assetid',
        's3_key',
      ],
    },
  });
}

/**
 * Create InteractiveResult controller for a specific result
 * Automatically logs click events when user interacts with result
 */
export function createInteractiveResult(engine, result) {
  return buildInteractiveResult(engine, {
    options: { result },
  });
}

/**
 * Create Facet controllers for filtering
 */
export function createFacets(engine) {
  return {
    category: buildFacet(engine, {
      options: {
        field: 'category',
        facetId: 'category',
        numberOfValues: 10,
        sortCriteria: 'occurrences',
      },
    }),
    subcategory: buildFacet(engine, {
      options: {
        field: 'subcategory',
        facetId: 'subcategory',
        numberOfValues: 15,
        sortCriteria: 'occurrences',
      },
    }),
    color: buildFacet(engine, {
      options: {
        field: 'color',
        facetId: 'color',
        numberOfValues: 15,
        sortCriteria: 'occurrences',
      },
    }),
    material: buildFacet(engine, {
      options: {
        field: 'material',
        facetId: 'material',
        numberOfValues: 10,
        sortCriteria: 'occurrences',
      },
    }),
    style: buildFacet(engine, {
      options: {
        field: 'style',
        facetId: 'style',
        numberOfValues: 10,
        sortCriteria: 'occurrences',
      },
    }),
    gender: buildFacet(engine, {
      options: {
        field: 'gender',
        facetId: 'gender',
        numberOfValues: 5,
        sortCriteria: 'occurrences',
      },
    }),
    priceRange: buildFacet(engine, {
      options: {
        field: 'pricerange',
        facetId: 'pricerange',
        numberOfValues: 6,
        sortCriteria: 'alphanumeric',
      },
    }),
  };
}

/**
 * Create QuerySummary controller
 */
export function createQuerySummary(engine) {
  return buildQuerySummary(engine);
}

/**
 * Create Pager controller
 */
export function createPager(engine) {
  return buildPager(engine, {
    options: {
      numberOfPages: 5,
    },
  });
}

/**
 * Log custom analytics event
 * Use this for image search, metadata extraction, etc.
 * Note: Custom events may not be available in all Headless versions
 */
export function logCustomEvent(engine, eventType, eventValue, customData = {}) {
  try {
    // Custom event logging - log to console for now
    // Full custom event support requires Coveo Analytics API directly
    console.log('Custom Event:', { eventType, eventValue, customData });
  } catch (e) {
    console.warn('Custom event logging not available:', e);
  }
}

/**
 * Log image search event
 */
export function logImageSearchEvent(engine, imageSize, matchCount) {
  console.log('Image Search Event:', { imageSize, matchCount, searchType: 'visual' });
}

/**
 * Log metadata extraction event
 */
export function logMetadataExtractionEvent(engine, extractedFields) {
  console.log('Metadata Extraction Event:', { extractedFields, model: 'nova-lite' });
}

/**
 * Execute a search query programmatically
 */
export function executeSearch(engine, query) {
  const searchActions = loadSearchActions(engine);
  
  engine.dispatch(searchActions.updateQuery({ q: query }));
  engine.dispatch(searchActions.executeSearch());
}

// Export a singleton engine instance
let engineInstance = null;

export function getEngine() {
  if (!engineInstance) {
    engineInstance = createSearchEngine();
  }
  return engineInstance;
}

export default {
  createSearchEngine,
  createSearchBox,
  createResultList,
  createInteractiveResult,
  createFacets,
  createQuerySummary,
  createPager,
  logCustomEvent,
  logImageSearchEvent,
  logMetadataExtractionEvent,
  executeSearch,
  getEngine,
};
