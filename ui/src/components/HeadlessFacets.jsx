/**
 * Headless Facets Component
 * 
 * Faceted navigation powered by Coveo Headless.
 * Automatically updates search results when facets are selected.
 */

import { useState } from 'react';
import { useFacets } from '../hooks/useCoveoSearch';
import { motion, AnimatePresence } from 'framer-motion';

// Facet display configuration
const FACET_CONFIG = {
  category: { label: 'Category', icon: '📁' },
  subcategory: { label: 'Type', icon: '📋' },
  color: { label: 'Color', icon: '🎨' },
  material: { label: 'Material', icon: '🧵' },
  style: { label: 'Style', icon: '✨' },
  gender: { label: 'Gender', icon: '👤' },
  priceRange: { label: 'Price Range', icon: '💰' },
};

function FacetSection({ name, config, values, isLoading, hasActiveValues, onToggle, onClear }) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!values || values.length === 0) return null;

  return (
    <div className="border-b border-luxury-gold/20 pb-4 mb-4">
      {/* Facet Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between py-2 text-luxury-cream 
                 hover:text-luxury-gold transition-colors"
      >
        <span className="flex items-center gap-2 text-sm font-medium tracking-wider uppercase">
          <span>{config.icon}</span>
          {config.label}
          {hasActiveValues && (
            <span className="w-2 h-2 bg-luxury-gold rounded-full" />
          )}
        </span>
        <svg
          className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Facet Values */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="pt-2 space-y-1">
              {values.slice(0, 8).map((facetValue) => (
                <button
                  key={facetValue.value}
                  onClick={() => onToggle(name, facetValue)}
                  disabled={isLoading}
                  className={`w-full flex items-center justify-between px-2 py-1.5 rounded-none
                           text-sm transition-colors ${
                             facetValue.state === 'selected'
                               ? 'bg-luxury-gold/20 text-luxury-gold'
                               : 'text-luxury-cream/70 hover:text-luxury-cream hover:bg-luxury-gold/10'
                           } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <span className="flex items-center gap-2">
                    <span
                      className={`w-4 h-4 border rounded-sm flex items-center justify-center
                               ${facetValue.state === 'selected'
                                 ? 'border-luxury-gold bg-luxury-gold'
                                 : 'border-luxury-cream/30'
                               }`}
                    >
                      {facetValue.state === 'selected' && (
                        <svg className="w-3 h-3 text-luxury-black" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </span>
                    <span className="truncate">{facetValue.value}</span>
                  </span>
                  <span className="text-xs text-luxury-cream/50">
                    {facetValue.numberOfResults}
                  </span>
                </button>
              ))}

              {/* Show more indicator */}
              {values.length > 8 && (
                <p className="text-xs text-luxury-cream/40 px-2 pt-1">
                  +{values.length - 8} more
                </p>
              )}

              {/* Clear facet button */}
              {hasActiveValues && (
                <button
                  onClick={() => onClear(name)}
                  className="w-full text-xs text-luxury-gold hover:text-luxury-gold/80 
                           px-2 pt-2 text-left transition-colors"
                >
                  Clear {config.label.toLowerCase()}
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function HeadlessFacets() {
  const { facets, isReady, toggleSelect, deselectAll } = useFacets();

  if (!isReady) {
    return (
      <div className="w-64 flex-shrink-0">
        <div className="glass-effect p-6 rounded-none animate-pulse">
          <div className="h-6 bg-luxury-gold/20 rounded mb-4" />
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="h-4 bg-luxury-gold/10 rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Check if any facets have values
  const hasFacets = Object.values(facets).some(f => f?.values?.length > 0);

  if (!hasFacets) {
    return null;
  }

  // Check if any facets are active
  const hasActiveFilters = Object.values(facets).some(f => f?.hasActiveValues);

  return (
    <div className="w-64 flex-shrink-0">
      <div className="glass-effect p-6 rounded-none sticky top-24">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-luxury-cream tracking-wider">
            Filters
          </h3>
          {hasActiveFilters && (
            <button
              onClick={() => {
                Object.keys(facets).forEach(name => deselectAll(name));
              }}
              className="text-xs text-luxury-gold hover:text-luxury-gold/80 transition-colors"
            >
              Clear all
            </button>
          )}
        </div>

        {/* Facet Sections */}
        {Object.entries(FACET_CONFIG).map(([name, config]) => {
          const facetState = facets[name];
          if (!facetState) return null;

          return (
            <FacetSection
              key={name}
              name={name}
              config={config}
              values={facetState.values}
              isLoading={facetState.isLoading}
              hasActiveValues={facetState.hasActiveValues}
              onToggle={toggleSelect}
              onClear={deselectAll}
            />
          );
        })}
      </div>
    </div>
  );
}
