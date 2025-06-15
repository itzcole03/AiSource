# Ultimate Copilot Unified Dashboard

A comprehensive, modern dashboard that consolidates all monitoring and control features for the Ultimate Copilot System into a single, powerful interface.

## Features

### 🖥️ System Overview
- **Real-time system monitoring** with CPU, memory, and VRAM usage
- **Component status tracking** for all system managers
- **Performance metrics** with historical charts
- **System controls** for restart, shutdown, and configuration reload
- **Uptime monitoring** and connection status

### 🤖 Model Management
- **Multi-provider support** for Ollama, LM Studio, vLLM, and OpenAI
- **Model loading/unloading** with one-click controls
- **Provider status monitoring** and health checks
- **Quick model selection** for common models
- **Memory usage tracking** per provider and model

### 👥 Agent Management
- **Agent lifecycle management** (create, monitor, terminate)
- **Real-time agent status** and performance tracking
- **Task assignment** and coordination
- **Agent type selection** (coding, research, general)

### 📋 Logs & Diagnostics
- **Real-time log streaming** with filtering by level
- **System health checks** and diagnostics
- **Log export functionality**
- **Error tracking** and alerting

### ⚙️ Settings & Configuration
- **Dashboard customization** (theme, refresh intervals)
- **Plugin management** (enable/disable, configure)
- **System configuration** management
- **Performance tuning** options

## Architecture

### Backend API Server (`dashboard_backend.py`)
- **FastAPI-based** REST API server
- **WebSocket support** for real-time updates
- **Direct integration** with Ultimate Copilot system components
- **Plugin architecture** for extensibility

### Frontend Dashboard (`unified_dashboard.py`)
- **Streamlit-based** web interface
- **Modern, responsive design** with custom CSS
- **Tab-based navigation** for different features
- **Real-time data updates** via API calls

### Plugin System
- **Modular architecture** for easy extension
- **Hot-reloadable plugins** for development
- **Configuration-driven** plugin management
- **Base plugin classes** for rapid development

## Installation & Setup

### Requirements
- Python 3.8+
- Streamlit
- FastAPI
- Uvicorn
- Plotly
- Pandas
- PyYAML
- Requests
- Psutil

### Quick Start

#### Option 1: Windows Batch Launcher
```bash
# Simply run the batch file
launch_unified_dashboard.bat
```

#### Option 2: Python Launcher
```bash
# Install dependencies
pip install streamlit fastapi uvicorn plotly pandas pyyaml requests psutil

# Launch dashboard
python frontend/launch_dashboard.py
```

#### Option 3: Manual Start
```bash
# Start backend API
python frontend/dashboard_backend.py

# In another terminal, start frontend
streamlit run frontend/unified_dashboard.py
```

### Access Points
- **Dashboard UI**: http://localhost:8501
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## Configuration

### Dashboard Configuration (`frontend/dashboard_config.yaml`)
```yaml
dashboard:
  title: "Ultimate Copilot System"
  theme: "default"
  refresh_interval: 30
  auto_refresh: true

backend:
  url: "http://127.0.0.1:8001"
  timeout: 5

plugins:
  system_monitor:
    enabled: true
    order: 1
  model_manager:
    enabled: true
    order: 2
  # ... more plugins
```

### Provider Configuration
```yaml
providers:
  ollama:
    enabled: true
    endpoint: "http://localhost:11434"
    priority: 1
  lmstudio:
    enabled: true
    endpoint: "http://localhost:1234"
    priority: 2
  # ... more providers
```

## Plugin Development

### Creating a New Plugin

1. **Create plugin file** in `frontend/dashboard_plugins/`
2. **Inherit from StreamlitPlugin**:

```python
from .base_plugin import StreamlitPlugin

class MyPlugin(StreamlitPlugin):
    def get_metadata(self):
        return {
            "name": "My Plugin",
            "version": "1.0.0",
            "description": "My custom plugin"
        }
    
    async def update_data(self):
        # Fetch data from API or system
        return {"my_data": "value"}
    
    def render(self, container):
        with container:
            st.header("My Plugin")
            # Render your UI here
```

3. **Register in plugin manager**
4. **Add to configuration**

### Plugin Capabilities
- **API integration** via `self.fetch_api_data()`
- **Data caching** with `self.cache_data()` and `self.get_cached_data()`
- **Configuration management** via `self.get_config()`
- **Logging** with `self.log_info()`, `self.log_error()`
- **UI helpers** like `self.render_header()`, `self.render_status_indicator()`

## API Endpoints

### System Control
- `GET /system/status` - Get system status
- `GET /system/metrics` - Get performance metrics
- `POST /system/control` - Control system operations

### Model Management
- `GET /models/status` - Get model provider status
- `POST /models/control` - Control model operations

### Agent Management
- `GET /agents/status` - Get agent status
- `POST /agents/control` - Control agent operations

### Logs & Diagnostics
- `GET /logs` - Get system logs
- `WebSocket /ws` - Real-time updates

## Features Consolidated

This unified dashboard consolidates features from multiple previous implementations:

### From Streamlit Dashboard (`frontend/dashboard.py`)
- ✅ Web-based interface
- ✅ Real-time monitoring
- ✅ System control functions
- ✅ Modern UI design

### From Enhanced Dashboard (`enhanced_dashboard.py`)
- ✅ Plugin architecture
- ✅ External app integration framework
- ✅ Modular design

### From Ultimate Dashboard v2 (`ultimate_dashboard_v2.py`)
- ✅ Advanced plugin system
- ✅ Event handling
- ✅ Hot-loading capabilities
- ✅ API endpoints

### From Simple Dashboard v2 (`simple_dashboard_v2.py`)
- ✅ Streamlined core functionality
- ✅ External app integration
- ✅ Mock mode support

### From Ultimate Copilot Dashboard (`ultimate_copilot_dashboard.py`)
- ✅ Comprehensive system integration
- ✅ Direct component access
- ✅ Background monitoring

### From vLLM Dashboard Plugin (`vllm_dashboard_plugin.py`)
- ✅ Specialized provider monitoring
- ✅ Health checks
- ✅ Model listing

## Troubleshooting

### Backend Connection Issues
1. Ensure backend server is running on port 8001
2. Check firewall settings
3. Verify API endpoints are accessible

### Plugin Loading Issues
1. Check plugin file syntax
2. Verify imports are correct
3. Check plugin configuration in YAML

### Performance Issues
1. Adjust refresh intervals
2. Enable/disable caching
3. Reduce history limits
4. Check system resources

## Development

### File Structure
```
frontend/
├── unified_dashboard.py          # Main Streamlit dashboard
├── dashboard_backend.py          # FastAPI backend server
├── launch_dashboard.py           # Python launcher
├── dashboard_config.yaml         # Configuration file
└── dashboard_plugins/            # Plugin system
    ├── __init__.py
    ├── base_plugin.py           # Base plugin classes
    ├── plugin_manager.py        # Plugin management
    ├── system_monitor.py        # System monitoring plugin
    └── model_manager.py         # Model management plugin
```

### Contributing
1. Follow the plugin architecture for new features
2. Use the base plugin classes for consistency
3. Add configuration options to YAML
4. Include proper error handling and logging
5. Test with both mock and real data

## License

Part of the Ultimate Copilot System project.
