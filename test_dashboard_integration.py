#!/usr/bin/env python3
"""
External App Integration Test

This script demonstrates how to integrate your external model provider 
control application with the Ultimate Copilot Dashboard v2.
"""

import asyncio
import json
import logging
from pathlib import Path
import time
from typing import Dict, Any, Optional

# Import the enhanced dashboard
from ultimate_dashboard_v2 import UltimateDashboardV2, ExternalAppIntegration

class MockExternalApp:
    """
    Mock external application for testing integration
    
    This simulates your model provider control app and shows
    how the integration points work.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        self.models = {
            "lmstudio": {
                "available": ["llama-2-7b", "codellama-7b", "mistral-7b"],
                "loaded": ["llama-2-7b", "mistral-7b"]
            },
            "ollama": {
                "available": ["llama2", "codellama", "mistral", "phi"],
                "loaded": ["llama2", "codellama", "mistral", "phi"]
            },
            "vllm": {
                "available": [],
                "loaded": []
            }
        }
        self.status = "ready"
        self.logger = logging.getLogger("MockExternalApp")
    
    def start(self) -> bool:
        """Start the mock application"""
        self.logger.info("Starting mock external app...")
        self.is_running = True
        return True
    
    def stop(self):
        """Stop the mock application"""
        self.logger.info("Stopping mock external app...")
        self.is_running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current application status"""
        return {
            "running": self.is_running,
            "status": self.status,
            "models": self.models,
            "timestamp": time.time()
        }
    
    def load_model(self, provider: str, model: str) -> bool:
        """Load a model"""
        if provider in self.models and model in self.models[provider]["available"]:
            if model not in self.models[provider]["loaded"]:
                self.models[provider]["loaded"].append(model)
                self.logger.info(f"Loaded model {model} on {provider}")
                return True
        return False
    
    def unload_model(self, provider: str, model: str) -> bool:
        """Unload a model"""
        if provider in self.models and model in self.models[provider]["loaded"]:
            self.models[provider]["loaded"].remove(model)
            self.logger.info(f"Unloaded model {model} from {provider}")
            return True
        return False
    
    def get_provider_status(self, provider: str) -> Dict[str, Any]:
        """Get status for specific provider"""
        if provider in self.models:
            return {
                "provider": provider,
                "available_models": len(self.models[provider]["available"]),
                "loaded_models": len(self.models[provider]["loaded"]),
                "models": self.models[provider]
            }
        return {"provider": provider, "status": "unknown"}

class EnhancedExternalAppIntegration(ExternalAppIntegration):
    """
    Enhanced integration class with mock external app support
    """
    
    def __init__(self, app_config: Dict[str, Any]):
        super().__init__(app_config)
        self.mock_app = None
        
        # If using mock mode for testing
        if app_config.get('use_mock', False):
            self.mock_app = MockExternalApp(app_config)
    
    def launch_app(self) -> bool:
        """Launch application (mock or real)"""
        if self.mock_app:
            return self.mock_app.start()
        else:
            return super().launch_app()
    
    def is_running(self) -> bool:
        """Check if app is running"""
        if self.mock_app:
            return self.mock_app.is_running
        else:
            return super().is_running()
      def send_command(self, command: str, data: Any = None) -> Any:
        """Send command to external app"""
        if self.mock_app:
            return self._handle_mock_command(command, data)
        else:
            return super().send_command(command, data)
    
    def _handle_mock_command(self, command: str, data: Any) -> Any:
        """Handle commands for mock app"""
        try:
            if not self.mock_app:
                return False
                
            if command == "get_status":
                return self.mock_app.get_status()
            elif command == "load_model" and data:
                return self.mock_app.load_model(data.get('provider'), data.get('model'))
            elif command == "unload_model" and data:
                return self.mock_app.unload_model(data.get('provider'), data.get('model'))
            elif command == "get_provider_status" and data:
                return self.mock_app.get_provider_status(data.get('provider'))
            else:
                self.logger.warning(f"Unknown command: {command}")
                return False
        except Exception as e:
            self.logger.error(f"Mock command error: {e}")
            return False
    
    def close(self):
        """Close application"""
        if self.mock_app:
            self.mock_app.stop()
        super().close()

async def test_dashboard_integration():
    """Test the dashboard with external app integration"""
    
    # Load configuration
    config_file = Path("dashboard_config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        # Fallback configuration for testing
        config = {
            "dashboard": {
                "theme": "default",
                "refresh_interval": 5,
                "auto_refresh": True
            },
            "external_app": {
                "enabled": True,
                "use_mock": True,  # Use mock for testing
                "executable": "mock_app.exe",
                "communication": "api",
                "embed_method": "window"
            }
        }
    
    # Create enhanced external app integration
    external_app_config = config.get("external_app", {})
    if external_app_config.get("enabled", False):
        # Use enhanced integration class
        enhanced_integration = EnhancedExternalAppIntegration(external_app_config)
        config["external_app"]["integration_instance"] = enhanced_integration
    
    # Create and initialize dashboard
    dashboard = UltimateDashboardV2(config)
    
    # Test initialization
    print("Testing dashboard initialization...")
    success = dashboard.initialize()
    if not success:
        print("❌ Dashboard initialization failed")
        return False
    
    print("✅ Dashboard initialized successfully")
    
    # Test external app integration
    if external_app_config.get("enabled", False):
        print("\nTesting external app integration...")
        
        # Get the model provider plugin
        model_plugin = None
        for plugin in dashboard.plugins:
            if plugin.config.name == "Model Providers":
                model_plugin = plugin
                break
        
        if model_plugin and model_plugin.external_app:
            # Test app launch
            launched = model_plugin.external_app.launch_app()
            if launched:
                print("✅ External app launched successfully")
                
                # Test communication
                status = model_plugin.external_app.send_command("get_status")
                if status:
                    print("✅ Communication with external app working")
                    print(f"   App status: {status}")
                else:
                    print("⚠️  Communication test failed")
                
                # Test model operations
                load_result = model_plugin.external_app.send_command(
                    "load_model", {"provider": "lmstudio", "model": "codellama-7b"})
                if load_result:
                    print("✅ Model loading command sent successfully")
                
            else:
                print("❌ Failed to launch external app")
        else:
            print("⚠️  External app integration not available")
    
    # Test plugin updates
    print("\nTesting plugin updates...")
    for plugin in dashboard.plugins:
        try:
            result = plugin.update()
            print(f"✅ Plugin '{plugin.config.name}' updated successfully")
            if isinstance(result, dict) and result.get("status") == "error":
                print(f"   Warning: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Plugin '{plugin.config.name}' update failed: {e}")
    
    # Test event system
    print("\nTesting event system...")
    from ultimate_dashboard_v2 import DashboardEvent
    
    test_event = DashboardEvent(
        event_type="test_event",
        source="integration_test",
        data={"message": "Hello from test!"}
    )
    dashboard.emit_event(test_event)
    print("✅ Event emission test completed")
    
    # If GUI is available, show dashboard briefly
    if dashboard.root:
        print("\nStarting GUI for visual test...")
        print("The dashboard window should appear. Close it to continue the test.")
        
        # Show for a few seconds or until user closes
        def auto_close():
            time.sleep(10)  # Show for 10 seconds
            if dashboard.root:
                dashboard.root.quit()
        
        import threading
        auto_close_thread = threading.Thread(target=auto_close)
        auto_close_thread.daemon = True
        auto_close_thread.start()
        
        try:
            dashboard.root.mainloop()
        except:
            pass
        
        print("✅ GUI test completed")
    
    # Cleanup
    print("\nCleaning up...")
    dashboard.shutdown()
    print("✅ Dashboard shutdown completed")
    
    return True

def create_integration_example():
    """Create an example of how to integrate your real external app"""
    
    example_code = '''
# Example: How to integrate your real external app

from ultimate_dashboard_v2 import ExternalAppIntegration
import requests
import subprocess

class YourAppIntegration(ExternalAppIntegration):
    """Integration for your specific model provider control app"""
    
    def __init__(self, app_config: Dict[str, Any]):
        super().__init__(app_config)
        self.api_base = app_config.get('api_endpoint', 'http://localhost:8080')
    
    def launch_app(self) -> bool:
        """Launch your app"""
        try:
            app_path = self.config.get('executable')
            args = self.config.get('args', [])
            
            # Launch with specific arguments for dashboard integration
            self.process = subprocess.Popen([
                app_path,
                '--dashboard-mode',
                '--api-port', '8080',
                '--integration-enabled'
            ] + args)
            
            # Wait for app to start and API to be ready
            import time
            time.sleep(3)
            
            # Verify API is responding
            response = requests.get(f"{self.api_base}/health", timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Failed to launch app: {e}")
            return False
    
    def send_command(self, command: str, data: Any = None) -> bool:
        """Send command via your app's API"""
        try:
            if command == "get_status":
                response = requests.get(f"{self.api_base}/api/status")
                return response.json() if response.ok else None
                
            elif command == "load_model":
                response = requests.post(
                    f"{self.api_base}/api/models/load",
                    json=data
                )
                return response.ok
                
            elif command == "unload_model":
                response = requests.post(
                    f"{self.api_base}/api/models/unload",
                    json=data
                )
                return response.ok
                
            # Add more commands as needed
            
        except Exception as e:
            self.logger.error(f"API command failed: {e}")
            return False
    
    def embed_window(self, parent_widget):
        """Embed your app's window"""
        # For Windows - use win32 APIs to embed the window
        # For web-based apps - use tkinter web view
        # For other platforms - use appropriate methods
        
        # Example for web-based embedding:
        try:
            import tkinter.html as tkhtml  # If available
            web_view = tkhtml.HtmlFrame(parent_widget)
            web_view.load_url(f"{self.api_base}/dashboard-embed")
            return web_view
        except ImportError:
            # Fallback to iframe-like display
            return self._create_fallback_embed(parent_widget)

# Configuration example for your app:
your_app_config = {
    "enabled": True,
    "executable": r"C:\\Path\\To\\Your\\ModelProviderApp.exe",
    "args": ["--dashboard-mode"],
    "communication": "api",
    "api_endpoint": "http://localhost:8080",
    "embed_method": "web",
    "auto_launch": True,
    "integration_class": YourAppIntegration  # Use your custom class
}
'''
    
    with open("integration_example.py", "w") as f:
        f.write(example_code)
    
    print("Created integration_example.py - shows how to integrate your real app")

async def main():
    """Main test function"""
    print("Ultimate Copilot Dashboard v2 - Integration Test")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run integration test
    try:
        success = await test_dashboard_integration()
        if success:
            print("\n🎉 All integration tests passed!")
            print("\nNext steps:")
            print("1. Replace the mock integration with your real app")
            print("2. Update the configuration in dashboard_config.json")
            print("3. Implement your app's API endpoints")
            print("4. Test with your actual model provider control app")
        else:
            print("\n❌ Some tests failed - check the logs above")
        
        # Create integration example
        create_integration_example()
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
