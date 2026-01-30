import { motion, AnimatePresence } from 'framer-motion'

export default function OpenSearchPanel({ results, isOpen, onToggle }) {
  if (!results || results.length === 0) return null

  return (
    <div className="fixed right-0 top-1/2 -translate-y-1/2 z-50">
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute -left-12 top-1/2 -translate-y-1/2 w-12 h-24
                   bg-luxury-charcoal border border-luxury-gold/30 border-r-0
                   flex items-center justify-center hover:bg-luxury-gold/10
                   transition-colors rounded-l-lg"
      >
        <div className="flex flex-col items-center">
          <svg 
            className={`w-5 h-5 text-luxury-gold transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          <span className="text-[10px] text-luxury-gold tracking-wider mt-1 
                         [writing-mode:vertical-lr] rotate-180">
            OPENSEARCH
          </span>
        </div>
      </button>

      {/* Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="w-80 h-[70vh] bg-luxury-charcoal border-l border-luxury-gold/30
                       overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="p-4 border-b border-luxury-gold/20">
              <h3 className="text-sm font-medium text-luxury-gold tracking-wider">
                OPENSEARCH RESULTS
              </h3>
              <p className="text-xs text-luxury-cream/50 mt-1">
                Vector similarity matches
              </p>
            </div>

            {/* Results List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {results.map((result, index) => (
                <motion.div
                  key={result.asset_id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center gap-3 p-3 bg-luxury-black/30 
                           border border-luxury-gold/10 rounded-none"
                >
                  {/* Thumbnail */}
                  <div className="w-12 h-12 flex-shrink-0 bg-luxury-charcoal overflow-hidden">
                    {result.image_url ? (
                      <img
                        src={result.image_url}
                        alt={result.asset_id}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none'
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <span className="text-xs text-luxury-gold/30">{index + 1}</span>
                      </div>
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-luxury-cream/70 truncate">
                      {result.asset_id}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex-1 h-1.5 bg-luxury-black/50 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-luxury-gold transition-all"
                          style={{ width: `${result.score * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-luxury-gold font-medium">
                        {(result.score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-luxury-gold/20 bg-luxury-black/30">
              <p className="text-xs text-luxury-cream/40 text-center">
                Showing top {results.length} matches from OpenSearch k-NN
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
