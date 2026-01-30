import { useState, useCallback } from 'react'
import Header from './components/Header'
import ImageUpload from './components/ImageUpload'
import FacetSidebar from './components/FacetSidebar'
import ProductGrid from './components/ProductGrid'
import OpenSearchPanel from './components/OpenSearchPanel'
import MetadataExtractor from './components/MetadataExtractor'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'

function App() {
  const [results, setResults] = useState([])
  const [opensearchResults, setOpensearchResults] = useState([])
  const [facets, setFacets] = useState({})
  const [selectedFacets, setSelectedFacets] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('text') // 'text', 'image', 'metadata'
  const [showOpenSearchPanel, setShowOpenSearchPanel] = useState(false)
  const [lastQuery, setLastQuery] = useState('')

  // Text search using Coveo
  const handleTextSearch = useCallback(async (query) => {
    setLoading(true)
    setError(null)
    setLastQuery(query)
    setActiveTab('text')
    setOpensearchResults([])
    
    try {
      const response = await fetch(`${API_URL}/text-search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query,
          facets: selectedFacets 
        }),
      })
      
      if (!response.ok) throw new Error('Search failed')
      
      const data = await response.json()
      setResults(data.results || [])
      setFacets(data.facets || {})
    } catch (err) {
      console.error('Search error:', err)
      // Fallback to direct Coveo search
      await searchCoveoDirect(query)
    } finally {
      setLoading(false)
    }
  }, [selectedFacets])

  // Direct Coveo search (fallback)
  const searchCoveoDirect = async (query) => {
    try {
      const orgId = 'kranthipoccoveoorg3fs5k79o'
      const apiKey = import.meta.env.VITE_COVEO_API_KEY
      
      // Build facet query
      let aq = ''
      Object.entries(selectedFacets).forEach(([field, values]) => {
        if (values && values.length > 0) {
          const facetQuery = values.map(v => `@${field}=="${v}"`).join(' OR ')
          aq += aq ? ` AND (${facetQuery})` : `(${facetQuery})`
        }
      })
      
      const response = await fetch(`https://${orgId}.org.coveo.com/rest/search/v2`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          q: query,
          aq: aq || undefined,
          numberOfResults: 50,
          groupBy: [
            { field: '@category', maximumNumberOfValues: 10 },
            { field: '@subcategory', maximumNumberOfValues: 10 },
            { field: '@color', maximumNumberOfValues: 15 },
            { field: '@pricerange', maximumNumberOfValues: 6 },
            { field: '@gender', maximumNumberOfValues: 5 },
            { field: '@style', maximumNumberOfValues: 10 },
            { field: '@material', maximumNumberOfValues: 10 },
            { field: '@size', maximumNumberOfValues: 10 },
          ],
        }),
      })
      
      if (!response.ok) throw new Error('Coveo search failed')
      
      const data = await response.json()
      setResults(data.results || [])
      
      // Extract facets from groupBy results
      const extractedFacets = {}
      if (data.groupByResults) {
        data.groupByResults.forEach(group => {
          const fieldName = group.field.replace('@', '')
          extractedFacets[fieldName] = group.values.map(v => ({
            value: v.value,
            count: v.numberOfResults
          }))
        })
      }
      setFacets(extractedFacets)
    } catch (err) {
      console.error('Coveo direct search error:', err)
      setError('Search failed. Please try again.')
    }
  }

  // Image search using OpenSearch + Coveo
  const handleImageSearch = useCallback(async (imageData) => {
    setLoading(true)
    setError(null)
    setActiveTab('image')
    setShowOpenSearchPanel(true)
    
    try {
      const response = await fetch(`${API_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          image: imageData,
          min_score: 0.5 // Minimum similarity threshold
        }),
      })
      
      if (!response.ok) throw new Error('Image search failed')
      
      const data = await response.json()
      setResults(data.results || [])
      setOpensearchResults(data.opensearch_results || [])
      
      // Extract facets from results
      const extractedFacets = extractFacetsFromResults(data.results || [])
      setFacets(extractedFacets)
    } catch (err) {
      console.error('Image search error:', err)
      setError('Image search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  // Extract facets from results
  const extractFacetsFromResults = (results) => {
    const facetData = {
      category: {},
      subcategory: {},
      color: {},
      pricerange: {},
      gender: {},
      style: {},
      material: {},
    }
    
    results.forEach(result => {
      const raw = result.raw || {}
      Object.keys(facetData).forEach(field => {
        const value = raw[field]
        if (value) {
          facetData[field][value] = (facetData[field][value] || 0) + 1
        }
      })
    })
    
    // Convert to array format
    const facets = {}
    Object.entries(facetData).forEach(([field, values]) => {
      facets[field] = Object.entries(values)
        .map(([value, count]) => ({ value, count }))
        .sort((a, b) => b.count - a.count)
    })
    
    return facets
  }

  // Handle facet changes
  const handleFacetChange = useCallback((facetName, values) => {
    setSelectedFacets(prev => ({
      ...prev,
      [facetName]: values
    }))
  }, [])

  // Filter results by selected facets (client-side for image search)
  const filteredResults = results.filter(result => {
    const raw = result.raw || {}
    
    for (const [field, values] of Object.entries(selectedFacets)) {
      if (values && values.length > 0) {
        const resultValue = raw[field]
        if (!resultValue || !values.includes(resultValue)) {
          return false
        }
      }
    }
    
    return true
  })

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
          
          {/* Search Bar with Mode Toggle */}
          <div className="max-w-4xl mx-auto mb-8">
            {/* Tab Toggle */}
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

            {/* Tab Content */}
            {activeTab === 'text' && (
              <form onSubmit={(e) => { e.preventDefault(); handleTextSearch(lastQuery || e.target.query.value) }}>
                <div className="relative">
                  <input
                    type="text"
                    name="query"
                    defaultValue={lastQuery}
                    onChange={(e) => setLastQuery(e.target.value)}
                    placeholder="Search for white shirt full sleeve, black leather shoes..."
                    className="w-full px-6 py-5 bg-luxury-charcoal/50 border border-luxury-gold/30 
                             rounded-none text-luxury-cream placeholder-luxury-cream/40
                             focus:outline-none focus:border-luxury-gold transition-colors
                             text-lg tracking-wide pr-32"
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="absolute right-2 top-1/2 -translate-y-1/2 px-8 py-3
                             bg-luxury-gold text-luxury-black font-medium tracking-wider
                             hover:bg-luxury-gold/90 transition-colors disabled:opacity-50
                             disabled:cursor-not-allowed rounded-none"
                  >
                    {loading ? 'SEARCHING...' : 'SEARCH'}
                  </button>
                </div>
              </form>
            )}
            {activeTab === 'image' && (
              <ImageUpload onSearch={handleImageSearch} loading={loading} />
            )}
          </div>
        </div>
      </section>

      {/* Metadata Extractor Section */}
      {activeTab === 'metadata' && (
        <section className="px-6 pb-24">
          <MetadataExtractor />
        </section>
      )}

      {/* Results Section */}
      {activeTab !== 'metadata' && (results.length > 0 || loading) && (
        <section className="px-6 pb-24">
          <div className="max-w-7xl mx-auto">
            <div className="flex gap-8">
              {/* Facet Sidebar */}
              {Object.keys(facets).length > 0 && (
                <FacetSidebar
                  facets={facets}
                  selectedFacets={selectedFacets}
                  onFacetChange={handleFacetChange}
                />
              )}
              
              {/* Product Grid */}
              <ProductGrid
                results={filteredResults}
                opensearchResults={opensearchResults}
                showOpenSearchPanel={activeTab === 'image'}
              />
            </div>
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

export default App
