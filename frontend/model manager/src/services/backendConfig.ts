// Cache for backend URL with TTL (5 minutes)
const BACKEND_URL_CACHE_TTL = 5 * 60 * 1000;
const DEFAULT_PORTS = [8002, 8000, 8080, 8081, 3000, 5000];
const FALLBACK_URL = 'http://localhost:8080';

interface BackendUrlCache {
  url: string | null;
  lastChecked: number;
  isChecking: boolean;
  lastError: Error | null;
}

const backendUrlCache: BackendUrlCache = {
  url: null,
  lastChecked: 0,
  isChecking: false,
  lastError: null,
};

// Simple in-memory lock to prevent concurrent checks
let checkInProgress = false;

/**
 * Check if a URL is reachable with exponential backoff
 */
async function checkUrlReachable(
  url: string,
  options: { signal?: AbortSignal; timeout?: number } = {}
): Promise<boolean> {
  const maxAttempts = 2;
  const initialDelay = 300; // Start with 300ms
  const maxDelay = 3000; // Max 3 seconds
  const timeout = options.timeout || 2000;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(`${url}/health`, {
        signal: controller.signal,
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        try {
          const data = await response.json();
          return data.status === 'healthy';
        } catch (e) {
          console.debug('Invalid JSON response from health check:', e);
          return false;
        }
      }
    } catch (error) {
      clearTimeout(timeoutId);
      if (attempt === maxAttempts) return false;
      
      // Exponential backoff with jitter
      const delay = Math.min(initialDelay * Math.pow(2, attempt - 1), maxDelay);
      const jitter = Math.random() * 500; // Add up to 500ms jitter
      await new Promise(resolve => setTimeout(resolve, delay + jitter));
    }
  }
  
  return false;
}

/**
 * Get the backend URL with caching and automatic discovery
 */
export const getBackendUrl = async (forceRefresh = false): Promise<string> => {
  const now = Date.now();
  
  // Return cached URL if it's still valid and not marked as failed
  if (!forceRefresh && backendUrlCache.url && now - backendUrlCache.lastChecked < BACKEND_URL_CACHE_TTL) {
    return backendUrlCache.url;
  }
  
  // If we recently failed, don't retry too often
  if (backendUrlCache.lastError && now - backendUrlCache.lastChecked < 10000) {
    console.debug('Skipping backend check due to recent error');
    return FALLBACK_URL;
  }
  
  // Prevent concurrent checks
  if (checkInProgress) {
    if (backendUrlCache.url) return backendUrlCache.url;
    console.debug('Backend check already in progress, returning fallback');
    return FALLBACK_URL;
  }
  
  checkInProgress = true;
  backendUrlCache.isChecking = true;
  backendUrlCache.lastError = null;
  
  try {
    // Try to read from config file first
    try {
      const response = await fetch('/backend_config.json', {
        cache: 'no-cache',
        signal: AbortSignal.timeout(1500),
        headers: { 'Cache-Control': 'no-cache' }
      });
      
      if (response.ok) {
        try {
          const config = await response.json();
          if (config?.backend_port) {
            const url = `http://localhost:${config.backend_port}`;
            const isReachable = await checkUrlReachable(url, { timeout: 1500 });
            
            if (isReachable) {
              console.log(`✅ Backend confirmed running on port ${config.backend_port}`);
              backendUrlCache.url = url;
              backendUrlCache.lastChecked = now;
              return url;
            }
          }
        } catch (e) {
          console.debug('Error parsing backend config:', e);
        }
      }
    } catch (error) {
      console.debug('Could not read backend config:', error);
    }
    
    // Fallback to common ports with parallel health checks
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    
    try {
      // Race all port checks with a timeout
      const checkPromises = DEFAULT_PORTS.map(port => 
        checkUrlReachable(`http://localhost:${port}`, { 
          signal: controller.signal,
          timeout: 1500
        })
        .then(isReachable => isReachable ? port : null)
        .catch(() => null)
      );
      
      // Wait for the first successful check or all to fail
      const workingPort = await Promise.race([
        Promise.race(checkPromises),
        new Promise<number | null>(resolve => setTimeout(() => resolve(null), 4000))
      ]);
      
      if (workingPort) {
        const url = `http://localhost:${workingPort}`;
        console.log(`✅ Found working backend on port ${workingPort}`);
        backendUrlCache.url = url;
        backendUrlCache.lastChecked = now;
        return url;
      }
    } finally {
      clearTimeout(timeoutId);
      controller.abort();
    }
  } catch (error) {
    console.debug('Backend connection attempt failed:', error);
    const connectionError = new Error('Could not connect to backend. Please make sure the backend server is running.');
    backendUrlCache.lastError = connectionError;
    backendUrlCache.lastChecked = now;
    console.warn('Using fallback backend URL:', FALLBACK_URL);
    return FALLBACK_URL;
  } finally {
    checkInProgress = false;
    backendUrlCache.isChecking = false;
  }
  
  // If we get here, no backend was found but we didn't throw
  console.warn('No backend found, using fallback URL:', FALLBACK_URL);
  return FALLBACK_URL;
};

// Cache the backend URL to avoid repeated detection
let cachedBackendUrl: string | null = null;

export const getCachedBackendUrl = async (): Promise<string> => {
  if (!cachedBackendUrl) {
    cachedBackendUrl = await getBackendUrl();
  }
  return cachedBackendUrl;
};

// Reset cache when needed (e.g., on connection errors)
export const resetBackendUrlCache = (): void => {
  cachedBackendUrl = null;
};