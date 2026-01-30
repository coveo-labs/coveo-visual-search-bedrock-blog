import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'

export default function MetadataExtractor() {
  const [preview, setPreview] = useState(null)
  const [metadata, setMetadata] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleFile = (file) => {
    if (!file || !file.type.startsWith('image/')) {
      setError('Please upload an image file')
      return
    }

    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result)
      setMetadata(null)
      setError(null)
    }
    reader.readAsDataURL(file)
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const extractMetadata = async () => {
    if (!preview || loading) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/extract-metadata`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: preview }),
      })

      if (!response.ok) throw new Error('Extraction failed')

      const data = await response.json()
      setMetadata(data.metadata)
    } catch (err) {
      console.error('Extraction error:', err)
      setError('Failed to extract metadata. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setPreview(null)
    setMetadata(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const copyToClipboard = () => {
    if (metadata) {
      navigator.clipboard.writeText(JSON.stringify(metadata, null, 2))
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-serif text-luxury-gold mb-2 tracking-wider">
          AI Metadata Extraction
        </h2>
        <p className="text-luxury-cream/60 text-sm tracking-wide">
          Upload an image to extract structured metadata using Amazon Bedrock Nova Lite
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <div className="glass-effect rounded-none p-8">
          <h3 className="text-lg font-medium text-luxury-cream mb-6 tracking-wide">
            Upload Image
          </h3>

          {!preview ? (
            <div
              className={`border-2 border-dashed rounded-none p-12 text-center transition-all ${
                dragActive
                  ? 'border-luxury-gold bg-luxury-gold/10'
                  : 'border-luxury-cream/30 hover:border-luxury-gold/50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleChange}
                className="hidden"
                id="metadata-upload"
              />
              
              <label htmlFor="metadata-upload" className="cursor-pointer">
                <div className="w-20 h-20 mx-auto mb-6 bg-luxury-gold/20 rounded-none 
                              flex items-center justify-center">
                  <svg className="w-10 h-10 text-luxury-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                
                <p className="text-luxury-cream mb-2">Drop your image here</p>
                <p className="text-sm text-luxury-cream/50 mb-4">or click to browse</p>
                
                <span className="inline-block px-6 py-3 bg-luxury-gold text-luxury-black 
                               font-medium tracking-wider hover:bg-luxury-gold/90 transition-colors">
                  CHOOSE IMAGE
                </span>
              </label>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="relative rounded-none overflow-hidden border border-luxury-gold/20">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-auto max-h-80 object-contain mx-auto bg-luxury-charcoal"
                />
              </div>
              
              <div className="flex gap-4">
                <button
                  onClick={extractMetadata}
                  disabled={loading}
                  className="flex-1 py-4 bg-luxury-gold text-luxury-black font-medium 
                           tracking-wider hover:bg-luxury-gold/90 transition-colors 
                           disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      EXTRACTING...
                    </span>
                  ) : 'EXTRACT METADATA'}
                </button>
                
                <button
                  onClick={handleClear}
                  disabled={loading}
                  className="px-6 py-4 border border-luxury-gold/30 text-luxury-cream 
                           hover:bg-luxury-gold/10 transition-colors disabled:opacity-50"
                >
                  CLEAR
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-900/30 border border-red-500/50 text-red-200 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        <div className="glass-effect rounded-none p-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-luxury-cream tracking-wide">
              Extracted Metadata
            </h3>
            {metadata && (
              <button
                onClick={copyToClipboard}
                className="text-xs text-luxury-gold hover:text-luxury-gold/80 
                         tracking-wider flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                COPY JSON
              </button>
            )}
          </div>

          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center py-16"
              >
                <div className="w-16 h-16 border-2 border-luxury-gold/30 border-t-luxury-gold 
                              rounded-full animate-spin mb-4" />
                <p className="text-luxury-cream/60 text-sm tracking-wide">
                  Analyzing image with Nova Lite...
                </p>
              </motion.div>
            ) : metadata ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="space-y-4 max-h-[500px] overflow-y-auto"
              >
                {/* Key Fields */}
                <div className="grid grid-cols-2 gap-3">
                  <MetadataField label="Title" value={metadata.title} />
                  <MetadataField label="Category" value={metadata.category} highlight />
                  <MetadataField label="Subcategory" value={metadata.subcategory} />
                  <MetadataField label="Color" value={metadata.color} highlight />
                  <MetadataField label="Material" value={metadata.material} />
                  <MetadataField label="Style" value={metadata.style} />
                  <MetadataField label="Gender" value={metadata.gender} />
                  <MetadataField label="Pattern" value={metadata.pattern} />
                  <MetadataField label="Occasion" value={metadata.occasion} />
                  <MetadataField label="Season" value={metadata.season} />
                </div>

                {/* Description */}
                {metadata.description && (
                  <div className="pt-4 border-t border-luxury-gold/20">
                    <p className="text-xs text-luxury-cream/50 uppercase tracking-wider mb-2">
                      Description
                    </p>
                    <p className="text-sm text-luxury-cream/80 leading-relaxed">
                      {metadata.description}
                    </p>
                  </div>
                )}

                {/* Arrays */}
                {metadata.features && metadata.features.length > 0 && (
                  <MetadataArray label="Features" items={metadata.features} />
                )}
                {metadata.tags && metadata.tags.length > 0 && (
                  <MetadataArray label="Search Tags" items={metadata.tags} />
                )}
                {metadata.quality_indicators && metadata.quality_indicators.length > 0 && (
                  <MetadataArray label="Quality Indicators" items={metadata.quality_indicators} />
                )}

                {/* Price Range */}
                {metadata.estimated_price_range && (
                  <div className="pt-4 border-t border-luxury-gold/20">
                    <p className="text-xs text-luxury-cream/50 uppercase tracking-wider mb-2">
                      Estimated Price Range
                    </p>
                    <p className="text-luxury-gold font-medium">
                      {metadata.estimated_price_range}
                    </p>
                  </div>
                )}

                {/* Raw JSON Toggle */}
                <details className="pt-4 border-t border-luxury-gold/20">
                  <summary className="text-xs text-luxury-cream/50 uppercase tracking-wider 
                                    cursor-pointer hover:text-luxury-gold">
                    View Raw JSON
                  </summary>
                  <pre className="mt-3 p-4 bg-luxury-black/50 text-xs text-luxury-cream/70 
                                overflow-x-auto rounded-none">
                    {JSON.stringify(metadata, null, 2)}
                  </pre>
                </details>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center py-16 text-center"
              >
                <div className="w-16 h-16 bg-luxury-charcoal/50 rounded-none 
                              flex items-center justify-center mb-4">
                  <svg className="w-8 h-8 text-luxury-gold/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-luxury-cream/50 text-sm">
                  Upload an image and click "Extract Metadata"
                </p>
                <p className="text-luxury-cream/30 text-xs mt-2">
                  Powered by Amazon Bedrock Nova Lite
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

// Helper Components
function MetadataField({ label, value, highlight }) {
  if (!value || value === 'Unknown') return null
  
  return (
    <div className="p-3 bg-luxury-black/30 rounded-none">
      <p className="text-xs text-luxury-cream/50 uppercase tracking-wider mb-1">
        {label}
      </p>
      <p className={`text-sm ${highlight ? 'text-luxury-gold' : 'text-luxury-cream'}`}>
        {value}
      </p>
    </div>
  )
}

function MetadataArray({ label, items }) {
  if (!items || items.length === 0) return null
  
  return (
    <div className="pt-4 border-t border-luxury-gold/20">
      <p className="text-xs text-luxury-cream/50 uppercase tracking-wider mb-2">
        {label}
      </p>
      <div className="flex flex-wrap gap-2">
        {items.map((item, idx) => (
          <span
            key={idx}
            className="px-3 py-1 bg-luxury-gold/10 text-luxury-cream/80 text-xs 
                     border border-luxury-gold/20 rounded-none"
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}
