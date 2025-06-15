// marketplace-aggregator.js
// Node.js Express server to aggregate model metadata from Ollama, LM Studio, vLLM, and Hugging Face
// Serves /providers/marketplace/models for the React frontend

import express from 'express';
import * as cheerio from 'cheerio';
import cors from 'cors';

const PORT = process.env.PORT || 3030;
const REFRESH_INTERVAL = 60 * 60 * 1000; // 1 hour
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
const REQUEST_TIMEOUT = 10000; // 10 seconds

// In-memory cache with TTL
const cache = {
  data: [],
  timestamp: 0,
  isRefreshing: false,
  refreshPromise: null,
  lastError: null
};

// Configure fetch with timeout
const fetchWithTimeout = async (url, options = {}) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

const app = express();
app.use(cors());

// Cache management functions
const getCachedData = () => {
  const now = Date.now();
  if (now - cache.timestamp < CACHE_TTL && cache.data.length > 0) {
    return {
      data: cache.data,
      isStale: now - cache.timestamp > REFRESH_INTERVAL,
      timestamp: cache.timestamp
    };
  }
  return null;
};

const updateCache = async () => {
  if (cache.isRefreshing) {
    return cache.refreshPromise;
  }

  cache.isRefreshing = true;
  cache.refreshPromise = (async () => {
    try {
      console.log('Fetching models from all providers...');
      const [huggingFaceModels, ollamaModels, vllmModels, lmstudioModels] = await Promise.allSettled([
        fetchHuggingFaceModels(),
        fetchOllamaModels(),
        fetchVLLMModels(),
        fetchLMStudioModels()
      ]);

      const allModels = [
        ...(huggingFaceModels.status === 'fulfilled' ? huggingFaceModels.value : []),
        ...(ollamaModels.status === 'fulfilled' ? ollamaModels.value : []),
        ...(vllmModels.status === 'fulfilled' ? vllmModels.value : []),
        ...(lmstudioModels.status === 'fulfilled' ? lmstudioModels.value : [])
      ];

      console.log(`Fetched ${allModels.length} total models:`, {
        huggingface: huggingFaceModels.status === 'fulfilled' ? huggingFaceModels.value.length : 0,
        ollama: ollamaModels.status === 'fulfilled' ? ollamaModels.value.length : 0,
        vllm: vllmModels.status === 'fulfilled' ? vllmModels.value.length : 0,
        lmstudio: lmstudioModels.status === 'fulfilled' ? lmstudioModels.value.length : 0
      });

      // Deduplicate models by ID
      const uniqueModels = Array.from(new Map(allModels.map(model => [model.id, model])).values());
      
      cache.data = uniqueModels;
      cache.timestamp = Date.now();
      cache.lastError = null;
      
      return uniqueModels;
    } catch (error) {
      console.error('Error updating cache:', error);
      cache.lastError = error.message;
      throw error;
    } finally {
      cache.isRefreshing = false;
      cache.refreshPromise = null;
    }
  })();

  return cache.refreshPromise;
};

// Fetch Hugging Face models
async function fetchHuggingFaceModels() {
  const url = 'https://huggingface.co/api/models?library=gguf&sort=downloads&limit=20';
  try {
    console.log('Fetching Hugging Face models...');
    const res = await fetchWithTimeout(url);
    if (!res.ok) {
      throw new Error(`Hugging Face API error: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    const models = data.map(model => ({
      id: `hf_${model.id.replace('/', '_')}`,
      name: model.id,
      description: model.description || '',
      provider: 'huggingface',
      category: 'Hugging Face',
      size: '',
      downloads: model.downloads || 0,
      rating: 0,
      tags: model.tags || [],
      modelUrl: model.id,
      homepage: `https://huggingface.co/${model.id}`,
      license: model.license || '',
      lastUpdated: model.lastModified || new Date().toISOString(),
      requirements: {
        minRam: '8 GB',
        recommendedRam: '16 GB',
        gpuSupport: true
      },
      isInstalled: false,
      isOfficial: false
    }));
    console.log(`Fetched ${models.length} Hugging Face models`);
    return models;
  } catch (err) {
    console.error('Hugging Face fetch failed:', err.message);
    return [];
  }
}

// Fetch Ollama models
async function fetchOllamaModels() {
  try {
    console.log('Fetching Ollama models...');
    const searchRes = await fetchWithTimeout('https://ollama.com/search');
    const searchHtml = await searchRes.text();
    const $ = cheerio.load(searchHtml);
    
    const models = [];
    $('a[href^="/library/"]').each((i, el) => {
      const href = $(el).attr('href');
      const name = href.replace('/library/', '');
      if (name && !models.find(m => m.name === name)) {
        models.push({
          id: `ollama_${name}`,
          name: name,
          description: $(el).text().trim(),
          provider: 'ollama',
          category: 'Ollama',
          size: 'Unknown',
          downloads: 0,
          rating: 0,
          tags: [],
          modelUrl: name,
          homepage: `https://ollama.com/library/${name}`,
          license: '',
          lastUpdated: new Date().toISOString(),
          requirements: {
            minRam: '4 GB',
            recommendedRam: '8 GB',
            gpuSupport: true
          },
          isInstalled: false,
          isOfficial: true
        });
      }
    });
    
    console.log(`Fetched ${models.length} Ollama models`);
    return models;
  } catch (err) {
    console.error('Ollama fetch failed:', err.message);
    return [];
  }
}

// Fetch VLLM models
async function fetchVLLMModels() {
  try {
    console.log('Fetching vLLM models...');
    const url = 'https://huggingface.co/api/models?library=transformers&sort=downloads&limit=15';
    const res = await fetchWithTimeout(url);
    if (!res.ok) {
      throw new Error(`vLLM API error: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    const models = data.map(model => ({
      id: `vllm_${model.id.replace('/', '_')}`,
      name: model.id,
      description: model.description || 'vLLM compatible model',
      provider: 'vllm',
      category: 'vLLM',
      size: 'Variable',
      downloads: model.downloads || 0,
      rating: 0,
      tags: model.tags || [],
      modelUrl: model.id,
      homepage: `https://huggingface.co/${model.id}`,
      license: model.license || '',
      lastUpdated: model.lastModified || new Date().toISOString(),
      requirements: {
        minRam: '16 GB',
        recommendedRam: '32 GB',
        gpuSupport: true
      },
      isInstalled: false,
      isOfficial: false
    }));
    console.log(`Fetched ${models.length} vLLM models`);
    return models;
  } catch (err) {
    console.error('vLLM fetch failed:', err.message);
    return [];
  }
}

// Fetch LM Studio models
async function fetchLMStudioModels() {
  try {
    console.log('Fetching LM Studio models...');
    const catalogRes = await fetchWithTimeout('https://lmstudio.ai/models');
    const catalogHtml = await catalogRes.text();
    const $ = cheerio.load(catalogHtml);
    
    const models = [];
    $('a[href*="/models/"]').each((i, el) => {
      const href = $(el).attr('href');
      const name = $(el).text().trim();
      if (name && href && name.length > 1) {
        models.push({
          id: `lmstudio_${name.replace(/[^a-zA-Z0-9]/g, '_')}`,
          name: name,
          description: 'LM Studio compatible model',
          provider: 'lmstudio',
          category: 'LM Studio',
          size: 'Variable',
          downloads: 0,
          rating: 0,
          tags: [],
          modelUrl: name,
          homepage: `https://lmstudio.ai${href}`,
          license: '',
          lastUpdated: new Date().toISOString(),
          requirements: {
            minRam: '8 GB',
            recommendedRam: '16 GB',
            gpuSupport: true
          },
          isInstalled: false,
          isOfficial: true
        });
      }
    });
    
    console.log(`Fetched ${models.length} LM Studio models`);
    return models;
  } catch (err) {
    console.error('LM Studio fetch failed:', err.message);
    return [];
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: Date.now(),
    cache: {
      size: cache.data.length,
      lastUpdate: cache.timestamp,
      isRefreshing: cache.isRefreshing,
      lastError: cache.lastError
    }
  });
});

// Main endpoint to get all marketplace models
app.get('/providers/marketplace/models', async (req, res) => {
  try {
    console.log('Request for marketplace models received');
    
    // Try to get cached data first
    const cached = getCachedData();
    const shouldRefresh = !cached || cached.isStale;

    // If we have valid cache, return it immediately
    if (cached && !shouldRefresh) {
      console.log(`Returning ${cached.data.length} cached models`);
      return res.json({
        models: cached.data,
        timestamp: cached.timestamp,
        isStale: cached.isStale
      });
    }

    // If we have stale cache, return it but refresh in background
    if (cached && cached.isStale) {
      console.log(`Returning ${cached.data.length} stale cached models, refreshing in background`);
      updateCache().catch(err => {
        console.error('Background refresh failed:', err);
      });
      return res.json({
        models: cached.data,
        timestamp: cached.timestamp,
        isStale: true
      });
    }

    // If no cache, wait for fresh data
    console.log('No cache available, fetching fresh data...');
    const models = await updateCache();
    return res.json({
      models,
      timestamp: cache.timestamp,
      isStale: false
    });
  } catch (error) {
    console.error('Error in /providers/marketplace/models:', error);
    res.status(500).json({
      error: 'Failed to fetch models',
      message: error.message,
      timestamp: Date.now()
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Marketplace aggregator running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`Models endpoint: http://localhost:${PORT}/providers/marketplace/models`);
  
  // Initial cache refresh
  updateCache().catch(err => {
    console.error('Initial cache refresh failed:', err);
  });
});
