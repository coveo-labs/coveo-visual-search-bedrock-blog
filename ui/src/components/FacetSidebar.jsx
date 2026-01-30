import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function FacetSidebar({ facets, selectedFacets, onFacetChange }) {
  const [expandedFacets, setExpandedFacets] = useState({
    category: true,
    color: true,
    pricerange: true,
    gender: false,
    style: false,
    material: false,
  })

  const toggleFacet = (facetName) => {
    setExpandedFacets(prev => ({
      ...prev,
      [facetName]: !prev[facetName]
    }))
  }

  const handleFacetSelect = (facetName, value) => {
    const currentValues = selectedFacets[facetName] || []
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value]
    
    onFacetChange(facetName, newValues)
  }

  const facetConfig = [
    { key: 'category', label: 'Category' },
    { key: 'subcategory', label: 'Type' },
    { key: 'color', label: 'Color' },
    { key: 'pricerange', label: 'Price Range' },
    { key: 'gender', label: 'Gender' },
    { key: 'style', label: 'Style' },
    { key: 'material', label: 'Material' },
    { key: 'size', label: 'Size' },
  ]

  const clearAllFacets = () => {
    facetConfig.forEach(f => onFacetChange(f.key, []))
  }

  const hasSelectedFacets = Object.values(selectedFacets).some(v => v && v.length > 0)

  return (
    <div className="w-72 flex-shrink-0">
      <div className="sticky top-4">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-serif text-luxury-gold tracking-wider">
            FILTERS
          </h3>
          {hasSelectedFacets && (
            <button
              onClick={clearAllFacets}
              className="text-xs text-luxury-cream/60 hover:text-luxury-gold 
                         tracking-wider transition-colors"
            >
              CLEAR ALL
            </button>
          )}
        </div>

        <div className="space-y-4">
          {facetConfig.map(({ key, label }) => {
            const facetValues = facets[key] || []
            if (facetValues.length === 0) return null

            const isExpanded = expandedFacets[key]
            const selectedValues = selectedFacets[key] || []

            return (
              <div key={key} className="border-b border-luxury-gold/20 pb-4">
                <button
                  onClick={() => toggleFacet(key)}
                  className="w-full flex items-center justify-between py-2 
                             text-luxury-cream hover:text-luxury-gold transition-colors"
                >
                  <span className="text-sm tracking-wider font-medium">
                    {label}
                    {selectedValues.length > 0 && (
                      <span className="ml-2 text-luxury-gold">
                        ({selectedValues.length})
                      </span>
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

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="pt-2 space-y-2 max-h-48 overflow-y-auto">
                        {facetValues.slice(0, 10).map(({ value, count }) => (
                          <label
                            key={value}
                            className="flex items-center gap-3 cursor-pointer group"
                          >
                            <input
                              type="checkbox"
                              checked={selectedValues.includes(value)}
                              onChange={() => handleFacetSelect(key, value)}
                              className="w-4 h-4 rounded-none border-luxury-gold/50 
                                         bg-transparent checked:bg-luxury-gold 
                                         checked:border-luxury-gold focus:ring-0
                                         focus:ring-offset-0 cursor-pointer"
                            />
                            <span className="text-sm text-luxury-cream/70 
                                           group-hover:text-luxury-cream transition-colors
                                           flex-1 truncate">
                              {value}
                            </span>
                            <span className="text-xs text-luxury-cream/40">
                              {count}
                            </span>
                          </label>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
