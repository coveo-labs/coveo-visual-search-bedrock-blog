/**
 * Headless SearchBox Component
 * 
 * A search box powered by Coveo Headless that:
 * - Provides query suggestions
 * - Automatically logs search events to Coveo Analytics
 * - Supports keyboard navigation
 */

import { useState, useRef, useEffect } from 'react';
import { useSearchBox } from '../hooks/useCoveoSearch';

export default function HeadlessSearchBox({ onSearchComplete }) {
  const {
    value,
    suggestions,
    isLoading,
    isReady,
    updateText,
    submit,
    clear,
    selectSuggestion,
  } = useSearchBox();

  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  // Handle input change
  const handleChange = (e) => {
    updateText(e.target.value);
    setShowSuggestions(true);
    setSelectedIndex(-1);
  };

  // Handle form submit
  const handleSubmit = (e) => {
    e.preventDefault();
    submit();
    setShowSuggestions(false);
    onSearchComplete?.();
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    selectSuggestion(suggestion.rawValue);
    setShowSuggestions(false);
    onSearchComplete?.();
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        if (selectedIndex >= 0) {
          e.preventDefault();
          handleSuggestionClick(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
    }
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(e.target) &&
        !inputRef.current.contains(e.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!isReady) {
    return (
      <div className="relative">
        <input
          type="text"
          disabled
          placeholder="Loading search..."
          className="w-full px-6 py-5 bg-luxury-charcoal/50 border border-luxury-gold/30 
                   rounded-none text-luxury-cream placeholder-luxury-cream/40
                   opacity-50 cursor-not-allowed text-lg tracking-wide"
        />
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowSuggestions(true)}
          placeholder="Search for white shirt, black leather shoes, gold watch..."
          className="w-full px-6 py-5 bg-luxury-charcoal/50 border border-luxury-gold/30 
                   rounded-none text-luxury-cream placeholder-luxury-cream/40
                   focus:outline-none focus:border-luxury-gold transition-colors
                   text-lg tracking-wide pr-32"
          autoComplete="off"
        />
        
        <button
          type="submit"
          disabled={isLoading}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-8 py-3
                   bg-luxury-gold text-luxury-black font-medium tracking-wider
                   hover:bg-luxury-gold/90 transition-colors disabled:opacity-50
                   disabled:cursor-not-allowed rounded-none"
        >
          {isLoading ? 'SEARCHING...' : 'SEARCH'}
        </button>

        {/* Clear button */}
        {value && (
          <button
            type="button"
            onClick={() => {
              clear();
              inputRef.current?.focus();
            }}
            className="absolute right-36 top-1/2 -translate-y-1/2 p-2
                     text-luxury-cream/50 hover:text-luxury-cream transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Query Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-1 bg-luxury-charcoal border border-luxury-gold/30
                   shadow-lg max-h-60 overflow-auto"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={suggestion.rawValue}
              type="button"
              onClick={() => handleSuggestionClick(suggestion)}
              className={`w-full px-6 py-3 text-left text-luxury-cream hover:bg-luxury-gold/10
                       transition-colors flex items-center gap-3 ${
                         index === selectedIndex ? 'bg-luxury-gold/20' : ''
                       }`}
            >
              <svg className="w-4 h-4 text-luxury-gold/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span
                dangerouslySetInnerHTML={{ __html: suggestion.highlightedValue }}
                className="[&>strong]:text-luxury-gold [&>strong]:font-semibold"
              />
            </button>
          ))}
        </div>
      )}
    </form>
  );
}
