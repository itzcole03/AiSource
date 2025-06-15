export class APIError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'APIError';
  }
}

export const apiCall = async (url: string, options: RequestInit = {}) => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // Increased to 10 seconds

    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new APIError(`HTTP ${response.status}: ${response.statusText}`, response.status);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return await response.text();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    if (error.name === 'AbortError') {
      throw new APIError('Request timeout - service may not be running or is slow to respond');
    }
    if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
      throw new APIError('Connection refused - service is not running or not accessible');
    }
    throw new APIError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

// Utility function for health checks with shorter timeout
export const healthCheck = async (url: string, timeout: number = 3000): Promise<boolean> => {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(url, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      },
    });

    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
};