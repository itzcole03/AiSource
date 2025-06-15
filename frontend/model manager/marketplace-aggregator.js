// marketplace-aggregator.js
// Node.js Express server to aggregate model metadata from Ollama and Hugging Face
// Serves /api/providers/marketplace/models for your React frontend

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

// Fetch Ollama models by scraping the Ollama library web page and exclude locally installed models


// Only one definition of fetchOllamaModels should exist in this file. Remove duplicate(s) below this comment if present.


// Fetch Hugging Face models, with error handling
async function fetchHuggingFaceModels() {
  const url = 'https://huggingface.co/api/models?library=gguf&sort=downloads';
  try {
    const res = await fetch(url);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Hugging Face API error: ${res.status} ${res.statusText} - ${text}`);
    }
    const data = await res.json();
    return data.map(model => ({
      id: model.id,
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
  } catch (err) {
    console.error('Hugging Face fetch failed:', err.message);
    return [];
  }
}

// Fetch VLLM-compatible models from Hugging Face (e.g., safetensors, transformers)
async function getVLLMModels() {
  const url = 'https://huggingface.co/api/models?library=transformers&sort=downloads';
  let hfModels = [];
  try {
    const res = await fetch(url);
    if (res.ok) {
      hfModels = await res.json();
    }
  } catch (err) {
    console.error('Failed to fetch Hugging Face VLLM models:', err.message);
  }
  // Map to aggregator schema
  return hfModels.map(model => ({
    id: model.id,
    name: model.id,
    description: model.description || 'VLLM compatible model',
    provider: 'vllm',
    category: (model.tags || []).includes('chat') ? 'chat' : 'text',
    size: model.safetensors ? model.safetensors.size : (model.modelSize || model.size || 'unknown'),
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
  }));
  return enriched;
}

// --- Enhanced Aggregator: LM Studio, Ollama, VLLM ---



async function fetchLMStudioModels() {
  const catalogRes = await fetch('https://lmstudio.ai/models');
  const catalogHtml = await catalogRes.text();
  const models = [];

  // Regex to extract: ### modelName\n(desc...)\n[...](url)
  const regex = /###\s*([\w\-. ]+)\n([\s\S]*?)(?:\[(?:[^\]]+)\]\((\/models\/[a-zA-Z0-9\-\/]+)\))/g;
  let match;
  while ((match = regex.exec(catalogHtml)) !== null) {
    const name = match[1].trim();
    let desc = match[2].replace(/\n/g, ' ').replace(/\s+/g, ' ').trim();
    const url = `https://lmstudio.ai${match[3]}`;
    // Try to extract size (7B, 14B, etc)
    const sizeMatch = desc.match(/([\d,.]+)\s*(B|billion|M|million)/i);
    const size = sizeMatch ? sizeMatch[0].replace(/\s+/g, ' ') : 'Unknown';
    if (name && url) {
      models.push({ name, url, size, desc });
    }
  }
  console.log('[LMStudio] Models extracted:', models.length);

  // Return models with normalized fields
  return models.map(model => ({
    name: model.name,
    url: model.url,
    provider: 'lmstudio',
    size: model.size || 'Unknown',
    bestUse: model.desc ? (model.desc.split('. ')[0] || model.desc).replace(/\s+/g, ' ').trim() : 'General use',
  }));
}


// Only one definition of fetchOllamaModels should exist in this file. Remove duplicate(s) below this comment if present.
async function fetchOllamaModels() {
  const searchRes = await fetch('https://ollama.com/search');
  const searchHtml = await searchRes.text();
  const $ = cheerio.load(searchHtml);
  const models = [];
  // Find all model library links
  $('a').each((i, el) => {
    const href = $(el).attr('href');
    if (href && href.startsWith('/library/')) {
      const modelUrl = `https://ollama.com${href}`;
      const name = $(el).text().trim();
      if (name && !models.find(m => m.url === modelUrl)) {
        models.push({ name, url: modelUrl });
      }
    }
  });
  // Scrape each model's library page for size and best use
  const enriched = await Promise.all(models.map(async model => {
    try {
      const res = await fetch(model.url);
      const html = await res.text();
      const $ = cheerio.load(html);
      // Try to find parameter count or file size
      let size = null;
      let desc = null;
      // Look for headers or bold text with 'B', 'parameters', etc.
      const sizeText = $('body').text().match(/([\d,.]+)\s*(B|billion|M|million)\s*(parameters|params|param|size)?/i);
      if (sizeText) size = sizeText[0].replace(/\s+/g, ' ');
      // Use first paragraph or summary as best use
      desc = $('p').first().text().trim() || $('body').text().split('\n')[0].trim();
      if (!desc || desc.length < 8) desc = $('body').text().split('\n').find(line => line.length > 12);
      return {
        name: model.name,
        url: model.url,
        provider: 'ollama',
        size: size || 'Unknown',
        bestUse: desc ? desc.split('. ')[0].replace(/\s+/g, ' ').trim() : 'General use',
      };
    } catch (e) {
      return { ...model, provider: 'ollama', size: 'Unknown', bestUse: 'General use' };
    }
  }));
  return enriched;
}

async function fetchVLLMModels() {
  const docRes = await fetch('https://docs.vllm.ai/en/v0.4.1/models/supported_models.html');
  const docHtml = await docRes.text();
  const $ = cheerio.load(docHtml);
  const models = [];
  // Find all model names in the doc (look for tables or lists)
  $('table tr').each((i, el) => {
    const cols = $(el).find('td');
    if (cols.length >= 2) {
      const name = $(cols[0]).text().trim();
      const desc = $(cols[1]).text().trim();
      if (name) {
        models.push({ name, desc });
      }
    }
  });
  // Fallback: parse code blocks or lists
  if (models.length === 0) {
    $('li').each((i, el) => {
      const text = $(el).text().trim();
      if (text && /[Bb]illion|[Mm]illion|[Bb]|[Mm]odel/.test(text)) {
        models.push({ name: text, desc: text });
      }
    });
  }
  // For each model, try to extract size and best use
  const enriched = await Promise.all(models.map(async model => {
    // Try to extract size from name or desc
    let size = null;
    let bestUse = null;
    const sizeMatch = model.name.match(/([\d,.]+)\s*(B|billion|M|million)/i) || model.desc.match(/([\d,.]+)\s*(B|billion|M|million)/i);
    if (sizeMatch) size = sizeMatch[0].replace(/\s+/g, ' ');
    // Use desc or fallback
    bestUse = model.desc ? model.desc.split('. ')[0].replace(/\s+/g, ' ').trim() : 'General use';
    return {
      name: model.name,
      url: '',
      provider: 'vllm',
      size: size || 'Unknown',
      bestUse: bestUse,
    };
  }));
  return enriched;
}

// Fetch all and merge
export async function getMarketplaceModels() {
  const [lmstudio, ollama, vllm] = await Promise.all([
    fetchLMStudioModels(),
    fetchOllamaModels(),
    fetchVLLMModels()
  ]);
  // Merge and deduplicate by name+provider
  const all = [...lmstudio, ...ollama, ...vllm];
  const seen = new Set();
  const merged = all.filter(m => {
    const key = m.provider + ':' + m.name.toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  return merged;
}
// --- END Enhanced Aggregator ---

// Merge, deduplicate, and serve all sources
async function getAllMarketplaceModels() {
  // Fetch only from compatible sources
  const [ollama, vllm, lmstudio] = await Promise.all([
    fetchOllamaModels(),
    fetchVLLMModels(),
    fetchLMStudioModels()
  ]);
  // Normalize provider field
  const normalizeProvider = (p) => {
    if (!p) return '';
    const s = p.toLowerCase();
    if (s.includes('ollama')) return 'ollama';
    if (s.includes('lmstudio')) return 'lmstudio';
    if (s.includes('vllm')) return 'vllm';
    return s;
  };
  const all = [...ollama, ...vllm, ...lmstudio].map(m => ({
    ...m,
    provider: normalizeProvider(m.provider)
  }));
  const seen = new Set();
  const deduped = all.filter(m => {
    if (seen.has(m.id)) return false;
    seen.add(m.id);
    return true;
  });
  // Debug: log count per provider
  const counts = deduped.reduce((acc, m) => {
    acc[m.provider] = (acc[m.provider] || 0) + 1;
    return acc;
  }, {});
  console.log('Marketplace provider counts:', counts);
  return deduped;
}

// --- END intelligent aggregator logic ---




async function refreshCache() {
  try {
    cachedModels = await getAllMarketplaceModels();
    lastRefresh = Date.now();
    console.log(`Marketplace cache refreshed: ${cachedModels.length} models`);
  } catch (e) {
    console.error('Marketplace refresh failed:', e);
  }
}

app.get('/api/providers/marketplace/models', async (req, res) => {
  try {
    // Try to get cached data first
    const cached = getCachedData();
    const shouldRefresh = !cached || cached.isStale;

    // If we have valid cache, return it immediately
    if (cached) {
      // Only send response if not already sent
      if (!res.headersSent) {
        return res.json({
          models: cached.data,
          timestamp: cached.timestamp,
          isStale: cached.isStale
        });
      }
      return;
    }

    // Refresh in background if needed
    if (shouldRefresh) {
      updateCache().catch(err => {
        console.error('Background refresh failed:', err);
      });
    }

    // If no cache, wait for refresh
    if (!cached) {
      const models = await updateCache();
      return res.json({
        models,
        timestamp: cache.timestamp,
        isStale: false
      });
    }
  } catch (error) {
    console.error('Error in /api/providers/marketplace/models:', error);
    res.status(500).json({
      error: 'Failed to fetch models',
      message: error.message,
      timestamp: Date.now()
    });
  }
  res.json({ models: cachedModels });
});

app.listen(PORT, () => {
  console.log(`Marketplace aggregator running on port ${PORT}`);
  refreshCache();
});
