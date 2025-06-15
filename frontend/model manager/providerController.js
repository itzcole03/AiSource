// providerController.js
// Unified cross-platform provider control for VLLM (WSL), Ollama & LM Studio (Windows)
const { exec } = require('child_process');
const path = require('path');

class ProviderController {
  constructor() {
    this.providers = {
      vllm: {
        start: (modelPath) => `wsl bash ~/launch_vllm_noninteractive.sh "${modelPath}"`,
        stop: 'wsl bash ~/stop_vllm.sh',
        status: 'wsl bash ~/vllm_server_status.sh',
        log: 'wsl cat ~/vllm_server.log',
      },
      ollama: {
        start: path.join(__dirname, 'start_ollama_silent.bat'),
        stop: path.join(__dirname, 'stop_ollama_silent.bat'),
        status: path.join(__dirname, 'status_ollama_silent.bat'),
        log: path.join(__dirname, 'ollama_server.log'),
      },
      lmstudio: {
        start: path.join(__dirname, 'start_lmstudio_silent.bat'),
        stop: path.join(__dirname, 'stop_lmstudio_silent.bat'),
        status: path.join(__dirname, 'status_lmstudio_silent.bat'),
        log: path.join(__dirname, 'lmstudio_server.log'),
      },
    };
  }

  async executeCommand(command, provider, modelPath) {
    let cmd;
    if (typeof this.providers[provider][command] === 'function') {
      cmd = this.providers[provider][command](modelPath);
    } else {
      cmd = `"${this.providers[provider][command]}"`;
    }
    return new Promise((resolve) => {
      exec(cmd, { windowsHide: true }, (error, stdout, stderr) => {
        try {
          const result = stdout ? JSON.parse(stdout) : { status: 'error', message: stderr || 'Unknown error' };
          resolve(result);
        } catch (e) {
          resolve({ status: 'error', message: 'Failed to parse command output' });
        }
      });
    });
  }

  async startProvider(provider, modelPath) {
    return this.executeCommand('start', provider, modelPath);
  }

  async stopProvider(provider) {
    return this.executeCommand('stop', provider);
  }

  async getProviderStatus(provider) {
    return this.executeCommand('status', provider);
  }

  async getProviderLog(provider) {
    if (provider === 'vllm') {
      return this.executeCommand('log', provider);
    } else {
      // For Windows providers, just read the log file
      return new Promise((resolve) => {
        require('fs').readFile(this.providers[provider].log, 'utf8', (error, data) => {
          resolve({ status: 'success', message: data });
        });
      });
    }
  }
}

module.exports = ProviderController;
