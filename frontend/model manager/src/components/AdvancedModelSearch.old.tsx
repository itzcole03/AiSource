import * as React from 'react';
import { useState, useEffect, useCallback, useMemo } from 'react';
import { Search, X, RefreshCw, Play, Trash2 } from 'lucide-react';

// Types
interface Model {
  id: string;
  name: string;
  provider: string;
  size?: number;
  format?: string;
  lastUsed?: string;
  isRunning?: boolean;
  status?: 'running' | 'stopped' | 'error';
}

// Loading spinner component
const LoadingSpinner = ({ size = 4 }: { size?: number }) => (
  <div className="flex items-center justify-center p-8">
    <div 
      className={`animate-spin rounded-full h-${size} w-${size} border-b-2 border-blue-500`}
      role="status"
      aria-label="Loading..."
    >
      <span className="sr-only">Loading...</span>
    </div>
  </div>
);

// Empty state component
const EmptyState = ({ message = 'No models found' }: { message?: string }) => (
  <div className="text-center p-8 text-gray-500">
    <p>{message}</p>
  </div>
);

// Custom hook for debouncing
const useDebounce = <T,>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

interface SearchFilters {
  provider: string;
  minSize: string;
  maxSize: string;
  format: string[];
  sizeRange: [number, number];
  sortBy: 'name' | 'size' | 'lastUsed';
  sortOrder: 'asc' | 'desc';
}

interface AdvancedModelSearchProps {
  models: Model[];
  onFilteredModels: (models: Model[]) => void;
  onModelAction: (action: 'start' | 'stop' | 'delete', model: Model) => Promise<void>;
  onRefresh: () => Promise<void>;
  className?: string;
  loadingModelId?: string | null;
  isLoading?: boolean;
  settings?: {
    autoRefresh: boolean;
    refreshInterval: number;
    onSettingsChange?: (updates: { [key: string]: any }) => Promise<boolean>;
  };
}

export const AdvancedModelSearch: React.FC<AdvancedModelSearchProps> = ({
  models = [],
  onFilteredModels,
  onModelAction,
  onRefresh,
  className = '',
  loadingModelId = null,
  isLoading = false,
  settings = {
    autoRefresh: true,
    refreshInterval: 30,
  }
}) => {
  // State for search and filters
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    provider: '',
    minSize: '',
    maxSize: '',
    format: [],
    sizeRange: [0, 100],
    sortBy: 'name',
    sortOrder: 'asc'
  });
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Debounce search term
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Extract unique formats and providers
  const { availableFormats, availableProviders } = useMemo(() => {
    const formats = new Set<string>();
    const providers = new Set<string>();
    
    models.forEach(model => {
      if (model.format) formats.add(model.format);
      providers.add(model.provider);
    });

    return {
      availableFormats: Array.from(formats),
      availableProviders: Array.from(providers)
    };
  }, [models]);

  // Filter and sort models based on current filters and search term
  const filteredAndSortedModels = useMemo(() => {
    let result = [...models];

    // Apply search term filter
    if (debouncedSearchTerm) {
      const term = debouncedSearchTerm.toLowerCase();
      result = result.filter(model => 
        model.name.toLowerCase().includes(term) ||
        model.provider.toLowerCase().includes(term) ||
        (model.format && model.format.toLowerCase().includes(term))
      );
    }

    // Apply provider filter
    if (filters.provider) {
      result = result.filter(model => model.provider === filters.provider);
    }

    // Apply size filters
    if (filters.minSize) {
      const minSize = parseFloat(filters.minSize);
      result = result.filter(model => {
        const size = parseFloat(model.size || '0');
        return size >= minSize;
      });
    }

    if (filters.maxSize) {
      const maxSize = parseFloat(filters.maxSize);
      result = result.filter(model => {
        const size = parseFloat(model.size || '0');
        return size <= maxSize;
      });
    }

    // Filter by size range
    result = result.filter(model => {
      const modelSize = Number(model.size) || 0;
      const [minSize, maxSize] = filters.sizeRange;
      return modelSize >= minSize && modelSize <= maxSize;
    });

    // Sort models
    result = result.sort((a, b) => {
      let comparison = 0;
      
      switch (filters.sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'size': {
          const sizeA = Number(a.size) || 0;
          const sizeB = Number(b.size) || 0;
          comparison = sizeA - sizeB;
          break;
        }
        case 'lastUsed': {
          const aDate = a.lastUsed ? new Date(a.lastUsed).getTime() : 0;
          const bDate = b.lastUsed ? new Date(b.lastUsed).getTime() : 0;
          comparison = aDate - bDate;
          break;
        }
      }
      
      return filters.sortOrder === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [models, debouncedSearchTerm, filters]);

  // Notify parent of filtered results
  useEffect(() => {
    onFilteredModels(filteredAndSortedModels);
  }, [filteredAndSortedModels, onFilteredModels]);

  // Model action handler
  const handleModelAction = useCallback(async (action: 'start' | 'stop' | 'delete', model: Model) => {
    try {
      await onModelAction(action, model);
    } catch (error) {
      console.error(`Failed to ${action} model:`, error);
    }
  }, [onModelAction]);

  // Refresh handler
  const handleRefresh = useCallback(async () => {
    try {
      await onRefresh();
    } catch (error) {
      console.error('Failed to refresh models:', error);
    }
  }, [onRefresh]);

  // Size range change handler
  const handleSizeRangeChange = useCallback((values: readonly number[]) => {
    setFilters(prev => ({
      ...prev,
      sizeRange: [values[0], values[1]] as [number, number],
      minSize: values[0].toString(),
      maxSize: values[1].toString()
    }));
  }, []);

  // Filter change handler
  const handleFilterChange = useCallback((key: keyof SearchFilters, value: SearchFilters[keyof SearchFilters]) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  // Toggle format filter
  const toggleFormat = useCallback((format: string, checked: boolean) => {
    setFilters(prev => ({
      ...prev,
      format: checked 
        ? [...prev.format, format]
        : prev.format.filter(f => f !== format)
    }));
  }, []);

  // Update size range
  const updateSizeRange = useCallback((index: number, value: number) => {
    const newRange = [...filters.sizeRange] as [number, number];
    newRange[index] = value;
    setFilters(prev => ({
      ...prev,
      sizeRange: newRange,
      minSize: newRange[0].toString(),
      maxSize: newRange[1].toString()
    }));
  }, [filters]);

  // Change sort field
  const changeSortField = useCallback((field: 'name' | 'size' | 'lastUsed') => {
    setFilters(prev => ({
      ...prev,
      sortBy: field,
      sortOrder: prev.sortBy === field && prev.sortOrder === 'asc' ? 'desc' : 'asc'
    }));
  }, []);

  // Toggle sort order
  const toggleSortOrder = useCallback(() => {
    setFilters(prev => ({
      ...prev,
      sortOrder: prev.sortOrder === 'asc' ? 'desc' : 'asc'
    }));
  }, []);

  // Clear all filters
  const clearFilters = useCallback(() => {
    setSearchTerm('');
    setFilters({
      provider: '',
      minSize: '',
      maxSize: '',
      format: [],
      sizeRange: [0, 100],
      sortBy: 'name',
      sortOrder: 'asc'
    });
  }, []);

  // Count active filters
  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (searchTerm) count++;
    if (filters.provider) count++;
    if (filters.minSize) count++;
    if (filters.maxSize) count++;
    if (filters.format.length > 0) count += filters.format.length;
    if (filters.sizeRange[0] > 0 || filters.sizeRange[1] < 100) count++;
    if (filters.sortBy !== 'name' || filters.sortOrder !== 'asc') count++;
    return count;
  }, [searchTerm, filters]);

  // Show loading spinner if models are loading
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size={8} />
      </div>
    );
  }

  // Show empty state if no models are available
  if (models.length === 0) {
    return <EmptyState message="No models found. Try refreshing the list." />;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Search and Filters */}
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search models..."
            className="w-full rounded-lg border border-gray-200 bg-white py-2 pl-10 pr-4 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            aria-label="Search models"
          />
        </div>

        {/* Quick Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Provider Filter */}
          <select
            className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={filters.provider}
            onChange={(e) => handleFilterChange('provider', e.target.value)}
            aria-label="Filter by provider"
          >
            <option value="">All Providers</option>
            {availableProviders.map(provider => (
              <option key={provider} value={provider}>
                {provider}
              </option>
            ))}
          </select>

          {/* Min Size Filter */}
          <input
            type="number"
            placeholder="Min Size (MB)"
            className="w-32 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={filters.minSize}
            onChange={(e) => handleFilterChange('minSize', e.target.value)}
            aria-label="Minimum model size in MB"
            min="0"
          />

          {/* Max Size Filter */}
          <input
            type="number"
            placeholder="Max Size (MB)"
            className="w-32 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={filters.maxSize}
            onChange={(e) => handleFilterChange('maxSize', e.target.value)}
            aria-label="Maximum model size in MB"
            min={filters.minSize || '0'}
          />

          {/* Sort Controls */}
          <div className="flex items-center space-x-2 ml-auto">
            <span className="text-sm text-gray-600">Sort by:</span>
            <select
              className="rounded-lg border border-gray-200 bg-white px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              value={filters.sortBy}
              onChange={(e) => changeSortField(e.target.value as 'name' | 'size' | 'lastUsed')}
              aria-label="Sort by"
            >
              <option value="name">Name</option>
              <option value="size">Size</option>
              <option value="lastUsed">Last Used</option>
            </select>
            <button
              onClick={toggleSortOrder}
              className="p-1 rounded hover:bg-gray-100"
              aria-label={`Sort ${filters.sortOrder === 'asc' ? 'descending' : 'ascending'}`}
            >
              {filters.sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>

          {/* Clear Filters Button */}
          {activeFiltersCount > 0 && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-1 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
              aria-label="Clear all filters"
            >
              <X className="w-3 h-3" />
              <span>Clear Filters ({activeFiltersCount})</span>
            </button>
          )}

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="ml-auto p-2 text-gray-600 hover:text-gray-900 disabled:opacity-50"
            aria-label="Refresh models"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Advanced Filters */}
      <div className="border-t border-gray-200 pt-4 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Format Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Format</label>
            <div className="space-y-1">
              {availableFormats.map(format => (
                <label key={format} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.format.includes(format)}
                    onChange={(e) => toggleFormat(format, e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    aria-label={`Filter by ${format} format`}
                  />
                  <span className="ml-2 text-sm text-gray-700">{format}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Size Range Slider */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Size Range (GB): {filters.sizeRange[0]} - {filters.sizeRange[1]}
            </label>
            <div className="space-y-2">
              <input
                type="range"
                min="0"
                max="100"
                value={filters.sizeRange[0]}
                onChange={(e) => updateSizeRange(0, parseInt(e.target.value))}
                className="w-full"
                aria-label="Minimum size in GB"
              />
              <input
                type="range"
                min="0"
                max="100"
                value={filters.sizeRange[1]}
                onChange={(e) => updateSizeRange(1, parseInt(e.target.value))}
                className="w-full"
                aria-label="Maximum size in GB"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Results Header */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          Showing {filteredAndSortedModels.length} of {models.length} models
        </div>
        
        <div className="flex items-center justify-between w-full">
          {/* Auto-refresh Toggle */}
          {settings.onSettingsChange && (
            <label className="flex items-center space-x-2 text-sm text-gray-600">
              <span>Auto-refresh:</span>
              <input
                type="checkbox"
                checked={settings.autoRefresh}
                onChange={async (e) => {
                  await settings.onSettingsChange?.({ autoRefresh: e.target.checked });
                }}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                aria-label="Auto-refresh models"
              />
            </label>
          )}

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:opacity-50"
            aria-label="Refresh models"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Advanced Filters */}
      <div className="border-t border-gray-200 pt-4 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Format Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Format</label>
            <div className="space-y-1">
              {availableFormats.map(format => (
                <label key={format} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.format.includes(format)}
                    onChange={(e) => toggleFormat(format, e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    aria-label={`Filter by ${format} format`}
                  />
                  <span className="ml-2 text-sm text-gray-700">{format}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Size Range Slider */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Size Range (GB): {filters.sizeRange[0]} - {filters.sizeRange[1]}
            </label>
            <div className="space-y-2">
              <input
                type="range"
                min="0"
                max="100"
                value={filters.sizeRange[0]}
                onChange={(e) => updateSizeRange(0, parseInt(e.target.value))}
                className="w-full"
                aria-label="Minimum size in GB"
              />
              <input
                type="range"
                min="0"
                max="100"
                value={filters.sizeRange[1]}
                onChange={(e) => updateSizeRange(1, parseInt(e.target.value))}
                className="w-full"
                aria-label="Maximum size in GB"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Results Header */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          Showing {filteredAndSortedModels.length} of {models.length} models
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Auto-refresh Toggle */}
          {settings.onSettingsChange && (
            <label className="flex items-center space-x-2 text-sm text-gray-600">
              <span>Auto-refresh:</span>
              <input
                type="checkbox"
                checked={settings.autoRefresh}
                onChange={async (e) => {
                  await settings.onSettingsChange?.({ autoRefresh: e.target.checked });
                }}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                aria-label="Auto-refresh models"
              />
            </label>
          )}

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:opacity-50"
            aria-label="Refresh models"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Model List */}
      <div className="space-y-2">
        {filteredAndSortedModels.length > 0 ? (
          filteredAndSortedModels.map((model) => (
            <div
              key={model.id}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-gray-900 truncate">{model.name}</h3>
                <div className="flex items-center mt-1 text-xs text-gray-500">
                  <span className="mr-2">{model.provider}</span>
                  {model.format && (
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full">
                      {model.format}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {model.status === 'running' ? (
                  <button
                    onClick={() => onModelAction('stop', model)}
                    disabled={loadingModelId === model.id}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-full disabled:opacity-50"
                    title="Stop model"
                  >
                    <X className="w-5 h-5" />
                  </button>
                ) : (
                  <button
                    onClick={() => onModelAction('start', model)}
                    disabled={loadingModelId === model.id}
                    className="p-2 text-green-600 hover:bg-green-50 rounded-full disabled:opacity-50"
                    title="Start model"
                  >
                    <Play className="w-5 h-5" />
                  </button>
                )}
                <button
                  onClick={() => onModelAction('delete', model)}
                  disabled={loadingModelId === model.id}
                  className="p-2 text-gray-500 hover:bg-gray-100 rounded-full disabled:opacity-50"
                  title="Delete model"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <EmptyState message="No models match your search criteria" />
        )}
      </div>
    </div>
  );
};
