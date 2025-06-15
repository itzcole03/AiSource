#!/usr/bin/env python3
"""
vLLM Dashboard Plugin for Ultimate Copilot

A simple dashboard plugin that adds vLLM monitoring and control capabilities
to the Ultimate Copilot dashboard.
"""

import asyncio
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from datetime import datetime
import threading

try:
    from vllm_integration import vllm_manager, get_vllm_status_sync
    VLLM_AVAILABLE = True
except ImportError:
    VLLM_AVAILABLE = False
    vllm_manager = None
    get_vllm_status_sync = None

logger = logging.getLogger(__name__)

class VLLMDashboardPlugin:
    """vLLM integration plugin for the Ultimate Copilot dashboard"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.name = "vLLM Monitor"
        self.version = "1.0"
        self.status_data = {}
        self.ui_widgets = {}
        self.auto_refresh = True
        self.refresh_interval = 10  # seconds
        self.refresh_thread = None
        self.running = False
        
        # Initialize vLLM manager if available
        if VLLM_AVAILABLE and vllm_manager:
            vllm_manager.base_url = base_url
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "vLLM server monitoring and control",
            "base_url": self.base_url,
            "vllm_available": VLLM_AVAILABLE,
            "capabilities": ["status_monitoring", "model_listing", "health_check"]
        }
    
    def create_ui(self, parent) -> tk.Widget:
        """Create the vLLM monitoring UI"""
        main_frame = ttk.Frame(parent)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = ttk.Label(header_frame, text="vLLM Server Monitor", 
                               font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_indicator = ttk.Label(header_frame, text="●", foreground="gray")
        self.status_indicator.pack(side=tk.RIGHT)
        
        # Server info frame
        info_frame = ttk.LabelFrame(main_frame, text="Server Information")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Server URL
        url_frame = ttk.Frame(info_frame)
        url_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(url_frame, text="Server URL:").pack(side=tk.LEFT)
        self.url_label = ttk.Label(url_frame, text=self.base_url, foreground="blue")
        self.url_label.pack(side=tk.LEFT, padx=5)
        
        # Status
        status_frame = ttk.Frame(info_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_text = ttk.Label(status_frame, text="Checking...")
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        # Models frame
        models_frame = ttk.LabelFrame(main_frame, text="Available Models")
        models_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Models listbox with scrollbar
        list_frame = ttk.Frame(models_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.models_listbox = tk.Listbox(list_frame)
        models_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                        command=self.models_listbox.yview)
        self.models_listbox.configure(yscrollcommand=models_scrollbar.set)
        
        self.models_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        models_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Refresh button
        ttk.Button(controls_frame, text="Refresh Status", 
                  command=self._manual_refresh).pack(side=tk.LEFT, padx=5)
        
        # Test connection button
        ttk.Button(controls_frame, text="Test Connection", 
                  command=self._test_connection).pack(side=tk.LEFT, padx=5)
        
        # Store widget references
        self.ui_widgets = {
            'main_frame': main_frame,
            'status_indicator': self.status_indicator,
            'status_text': self.status_text,
            'models_listbox': self.models_listbox,
            'url_label': self.url_label
        }
        
        # Start monitoring
        self.start_monitoring()
        
        return main_frame
    
    def start_monitoring(self):
        """Start the monitoring background thread"""
        if not self.running:
            self.running = True
            self.refresh_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.refresh_thread.start()
    
    def stop_monitoring(self):
        """Stop the monitoring background thread"""
        self.running = False
        if self.refresh_thread:
            self.refresh_thread.join(timeout=2)
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                if self.auto_refresh:
                    self._update_status()
                
                # Sleep for the refresh interval
                for _ in range(self.refresh_interval * 10):  # Check every 0.1 seconds
                    if not self.running:
                        break
                    threading.Event().wait(0.1)
                    
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                threading.Event().wait(5)  # Wait 5 seconds on error
    
    def _update_status(self):
        """Update vLLM status data"""
        try:
            if VLLM_AVAILABLE and get_vllm_status_sync:
                self.status_data = get_vllm_status_sync()
            else:
                self.status_data = {
                    "status": "unavailable",
                    "error_message": "vLLM integration not available",
                    "models": [],
                    "last_check": datetime.now().isoformat()
                }
            
            # Update UI in main thread
            if hasattr(self, 'ui_widgets') and self.ui_widgets:
                self._schedule_ui_update()
                
        except Exception as e:
            logger.error(f"Failed to update vLLM status: {e}")
            self.status_data = {
                "status": "error",
                "error_message": str(e),
                "models": [],
                "last_check": datetime.now().isoformat()
            }
    
    def _schedule_ui_update(self):
        """Schedule UI update in the main thread"""
        if self.ui_widgets.get('main_frame'):
            try:
                self.ui_widgets['main_frame'].after_idle(self._update_ui)
            except:
                pass  # Widget might be destroyed
    
    def _update_ui(self):
        """Update UI elements with current status"""
        try:
            status = self.status_data.get("status", "unknown")
            
            # Update status indicator and text
            if status == "running":
                self.status_indicator.config(text="●", foreground="green")
                self.status_text.config(text="Online", foreground="green")
            elif status == "not_running":
                self.status_indicator.config(text="●", foreground="red")
                self.status_text.config(text="Offline", foreground="red")
            elif status == "unavailable":
                self.status_indicator.config(text="●", foreground="gray")
                self.status_text.config(text="Unavailable", foreground="gray")
            else:
                self.status_indicator.config(text="●", foreground="orange")
                self.status_text.config(text="Error", foreground="orange")
            
            # Update models list
            models = self.status_data.get("models", [])
            self.models_listbox.delete(0, tk.END)
            for model in models:
                self.models_listbox.insert(tk.END, model)
            
            if not models:
                self.models_listbox.insert(tk.END, "No models available")
                
        except Exception as e:
            logger.error(f"Failed to update UI: {e}")
    
    def _manual_refresh(self):
        """Manually refresh status"""
        self._update_status()
    
    def _test_connection(self):
        """Test connection to vLLM server"""
        self._update_status()
        status = self.status_data.get("status", "unknown")
        
        if status == "running":
            messagebox.showinfo("Connection Test", 
                              f"✅ Successfully connected to vLLM server!\n"
                              f"Found {len(self.status_data.get('models', []))} model(s)")
        elif status == "unavailable":
            messagebox.showwarning("Connection Test", 
                                 "⚠️ vLLM integration is not available.\n"
                                 "Please ensure the vLLM integration module is installed.")
        else:
            error_msg = self.status_data.get("error_message", "Unknown error")
            messagebox.showerror("Connection Test", 
                               f"❌ Failed to connect to vLLM server.\n"
                               f"Error: {error_msg}")
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the current status"""
        return {
            "name": "vLLM",
            "status": self.status_data.get("status", "unknown"),
            "models": len(self.status_data.get("models", [])),
            "last_check": self.status_data.get("last_check"),
            "base_url": self.base_url
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_monitoring()

# Factory function for easy integration
def create_vllm_plugin(base_url: str = "http://localhost:8000") -> VLLMDashboardPlugin:
    """Create a vLLM dashboard plugin instance"""
    return VLLMDashboardPlugin(base_url)

if __name__ == "__main__":
    # Simple test
    import tkinter as tk
    
    root = tk.Tk()
    root.title("vLLM Plugin Test")
    root.geometry("600x500")
    
    plugin = VLLMDashboardPlugin()
    ui = plugin.create_ui(root)
    ui.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
    plugin.cleanup()
