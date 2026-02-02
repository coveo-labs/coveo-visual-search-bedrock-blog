/**
 * Headless ResultList Component
 * 
 * Displays search results powered by Coveo Headless.
 * Automatically logs click events when users interact with results.
 */

import { useResultList, useQuerySummary, useInteractiveResult } from '../hooks/useCoveoSearch';
import { motion } from 'framer-motion';

/**
 * Single Result Card with click tracking
 */
function ResultCard({ result, index }) {
  const { select, beginDelayedSelect, cancelPendingSelect } = useInteractiveResult(result);

  // Extract fields from result
  const title = result.title || 'Untitled Product';
  const description = result.raw?.description || result.excerpt || '';
  const imageUrl = result.raw?.imageurl || result.raw?.thumbnailurl || '';
  const category = result.raw?.category || '';
  const color = result.raw?.color || '';
  const material = result.raw?.material || '';
  const priceRange = result.raw?.pricerange || '';
  const brand = result.raw?.brand || 'Hermès';

  const handleClick = () => {
    // Log click event to Coveo Analytics
    select();
    
    // Open image in new tab
    if (imageUrl) {
      window.open(imageUrl, '_blank');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group"
      onMouseEnter={beginDelayedSelect}
      onMouseLeave={cancelPendingSelect}
    >
      <div
        onClick={handleClick}
        className="glass-effect rounded-none overflow-hidden cursor-pointer
                 hover:border-luxury-gold/50 transition-all duration-300
                 border border-transparent"
      >
        {/* Image */}
        <div className="aspect-square overflow-hidden bg-luxury-charcoal/50">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-luxury-cream/30">
              <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} 
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          {/* Brand */}
          <p className="text-xs text-luxury-gold tracking-widest mb-1">{brand}</p>
          
          {/* Title */}
          <h3 className="text-luxury-cream font-medium mb-2 line-clamp-2 group-hover:text-luxury-gold transition-colors">
            {title}
          </h3>

          {/* Description */}
          {description && (
            <p className="text-sm text-luxury-cream/60 line-clamp-2 mb-3">
              {description}
            </p>
          )}

          {/* Metadata Tags */}
          <div className="flex flex-wrap gap-1.5">
            {category && (
              <span className="px-2 py-0.5 text-xs bg-luxury-gold/10 text-luxury-cream/70 rounded-none">
                {category}
              </span>
            )}
            {color && (
              <span className="px-2 py-0.5 text-xs bg-luxury-gold/10 text-luxury-cream/70 rounded-none">
                {color}
              </span>
            )}
            {material && (
              <span className="px-2 py-0.5 text-xs bg-luxury-gold/10 text-luxury-cream/70 rounded-none">
                {material}
              </span>
            )}
          </div>

          {/* Price Range */}
          {priceRange && (
            <p className="mt-3 text-luxury-gold font-medium">
              {priceRange}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
}

/**
 * Loading skeleton
 */
function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
        <div key={i} className="glass-effect rounded-none overflow-hidden animate-pulse">
          <div className="aspect-square bg-luxury-gold/10" />
          <div className="p-4 space-y-3">
            <div className="h-3 bg-luxury-gold/10 rounded w-1/4" />
            <div className="h-4 bg-luxury-gold/10 rounded w-3/4" />
            <div className="h-3 bg-luxury-gold/10 rounded w-full" />
            <div className="flex gap-2">
              <div className="h-5 bg-luxury-gold/10 rounded w-16" />
              <div className="h-5 bg-luxury-gold/10 rounded w-12" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * No results message
 */
function NoResults({ query }) {
  return (
    <div className="text-center py-16">
      <div className="w-20 h-20 mx-auto mb-6 bg-luxury-charcoal/50 rounded-full 
                    flex items-center justify-center">
        <svg className="w-10 h-10 text-luxury-gold/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <h3 className="text-xl text-luxury-cream mb-2">No results found</h3>
      {query && (
        <p className="text-luxury-cream/60">
          No products match "{query}". Try adjusting your search or filters.
        </p>
      )}
    </div>
  );
}

export default function HeadlessResultList() {
  const { results, isLoading, hasResults, firstSearchExecuted } = useResultList();
  const { total, query, durationInSeconds } = useQuerySummary();

  // Show nothing before first search
  if (!firstSearchExecuted) {
    return null;
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex-1">
        <LoadingSkeleton />
      </div>
    );
  }

  // Show no results
  if (!hasResults) {
    return (
      <div className="flex-1">
        <NoResults query={query} />
      </div>
    );
  }

  return (
    <div className="flex-1">
      {/* Results Summary */}
      <div className="flex items-center justify-between mb-6">
        <p className="text-luxury-cream/60 text-sm">
          {total.toLocaleString()} results
          {query && <span> for "{query}"</span>}
          <span className="text-luxury-cream/40 ml-2">
            ({durationInSeconds.toFixed(2)}s)
          </span>
        </p>
      </div>

      {/* Results Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {results.map((result, index) => (
          <ResultCard
            key={result.uniqueId}
            result={result}
            index={index}
          />
        ))}
      </div>
    </div>
  );
}
