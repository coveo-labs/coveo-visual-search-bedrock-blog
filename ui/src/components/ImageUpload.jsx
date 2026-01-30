import { useState, useRef } from 'react'
import { motion } from 'framer-motion'

export default function ImageUpload({ onSearch, loading }) {
  const [preview, setPreview] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleFile = (file) => {
    if (!file || !file.type.startsWith('image/')) {
      alert('Please upload an image file')
      return
    }

    const reader = new FileReader()
    reader.onloadend = () => {
      const base64String = reader.result
      setPreview(base64String)
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
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleSearch = () => {
    if (preview && !loading) {
      onSearch(preview)
    }
  }

  const handleClear = () => {
    setPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="glass-effect rounded-none p-12"
      >
        {!preview ? (
          <div
            className={`border-2 border-dashed rounded-none p-16 text-center transition-all duration-300 ${
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
              id="file-upload"
            />
            
            <label htmlFor="file-upload" className="cursor-pointer">
              <div className="w-24 h-24 mx-auto mb-8 gold-gradient rounded-none flex items-center justify-center">
                <svg className="w-12 h-12 text-luxury-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              
              <p className="text-xl text-luxury-cream mb-3 font-light tracking-wide">
                Drop your image here
              </p>
              <p className="text-sm text-luxury-cream/60 mb-6 tracking-wide">
                or click to browse
              </p>
              
              <span className="inline-block px-8 py-4 gold-gradient rounded-none text-luxury-black font-medium tracking-wider hover:opacity-90 transition-opacity uppercase text-sm">
                Choose Image
              </span>
            </label>
          </div>
        ) : (
          <div className="space-y-8">
            <div className="relative rounded-none overflow-hidden border border-luxury-cream/20">
              <img
                src={preview}
                alt="Preview"
                className="w-full h-auto max-h-96 object-contain mx-auto"
              />
            </div>
            
            <div className="flex gap-6">
              <button
                onClick={handleSearch}
                disabled={loading}
                className="flex-1 py-5 gold-gradient rounded-none text-luxury-black font-medium text-base tracking-wider hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed uppercase"
              >
                {loading ? 'Searching...' : 'Search Similar Items'}
              </button>
              
              <button
                onClick={handleClear}
                disabled={loading}
                className="px-8 py-5 glass-effect rounded-none text-luxury-cream hover:bg-luxury-cream/10 transition-all disabled:opacity-50 disabled:cursor-not-allowed tracking-wider uppercase text-sm"
              >
                Clear
              </button>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
