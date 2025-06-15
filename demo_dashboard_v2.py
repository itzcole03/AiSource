#!/usr/bin/env python3
"""
Ultimate Copilot Dashboard v2 - Demo Script

This script demonstrates the enhanced dashboard with external app integration.
Run this to see the dashboard in action.
"""

import json
import logging
from pathlib import Path

def create_demo_config():
    """Create a demo configuration for testing"""
    demo_config = {
        "dashboard": {
            "theme": "default",
            "refresh_interval": 5,
            "auto_refresh": True,
            "window_geometry": "1400x900"
        },
        "external_app": {
            "enabled": True,
            "use_mock": True,  # Use mock mode for demo
            "executable": "mock_app.exe",
            "communication": "api",
            "embed_method": "window",
            "auto_launch": True
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
        }
    }
    
    # Save demo config
    with open("demo_config.json", "w") as f:
        json.dump(demo_config, f, indent=2)
    
    print("✅ Created demo configuration (demo_config.json)")
    return demo_config

def main():
    """Main demo function"""
    print("🚀 Ultimate Copilot Dashboard v2 - Demo")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create demo configuration
        config = create_demo_config()
        
        # Import dashboard
        print("📦 Loading dashboard module...")
        from simple_dashboard_v2 import SimpleDashboard
        print("✅ Dashboard module loaded")
        
        # Create dashboard instance
        print("🔧 Creating dashboard instance...")
        dashboard = SimpleDashboard(config)
        print("✅ Dashboard instance created")
        
        # Initialize
        print("⚡ Initializing dashboard...")
        success = dashboard.initialize()
        
        if success:
            print("✅ Dashboard initialized successfully!")
            print("\n🎯 Dashboard Features:")
            print("   • Model Provider Control with External App Integration")
            print("   • System Overview and Monitoring")
            print("   • Real-time Status Updates")
            print("   • Professional Modern UI")
            print("\n📋 Integration Points for Your App:")
            print("   • Dedicated tab in 'Model Providers'")
            print("   • API communication framework")
            print("   • Window embedding capabilities")
            print("   • Event-driven synchronization")
            
            print("\n🚀 Launching dashboard GUI...")
            print("   (Close the window to exit)")
            
            # Run dashboard
            dashboard.run()
            
        else:
            print("❌ Dashboard initialization failed")
            return 1
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure simple_dashboard_v2.py is in the current directory")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n👋 Demo completed successfully!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
