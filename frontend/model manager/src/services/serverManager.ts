import { ServerCommand } from '../types';
import { getCachedBackendUrl, resetBackendUrlCache } from './backendConfig';

export class ServerManagerService {
  async executeServerCommand(command: ServerCommand): Promise<{ success: boolean; message: string }> {
    try {
      // Try the backend first with enhanced error handling
      const backendResult = await this.tryBackendCommand(command);
      if (backendResult) {
        return backendResult;
      }

      // Fallback to direct provider management
      return await this.directProviderCommand(command);
    } catch (error) {
      console.error('Server command execution failed:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  private async tryBackendCommand(command: ServerCommand): Promise<{ success: boolean; message: string } | null> {
    try {
      const backendUrl = await getCachedBackendUrl();
      const body: any = {};
      
      if (command.modelName && command.action === 'start') {
        body.modelName = command.modelName;
      }

      const response = await fetch(`${backendUrl}/providers/${command.provider}/${command.action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: Object.keys(body).length > 0 ? JSON.stringify(body) : undefined,
        signal: AbortSignal.timeout(15000) // Increased timeout for server operations
      });

      if (!response.ok) {
        throw new Error(`Backend request failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      return {
        success: result.status !== 'error',
        message: result.message || `${command.provider} ${command.action} completed`
      };
    } catch (error) {
      console.warn('Backend command failed:', error);
      resetBackendUrlCache(); // Reset cache on error
      return null;
    }
  }

  private async directProviderCommand(command: ServerCommand): Promise<{ success: boolean; message: string }> {
    switch (command.provider) {
      case 'ollama':
        return await this.directOllamaCommand(command.action);
      case 'vllm':
        return await this.directVLLMCommand(command.action, command.modelName);
      case 'lmstudio':
        return await this.directLMStudioCommand(command.action);
      default:
        throw new Error(`Unsupported provider: ${command.provider}`);
    }
  }

  private async directOllamaCommand(action: 'start' | 'stop' | 'restart'): Promise<{ success: boolean; message: string }> {
    switch (action) {
      case 'start':
        const isRunning = await this.checkProviderStatus('ollama');
        if (isRunning === 'running') {
          return {
            success: true,
            message: 'Ollama server is already running'
          };
        }
        
        return {
          success: true,
          message: 'To start Ollama server:\n\n' +
                  '1. Open Command Prompt or PowerShell as Administrator\n' +
                  '2. Run: ollama serve\n' +
                  '3. Keep the terminal open\n\n' +
                  'Alternative: Start Ollama from the system tray if installed as a service.\n' +
                  'The server will be available at http://localhost:11434'
        };
      
      case 'stop':
        return {
          success: true,
          message: 'To stop Ollama server:\n\n' +
                  '1. Press Ctrl+C in the terminal running "ollama serve"\n' +
                  '2. Or close the Ollama system tray application\n' +
                  '3. Or use Task Manager to end ollama.exe processes\n\n' +
                  'All running models will be unloaded when the server stops.'
        };
      
      case 'restart':
        return {
          success: true,
          message: 'To restart Ollama server:\n\n' +
                  '1. Stop the current server (Ctrl+C or close terminal)\n' +
                  '2. Wait a few seconds for complete shutdown\n' +
                  '3. Run: ollama serve\n\n' +
                  'The server will restart with all previously downloaded models available.'
        };
      
      default:
        throw new Error(`Invalid action: ${action}`);
    }
  }

  private async directVLLMCommand(action: 'start' | 'stop' | 'restart', modelName?: string): Promise<{ success: boolean; message: string }> {
    switch (action) {
      case 'start':
        if (!modelName) {
          return {
            success: false,
            message: 'Model name is required to start vLLM server.\n\n' +
                    'To start vLLM:\n' +
                    '1. Select a model from your collection\n' +
                    '2. Use the server controls to start with that model\n' +
                    '3. Or use your launcher script with --model parameter'
          };
        }
        
        return {
          success: true,
          message: `To start vLLM with model "${modelName}":\n\n` +
                  '1. Open WSL terminal (run "wsl" in Command Prompt)\n' +
                  '2. Activate your vLLM environment:\n' +
                  '   conda activate vllm\n' +
                  `3. Start the server:\n` +
                  `   python -m vllm.entrypoints.openai.api_server --model ${modelName}\n` +
                  '4. Wait for model loading (may take several minutes)\n\n' +
                  'Alternative - Use your launcher script:\n' +
                  `bash ~/launch_vllm_auto.sh --model "${modelName}"\n\n` +
                  'Server will be available at http://localhost:8000'
        };
      
      case 'stop':
        return {
          success: true,
          message: 'To stop vLLM server:\n\n' +
                  '1. Press Ctrl+C in the WSL terminal running vLLM\n' +
                  '2. Or run in WSL: pkill -f vllm\n' +
                  '3. Or use your stop script: bash ~/stop_vllm.sh\n\n' +
                  'This will unload the model and free GPU memory.\n' +
                  'All active connections will be terminated.'
        };
      
      case 'restart':
        const modelText = modelName ? ` with model "${modelName}"` : '';
        return {
          success: true,
          message: `To restart vLLM${modelText}:\n\n` +
                  '1. Stop the current server:\n' +
                  '   - Press Ctrl+C or run: pkill -f vllm\n' +
                  '2. Wait for complete shutdown (check GPU memory)\n' +
                  '3. Start vLLM again with your desired model\n\n' +
                  'Use your launcher script for easier management:\n' +
                  'bash ~/launch_vllm_auto.sh\n\n' +
                  'Note: Model loading may take several minutes on restart.'
        };
      
      default:
        throw new Error(`Invalid action: ${action}`);
    }
  }

  private async directLMStudioCommand(action: 'start' | 'stop' | 'restart'): Promise<{ success: boolean; message: string }> {
    switch (action) {
      case 'start':
        return {
          success: true,
          message: 'To start LM Studio server:\n\n' +
                  '1. Open LM Studio application\n' +
                  '2. Navigate to the "Local Server" tab\n' +
                  '3. Click "Start Server" button\n' +
                  '4. Optionally load a model in the Chat tab\n' +
                  '5. Configure server settings if needed\n\n' +
                  'The server will be available at http://localhost:1234\n' +
                  'API documentation: http://localhost:1234/docs'
        };
      
      case 'stop':
        return {
          success: true,
          message: 'To stop LM Studio server:\n\n' +
                  '1. Open LM Studio application\n' +
                  '2. Go to the "Local Server" tab\n' +
                  '3. Click "Stop Server" button\n\n' +
                  'Alternative: Close the LM Studio application entirely.\n' +
                  'Any loaded models will be unloaded when the server stops.'
        };
      
      case 'restart':
        return {
          success: true,
          message: 'To restart LM Studio server:\n\n' +
                  '1. Stop the server:\n' +
                  '   Local Server tab → Stop Server\n' +
                  '2. Wait a moment for complete shutdown\n' +
                  '3. Click "Start Server" again\n\n' +
                  'Note: Any loaded models will need to be reloaded after restart.\n' +
                  'Server settings will be preserved.'
        };
      
      default:
        throw new Error(`Invalid action: ${action}`);
    }
  }

  async checkServerStatus(provider: 'ollama' | 'vllm' | 'lmstudio'): Promise<'running' | 'stopped' | 'error'> {
    try {
      const urls = {
        ollama: 'http://localhost:11434/api/tags',
        vllm: 'http://localhost:8000/health',
        lmstudio: 'http://localhost:1234/v1/models'
      };

      const response = await fetch(urls[provider], {
        method: 'GET',
        signal: AbortSignal.timeout(5000)
      });

      return response.ok ? 'running' : 'error';
    } catch {
      return 'stopped';
    }
  }

  async checkProviderStatus(provider: 'ollama' | 'vllm' | 'lmstudio'): Promise<'running' | 'stopped' | 'error'> {
    return this.checkServerStatus(provider);
  }

  getServerCommands(provider: 'ollama' | 'vllm' | 'lmstudio'): string[] {
    const commands = {
      ollama: [
        'ollama serve',
        'ollama pull <model-name>',
        'ollama list',
        'ollama ps',
        'ollama stop <model-name>',
        'ollama rm <model-name>'
      ],
      vllm: [
        'python -m vllm.entrypoints.openai.api_server --model <model-name>',
        'python -m vllm.entrypoints.openai.api_server --model <model-name> --port 8000',
        'python -m vllm.entrypoints.openai.api_server --model <model-name> --tensor-parallel-size 2',
        'bash ~/launch_vllm_auto.sh --model <model-name>',
        'bash ~/stop_vllm.sh',
        'pkill -f vllm'
      ],
      lmstudio: [
        'Open LM Studio application',
        'Go to Local Server tab',
        'Click "Start Server"',
        'Load a model in Chat tab',
        'Use API at http://localhost:1234',
        'View docs at http://localhost:1234/docs'
      ]
    };

    return commands[provider] || [];
  }

  async getProviderPaths(): Promise<{ [key: string]: string }> {
    // Return the actual paths from your system
    return {
      ollama: 'C:\\Users\\bcmad\\AppData\\Local\\Programs\\Ollama\\ollama.exe',
      lmstudio: 'C:\\Users\\bcmad\\AppData\\Local\\Programs\\LM Studio\\LM Studio.exe',
      vllm: 'Ubuntu/WSL (~/launch_vllm_auto.sh)'
    };
  }
}