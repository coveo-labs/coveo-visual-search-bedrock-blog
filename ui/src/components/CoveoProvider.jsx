/**
 * Coveo Provider Component
 * 
 * Provides Coveo Headless engine context to the application.
 * Initializes the engine and makes it available to all child components.
 */

import { createContext, useContext, useState, useEffect } from 'react';
import { getEngine } from '../lib/coveo-engine';

// Create context for the Coveo engine
const CoveoContext = createContext(null);

/**
 * Hook to access the Coveo engine from context
 */
export function useCoveo() {
  const context = useContext(CoveoContext);
  if (!context) {
    console.warn('useCoveo must be used within a CoveoProvider');
    return { engine: null, isReady: false };
  }
  return context;
}

/**
 * Provider component that initializes and provides the Coveo engine
 */
export function CoveoProvider({ children }) {
  const [engine, setEngine] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    try {
      const eng = getEngine();
      if (eng) {
        setEngine(eng);
        setIsReady(true);
        console.log('Coveo Headless engine initialized');
      } else {
        setError('Failed to initialize Coveo engine. Check API key configuration.');
      }
    } catch (err) {
      console.error('Error initializing Coveo engine:', err);
      setError(err.message);
    }
  }, []);

  // Log analytics status
  useEffect(() => {
    if (engine && isReady) {
      console.log('Coveo Analytics enabled (Coveo UA protocol)');
    }
  }, [engine, isReady]);

  const value = {
    engine,
    isReady,
    error,
  };

  return (
    <CoveoContext.Provider value={value}>
      {children}
    </CoveoContext.Provider>
  );
}

export default CoveoProvider;
