import { useState, useEffect, useCallback } from 'react';

interface Settings {
  autoRefresh: boolean;
  refreshInterval: number;
  darkMode: boolean;
  notifications: boolean;
  defaultModel?: string;
  advancedSettings: {
    debugMode: boolean;
    logLevel: 'error' | 'warn' | 'info' | 'debug';
  };
}

const DEFAULT_SETTINGS: Settings = {
  autoRefresh: true,
  refreshInterval: 30, // seconds
  darkMode: false,
  notifications: true,
  advancedSettings: {
    debugMode: false,
    logLevel: 'info',
  },
};

export const useSettings = () => {
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load settings from backend on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('/api/settings');
        if (response.ok) {
          const data = await response.json();
          setSettings({ ...DEFAULT_SETTINGS, ...data });
        } else {
          console.warn('Failed to load settings, using defaults');
        }
      } catch (err) {
        console.error('Error loading settings:', err);
        setError('Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };

    loadSettings();
  }, []);

  // Save settings to backend
  const saveSettings = useCallback(async (updates: Partial<Settings>) => {
    try {
      const newSettings = { ...settings, ...updates };
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSettings),
      });

      if (response.ok) {
        setSettings(newSettings);
        return true;
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (err) {
      console.error('Error saving settings:', err);
      setError('Failed to save settings');
      return false;
    }
  }, [settings]);

  // Update a specific setting
  const updateSetting = useCallback(async <K extends keyof Settings>(
    key: K,
    value: Settings[K]
  ) => {
    return saveSettings({ [key]: value });
  }, [saveSettings]);

  // Toggle a boolean setting
  const toggleSetting = useCallback(async (key: keyof Settings) => {
    const currentValue = settings[key];
    if (typeof currentValue === 'boolean') {
      return saveSettings({ [key]: !currentValue } as Partial<Settings>);
    }
    return false;
  }, [settings, saveSettings]);

  return {
    settings,
    isLoading,
    error,
    saveSettings,
    updateSetting,
    toggleSetting,
  };
};
