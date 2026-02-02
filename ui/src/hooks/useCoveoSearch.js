/**
 * React Hooks for Coveo Headless
 * 
 * Custom hooks that wrap Coveo Headless controllers for React components.
 * These hooks handle subscriptions and state updates automatically.
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  getEngine,
  createSearchBox,
  createResultList,
  createFacets,
  createQuerySummary,
  createInteractiveResult,
  logImageSearchEvent,
  logMetadataExtractionEvent,
  logCustomEvent,
} from '../lib/coveo-engine';

/**
 * Hook to access the Coveo engine
 */
export function useCoveoEngine() {
  const [engine, setEngine] = useState(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const eng = getEngine();
    if (eng) {
      setEngine(eng);
      setIsReady(true);
    }
  }, []);

  return { engine, isReady };
}

/**
 * Hook for SearchBox functionality
 * Automatically logs search events
 */
export function useSearchBox() {
  const { engine, isReady } = useCoveoEngine();
  const [state, setState] = useState({
    value: '',
    suggestions: [],
    isLoading: false,
  });

  const controller = useMemo(() => {
    if (!engine) return null;
    return createSearchBox(engine);
  }, [engine]);

  useEffect(() => {
    if (!controller) return;

    const unsubscribe = controller.subscribe(() => {
      setState({
        value: controller.state.value,
        suggestions: controller.state.suggestions,
        isLoading: controller.state.isLoading,
      });
    });

    return unsubscribe;
  }, [controller]);

  const updateText = useCallback((text) => {
    controller?.updateText(text);
  }, [controller]);

  const submit = useCallback(() => {
    controller?.submit();
  }, [controller]);

  const clear = useCallback(() => {
    controller?.clear();
  }, [controller]);

  const selectSuggestion = useCallback((suggestion) => {
    controller?.selectSuggestion(suggestion);
  }, [controller]);

  return {
    ...state,
    isReady,
    updateText,
    submit,
    clear,
    selectSuggestion,
  };
}

/**
 * Hook for ResultList functionality
 */
export function useResultList() {
  const { engine, isReady } = useCoveoEngine();
  const [state, setState] = useState({
    results: [],
    isLoading: false,
    hasResults: false,
    firstSearchExecuted: false,
  });

  const controller = useMemo(() => {
    if (!engine) return null;
    return createResultList(engine);
  }, [engine]);

  useEffect(() => {
    if (!controller) return;

    const unsubscribe = controller.subscribe(() => {
      setState({
        results: controller.state.results,
        isLoading: controller.state.isLoading,
        hasResults: controller.state.hasResults,
        firstSearchExecuted: controller.state.firstSearchExecuted,
      });
    });

    return unsubscribe;
  }, [controller]);

  return {
    ...state,
    isReady,
  };
}

/**
 * Hook for a single interactive result
 * Automatically logs click events
 */
export function useInteractiveResult(result) {
  const { engine } = useCoveoEngine();

  const controller = useMemo(() => {
    if (!engine || !result) return null;
    return createInteractiveResult(engine, result);
  }, [engine, result]);

  const select = useCallback(() => {
    controller?.select();
  }, [controller]);

  const beginDelayedSelect = useCallback(() => {
    controller?.beginDelayedSelect();
  }, [controller]);

  const cancelPendingSelect = useCallback(() => {
    controller?.cancelPendingSelect();
  }, [controller]);

  return {
    select,
    beginDelayedSelect,
    cancelPendingSelect,
  };
}

/**
 * Hook for Facets functionality
 */
export function useFacets() {
  const { engine, isReady } = useCoveoEngine();
  const [facetStates, setFacetStates] = useState({});

  const controllers = useMemo(() => {
    if (!engine) return null;
    return createFacets(engine);
  }, [engine]);

  useEffect(() => {
    if (!controllers) return;

    const unsubscribes = Object.entries(controllers).map(([name, controller]) => {
      return controller.subscribe(() => {
        setFacetStates(prev => ({
          ...prev,
          [name]: {
            values: controller.state.values,
            isLoading: controller.state.isLoading,
            hasActiveValues: controller.state.hasActiveValues,
          },
        }));
      });
    });

    return () => {
      unsubscribes.forEach(unsub => unsub());
    };
  }, [controllers]);

  const toggleSelect = useCallback((facetName, value) => {
    controllers?.[facetName]?.toggleSelect(value);
  }, [controllers]);

  const deselectAll = useCallback((facetName) => {
    controllers?.[facetName]?.deselectAll();
  }, [controllers]);

  return {
    facets: facetStates,
    isReady,
    toggleSelect,
    deselectAll,
  };
}

/**
 * Hook for QuerySummary
 */
export function useQuerySummary() {
  const { engine, isReady } = useCoveoEngine();
  const [state, setState] = useState({
    total: 0,
    query: '',
    durationInSeconds: 0,
    hasQuery: false,
    hasResults: false,
  });

  const controller = useMemo(() => {
    if (!engine) return null;
    return createQuerySummary(engine);
  }, [engine]);

  useEffect(() => {
    if (!controller) return;

    const unsubscribe = controller.subscribe(() => {
      setState({
        total: controller.state.total,
        query: controller.state.query,
        durationInSeconds: controller.state.durationInSeconds,
        hasQuery: controller.state.hasQuery,
        hasResults: controller.state.hasResults,
      });
    });

    return unsubscribe;
  }, [controller]);

  return {
    ...state,
    isReady,
  };
}

/**
 * Hook for logging custom analytics events
 */
export function useAnalytics() {
  const { engine, isReady } = useCoveoEngine();

  const logImageSearch = useCallback((imageSize, matchCount) => {
    if (engine) {
      logImageSearchEvent(engine, imageSize, matchCount);
    }
  }, [engine]);

  const logMetadataExtraction = useCallback((extractedFields) => {
    if (engine) {
      logMetadataExtractionEvent(engine, extractedFields);
    }
  }, [engine]);

  const logCustom = useCallback((eventType, eventValue, customData) => {
    if (engine) {
      logCustomEvent(engine, eventType, eventValue, customData);
    }
  }, [engine]);

  return {
    isReady,
    logImageSearch,
    logMetadataExtraction,
    logCustom,
  };
}

export default {
  useCoveoEngine,
  useSearchBox,
  useResultList,
  useInteractiveResult,
  useFacets,
  useQuerySummary,
  useAnalytics,
};
