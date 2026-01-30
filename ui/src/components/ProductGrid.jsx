import { motion } from 'framer-motion'

export default function ProductGrid({ results, opensearchResults, showOpenSearchPanel }) {
  if (!results || results.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-16"
      >
        <div className="w-24 h-24 mx-auto mb-6 rounded-none bg-luxury-charcoal/50 
                        flex items-center justify-center">
          <svg className="w-12 h-12 text-luxury-gold/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <p className="text-xl text-luxury-cream/70 font-light tracking-wide">
          No results found
        </p>
        <p className="text-sm text-luxury-cream/50 mt-2">
          Try adjusting your search or filters
        </p>
      </motion.div>
    )
  }

  // Create a map of asset_id to similarity score
  const scoreMap = {}
  if (opensearchResults) {
    opensearchResults.forEach(r => {
      scoreMap[r.asset_id] = r.score
    })
  }

  return (
    <div className="flex-1">
      {/* Results Header */}
      <div className="flex items-center justify-between mb-8">
        <p className="text-luxury-cream/70 tracking-wide">
          <span className="text-luxury-gold font-medium">{results.length}</span> products found
        </p>
        
        {showOpenSearchPanel && opensearchResults && opensearchResults.length > 0 && (
          <div className="text-xs text-luxury-cream/50 tracking-wide">
            Similarity scores from OpenSearch
          </div>
        )}
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {results.map((result, index) => {
          const assetId = result.raw?.assetid || ''
          const similarityScore = scoreMap[assetId]
          const imageUrl = result.raw?.imageurl || result.clickUri || ''
          
          return (
            <motion.div
              key={result.uniqueId || index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="group"
            >
              <div className="bg-luxury-charcoal/30 border border-luxury-gold/10 
                            hover:border-luxury-gold/30 transition-all duration-300
                            rounded-none overflow-hidden">
                {/* Image */}
                <div className="aspect-square relative overflow-hidden bg-luxury-charcoal">
                  {imageUrl ? (
                    <img
                      src={imageUrl}
                      alt={result.title}
                      className="w-full h-full object-cover transition-transform 
                               duration-500 group-hover:scale-105"
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/400x400/1a1a1a/D4AF37?text=No+Image'
                      }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <svg className="w-16 h-16 text-luxury-gold/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  )}
                  
                  {/* Similarity Score Badge */}
                  {showOpenSearchPanel && similarityScore !== undefined && (
                    <div className="absolute top-3 right-3 px-2 py-1 
                                  bg-luxury-black/80 text-luxury-gold text-xs
                                  tracking-wider rounded-none">
                      {(similarityScore * 100).toFixed(0)}% match
                    </div>
                  )}
                  
                  {/* Category Badge */}
                  {result.raw?.category && (
                    <div className="absolute top-3 left-3 px-2 py-1 
                                  bg-luxury-gold/90 text-luxury-black text-xs
                                  tracking-wider uppercase rounded-none">
                      {result.raw.category}
                    </div>
                  )}
                </div>

                {/* Product Info */}
                <div className="p-4">
                  <h3 className="text-sm font-medium text-luxury-cream mb-1 
                               line-clamp-2 tracking-wide group-hover:text-luxury-gold
                               transition-colors">
                    {result.title}
                  </h3>
                  
                  {/* Color & Material */}
                  <div className="flex items-center gap-2 mb-2">
                    {result.raw?.color && (
                      <span className="text-xs text-luxury-cream/50">
                        {result.raw.color}
                      </span>
                    )}
                    {result.raw?.color && result.raw?.material && (
                      <span className="text-luxury-cream/30">•</span>
                    )}
                    {result.raw?.material && (
                      <span className="text-xs text-luxury-cream/50">
                        {result.raw.material}
                      </span>
                    )}
                  </div>
                  
                  {/* Price */}
                  {result.raw?.price && (
                    <p className="text-luxury-gold font-medium tracking-wider">
                      {result.raw.price}
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
