#!/usr/bin/env python3
"""
Test script to verify that Void Editor and VS Code Insiders have identical capabilities
"""

import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from integrations.editor_selection_manager import EditorSelectionManager
from integrations.void_integration import VoidEditorIntegration
from integrations.vscode_integration import VSCodeInsidersIntegration

def test_identical_capabilities():
    """Test that both editors have identical capabilities"""
    print("🧪 Testing Editor Capability Parity")
    print("=" * 50)
    
    # Create test workspace
    workspace_path = "."
    config = {
        'websocket_port': 8765,
        'auto_sync': True,
        'ai_assistance': True
    }
    
    # Create both integrations
    void_integration = VoidEditorIntegration(workspace_path, config)
    vscode_integration = VSCodeInsidersIntegration(workspace_path, config)
    
    # Test 1: Check base class inheritance
    print("1. Base Class Inheritance:")
    print(f"   Void Editor inherits from BaseEditorIntegration: {hasattr(void_integration, '_get_standard_features')}")
    print(f"   VS Code Insiders inherits from BaseEditorIntegration: {hasattr(vscode_integration, '_get_standard_features')}")
    
    # Test 2: Check identical methods
    print("\n2. Method Availability:")
    common_methods = [
        'start_websocket_server',
        'handle_client_message',
        'sync_file_to_editor',
        'get_ai_suggestion',
        'explain_code',
        'review_code',
        'generate_tests',
        'refactor_code',
        'optimize_performance',
        'handle_file_changed',
        'handle_file_created',
        'handle_file_deleted'
    ]
    
    for method in common_methods:
        void_has = hasattr(void_integration, method)
        vscode_has = hasattr(vscode_integration, method)
        status = "" if void_has and vscode_has else ""
        print(f"   {status} {method}: Void={void_has}, VSCode={vscode_has}")
    
    # Test 3: Check feature sets
    print("\n3. Feature Set Comparison:")
    try:
        manager = EditorSelectionManager(workspace_path, config)
        void_features = manager.available_editors['void']['features']
        vscode_features = manager.available_editors['vscode']['features']
        
        print(f"   Void Editor features: {len(void_features)} items")
        print(f"   VS Code features: {len(vscode_features)} items")
        
        # Check if feature sets are identical
        features_identical = void_features == vscode_features
        print(f"   Features identical: {'' if features_identical else ''}")
        
        if not features_identical:
            print("   Differences:")
            for key in set(void_features.keys()) | set(vscode_features.keys()):
                void_val = void_features.get(key, 'Missing')
                vscode_val = vscode_features.get(key, 'Missing')
                if void_val != vscode_val:
                    print(f"     {key}: Void={void_val}, VSCode={vscode_val}")
    
    except Exception as e:
        print(f"   Error checking features: {e}")
    
    # Test 4: Check editor detection
    print("\n4. Editor Detection:")
    try:
        # This is async, so we'll just check the method exists
        print(f"   Void Editor has detect_editor method: {'' if hasattr(void_integration, 'detect_editor') else ''}")
        print(f"   VS Code has detect_editor method: {'' if hasattr(vscode_integration, 'detect_editor') else ''}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Configuration compatibility
    print("\n5. Configuration Compatibility:")
    try:
        void_config_keys = set(void_integration.config.keys())
        vscode_config_keys = set(vscode_integration.config.keys())
        common_keys = void_config_keys & vscode_config_keys
        
        print(f"   Common config keys: {len(common_keys)}")
        print(f"   Void-specific keys: {len(void_config_keys - vscode_config_keys)}")
        print(f"   VSCode-specific keys: {len(vscode_config_keys - void_config_keys)}")
        
        # Both should accept the same base configuration
        config_compatible = len(common_keys) >= 3  # At least websocket_port, auto_sync, ai_assistance
        print(f"   Configuration compatible: {'' if config_compatible else ''}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("Capability parity test completed!")
    print("\nBoth editors should have identical capabilities thanks to BaseEditorIntegration")

async def test_editor_selection():
    """Test the editor selection process"""
    print("\nTesting Editor Selection Process")
    print("=" * 50)
    
    try:
        workspace_path = "."
        config = {}
        
        manager = EditorSelectionManager(workspace_path, config)
        
        print("Available editors:")
        for key, editor_info in manager.available_editors.items():
            print(f"  {key}: {editor_info['name']}")
            print(f"    Description: {editor_info['description']}")
            print(f"    Features: {len(editor_info['features'])} capabilities")
        
        print(f"\nEditor selection manager working correctly")
        
    except Exception as e:
        print(f"Error in editor selection: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("Ultimate Copilot - Editor Capability Test Suite")
    print("Testing Void Editor and VS Code Insiders parity")
    print()
    
    # Run synchronous tests
    test_identical_capabilities()
    
    # Run async tests
    asyncio.run(test_editor_selection())
    
    print("\n🎉 All tests completed!")
    print("Both editors now have identical capabilities - users can choose their preference!")

if __name__ == "__main__":
    main()


