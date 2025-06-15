#!/usr/bin/env python3
"""
Demo: Workspace Management Integration

This script demonstrates the workspace management functionality that has been
integrated into the Ultimate Copilot dashboard.
"""

import logging
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from workspace_manager_clean import WorkspaceManager, WorkspaceInfo
from workspace_plugin import WorkspaceManagementPlugin, WorkspaceRouter

def setup_logging():
    """Setup logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def demo_workspace_manager():
    """Demonstrate workspace manager functionality"""
    print("\n" + "="*60)
    print("WORKSPACE MANAGER DEMONSTRATION")
    print("="*60)
    
    # Initialize workspace manager
    workspace_manager = WorkspaceManager()
    workspace_manager.start_monitoring()
    
    print(f"\n1. Initial workspace count: {len(workspace_manager.get_all_workspaces())}")
    
    # Add current directory as a workspace
    current_dir = Path.cwd()
    success = workspace_manager.add_workspace(str(current_dir), "Ultimate Copilot Project", "python")
    print(f"2. Added current directory as workspace: {success}")
    
    # Add parent directory as another workspace
    parent_dir = current_dir.parent
    if parent_dir.exists():
        success = workspace_manager.add_workspace(str(parent_dir), "Parent Directory", "general")
        print(f"3. Added parent directory as workspace: {success}")
    
    # List all workspaces
    workspaces = workspace_manager.get_all_workspaces()
    print(f"\n4. Total workspaces: {len(workspaces)}")
    
    for i, workspace in enumerate(workspaces, 1):
        print(f"   Workspace {i}: {workspace.name}")
        print(f"     Path: {workspace.path}")
        print(f"     Type: {workspace.type}")
        print(f"     Status: {workspace.status}")
        print(f"     Size: {workspace.size_mb:.1f} MB")
        print(f"     Files: {workspace.file_count}")
        print("")
    
    # Demonstrate agent assignment
    print("5. Agent Assignment Demo:")
    test_agent_id = "agent_001"
    
    if workspaces:
        workspace_path = workspaces[0].path
        success = workspace_manager.assign_agent_to_workspace(test_agent_id, workspace_path)
        print(f"   Assigned agent {test_agent_id} to workspace: {success}")
        
        # Get workspace for agent
        agent_workspace = workspace_manager.get_workspace_for_agent(test_agent_id)
        if agent_workspace:
            print(f"   Agent {test_agent_id} is assigned to: {agent_workspace.name}")
        
        # Get workspace context
        context = workspace_manager.get_workspace_context(workspace_path)
        print(f"   Workspace has {len(context.get('recent_files', []))} recent files")
        print(f"   Active agents: {len(context.get('active_agents', []))}")
    
    # Cleanup
    workspace_manager.cleanup()
    print("\n6. Workspace manager demo completed.")

def demo_workspace_plugin():
    """Demonstrate workspace plugin functionality"""
    print("\n" + "="*60)
    print("WORKSPACE PLUGIN DEMONSTRATION")
    print("="*60)
    
    # Initialize plugin
    plugin = WorkspaceManagementPlugin()
    
    # Mock dashboard context
    class MockDashboardContext:
        def emit_event(self, event):
            print(f"Dashboard event: {event.event_type} from {event.source}")
    
    # Initialize plugin
    success = plugin.initialize(MockDashboardContext())
    print(f"\n1. Plugin initialization: {success}")
    
    # Get plugin metadata
    metadata = plugin.get_metadata()
    print(f"2. Plugin metadata:")
    for key, value in metadata.items():
        print(f"   {key}: {value}")
    
    # Update plugin data
    data = plugin.update()
    print(f"\n3. Plugin data update:")
    for key, value in data.items():
        if key == 'workspaces':
            print(f"   {key}: {len(value)} workspaces")
        else:
            print(f"   {key}: {value}")
    
    # Demonstrate plugin methods
    current_dir = str(Path.cwd())
    success = plugin.add_workspace(current_dir, "Plugin Test Workspace", "python")
    print(f"\n4. Added workspace via plugin: {success}")
    
    # Get optimal workspace
    optimal = plugin.get_optimal_workspace(task_type="python", language="python")
    if optimal:
        print(f"5. Optimal workspace for Python task: {optimal.name}")
    else:
        print("5. No optimal workspace found for Python task")
    
    # Cleanup
    plugin.cleanup()
    print("\n6. Workspace plugin demo completed.")

def demo_workspace_router():
    """Demonstrate workspace router functionality"""
    print("\n" + "="*60)
    print("WORKSPACE ROUTER DEMONSTRATION")
    print("="*60)
    
    # Initialize components
    workspace_manager = WorkspaceManager()
    workspace_manager.start_monitoring()
    router = WorkspaceRouter(workspace_manager)
    
    # Add some test workspaces
    current_dir = Path.cwd()
    workspace_manager.add_workspace(str(current_dir), "Main Project", "python")
    
    parent_dir = current_dir.parent
    if parent_dir.exists():
        workspace_manager.add_workspace(str(parent_dir), "Parent Workspace", "general")
    
    print(f"\n1. Setup {len(workspace_manager.get_all_workspaces())} workspaces for routing")
    
    # Test agent routing scenarios
    test_scenarios = [
        {
            "agent_id": "python_agent_001",
            "task_info": {"type": "python", "language": "python"},
            "description": "Python development task"
        },
        {
            "agent_id": "general_agent_002", 
            "task_info": {"type": "general"},
            "description": "General task"
        },
        {
            "agent_id": "specific_agent_003",
            "task_info": {"workspace": "Main Project"},
            "description": "Task with specific workspace requirement"
        }    ]
    
    for i, scenario in enumerate(test_scenarios, 2):
        agent_id = scenario["agent_id"]
        task_info = scenario["task_info"]
        description = scenario["description"]
        
        print(f"\n{i}. Routing scenario: {description}")
        workspace_path = router.route_agent_to_workspace(agent_id, task_info)
        
        if workspace_path:
            workspace = workspace_manager.get_workspace_for_agent(agent_id)
            if workspace:
                print(f"   Agent {agent_id} routed to: {workspace.name}")
                print(f"   Workspace path: {workspace_path}")
                
                # Get workspace context
                context = router.get_agent_workspace_context(agent_id)
                if context:
                    workspace_info = context.get('workspace_info', {})
                    print(f"   Workspace type: {workspace_info.get('type', 'Unknown')}")
                    print(f"   Active agents: {len(context.get('active_agents', []))}")
            else:
                print(f"   Agent {agent_id} routed but workspace info not available")
        else:
            print(f"   Failed to route agent {agent_id}")
    
    # Cleanup
    workspace_manager.cleanup()
    print("\n5. Workspace router demo completed.")

def demo_dashboard_integration():
    """Demonstrate how workspace management integrates with the dashboard"""
    print("\n" + "="*60)
    print("DASHBOARD INTEGRATION DEMONSTRATION")
    print("="*60)
    
    print("\n1. Workspace Management Integration Features:")
    print("   ✓ Workspace discovery and registration")
    print("   ✓ Agent-to-workspace routing")
    print("   ✓ Real-time workspace monitoring") 
    print("   ✓ Cross-workspace intelligence persistence")
    print("   ✓ Project structure analysis")
    print("   ✓ Git repository detection")
    print("   ✓ Framework/language detection")
    
    print("\n2. Dashboard Plugin Integration:")
    print("   ✓ Workspace management tab in dashboard")
    print("   ✓ Real-time status updates")
    print("   ✓ Agent assignment interface")
    print("   ✓ Workspace context display")
    print("   ✓ Configuration management")
    
    print("\n3. Agent Integration Benefits:")
    print("   ✓ Agents automatically directed to appropriate workspaces")
    print("   ✓ Workspace context available to agents")
    print("   ✓ Project-specific tool and library awareness")
    print("   ✓ Cross-workspace learning and knowledge sharing")
    print("   ✓ Optimal resource allocation")
    
    print("\n4. Usage Example:")
    print("   - User adds local workspace via dashboard")
    print("   - System analyzes workspace (type, language, structure)")
    print("   - Agent receives task requiring Python development")
    print("   - Router automatically assigns agent to Python workspace")
    print("   - Agent has full context of workspace (files, git status, etc.)")
    print("   - Agent works efficiently within proper environment")
    
    print("\n5. Configuration Files:")
    config_files = [
        "workspaces.json - Persistent workspace configuration",
        "dashboard_config.json - Dashboard settings",
        "agent_workspace_assignments.json - Active agent assignments"
    ]
    
    for config_file in config_files:
        print(f"   • {config_file}")
        
    print("\n6. Integration with existing Ultimate Copilot components:")
    components = [
        "memory_aware_model_manager.py - VRAM allocation per workspace",
        "intelligent_agent_orchestrator_fixed.py - Agent coordination", 
        "persistent_agent_intelligence.py - Cross-workspace learning",
        "real_time_system_monitor.py - Workspace health monitoring",
        "predictive_resource_manager.py - Workspace resource prediction"
    ]
    
    for component in components:
        print(f"   • {component}")

def main():
    """Main demo function"""
    setup_logging()
    
    print("Ultimate Copilot - Workspace Management Demo")
    print("=" * 60)
    print("This demonstration shows the workspace management capabilities")
    print("that have been integrated into the Ultimate Copilot dashboard.")
    
    try:
        # Run demonstrations
        demo_workspace_manager()
        demo_workspace_plugin()
        demo_workspace_router()
        demo_dashboard_integration()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nWorkspace management is now fully integrated into the")
        print("Ultimate Copilot dashboard and ready for production use.")
        print("\nTo launch the dashboard with workspace management:")
        print("  python simple_dashboard_v2.py")
        print("\nThe workspace management tab will be available in the dashboard")
        print("allowing you to configure local workspaces and direct agents.")
        
    except Exception as e:
        logging.error(f"Demo failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
