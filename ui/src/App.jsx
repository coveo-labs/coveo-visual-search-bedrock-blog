import { useState, useCallback } from 'react'
import Header from './components/Header'
import ImageUpload from './components/ImageUpload'
import MetadataExtractor from './components/MetadataExtractor'
import OpenSearchPanel from './components/OpenSearchPanel'
import { CoveoProvider } from './components/CoveoProvider'
import HeadlessSearchBox from './components/HeadlessSearchBox'
import HeadlessResultList from './components/HeadlessResultList'
import HeadlessFacets from './components/HeadlessFacets'
import { useAnalytics } from './hooks/useCoveoSearch'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'

// Image Search Results Component (keeps existing functionality)
function ImageSearchResults({ results, opensearchResults, loading }) {
  if (loading) {
    return (
      <div className="flex-1">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
            <div key={i} className="glass-effect rounded-none overflow-hidden animate-pulse">
              <div className="aspect-square bg-luxury-gold/10" />
              <div className="p-4 space-y-3">
                <div className="h-3 bg-luxury-gold/10 rounded w-1/4" />
                <div className="h-4 bg-luxury-gold/10 rounded w-3/4" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <div className="flex-1 text-center py-16">
        <p className="text-luxury-cream/60">Upload an image to find similar products</p>
      </div>
    )
  }

  return (
    <div className="flex-1">
      <p className="text-luxury-cream/60 text-sm mb-6">
        {results.length} similar products found
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {results.map((result, index) => {
          const raw = result.raw || {}
          const imageUrl = raw.imageurl || raw.thumbnailurl || ''
          const title = result.title || raw.title || 'Product'
          
          return (
            <div key={result.uniqueId || index} className="group glass-effect rounded-none overflow-hidden">
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
              <div className="p-4">
                <p className="text-xs text-luxury-gold tracking-widest mb-1">
                  {raw.brand || 'Hermès'}
                </p>
                <h3 className="text-luxury-cream font-medium mb-2 line-clamp-2 group-hover:text-luxury-gold transition-colors">
                  {title}
                </h3>
                <div className="flex flex-wrap gap-1.5">
                  {raw.category && (
                    <span className="px-2 py-0.5 text-xs bg-luxury-gold/10 text-luxury-cream/70">{raw.category}</span>
                  )}
                  {raw.color && (
                    <span className="px-2 py-0.5 text-xs bg-luxury-gold/10 text-luxury-cream/70">{raw.color}</span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Main App Content (inside CoveoProvider)
function AppContent() {
  const [imageResults, setImageResults] = useState([])
  const [opensearchResults, setOpensearchResults] = useState([])
  const [imageLoading, setImageLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('text')
  const [showOpenSearchPanel, setShowOpenSearchPanel] = useState(false)
  
  // Analytics hook for custom events
  const { logImageSearch, logMetadataExtraction, logCustom, isReady: analyticsReady } = useAnalytics()

  // Image search using OpenSearch + Coveo
  const handleImageSearch = useCallback(async (imageData) => {
    setImageLoading(true)
    setError(null)
    setActiveTab('image')
    setShowOpenSearchPanel(true)
    
    try {
      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          image: imageData,
          min_score: 0.6 // 60% similarity threshold
        }),
      })
      
      if (!response.ok) throw new Error('Image search failed')
      
      const data = await response.json()
      setImageResults(data.results || [])
      setOpensearchResults(data.opensearch_results || [])
      
      // Log image search event to Coveo Analytics
      if (analyticsReady) {
        const imageSize = imageData.length
        const matchCount = data.results?.length || 0
        logImageSearch(imageSize, matchCount)
      }
    } catch (err) {
      console.error('Image search error:', err)
      setError('Image search failed. Please try again.')
    } finally {
      setImageLoading(false)
    }
  }, [analyticsReady, logImageSearch])

  return (
    <div className="min-h-screen bg-gradient-to-br from-luxury-black via-luxury-charcoal to-luxury-black">
      <Header />
      
      {/* Hero Section */}
      <section className="pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-serif font-bold text-luxury-gold mb-4 tracking-wider">
            Discover Hermès
          </h1>
          <p className="text-xl text-luxury-cream/70 font-light tracking-wide mb-12">
            Search by text or upload an image to find similar luxury items
          </p>
          
          {/* Tab Toggle */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="flex justify-center mb-6">
              <div className="inline-flex rounded-none border border-luxury-gold/30 overflow-hidden">
                <button
                  onClick={() => setActiveTab('text')}
                  className={`px-6 py-3 text-sm tracking-wider transition-all ${
                    activeTab === 'text'
                      ? 'bg-luxury-gold text-luxury-black font-medium'
                      : 'bg-transparent text-luxury-cream hover:bg-luxury-gold/10'
                  }`}
                >
                  TEXT SEARCH
                </button>
                <button
                  onClick={() => setActiveTab('image')}
                  className={`px-6 py-3 text-sm tracking-wider transition-all ${
                    activeTab === 'image'
                      ? 'bg-luxury-gold text-luxury-black font-medium'
                      : 'bg-transparent text-luxury-cream hover:bg-luxury-gold/10'
                  }`}
                >
                  IMAGE SEARCH
                </button>
                <button
                  onClick={() => setActiveTab('metadata')}
                  className={`px-6 py-3 text-sm tracking-wider transition-all ${
                    activeTab === 'metadata'
                      ? 'bg-luxury-gold text-luxury-black font-medium'
                      : 'bg-transparent text-luxury-cream hover:bg-luxury-gold/10'
                  }`}
                >
                  AI METADATA
                </button>
              </div>
            </div>

            {/* Search Input based on active tab */}
            {activeTab === 'text' && <HeadlessSearchBox />}
            {activeTab === 'image' && (
              <ImageUpload onSearch={handleImageSearch} loading={imageLoading} />
            )}
          </div>
        </div>
      </section>

      {/* Metadata Extractor Section */}
      {activeTab === 'metadata' && (
        <section className="px-6 pb-24">
          <MetadataExtractor onExtract={(fields) => {
            if (analyticsReady) {
              logMetadataExtraction(Object.keys(fields))
            }
          }} />
        </section>
      )}

      {/* Text Search Results (Coveo Headless) */}
      {activeTab === 'text' && (
        <section className="px-6 pb-24">
          <div className="max-w-7xl mx-auto">
            <div className="flex gap-8">
              <HeadlessFacets />
              <HeadlessResultList />
            </div>
          </div>
        </section>
      )}

      {/* Image Search Results */}
      {activeTab === 'image' && (imageResults.length > 0 || imageLoading) && (
        <section className="px-6 pb-24">
          <div className="max-w-7xl mx-auto">
            <ImageSearchResults 
              results={imageResults} 
              opensearchResults={opensearchResults}
              loading={imageLoading}
            />
          </div>
        </section>
      )}

      {/* Error Message */}
      {error && (
        <div className="fixed bottom-6 right-6 bg-red-900/90 text-white px-6 py-4 
                      rounded-none border border-red-500/50">
          {error}
        </div>
      )}

      {/* OpenSearch Panel (for image search) */}
      {activeTab === 'image' && opensearchResults.length > 0 && (
        <OpenSearchPanel
          results={opensearchResults}
          isOpen={showOpenSearchPanel}
          onToggle={() => setShowOpenSearchPanel(!showOpenSearchPanel)}
        />
      )}
    </div>
  )
}

function App() {
  return (
    <CoveoProvider>
      <AppContent />
    </CoveoProvider>
  )
}

export default App
