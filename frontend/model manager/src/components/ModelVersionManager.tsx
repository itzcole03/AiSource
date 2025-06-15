import React, { useState, useEffect } from 'react';
import { Package, Download, Trash2, Star, Clock, HardDrive } from 'lucide-react';

interface ModelVersion {
  id: string;
  version: string;
  size: string;
  downloadDate: Date;
  isActive: boolean;
  isLatest: boolean;
  description?: string;
  tags: string[];
}

interface ModelVersionManagerProps {
  modelId: string;
  modelName: string;
  provider: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ModelVersionManager: React.FC<ModelVersionManagerProps> = ({
  modelId,
  modelName,
  provider,
  isOpen,
  onClose
}) => {
  const [versions, setVersions] = useState<ModelVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadVersions();
    }
  }, [isOpen, modelId]);

  const loadVersions = async () => {
    setLoading(true);
    try {
      // Simulate loading versions
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockVersions: ModelVersion[] = [
        {
          id: `${modelId}-v1.0`,
          version: '1.0.0',
          size: '4.1 GB',
          downloadDate: new Date('2024-01-15'),
          isActive: true,
          isLatest: false,
          description: 'Stable release',
          tags: ['stable', 'recommended']
        },
        {
          id: `${modelId}-v1.1`,
          version: '1.1.0',
          size: '4.3 GB',
          downloadDate: new Date('2024-02-01'),
          isActive: false,
          isLatest: true,
          description: 'Latest with performance improvements',
          tags: ['latest', 'performance']
        },
        {
          id: `${modelId}-v0.9`,
          version: '0.9.0',
          size: '3.8 GB',
          downloadDate: new Date('2024-01-01'),
          isActive: false,
          isLatest: false,
          description: 'Legacy version',
          tags: ['legacy']
        }
      ];
      
      setVersions(mockVersions);
    } catch (error) {
      console.error('Failed to load versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleActivateVersion = async (versionId: string) => {
    try {
      setVersions(prev => prev.map(v => ({
        ...v,
        isActive: v.id === versionId
      })));
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
    } catch (error) {
      console.error('Failed to activate version:', error);
    }
  };

  const handleDeleteVersion = async (versionId: string) => {
    if (!confirm('Are you sure you want to delete this version?')) {
      return;
    }

    try {
      setVersions(prev => prev.filter(v => v.id !== versionId));
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
    } catch (error) {
      console.error('Failed to delete version:', error);
    }
  };

  const handleDownloadVersion = async (version: string) => {
    try {
      // Simulate download
      console.log(`Downloading ${modelName} version ${version}`);
    } catch (error) {
      console.error('Failed to download version:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Package className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{modelName}</h2>
              <p className="text-sm text-gray-500">Version Management</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent" />
              <span className="ml-3 text-gray-600">Loading versions...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {versions.map((version) => (
                <div
                  key={version.id}
                  className={`border rounded-lg p-4 transition-colors ${
                    version.isActive 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-medium text-gray-900">
                          Version {version.version}
                        </h3>
                        
                        <div className="flex space-x-2">
                          {version.isLatest && (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                              Latest
                            </span>
                          )}
                          {version.isActive && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                              Active
                            </span>
                          )}
                          {version.tags.map(tag => (
                            <span
                              key={tag}
                              className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>

                      {version.description && (
                        <p className="text-gray-600 mb-3">{version.description}</p>
                      )}

                      <div className="flex items-center space-x-6 text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <HardDrive className="w-4 h-4" />
                          <span>{version.size}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="w-4 h-4" />
                          <span>Downloaded {version.downloadDate.toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      {!version.isActive && (
                        <button
                          onClick={() => handleActivateVersion(version.id)}
                          className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          <Star className="w-4 h-4" />
                          <span>Activate</span>
                        </button>
                      )}
                      
                      {version.isLatest && !version.isActive && (
                        <button
                          onClick={() => handleDownloadVersion(version.version)}
                          className="flex items-center space-x-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          <span>Update</span>
                        </button>
                      )}
                      
                      {!version.isActive && (
                        <button
                          onClick={() => handleDeleteVersion(version.id)}
                          className="flex items-center space-x-1 px-3 py-1.5 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                          <span>Delete</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {!loading && versions.length === 0 && (
            <div className="text-center py-12">
              <Package className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No versions found</h3>
              <p className="text-gray-500">This model doesn't have any downloaded versions.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};