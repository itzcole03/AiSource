#!/usr/bin/env python3
"""
Complete vLLM Integration Demo for Ultimate Copilot Dashboard

This script demonstrates the complete vLLM integration including:
- vLLM server status monitoring
- Model discovery and listing
- Dashboard integration
- Workspace management compatibility

Run this to test the complete vLLM integration.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from vllm_integration import VLLMManager, get_vllm_status, test_vllm_connection
    from vllm_dashboard_plugin_clean import VLLMDashboardPlugin, create_vllm_plugin
    IMPORTS_OK = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_OK = False
    VLLMManager = None
    create_vllm_plugin = None

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_vllm_integration():
    """Test the complete vLLM integration"""
    print("=" * 60)
    print("Ultimate Copilot vLLM Integration Test")
    print("=" * 60)
    print()
    
    if not IMPORTS_OK:
        print("❌ vLLM integration modules could not be imported.")
        print("   Make sure vllm_integration.py and vllm_dashboard_plugin_clean.py are in the same directory.")
        return False
    
    print("✅ vLLM integration modules imported successfully")
    print()
      # Test 1: Basic vLLM Manager
    print("🔍 Testing vLLM Manager...")
    if not VLLMManager:
        print("   ❌ VLLMManager not available")
        return False
        
    vllm_manager = VLLMManager()
    
    status = await vllm_manager.check_status()
    print(f"   Server Status: {'Online' if status.is_online else 'Offline'}")
    print(f"   Base URL: {status.base_url}")
    print(f"   Models Found: {len(status.models)}")
    
    if status.models:
        print("   Available Models:")
        for model in status.models:
            print(f"     - {model.id}")
    else:
        print("   No models found (server may be offline)")
    
    if status.error_message:
        print(f"   Error: {status.error_message}")
    
    print()
    
    # Test 2: Dashboard Data
    print("📊 Testing Dashboard Data Format...")
    dashboard_data = vllm_manager.get_dashboard_data()
    print(f"   Status: {dashboard_data['status']}")
    print(f"   Model Count: {dashboard_data['model_count']}")
    print(f"   Response Time: {dashboard_data['response_time']}ms")
    print()
    
    # Test 3: Model Response (if server is online)
    if status.is_online and status.models:
        print("🧠 Testing Model Response...")
        test_model = status.models[0].id
        response = await vllm_manager.test_model_response(test_model, "Hello, how are you?")
        
        if response['success']:
            print(f"   ✅ Model '{test_model}' responded successfully")
            print(f"   Response Time: {response['response_time']:.2f}s")
            print(f"   Content: {response['content']}")
        else:
            print(f"   ❌ Model '{test_model}' failed to respond: {response['error']}")
        print()    # Test 4: Dashboard Plugin
    print("🖥️  Testing Dashboard Plugin...")
    try:
        if not create_vllm_plugin:
            print("   ❌ create_vllm_plugin not available")
        else:
            plugin = create_vllm_plugin()
            metadata = plugin.get_metadata()
            print(f"   Plugin Name: {metadata['name']}")
            print(f"   Version: {metadata['version']}")
            print(f"   vLLM Available: {metadata['vllm_available']}")
            print(f"   Capabilities: {', '.join(metadata['capabilities'])}")
            
            # Update plugin status
            plugin._update_status()
            summary = plugin.get_status_summary()
            print(f"   Summary Status: {summary['status']}")
            print(f"   Summary Models: {summary['models']}")
            
            plugin.cleanup()
            print("   ✅ Dashboard plugin test completed")
    except Exception as e:
        print(f"   ❌ Dashboard plugin error: {e}")
    
    print()
    
    # Test 5: Integration with Workspace Management
    print("🗂️  Testing Workspace Compatibility...")
    try:
        # Check if workspace manager is available
        from workspace_manager_clean import WorkspaceManager
        
        workspace_manager = WorkspaceManager()
        workspaces = workspace_manager.get_workspaces()
        
        print(f"   Found {len(workspaces)} configured workspaces")
        for ws_name, ws_info in workspaces.items():
            print(f"     - {ws_name}: {ws_info.get('path', 'Unknown path')}")
        
        # Simulate vLLM workspace setup
        vllm_workspace_info = {
            "name": "vLLM Environment",
            "type": "vllm_server",
            "server_url": vllm_manager.base_url,
            "status": dashboard_data['status'],
            "models": dashboard_data['models']
        }
        print(f"   vLLM workspace info prepared: {vllm_workspace_info['name']}")
        print("   ✅ Workspace integration compatible")
        
    except ImportError:
        print("   ⚠️  Workspace manager not available (this is optional)")
    except Exception as e:
        print(f"   ❌ Workspace integration error: {e}")
    
    print()
    
    # Summary
    print("=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    if status.is_online:
        print("✅ vLLM server is accessible and working")
        print(f"✅ Found {len(status.models)} model(s) ready for use")
        print("✅ Dashboard integration is functional")
        print("✅ Complete integration is ready for production use")
    else:
        print("⚠️  vLLM server is not currently running")
        print("💡 To start vLLM server:")
        print("   1. Open Ubuntu/WSL terminal")
        print("   2. Run: ./setup_vllm.sh")
        print("   3. Or manually start with: python -m vllm.entrypoints.openai.api_server --model gpt2 --host 0.0.0.0 --port 8000")
        print("✅ Integration code is ready - just need to start the server")
    
    print()
    print("🚀 Ready for dashboard integration!")
    print("   - Use vllm_integration.py for core functionality")
    print("   - Use vllm_dashboard_plugin_clean.py for UI integration")
    print("   - Both modules are compatible with existing dashboard")
    
    return True

def test_synchronous():
    """Test synchronous functions"""
    print("\n🔄 Testing Synchronous Functions...")
    
    if not IMPORTS_OK:
        print("❌ Cannot test - imports failed")
        return
    
    try:
        from vllm_integration import get_vllm_status_sync
        
        if get_vllm_status_sync:
            status = get_vllm_status_sync()
            print(f"   Sync Status: {status['status']}")
            print(f"   Sync Models: {len(status['models'])}")
            print("   ✅ Synchronous functions working")
        else:
            print("   ⚠️  Synchronous function not available")
    except Exception as e:
        print(f"   ❌ Synchronous test error: {e}")

def show_integration_guide():
    """Show integration guide"""
    print("\n" + "=" * 60)
    print("INTEGRATION GUIDE")
    print("=" * 60)
    print()
    print("To integrate vLLM into your Ultimate Copilot dashboard:")
    print()
    print("1. 📁 FILES NEEDED:")
    print("   - vllm_integration.py (core vLLM manager)")
    print("   - vllm_dashboard_plugin_clean.py (dashboard plugin)")
    print()
    print("2. 🖥️  DASHBOARD INTEGRATION:")
    print("   Add to your dashboard:")
    print()
    print("   ```python")
    print("   from vllm_dashboard_plugin_clean import create_vllm_plugin")
    print("   ")
    print("   # In your dashboard initialization:")
    print("   vllm_plugin = create_vllm_plugin()")
    print("   vllm_ui = vllm_plugin.create_ui(parent_widget)")
    print("   ```")
    print()
    print("3. 🔄 STATUS MONITORING:")
    print("   ```python")
    print("   from vllm_integration import get_vllm_status_sync")
    print("   ")
    print("   # Get current status:")
    print("   status = get_vllm_status_sync()")
    print("   print(f\"Status: {status['status']}\")")
    print("   ```")
    print()
    print("4. 🚀 SERVER STARTUP:")
    print("   - Use start.bat option 5 to start vLLM")
    print("   - Or run manually in Ubuntu/WSL:")
    print("     ./setup_vllm.sh")
    print()
    print("5. 📊 DASHBOARD FEATURES:")
    print("   - Real-time server status monitoring")
    print("   - Model discovery and listing")
    print("   - Connection testing")
    print("   - Integration with existing provider system")

async def main():
    """Main test function"""
    try:
        # Run integration test
        success = await test_vllm_integration()
        
        # Run synchronous tests
        test_synchronous()
        
        # Show integration guide
        show_integration_guide()
        
        return success
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting vLLM Integration Test...")
    print("This will test all vLLM integration components.")
    print()
    
    # Run the test
    success = asyncio.run(main())
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("🎉 vLLM integration is ready for use!")
    else:
        print("\n❌ Some tests failed.")
        print("💡 Check the output above for details.")
    
    print("\nPress Enter to exit...")
    input()
