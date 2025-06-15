import { useState, useCallback, useEffect, useMemo, ChangeEvent, Component, ErrorInfo, ReactNode } from 'react';
import PropTypes from 'prop-types';
import { Model } from '../types';
import { ModelCard } from './ModelCard';
import { useDebounce } from '../hooks/useDebounce';
import { Grid, List } from 'lucide-react';

// Error Boundary Component
class ErrorBoundary extends Component<{ children: ReactNode, fallback?: ReactNode }, { hasError: boolean }> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error in AdvancedModelSearch:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <div className="error-fallback">Something went wrong. Please try again.</div>;
    }
    return this.props.children;
  }
}

// Loading Spinner Component
const LoadingSpinner = ({ size = 24 }: { size?: number }) => (
  <div 
    className={`loading-spinner ${size === 20 ? 'loading-spinner-small' : ''}`}
  />
);

// Extend the Model type to include lastUsed and status
interface ExtendedModel extends Omit<Model, 'lastUsed'|'status'> {
  lastUsed?: Date | string | null;
  status?: Model['status'] | string; // Allow string for backward compatibility
}

interface AdvancedModelSearchProps {
  models: ExtendedModel[];
  onFilteredModels: (filtered: ExtendedModel[]) => void;
  onModelAction: (action: 'start'|'stop'|'delete', model: ExtendedModel) => Promise<void>;
  onRefresh?: () => Promise<void>;
  isLoading?: boolean;
  compactMode?: boolean;
  settings?: {
    autoRefresh?: boolean;
    refreshInterval?: number;
  };
}

interface Filters {
  provider: string;
  minSize: string;
  maxSize: string;
  sizeRange: [number, number];
  sortBy: 'name' | 'size' | 'lastUsed';
  sortOrder: 'asc' | 'desc';
}

const DEFAULT_FILTERS: Filters = {
  provider: '',
  minSize: '0',
  maxSize: '100',
  sizeRange: [0, 100],
  sortBy: 'name',
  sortOrder: 'asc'
};

// Type for model actions
type ModelAction = 'start' | 'stop' | 'delete';

// Prop Types validation
const advancedModelSearchPropTypes = {
  models: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      provider: PropTypes.string.isRequired,
      size: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      lastUsed: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
      status: PropTypes.string
    })
  ).isRequired,
  onFilteredModels: PropTypes.func,
  onModelAction: PropTypes.func,
  onRefresh: PropTypes.func,
  isLoading: PropTypes.bool,
  settings: PropTypes.shape({
    autoRefresh: PropTypes.bool,
    refreshInterval: PropTypes.number
  })
};

const AdvancedModelSearch = ({
  models = [],
  onFilteredModels,
  onModelAction,
  onRefresh,
  isLoading = false,
  compactMode = false,
  settings = {
    autoRefresh: false,
    refreshInterval: 30
  }
}: AdvancedModelSearchProps) => {
  // State management
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid'); // Default to grid view
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Get unique providers from models
  const providers = useMemo(() => {
    if (!Array.isArray(models)) return [];
    return Array.from(new Set(models.filter(m => m?.provider).map(m => m.provider)));
  }, [models]);

  // Helper function to parse size strings to numbers for comparison
  const parseSize = (sizeStr: string): number => {
    if (!sizeStr) return 0;
    
    // Handle different size formats: "3.5 GB", "1.59GB", "4.87 GB", "gguf", etc.
    const cleanStr = sizeStr.toString().toLowerCase().trim();
    
    // Extract number from the string
    const match = cleanStr.match(/([0-9.]+)\s*(gb|mb|kb)?/);
    if (!match) return 0;
    
    const value = parseFloat(match[1]);
    const unit = match[2] || 'gb'; // Default to GB if no unit specified
    
    // Convert to GB for consistent comparison
    switch (unit) {
      case 'kb':
        return value / (1024 * 1024);
      case 'mb':
        return value / 1024;
      case 'gb':
      default:
        return value;
    }
  };

  // Filter and sort models based on search and filters
  const filteredAndSortedModels = useMemo(() => {
    // Ensure models is a valid array
    if (!Array.isArray(models)) {
      console.warn('AdvancedModelSearch: models prop is not an array:', models);
      return [];
    }
    
    // Filter out any invalid model objects
    let result = models.filter(model => 
      model && 
      typeof model === 'object' && 
      model.name && 
      model.provider
    );

    // Apply search term filter
    if (debouncedSearchTerm) {
      const term = debouncedSearchTerm.toLowerCase();
      result = result.filter(model => 
        model.name?.toLowerCase().includes(term) ||
        model.provider?.toLowerCase().includes(term)
      );
    }

    // Apply provider filter
    if (filters.provider) {
      result = result.filter(model => model.provider === filters.provider);
    }

    // Apply size range filter
    const minSize = Number(filters.minSize) || 0;
    const maxSize = Number(filters.maxSize) || 100;

    result = result.filter(model => {
      const modelSize = parseSize(model.size || '0');
      return modelSize >= minSize && modelSize <= maxSize;
    });

    // Apply sorting
    result.sort((a, b) => {
      let comparison = 0;
      let aDate: number;
      let bDate: number;

      switch (filters.sortBy) {
        case 'name': {
          const aName = a?.name || '';
          const bName = b?.name || '';
          comparison = aName.localeCompare(bName);
          break;
        }
        case 'size': {
          const aSize = a?.size || '0';
          const bSize = b?.size || '0';
          comparison = parseSize(aSize) - parseSize(bSize);
          break;
        }
        case 'lastUsed':
          aDate = a?.lastUsed ? new Date(a.lastUsed).getTime() : 0;
          bDate = b?.lastUsed ? new Date(b.lastUsed).getTime() : 0;
          comparison = aDate - bDate;
          break;
      }

      return filters.sortOrder === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [models, debouncedSearchTerm, filters]);

  // Notify parent of filtered models
  useEffect(() => {
    if (onFilteredModels) {
      onFilteredModels(filteredAndSortedModels);
    }
  }, [filteredAndSortedModels, onFilteredModels]);

  // Event handlers
  const handleSearchChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  }, []);

  const handleProviderChange = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
    setFilters(prev => ({ ...prev, provider: e.target.value }));
  }, []);

  const handleSortByChange = useCallback((e: ChangeEvent<HTMLSelectElement>) => {
    setFilters(prev => ({ ...prev, sortBy: e.target.value as 'name' | 'size' | 'lastUsed' }));
  }, []);

  const handleRangeChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFilters(prev => ({
      ...prev,
      maxSize: value,
      sizeRange: [Number(prev.minSize), Number(value)]
    }));
  }, []);

  const handleMinRangeChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFilters(prev => ({
      ...prev,
      minSize: value,
      sizeRange: [Number(value), Number(prev.maxSize)]
    }));
  }, []);

  const toggleSortOrder = useCallback(() => {
    setFilters(prev => ({
      ...prev,
      sortOrder: prev.sortOrder === 'asc' ? 'desc' : 'asc'
    }));
  }, []);

  const [actionState, setActionState] = useState<{
    [key: string]: { loading: boolean; error: string | null }
  }>({});

  const handleModelAction = useCallback(async (action: ModelAction, model: ExtendedModel) => {
    if (!onModelAction) return;
    
    setActionState(prev => ({
      ...prev,
      [model.id]: { loading: true, error: null }
    }));

    try {
      await onModelAction(action, model);
      setActionState(prev => ({
        ...prev,
        [model.id]: { loading: false, error: null }
      }));
    } catch (error) {
      console.error(`Failed to ${action} model:`, error);
      setActionState(prev => ({
        ...prev,
        [model.id]: { 
          loading: false, 
          error: `Failed to ${action} model: ${error instanceof Error ? error.message : 'Unknown error'}`
        }
      }));
      
      // Clear error after 5 seconds
      setTimeout(() => {
        setActionState(prev => {
          const newState = { ...prev };
          delete newState[model.id];
          return newState;
        });
      }, 5000);
    }
  }, [onModelAction]);

  const handleRefresh = useCallback(async () => {
    if (isLoading || !onRefresh) return;
    try {
      await onRefresh();
    } catch (error) {
      console.error('Failed to refresh models:', error);
    }
  }, [isLoading, onRefresh]);

  const clearFilters = useCallback(() => {
    setSearchTerm('');
    setFilters(DEFAULT_FILTERS);
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    if (!settings.autoRefresh || !settings.refreshInterval) return;

    const interval = setInterval(() => {
      handleRefresh();
    }, (settings.refreshInterval || 30) * 1000);

    return () => clearInterval(interval);
  }, [handleRefresh, settings.autoRefresh, settings.refreshInterval]);



  // Add loading state for the entire component
  if (isLoading) {
    return (
      <div className="loading-overlay">
        <LoadingSpinner size={48} />
        <p>Loading models...</p>
      </div>
    );
  }

  // Add error boundary around the entire component
  return (
    <ErrorBoundary fallback={
      <div className="error-boundary">
        <h3>Something went wrong</h3>
        <p>Please refresh the page or try again later.</p>
        <button onClick={() => window.location.reload()} className="retry-button">
          Retry
        </button>
      </div>
    }>
      <div className={`advanced-model-search ${compactMode ? 'compact' : ''}`}>
        {/* Compact mode header */}
        {compactMode && (
          <div className="search-header">
            <div className="search-title">Model Search</div>
            <div className="model-count">
              {filteredAndSortedModels.length} models
            </div>
          </div>
        )}

      {/* Search and filter controls */}
      <div className={`search-controls ${compactMode ? 'compact' : ''}`}>
        <label htmlFor="search-input" className="sr-only">Search models</label>
        <input
          id="search-input"
          type="search"
          placeholder={compactMode ? "Search..." : "Search models..."}
          value={searchTerm}
          onChange={handleSearchChange}
          className="search-input"
          aria-label="Search models"
        />
        
        <label htmlFor="provider-select" className="sr-only">Filter by provider</label>
        <select
          id="provider-select"
          value={filters.provider}
          onChange={handleProviderChange}
          className="provider-select"
          aria-label="Filter by provider"
        >
          <option value="">All Providers</option>
          {providers.map(provider => (
            <option key={provider} value={provider}>
              {provider}
            </option>
          ))}
        </select>

        {compactMode ? (
          <>
            <div className="controls-row">
              <div className="compact-sort-controls">
                <select
                  value={filters.sortBy}
                  onChange={handleSortByChange}
                  className="compact-sort-select"
                  aria-label="Sort models by"
                >
                  <option value="name">Name</option>
                  <option value="size">Size</option>
                  <option value="lastUsed">Last Used</option>
                </select>
                <button 
                  type="button" 
                  onClick={toggleSortOrder}
                  className="compact-sort-order"
                  aria-label={`Sort ${filters.sortOrder === 'asc' ? 'descending' : 'ascending'}`}
                  title={`Sort ${filters.sortOrder === 'asc' ? 'A-Z' : 'Z-A'}`}
                >
                  {filters.sortOrder === 'asc' ? '↑' : '↓'}
                </button>
              </div>
              
              {/* View Mode Toggle */}
              <div className="view-toggle">
                <button
                  type="button"
                  onClick={() => setViewMode('grid')}
                  className={`view-toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
                  title="Card View"
                  aria-label="Switch to card view"
                >
                  <Grid className="w-3 h-3" />
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('list')}
                  className={`view-toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
                  title="List View"
                  aria-label="Switch to list view"
                >
                  <List className="w-3 h-3" />
                </button>
              </div>
            </div>
            
            <div className="controls-row">
              <button 
                type="button" 
                onClick={clearFilters}
                className="clear-filters compact"
                disabled={!searchTerm && !filters.provider && filters.sizeRange[0] === 0 && filters.sizeRange[1] === 100}
                aria-label="Clear all filters"
              >
                Clear
              </button>
              
              <button 
                type="button" 
                onClick={handleRefresh}
                className="refresh-button compact"
                aria-label="Refresh models"
                disabled={isLoading}
                title="Refresh Models"
              >
                {isLoading ? '⟳' : '↻'}
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Size range filter */}
            <div className="size-range">
              <label htmlFor="min-size">Min Size (MB):</label>
              <input
                id="min-size"
                type="number"
                min="0"
                max={filters.sizeRange[1]}
                value={filters.minSize}
                onChange={handleMinRangeChange}
                aria-label="Minimum model size"
              />
              
              <label htmlFor="max-size">Max Size (MB):</label>
              <input
                id="max-size"
                type="number"
                min={filters.sizeRange[0]}
                max="100"
                value={filters.maxSize}
                onChange={handleRangeChange}
                aria-label="Maximum model size"
              />
            </div>

            {/* Sort controls */}
            <div className="sort-controls">
              <label htmlFor="sort-by">Sort by:</label>
              <select
                id="sort-by"
                value={filters.sortBy}
                onChange={handleSortByChange}
                aria-label="Sort models by"
              >
                <option value="name">Name</option>
                <option value="size">Size</option>
                <option value="lastUsed">Last Used</option>
              </select>
              
              <button 
                type="button" 
                onClick={toggleSortOrder}
                className="sort-order-button"
                aria-label={`Sort ${filters.sortOrder === 'asc' ? 'descending' : 'ascending'}`}
              >
                {filters.sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>

            <div className="flex items-center gap-2">
              <button 
                type="button" 
                onClick={clearFilters}
                className="clear-filters"
                disabled={!searchTerm && !filters.provider && filters.sizeRange[0] === 0 && filters.sizeRange[1] === 100}
                aria-label="Clear all filters"
              >
                Clear
              </button>

              {/* View Mode Toggle */}
              <div className="view-toggle">
                <button
                  type="button"
                  onClick={() => setViewMode('grid')}
                  className={`view-toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
                  title="Card View"
                  aria-label="Switch to card view"
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('list')}
                  className={`view-toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
                  title="List View"
                  aria-label="Switch to list view"
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Model display */}
      <div className={`model-display ${viewMode} ${compactMode ? 'compact' : ''}`} role="list">
        {filteredAndSortedModels.length > 0 ? (
          viewMode === 'grid' ? (
            <div className={`grid gap-3 ${
              compactMode 
                ? 'grid-cols-1' 
                : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
            }`}>
              {filteredAndSortedModels.map(model => (
                <ModelCard
                  key={model.id}
                  model={{
                    ...model,
                    status: model.status as Model['status'] || 'available',
                    lastUsed: model.lastUsed ? new Date(model.lastUsed) : undefined
                  }}
                  onStart={() => handleModelAction('start', model)}
                  onStop={() => handleModelAction('stop', model)}
                  compactView={compactMode}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-2">
              {filteredAndSortedModels.map(model => (
                <div key={model.id} className={`flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors ${compactMode ? 'text-sm' : ''}`} role="listitem">
                  <div className="flex items-center space-x-2 min-w-0 flex-1">
                    <div className={`${compactMode ? 'w-2 h-2' : 'w-3 h-3'} rounded-full ${
                      model.status === 'running' ? 'bg-green-500' :
                      model.status === 'loading' ? 'bg-blue-500 animate-pulse' :
                      model.status === 'error' ? 'bg-red-500' : 'bg-gray-400'
                    }`} />
                    <div className="min-w-0 flex-1">
                      <div className={`font-medium text-gray-900 dark:text-white truncate ${compactMode ? 'text-xs' : 'text-sm'}`}>
                        {model.name}
                      </div>
                      {!compactMode && (
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {model.provider} • {model.size} MB
                          {model.lastUsed && (
                            <> • {new Date(model.lastUsed).toLocaleDateString()}</>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    {actionState[model.id]?.loading ? (
                      <div className="action-loading">
                        <LoadingSpinner size={compactMode ? 16 : 20} />
                      </div>
                    ) : (
                      <>
                        <button 
                          type="button"
                          onClick={() => handleModelAction('start', model)}
                          disabled={model.status === 'running' || actionState[model.id]?.loading}
                          className={`${compactMode ? 'px-2 py-1 text-xs' : 'px-3 py-1 text-xs'} bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 transition-colors`}
                          aria-label={`Start ${model.name}`}
                        >
                          {compactMode ? '▶' : 'Start'}
                        </button>
                        <button 
                          type="button"
                          onClick={() => handleModelAction('stop', model)}
                          disabled={model.status !== 'running'}
                          className={`${compactMode ? 'px-2 py-1 text-xs' : 'px-3 py-1 text-xs'} bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50 transition-colors`}
                          aria-label={`Stop ${model.name}`}
                        >
                          {compactMode ? '⏹' : 'Stop'}
                        </button>
                        {!compactMode && (
                          <button 
                            type="button"
                            onClick={() => handleModelAction('delete', model)}
                            className="px-3 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600 transition-colors"
                            aria-label={`Delete ${model.name}`}
                          >
                            Delete
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )
        ) : (
          <div className="no-results">
            No models found matching your criteria.
          </div>
        )}
      </div>

      {/* Refresh button */}
      {!compactMode && (
        <div className="refresh-controls">
          <button 
            type="button" 
            onClick={handleRefresh}
            className="refresh-button"
            aria-label="Refresh models"
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing...' : 'Refresh Models'}
          </button>
        </div>
      )}
      </div>
    </ErrorBoundary>
  );
};

// Add prop types to the component
AdvancedModelSearch.propTypes = advancedModelSearchPropTypes;

// Add display name for better debugging
AdvancedModelSearch.displayName = 'AdvancedModelSearch';

export default AdvancedModelSearch;

// CSS has been moved to AdvancedModelSearch.css

// Import CSS file
import './AdvancedModelSearch.css';
