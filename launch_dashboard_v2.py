#!/usr/bin/env python3
"""
Launch Enhanced Ultimate Copilot Dashboard

This script launches the enhanced dashboard with external app integration support.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/dashboard.log', mode='a')
        ]
    )

def load_config() -> dict:
    """Load dashboard configuration"""
    config_file = Path("dashboard_config.json")
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"✅ Loaded configuration from {config_file}")
            return config
        except Exception as e:
            print(f"⚠️  Failed to load config file: {e}")
    
    # Fallback configuration
    default_config = {
        "dashboard": {
            "theme": "default",
            "refresh_interval": 5,
            "auto_refresh": True,
            "window_geometry": "1600x1000"
        },
        "external_app": {
            "enabled": False,  # Disabled by default for initial testing
            "use_mock": True,
            "executable": "",
            "communication": "api",
            "embed_method": "window"
        },
        "providers": {
            "lmstudio": {
                "enabled": True,
                "endpoint": "http://localhost:1234",
                "priority": 1
            },
            "ollama": {
                "enabled": True,
                "endpoint": "http://localhost:11434",
                "priority": 2
            },
            "vllm": {
                "enabled": True,
                "endpoint": "http://localhost:8000",
                "priority": 3
            }
        },
        "memory": {
            "max_vram_mb": 7168,
            "safety_margin_mb": 512
        }
    }
    
    print("ℹ️  Using default configuration")
    return default_config

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import tkinter
        print("✅ Tkinter GUI support available")
    except ImportError:
        missing_deps.append("tkinter")
        print("❌ Tkinter not available - GUI will be disabled")
    
    # Check for optional dependencies
    try:
        import requests
        print("✅ Requests library available for API communication")
    except ImportError:
        print("⚠️  Requests library not available - some features may be limited")
    
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        return False
    
    return True

def main():
    """Main entry point"""
    print("Ultimate Copilot Dashboard v2 - Launch Script")
    print("=" * 50)
    
    # Setup logging
    Path("logs").mkdir(exist_ok=True)
    setup_logging()
    logger = logging.getLogger("Launcher")
    
    try:
        # Check dependencies
        if not check_dependencies():
            print("\n❌ Critical dependencies missing. Please install required packages.")
            return 1
        
        # Load configuration
        config = load_config()
        
        # Import and create dashboard
        print("\nInitializing dashboard...")
        try:
            from ultimate_dashboard_v2 import UltimateDashboardV2
            dashboard = UltimateDashboardV2(config)
        except ImportError as e:
            print(f"❌ Failed to import dashboard: {e}")
            print("Make sure ultimate_dashboard_v2.py exists in the current directory")
            return 1
        
        # Initialize dashboard
        print("Starting dashboard initialization...")
        success = dashboard.initialize()
        
        if not success:
            print("❌ Dashboard initialization failed")
            return 1
        
        print("✅ Dashboard initialized successfully")
        
        # Show configuration summary
        print("\nConfiguration Summary:")
        print(f"  Theme: {config.get('dashboard', {}).get('theme', 'default')}")
        print(f"  Auto-refresh: {config.get('dashboard', {}).get('auto_refresh', True)}")
        print(f"  External app: {'Enabled' if config.get('external_app', {}).get('enabled', False) else 'Disabled'}")
        
        # Run dashboard
        print("\n🚀 Starting Ultimate Copilot Dashboard...")
        print("Close the dashboard window to exit.")
        
        return_code = 0 if dashboard.run() else 1
        
        print("\nDashboard session ended.")
        return return_code
        
    except KeyboardInterrupt:
        print("\n\n⛔ Dashboard interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
