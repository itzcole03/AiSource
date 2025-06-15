# Ultimate Copilot Dashboard v2 - External App Integration Guide

## Overview

The Ultimate Copilot Dashboard v2 provides a comprehensive framework for integrating your external model provider control application. This guide explains how to seamlessly integrate your app into the dashboard for unified control and monitoring.

## Integration Methods

### 1. Plugin-Based Integration

The dashboard uses a plugin architecture where your app can be integrated as a plugin:

```python
from ultimate_dashboard_v2 import DashboardPlugin, PluginConfig

class YourModelControlPlugin(DashboardPlugin):
    def __init__(self, external_app_config):
        super().__init__(PluginConfig(name="Your Model Control", order=1))
        self.external_app = YourAppIntegration(external_app_config)
    
    def get_metadata(self):
        return {
            "name": "Your Model Provider Control",
            "version": "1.0",
            "description": "Integration with your model provider app"
        }
    
    def initialize(self, dashboard_context):
        self.dashboard_context = dashboard_context
        return self.external_app.launch_app()
    
    def create_ui(self, parent):
        # Create your custom UI here
        return self.external_app.embed_window(parent)
    
    def update(self):
        # Update data from your app
        return self.external_app.send_command("get_status")
```

### 2. Window Embedding

Your app's window can be embedded directly into the dashboard:

```python
class YourAppIntegration:
    def embed_window(self, parent_widget):
        """Embed your app's window into the dashboard"""
        
        # Method 1: Native window embedding (Windows)
        if platform.system() == "Windows":
            return self._embed_windows_native(parent_widget)
        
        # Method 2: Web view embedding
        elif self.config.get('web_interface'):
            return self._embed_web_view(parent_widget)
        
        # Method 3: Custom widget
        else:
            return self._create_custom_widget(parent_widget)
    
    def _embed_windows_native(self, parent):
        """Embed using Windows native APIs"""
        import win32gui
        import win32con
        
        # Find your app's window
        hwnd = win32gui.FindWindow(None, "Your App Window Title")
        if hwnd:
            # Embed into tkinter frame
            frame = tk.Frame(parent)
            frame_id = frame.winfo_id()
            win32gui.SetParent(hwnd, frame_id)
            return frame
        return None
    
    def _embed_web_view(self, parent):
        """Embed web interface"""
        try:
            import tkinter.html as tkhtml
            web_view = tkhtml.HtmlFrame(parent)
            web_view.load_url(f"{self.api_base}/dashboard-embed")
            return web_view
        except ImportError:
            # Fallback to iframe-like display
            return self._create_web_fallback(parent)
```

### 3. API Communication

Communicate with your app through its API:

```python
class YourAppIntegration:
    def __init__(self, config):
        self.api_base = config.get('api_endpoint', 'http://localhost:8080')
        self.api_key = config.get('api_key', '')
    
    def send_command(self, command, data=None):
        """Send command to your app's API"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
        }
        
        try:
            if command == "get_status":
                response = requests.get(f"{self.api_base}/api/status", headers=headers)
                return response.json() if response.ok else None
            
            elif command == "load_model":
                response = requests.post(
                    f"{self.api_base}/api/models/load",
                    json=data,
                    headers=headers
                )
                return response.ok
            
            elif command == "unload_model":
                response = requests.post(
                    f"{self.api_base}/api/models/unload",
                    json=data,
                    headers=headers
                )
                return response.ok
            
            elif command == "get_models":
                response = requests.get(f"{self.api_base}/api/models", headers=headers)
                return response.json() if response.ok else []
            
            elif command == "get_providers":
                response = requests.get(f"{self.api_base}/api/providers", headers=headers)
                return response.json() if response.ok else []
            
        except Exception as e:
            self.logger.error(f"API call failed: {e}")
            return None
```

## Configuration

### Dashboard Configuration (dashboard_config.json)

```json
{
  "external_app": {
    "enabled": true,
    "executable": "C:\\Path\\To\\Your\\ModelProviderApp.exe",
    "args": ["--dashboard-mode", "--api-port", "8080"],
    "working_directory": "C:\\Path\\To\\Your\\App",
    "communication": "api",
    "api_endpoint": "http://localhost:8080",
    "api_key": "your-api-key-if-needed",
    "embed_method": "window",
    "window_title": "Your Model Provider Control",
    "auto_launch": true,
    "sync_interval": 10,
    "timeout": 30
  }
}
```

### Your App's Integration Configuration

Your app should support these command-line arguments for dashboard integration:

- `--dashboard-mode`: Run in dashboard integration mode
- `--api-port <port>`: Specify API port for communication
- `--integration-enabled`: Enable integration features
- `--embed-ready`: Prepare for window embedding

## Required API Endpoints

Your app should provide these API endpoints for dashboard integration:

### Health Check
```
GET /health
Response: {"status": "ok", "version": "1.0"}
```

### System Status
```
GET /api/status
Response: {
  "running": true,
  "models_loaded": 5,
  "memory_usage": "4.2GB",
  "providers": ["lmstudio", "ollama"]
}
```

### Model Management
```
GET /api/models
Response: [
  {
    "id": "llama-2-7b",
    "provider": "lmstudio",
    "status": "loaded",
    "memory_usage": "4.1GB"
  }
]

POST /api/models/load
Body: {"model_id": "llama-2-7b", "provider": "lmstudio"}
Response: {"success": true, "message": "Model loaded"}

POST /api/models/unload
Body: {"model_id": "llama-2-7b"}
Response: {"success": true, "message": "Model unloaded"}
```

### Provider Management
```
GET /api/providers
Response: [
  {
    "name": "lmstudio",
    "status": "connected",
    "endpoint": "http://localhost:1234",
    "models_available": 17,
    "models_loaded": 3
  }
]
```

### Dashboard Embedding
```
GET /dashboard-embed
Response: HTML page optimized for embedding in dashboard
```

## Event System Integration

Your app can send events to the dashboard:

```python
# In your app's integration code
def notify_dashboard(event_type, data):
    """Send event to dashboard"""
    webhook_url = "http://localhost:9090/webhooks/events"
    payload = {
        "event_type": event_type,
        "source": "your_app",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print(f"Failed to notify dashboard: {e}")

# Example usage
notify_dashboard("model_loaded", {
    "model_id": "llama-2-7b",
    "provider": "lmstudio",
    "memory_usage": "4.1GB"
})

notify_dashboard("provider_status_changed", {
    "provider": "ollama",
    "status": "connected",
    "models_count": 14
})
```

## Step-by-Step Integration

### 1. Prepare Your App

1. Add command-line argument support for dashboard mode
2. Implement the required API endpoints
3. Add window embedding support (optional)
4. Test API functionality independently

### 2. Create Integration Class

1. Copy the integration template from `integration_example.py`
2. Customize for your app's specific API
3. Implement window embedding if needed
4. Add error handling and logging

### 3. Configure Dashboard

1. Update `dashboard_config.json` with your app's details
2. Set correct executable path and arguments
3. Configure API endpoint and authentication
4. Choose embedding method

### 4. Test Integration

1. Run the integration test: `python test_dashboard_integration_fixed.py`
2. Launch dashboard: `python launch_dashboard_v2.py`
3. Verify your app appears in the "Model Providers" tab
4. Test communication and control functions

### 5. Customize UI

1. Modify the plugin's `create_ui` method
2. Add custom controls and displays
3. Implement real-time updates
4. Add error handling and user feedback

## Advanced Features

### Bidirectional Data Sync

```python
class AdvancedIntegration:
    def __init__(self, config):
        self.sync_interval = config.get('sync_interval', 10)
        self.last_sync = None
    
    async def start_sync_loop(self):
        """Start bidirectional data synchronization"""
        while True:
            try:
                # Get data from your app
                app_data = self.send_command("get_full_status")
                
                # Update dashboard
                if self.dashboard_context:
                    self.dashboard_context.update_external_data(app_data)
                
                # Get dashboard data
                dashboard_data = self.dashboard_context.get_system_status()
                
                # Send to your app
                self.send_command("update_dashboard_data", dashboard_data)
                
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                self.logger.error(f"Sync error: {e}")
                await asyncio.sleep(self.sync_interval)
```

### Custom Themes

```python
def apply_custom_theme(self, parent_widget):
    """Apply your app's theme to dashboard integration"""
    style = ttk.Style()
    
    # Define your app's colors
    bg_color = "#2b2b2b"
    fg_color = "#ffffff"
    accent_color = "#007acc"
    
    # Apply theme
    style.configure("YourApp.TFrame", background=bg_color)
    style.configure("YourApp.TLabel", background=bg_color, foreground=fg_color)
    style.configure("YourApp.TButton", background=accent_color, foreground=fg_color)
    
    # Apply to your widgets
    parent_widget.configure(style="YourApp.TFrame")
```

## Troubleshooting

### Common Issues

1. **App won't launch**: Check executable path and permissions
2. **API not responding**: Verify port and endpoint configuration
3. **Window embedding fails**: Check platform compatibility
4. **Events not received**: Verify webhook endpoint and networking

### Debug Mode

Enable debug mode in your integration:

```python
class DebugIntegration(YourAppIntegration):
    def __init__(self, config):
        super().__init__(config)
        self.debug = config.get('debug', False)
        
        if self.debug:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def send_command(self, command, data=None):
        if self.debug:
            print(f"DEBUG: Sending command {command} with data {data}")
        
        result = super().send_command(command, data)
        
        if self.debug:
            print(f"DEBUG: Command result: {result}")
        
        return result
```

## Example Integration

See `integration_example.py` for a complete working example of how to integrate your model provider control app with the Ultimate Copilot Dashboard.

## Support

For additional help with integration:

1. Check the example files provided
2. Review the dashboard source code for plugin patterns
3. Test with the mock integration first
4. Enable debug logging for troubleshooting

The dashboard is designed to be flexible and accommodate various integration patterns. Choose the approach that best fits your app's architecture and capabilities.
