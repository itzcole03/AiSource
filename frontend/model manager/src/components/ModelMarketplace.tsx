import React, { useState, useEffect } from 'react';
import { Search, Download, Star, Clock, HardDrive, Tag, ExternalLink, CheckCircle, Filter, SortAsc, X } from 'lucide-react';
import { MarketplaceModel, ModelCategory, Model } from '../types';
import { useDebounce } from '../hooks/useDebounce';

interface ModelMarketplaceProps {
  isOpen: boolean;
  onClose: () => void;
  onInstallModel?: (model: MarketplaceModel) => Promise<void>;
  installedModels: Model[];
}

const ModelMarketplace: React.FC<ModelMarketplaceProps> = ({ 
  isOpen, 
  onClose,
  onInstallModel,
  installedModels = []
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedProvider, setSelectedProvider] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'popularity' | 'size' | 'recent' | 'rating'>('popularity');
  const [models, setModels] = useState<MarketplaceModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [installingModels, setInstallingModels] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [visibleCount, setVisibleCount] = useState(12);
  const [showFilters, setShowFilters] = useState(false);

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Load models when component mounts and when isOpen changes to true
  useEffect(() => {
    if (isOpen) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        loadMarketplaceModels().catch(err => {
          if (!controller.signal.aborted) {
            setError(`Failed to load models: ${err.message}`);
            console.error('Error loading models:', err);
          }
        });
      }, 300); // Small delay to prevent rapid successive calls

      return () => {
        controller.abort();
        clearTimeout(timeoutId);
      };
    }
  }, [isOpen]);

  // Cache for storing fetched models
  const modelsCache = React.useRef<{
    data: MarketplaceModel[];
    timestamp: number;
    isStale: boolean;
  } | null>(null);

  const loadMarketplaceModels = async () => {
    // Skip if already loading
    if (loading) return;
    
    // Check cache first
    const now = Date.now();
    const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
    
    if (modelsCache.current && now - modelsCache.current.timestamp < CACHE_TTL) {
      setModels(modelsCache.current.data);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Add cache-busting parameter
      const response = await fetch(`/api/providers/marketplace/models?_=${now}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch models: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (!data?.models || !Array.isArray(data.models)) {
        throw new Error('Invalid marketplace data format');
      }

      // Process and enhance the models
      const processedModels: MarketplaceModel[] = data.models.map((model: any, index: number) => {
        const baseId = model.id || `${model.provider || 'model'}-${model.name || index}`.toLowerCase().replace(/\s+/g, '-');
        
        return {
          ...model,
          id: baseId,
          provider: model.provider ? model.provider.toLowerCase() : 'unknown',
          category: model.category ? model.category.toLowerCase() : 'other',
          lastUpdated: model.lastUpdated ? new Date(model.lastUpdated) : new Date(),
          downloads: typeof model.downloads === 'string' ? parseInt(model.downloads, 10) : (model.downloads || 0),
          rating: typeof model.rating === 'string' ? parseFloat(model.rating) : (model.rating || 0),
          tags: Array.isArray(model.tags) ? model.tags : [],
          requirements: model.requirements || {},
          isInstalled: installedModels.some(installed => 
            installed.name.toLowerCase() === model.name.toLowerCase() ||
            installed.id.toLowerCase() === baseId.toLowerCase()
          ),
          isOfficial: model.isOfficial || false
        };
      });

      setModels(processedModels);
      // Update cache
      modelsCache.current = {
        data: processedModels,
        timestamp: now,
        isStale: false
      };
    } catch (err) {
      console.error('Marketplace fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load marketplace models');
      
      // Fallback to demo data
      setModels(generateDemoModels());
      // Update cache
      modelsCache.current = {
        data: generateDemoModels(),
        timestamp: now,
        isStale: false
      };
    } finally {
      setLoading(false);
    }
  };

  const generateDemoModels = (): MarketplaceModel[] => {
    return [
      {
        id: 'llama2-7b-chat',
        name: 'Llama 2 7B Chat',
        description: 'A 7 billion parameter language model fine-tuned for chat use cases',
        provider: 'ollama',
        category: 'chat',
        size: '3.8 GB',
        downloads: 125000,
        rating: 4.8,
        tags: ['chat', 'conversational', 'general'],
        modelUrl: 'llama2:7b-chat',
        homepage: 'https://ollama.ai/library/llama2',
        license: 'Custom',
        lastUpdated: new Date('2024-01-15'),
        requirements: {
          minRam: '8 GB',
          recommendedRam: '16 GB',
          gpuSupport: true
        },
        isInstalled: installedModels.some(m => m.name.includes('llama2')),
        isOfficial: true
      },
      {
        id: 'codellama-13b',
        name: 'Code Llama 13B',
        description: 'Large language model specialized for code generation and understanding',
        provider: 'ollama',
        category: 'code',
        size: '7.3 GB',
        downloads: 89000,
        rating: 4.7,
        tags: ['code', 'programming', 'development'],
        modelUrl: 'codellama:13b',
        homepage: 'https://ollama.ai/library/codellama',
        license: 'Custom',
        lastUpdated: new Date('2024-01-20'),
        requirements: {
          minRam: '16 GB',
          recommendedRam: '32 GB',
          gpuSupport: true
        },
        isInstalled: installedModels.some(m => m.name.includes('codellama')),
        isOfficial: true
      },
      {
        id: 'mistral-7b-instruct',
        name: 'Mistral 7B Instruct',
        description: 'High-performance 7B parameter model optimized for instruction following',
        provider: 'vllm',
        category: 'text',
        size: '13.5 GB',
        downloads: 156000,
        rating: 4.9,
        tags: ['instruct', 'high-performance', 'efficient'],
        modelUrl: 'mistralai/Mistral-7B-Instruct-v0.1',
        homepage: 'https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1',
        license: 'Apache 2.0',
        lastUpdated: new Date('2024-02-01'),
        requirements: {
          minRam: '16 GB',
          recommendedRam: '32 GB',
          gpuSupport: true
        },
        isInstalled: installedModels.some(m => m.name.includes('mistral')),
        isOfficial: true
      },
      {
        id: 'phi-2',
        name: 'Phi-2',
        description: 'Small but powerful 2.7B parameter model from Microsoft',
        provider: 'lmstudio',
        category: 'text',
        size: '1.6 GB',
        downloads: 67000,
        rating: 4.5,
        tags: ['small', 'efficient', 'microsoft'],
        modelUrl: 'microsoft/phi-2',
        homepage: 'https://huggingface.co/microsoft/phi-2',
        license: 'MIT',
        lastUpdated: new Date('2024-01-10'),
        requirements: {
          minRam: '4 GB',
          recommendedRam: '8 GB',
          gpuSupport: false
        },
        isInstalled: installedModels.some(m => m.name.includes('phi')),
        isOfficial: true
      }
    ];
  };

  const filteredModels = models.filter((model: MarketplaceModel) => {
    const matchesSearch = !debouncedSearchTerm || 
      model.name.toLowerCase().includes(debouncedSearchTerm.toLowerCase()) ||
      model.description.toLowerCase().includes(debouncedSearchTerm.toLowerCase()) ||
      model.tags.some(tag => tag.toLowerCase().includes(debouncedSearchTerm.toLowerCase()));

    const matchesCategory = selectedCategory === 'all' || model.category === selectedCategory;
    const matchesProvider = selectedProvider === 'all' || model.provider === selectedProvider;

    return matchesSearch && matchesCategory && matchesProvider;
  }).sort((a, b) => {
    switch (sortBy) {
      case 'popularity':
        return b.downloads - a.downloads;
      case 'size':
        const sizeA = parseFloat(a.size.replace(/[^0-9.]/g, '')) || 0;
        const sizeB = parseFloat(b.size.replace(/[^0-9.]/g, '')) || 0;
        return sizeA - sizeB;
      case 'recent':
        return b.lastUpdated.getTime() - a.lastUpdated.getTime();
      case 'rating':
        return b.rating - a.rating;
      default:
        return 0;
    }
  });

  const handleInstallModel = async (model: MarketplaceModel) => {
    if (!onInstallModel) return;
    
    setInstallingModels(prev => new Set(prev).add(model.id));
    try {
      await onInstallModel(model);
      // Update model as installed
      setModels(prev => prev.map(m => 
        m.id === model.id ? { ...m, isInstalled: true } : m
      ));
    } catch (error) {
      console.error('Installation failed:', error);
    } finally {
      setInstallingModels(prev => {
        const next = new Set(prev);
        next.delete(model.id);
        return next;
      });
    }
  };

  // Get unique categories and providers
  const categories = ['all', ...Array.from(new Set(models.map(m => m.category)))];
  const providers = ['all', ...Array.from(new Set(models.map(m => m.provider)))];

  const providerDisplayNames: Record<string, string> = {
    huggingface: 'Hugging Face',
    lmstudio: 'LM Studio',
    ollama: 'Ollama',
    vllm: 'vLLM',
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-7xl w-full max-h-[95vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <Download className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Model Marketplace</h2>
            <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs font-medium rounded-full">
              {filteredModels.length} models
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 dark:text-gray-300 hover:text-gray-600 dark:hover:text-gray-100 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Enhanced Search and Filters */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-300 w-4 h-4" />
              <input
                type="text"
                placeholder="Search models, descriptions, or tags..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              />
            </div>
            
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center space-x-2 px-3 py-2 border rounded-lg transition-colors ${
                  showFilters 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300' 
                    : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                <Filter className="w-4 h-4" />
                <span>Filters</span>
              </button>

              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                aria-label="Filter by category"
                title="Filter by category"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>
                    {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>

              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                aria-label="Filter by provider"
                title="Filter by provider"
              >
                {providers.map(provider => (
                  <option key={provider} value={provider}>
                    {provider === 'all' 
                      ? 'All Providers' 
                      : providerDisplayNames[provider] || provider.charAt(0).toUpperCase() + provider.slice(1)
                    }
                  </option>
                ))}
              </select>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'popularity' | 'size' | 'recent' | 'rating')}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                aria-label="Sort models by"
                title="Sort models by"
              >
                <option value="popularity">Most Popular</option>
                <option value="rating">Highest Rated</option>
                <option value="recent">Recently Updated</option>
                <option value="size">Smallest Size</option>
              </select>
            </div>
          </div>

          {showFilters && (
            <div className="mt-4 p-4 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Model Size</label>
                  <div className="space-y-1">
                    {['< 2 GB', '2-5 GB', '5-10 GB', '> 10 GB'].map(size => (
                      <label key={size} className="flex items-center">
                        <input type="checkbox" className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 bg-white dark:bg-gray-600" />
                        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{size}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">License</label>
                  <div className="space-y-1">
                    {['Apache 2.0', 'MIT', 'Custom', 'Commercial'].map(license => (
                      <label key={license} className="flex items-center">
                        <input type="checkbox" className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500 bg-white dark:bg-gray-600" />
                        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{license}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Features</label>
                  <div className="space-y-1">
                    {['GPU Support', 'CPU Only', 'Quantized', 'Fine-tuned'].map(feature => (
                      <label key={feature} className="flex items-center">
                        <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                        <span className="ml-2 text-sm text-gray-700">{feature}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Models Grid */}
        <div className="p-6 overflow-y-auto max-h-[calc(95vh-200px)]">
          {error && (
            <div className="text-center py-8">
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
                <p className="text-red-600 dark:text-red-400 font-semibold">{error}</p>
                <button
                  onClick={loadMarketplaceModels}
                  className="mt-2 px-4 py-2 bg-red-600 dark:bg-red-700 text-white rounded-lg hover:bg-red-700 dark:hover:bg-red-600 transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          )}
          
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent" />
              <span className="ml-3 text-gray-600">Loading models...</span>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredModels.slice(0, visibleCount).map((model: MarketplaceModel) => (
                  <ModelCard
                    key={model.id}
                    model={model}
                    isInstalling={installingModels.has(model.id)}
                    onInstall={() => handleInstallModel(model)}
                  />
                ))}
              </div>
              
              {filteredModels.length > visibleCount && (
                <div className="flex justify-center mt-6">
                  <button
                    onClick={() => setVisibleCount(vc => vc + 12)}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Load More Models ({filteredModels.length - visibleCount} remaining)
                  </button>
                </div>
              )}
            </>
          )}
          
          {!loading && filteredModels.length === 0 && !error && (
            <div className="text-center py-12">
              <Search className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No models found</h3>
              <p className="text-gray-500 dark:text-gray-400">Try adjusting your search criteria or filters.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

interface ModelCardProps {
  model: MarketplaceModel;
  isInstalling: boolean;
  onInstall: () => void;
}

const ModelCard: React.FC<ModelCardProps> = ({ model, isInstalling, onInstall }) => {
  const formatModelSize = (size: string | number | undefined): string => {
    if (typeof size === 'number') {
      if (size > 100000000) return (size / (1024 ** 3)).toFixed(1) + ' GB';
      if (size > 100000) return (size / (1024 ** 2)).toFixed(1) + ' MB';
      return size + ' bytes';
    }
    if (typeof size === 'string' && /^\d+$/.test(size)) {
      const n = parseInt(size, 10);
      if (n > 100000000) return (n / (1024 ** 3)).toFixed(1) + ' GB';
      if (n > 100000) return (n / (1024 ** 2)).toFixed(1) + ' MB';
      return n + ' bytes';
    }
    return size || 'Unknown';
  };

  const getProviderColor = (provider: string) => {
    switch (provider) {
      case 'ollama': return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case 'huggingface': return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      case 'vllm': return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case 'lmstudio': return 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200';
      default: return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'chat': return '💬';
      case 'code': return '💻';
      case 'text': return '📝';
      case 'embedding': return '🔗';
      case 'multimodal': return '🎭';
      default: return '🤖';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-6 hover:shadow-lg transition-all duration-200 hover:border-blue-300 dark:hover:border-blue-600">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white line-clamp-1">{model.name}</h3>
            {model.isOfficial && (
              <div title="Official Model">
                <CheckCircle className="w-4 h-4 text-blue-500 flex-shrink-0" />
              </div>
            )}
          </div>
          <div className="flex items-center space-x-2 mb-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getProviderColor(model.provider)}`}>
              {model.provider.toUpperCase()}
            </span>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {getCategoryIcon(model.category)} {model.category}
            </span>
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="flex items-center space-x-1 mb-1">
            <Star className="w-4 h-4 text-yellow-400 fill-current" />
            <span className="text-sm font-medium text-gray-900 dark:text-white">{model.rating.toFixed(1)}</span>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">{model.downloads.toLocaleString()} downloads</div>
        </div>
      </div>

      <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-2">{model.description}</p>

      <div className="flex flex-wrap gap-1 mb-4">
        {model.tags.slice(0, 3).map((tag: string) => (
          <span
            key={`${model.id}-${tag}`}
            className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300"
          >
            <Tag className="w-3 h-3 mr-1" />
            {tag}
          </span>
        ))}
        {model.tags.length > 3 && (
          <span className="text-xs text-gray-500 dark:text-gray-400">+{model.tags.length - 3} more</span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-300">
          <HardDrive className="w-4 h-4" />
          <span>{formatModelSize(model.size)}</span>
        </div>
        <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-300">
          <Clock className="w-4 h-4" />
          <span>{model.lastUpdated.toLocaleDateString()}</span>
        </div>
      </div>

      {model.requirements && (
        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Requirements:</div>
          <div className="text-xs text-gray-600 dark:text-gray-300">
            {model.requirements.minRam && `RAM: ${model.requirements.minRam}`}
            {model.requirements.recommendedRam && ` (rec: ${model.requirements.recommendedRam})`}
            {model.requirements.gpuSupport && ' • GPU supported'}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="flex space-x-2">
          <button
            onClick={() => window.open(model.homepage, '_blank')}
            className="p-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            title="View Homepage"
          >
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>

        {model.isInstalled ? (
          <div className="flex items-center space-x-1 text-green-600">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Installed</span>
          </div>
        ) : (
          <button
            onClick={onInstall}
            disabled={isInstalling}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isInstalling ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Installing...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Install</span>
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};

export default ModelMarketplace;