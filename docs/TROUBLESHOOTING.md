# Ultimate Copilot System - Troubleshooting Guide

## 🔧 Common Issues and Solutions

### 1. System Won't Start

#### Issue: "Python is not installed or not in PATH"
**Solution:**
```bash
# Install Python 3.8+ from python.org
# Verify installation:
python --version

# If still not working, add Python to PATH:
# Windows: Add Python installation directory to System PATH
```

#### Issue: "Module not found" errors
**Solution:**
```bash
# Install dependencies:
pip install -r requirements.txt

# If specific module missing:
pip install [module-name]

# For development dependencies:
pip install -r requirements.txt --upgrade
```

#### Issue: "Configuration file not found"
**Solution:**
```bash
# Copy example configurations:
copy config\system_config.yaml.example config\system_config.yaml
copy config\hybrid_config.yaml.example config\hybrid_config.yaml
```

### 2. VRAM and Memory Issues

#### Issue: "VRAM usage critically high"
**Solution:**
```yaml
# In config/system_config.yaml, reduce max VRAM:
vram:
  max_usage_gb: 6.0  # Reduce from 7.5
  aggressive_cleanup: true
  enable_model_rotation: true
```

#### Issue: Models not loading
**Solution:**
```bash
# Check available VRAM:
# 1. Close other GPU-intensive applications
# 2. Restart the system
# 3. Use smaller models:

# In config, prefer smaller models:
agents:
  architect:
    model: "ollama/phi-2"  # Smaller model
```

#### Issue: System running slowly
**Solution:**
```yaml
# Optimize performance settings:
tasks:
  max_concurrent: 1  # Reduce from 3
  
vram:
  aggressive_cleanup: true
  monitor_interval: 15  # More frequent cleanup
```

### 3. Integration Issues

#### Issue: Void Editor not connecting
**Solution:**
```bash
# 1. Verify Void Editor is running
# 2. Check WebSocket port (default 8766):
netstat -an | findstr 8766

# 3. In config/system_config.yaml:
integrations:
  void_editor:
    enabled: true
    websocket_port: 8766  # Verify correct port
```

#### Issue: VS Code integration not working
**Solution:**
```bash
# 1. Ensure VS Code Insiders is installed
# 2. Check if extension is needed
# 3. Verify configuration:

integrations:
  vscode:
    enabled: true
    websocket_port: 8765
```

#### Issue: Dashboard not accessible
**Solution:**
```bash
# 1. Check if port 8501 is available:
netstat -an | findstr 8501

# 2. Start dashboard manually:
python start_dashboard.py

# 3. Try different port:
streamlit run frontend/dashboard.py --server.port 8502
```

### 4. Model Provider Issues

#### Issue: Ollama not detected
**Solution:**
```bash
# 1. Verify Ollama is running:
curl http://localhost:11434/api/tags

# 2. Start Ollama if not running:
ollama serve

# 3. Check configuration:
llm_providers:
  ollama:
    base_url: "http://localhost:11434"
    enabled: true
```

#### Issue: LM Studio not connecting
**Solution:**
```bash
# 1. Ensure LM Studio server is running on port 1234
# 2. Check LM Studio settings for API access
# 3. Verify configuration:

llm_providers:
  lmstudio:
    base_url: "http://localhost:1234"
    enabled: true
```

#### Issue: No models available
**Solution:**
```bash
# For Ollama:
ollama pull llama3
ollama pull codellama
ollama pull mistral

# For LM Studio:
# Download models through LM Studio interface

# Verify models are loaded:
# Check dashboard or logs for model detection
```

### 5. CodeGPT Integration Issues

#### Issue: "CodeGPT API credentials not found"
**Solution:**
```bash
# Set environment variables:
set CODEGPT_API_KEY=your_api_key_here
set CODEGPT_ORG_ID=your_org_id_here

# Or add to config/hybrid_config.yaml:
codegpt:
  api_key: "your_api_key_here"
  org_id: "your_org_id_here"
```

#### Issue: "CodeGPT quota exceeded"
**Solution:**
```yaml
# This is expected with free tier (3/30 requests)
# Options:
# 1. Disable CodeGPT integration:
codegpt:
  enabled: false

# 2. Use custom agents only:
routing:
  prefer_custom: true
  fallback_to_custom: true
```

### 6. Performance Issues

#### Issue: Slow response times
**Solution:**
```yaml
# 1. Reduce concurrent tasks:
tasks:
  max_concurrent: 1

# 2. Use faster models:
agents:
  orchestrator:
    model: "ollama/phi-2"  # Faster, smaller model

# 3. Enable aggressive cleanup:
vram:
  aggressive_cleanup: true
```

#### Issue: High CPU usage
**Solution:**
```yaml
# 1. Reduce monitoring frequency:
monitoring:
  metrics_interval: 120  # Increase from 60
  health_check_interval: 60  # Increase from 30

# 2. Disable debug logging:
logging:
  level: "WARNING"  # Reduce from INFO
```

### 7. Network and Connectivity Issues

#### Issue: "Connection refused" errors
**Solution:**
```bash
# 1. Check if required services are running:
# - Ollama: curl http://localhost:11434/api/tags
# - LM Studio: curl http://localhost:1234/v1/models
# - Qdrant: curl http://localhost:6333/collections

# 2. Check firewall settings
# 3. Verify port availability:
netstat -an | findstr "11434 1234 6333 8501"
```

#### Issue: WebSocket connection failures
**Solution:**
```yaml
# Increase timeout settings:
integrations:
  void_editor:
    connection_timeout: 30
    retry_attempts: 5
    retry_delay: 5
```

## 🔍 Diagnostic Commands

### System Health Check
```bash
# Use the built-in status checker:
start.bat
# Choose option 5: "Show System Status"
```

### Manual Diagnostics
```bash
# Check Python environment:
python --version
pip list | findstr "fastapi streamlit aiohttp"

# Check service availability:
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:1234/v1/models  # LM Studio
curl http://localhost:6333/collections  # Qdrant

# Check log files:
type logs\system.log | findstr ERROR
type logs\system.log | findstr WARNING
```

### Performance Monitoring
```bash
# Monitor VRAM usage:
# Check dashboard at http://localhost:8501

# Monitor system resources:
# Task Manager > Performance > GPU
```

## 📋 Debug Mode

### Enable Debug Logging
```yaml
# In config/system_config.yaml:
system:
  debug: true

logging:
  level: "DEBUG"
```

### Verbose Output
```bash
# Start with debug environment:
set LOG_LEVEL=DEBUG
python main.py
```

## 🆘 Getting Help

### Log Files to Check
1. `logs/system.log` - Main system log
2. `logs/agent_*.log` - Individual agent logs
3. Console output - Real-time status

### Information to Provide When Seeking Help
1. **System specs**: RAM, GPU, OS version
2. **Python version**: `python --version`
3. **Error messages**: Full error text from logs
4. **Configuration**: Relevant config file sections
5. **Steps to reproduce**: What you were doing when the issue occurred

### Common Log Patterns
```bash
# Look for these patterns in logs:
findstr "ERROR" logs\system.log
findstr "Failed" logs\system.log
findstr "Connection" logs\system.log
findstr "VRAM" logs\system.log
```

---

**Most issues can be resolved by checking logs, verifying configurations, and ensuring all required services are running.**