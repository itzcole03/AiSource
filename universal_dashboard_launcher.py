#!/usr/bin/env python3
"""
Universal Dashboard Launcher with Dependency Management

Automatically installs missing dependencies and launches the best available dashboard.
Handles all limitations and provides graceful fallbacks.
"""

import sys
import os
import subprocess
import logging
import importlib
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("UniversalLauncher")

class DependencyManager:
    """Manages dependencies and auto-installation"""
    
    def __init__(self):
        self.required_packages = {
            'fastapi': 'fastapi>=0.104.0',
            'uvicorn': 'uvicorn>=0.24.0', 
            'pydantic': 'pydantic>=2.0.0',
            'requests': 'requests>=2.31.0'
        }
        self.optional_packages = {
            'streamlit': 'streamlit>=1.29.0',
            'pandas': 'pandas>=2.1.0',
            'matplotlib': 'matplotlib>=3.7.0'
        }
        
    def check_package(self, package_name: str) -> bool:
        """Check if a package is available"""
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False
    
    def install_package(self, package_spec: str) -> bool:
        """Install a package using pip"""
        try:
            logger.info(f"Installing {package_spec}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package_spec],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"✅ Successfully installed {package_spec}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {package_spec}: {e}")
            return False
    
    def ensure_dependencies(self, packages: Dict[str, str]) -> Dict[str, bool]:
        """Ensure required packages are available"""
        results = {}
        
        for package_name, package_spec in packages.items():
            if self.check_package(package_name):
                logger.info(f"✅ {package_name} is available")
                results[package_name] = True
            else:
                logger.warning(f"⚠️ {package_name} not found, attempting to install...")
                results[package_name] = self.install_package(package_spec)
        
        return results
    
    def get_available_features(self) -> Dict[str, bool]:
        """Check what features are available"""
        # Check core dependencies
        core_deps = self.ensure_dependencies(self.required_packages)
        
        # Check optional dependencies (don't auto-install)
        optional_deps = {}
        for package_name in self.optional_packages:
            optional_deps[package_name] = self.check_package(package_name)
        
        # Check GUI availability
        gui_available = True
        try:
            import tkinter
        except ImportError:
            gui_available = False
        
        return {
            'api_server': all(core_deps.values()),
            'web_interface': core_deps.get('requests', False),
            'gui_interface': gui_available,
            'streamlit_interface': optional_deps.get('streamlit', False),
            **core_deps,
            **optional_deps
        }

class UniversalDashboardLauncher:
    """Universal launcher for all dashboard types"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dependency_manager = DependencyManager()
        self.features = {}
        
    def check_system_status(self) -> Dict[str, bool]:
        """Check overall system status"""
        logger.info("🔍 Checking system status...")
        
        # Check enhanced agent system
        enhanced_agents_available = False
        try:
            sys.path.insert(0, str(self.project_root))
            from working_agent_upgrade import WorkingAgentUpgrade
            enhanced_agents_available = True
            logger.info("✅ Enhanced agent system available")
        except ImportError as e:
            logger.error(f"❌ Enhanced agent system not available: {e}")
        
        # Check dependencies
        self.features = self.dependency_manager.get_available_features()
        
        # Check dashboard files
        dashboard_files = {
            'enhanced_integration': (self.project_root / 'enhanced_dashboard_integration.py').exists(),
            'api_server': (self.project_root / 'enhanced_dashboard_api.py').exists(),
            'web_interface': (self.project_root / 'enhanced_dashboard.html').exists(),
            'gui_dashboard': (self.project_root / 'consolidated_dashboard.py').exists()
        }
        
        status = {
            'enhanced_agents': enhanced_agents_available,
            **self.features,
            **dashboard_files
        }
        
        return status
    
    def launch_enhanced_integration(self) -> bool:
        """Launch the enhanced dashboard integration (console)"""
        try:
            logger.info("🚀 Launching Enhanced Dashboard Integration...")
            from enhanced_dashboard_integration import EnhancedDashboardIntegration
            
            async def run_integration():
                dashboard = EnhancedDashboardIntegration()
                if await dashboard.initialize():
                    await self.run_interactive_demo(dashboard)
                else:
                    logger.error("Failed to initialize dashboard integration")
                    return False
                return True
            
            return asyncio.run(run_integration())
            
        except Exception as e:
            logger.error(f"Enhanced integration failed: {e}")
            return False
    
    async def run_interactive_demo(self, dashboard):
        """Run interactive demo with the dashboard"""
        print("\n🚀 Enhanced Dashboard Integration")
        print("================================")
        print("Commands: status, test, task <agent> <description>, memory, history, quit")
        
        dashboard.start_status_monitoring(10)
        
        try:
            while True:
                command = input("\nEnter command: ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "status":
                    status = dashboard.get_system_status()
                    print(f"Agents: {status['agents']['active']}/{status['agents']['total']}")
                    print(f"Tasks: {status['tasks']['completed']} completed, {status['tasks']['errors']} errors")
                    print(f"Success Rate: {status['tasks']['success_rate']:.1f}%")
                elif command == "test":
                    print("Testing all agents...")
                    results = await dashboard.test_all_agents()
                    for agent, result in results.items():
                        success = "✅" if not result.get("error") else "❌"
                        print(f"  {agent}: {success}")
                elif command.startswith("task "):
                    parts = command.split(" ", 2)
                    if len(parts) >= 3:
                        agent, task_desc = parts[1], parts[2]
                        if agent in ["architect", "backend", "frontend", "QA"]:
                            print(f"Executing task with {agent}...")
                            result = await dashboard.execute_task(agent, task_desc)
                            success = "✅" if not result.get("error") else "❌"
                            print(f"{success} Task completed")
                        else:
                            print("❌ Available agents: architect, backend, frontend, QA")
                    else:
                        print("❌ Usage: task <agent> <description>")
                elif command == "memory":
                    memory_info = dashboard.get_agent_memory_info()
                    if "error" not in memory_info:
                        for agent, info in memory_info.items():
                            print(f"  {agent}: {info['memory_size']} bytes")
                    else:
                        print(f"Memory info: {memory_info}")
                elif command == "history":
                    print("Recent tasks:")
                    for task in dashboard.task_history[-5:]:
                        status_icon = "✅" if task["status"] == "completed" else "❌"
                        print(f"  {status_icon} {task['agent']}: {task['task'][:50]}...")
                else:
                    print("❌ Unknown command")
        
        except KeyboardInterrupt:
            print("\n🛑 Stopping dashboard...")
        finally:
            dashboard.stop()
    
    def launch_api_server(self) -> bool:
        """Launch the API server"""
        if not self.features.get('api_server', False):
            logger.error("❌ API server dependencies not available")
            return False
        
        try:
            logger.info("🚀 Launching API Server...")
            from enhanced_dashboard_api import EnhancedDashboardAPI
            
            async def run_api():
                api = EnhancedDashboardAPI()
                if await api.initialize():
                    logger.info("API server starting on http://127.0.0.1:8001")
                    api.run_server()
                    return True
                else:
                    logger.error("Failed to initialize API")
                    return False
            
            return asyncio.run(run_api())
            
        except Exception as e:
            logger.error(f"API server failed: {e}")
            return False
    
    def launch_gui_dashboard(self) -> bool:
        """Launch the GUI dashboard"""
        if not self.features.get('gui_interface', False):
            logger.error("❌ GUI interface not available (tkinter not found)")
            return False
        
        try:
            logger.info("🚀 Launching GUI Dashboard...")
            from consolidated_dashboard import ConsolidatedDashboard
            
            async def run_gui():
                dashboard = ConsolidatedDashboard()
                if await dashboard.initialize():
                    if dashboard.create_gui():
                        dashboard.run()
                        return True
                    else:
                        logger.error("Failed to create GUI")
                        return False
                else:
                    logger.error("Failed to initialize dashboard")
                    return False
            
            return asyncio.run(run_gui())
            
        except Exception as e:
            logger.error(f"GUI dashboard failed: {e}")
            return False
    
    def show_web_instructions(self):
        """Show instructions for web interface"""
        web_file = self.project_root / 'enhanced_dashboard.html'
        if web_file.exists():
            print("\n🌐 Web Interface Available!")
            print("==========================")
            print(f"1. Start the API server first:")
            print(f"   python enhanced_dashboard_api.py")
            print(f"2. Open in browser:")
            print(f"   file:///{web_file.absolute()}")
            print(f"3. Or serve with Python:")
            print(f"   python -m http.server 8080")
            print(f"   Then visit: http://localhost:8080/enhanced_dashboard.html")
        else:
            logger.error("❌ Web interface file not found")
    
    def choose_dashboard(self) -> str:
        """Let user choose dashboard type"""
        print("\n📊 Available Dashboard Options:")
        print("==============================")
        
        options = []
        
        if self.features.get('enhanced_agents', False):
            options.append(("1", "Enhanced Integration (Console)", "launch_enhanced_integration"))
        
        if self.features.get('api_server', False):
            options.append(("2", "API Server (for Web Interface)", "launch_api_server"))
        
        if self.features.get('gui_interface', False):
            options.append(("3", "GUI Dashboard (Desktop)", "launch_gui_dashboard"))
        
        if self.features.get('web_interface', False):
            options.append(("4", "Show Web Interface Instructions", "show_web_instructions"))
        
        options.append(("5", "Install Missing Dependencies", "install_dependencies"))
        options.append(("6", "System Status Check", "system_status"))
        options.append(("q", "Quit", "quit"))
        
        for opt_num, description, _ in options:
            availability = "✅" if opt_num not in ["5", "6", "q"] else "🔧"
            print(f"  {opt_num}. {description} {availability}")
        
        while True:
            choice = input("\nSelect option (1-6, q): ").strip().lower()
            for opt_num, _, method in options:
                if choice == opt_num:
                    return method
            print("❌ Invalid choice, please try again")
    
    def install_dependencies(self):
        """Install missing dependencies"""
        print("\n📦 Installing Dependencies...")
        print("============================")
        
        results = self.dependency_manager.ensure_dependencies(
            self.dependency_manager.required_packages
        )
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n✅ Installed {success_count}/{total_count} dependencies")
        
        # Refresh features
        self.features = self.dependency_manager.get_available_features()
        print("🔄 Dependencies refreshed")
    
    def show_system_status(self):
        """Show detailed system status"""
        status = self.check_system_status()
        
        print("\n🔍 System Status Report")
        print("======================")
        
        for feature, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"  {status_icon} {feature.replace('_', ' ').title()}")
        
        # Calculate overall health
        available_count = sum(status.values())
        total_count = len(status)
        health_percentage = (available_count / total_count) * 100
        
        print(f"\n📊 System Health: {health_percentage:.1f}% ({available_count}/{total_count})")
        
        if health_percentage >= 90:
            print("🎉 System is fully operational!")
        elif health_percentage >= 70:
            print("⚠️ System is mostly functional with minor limitations")
        else:
            print("🔧 System needs attention - install missing dependencies")
    
    def run(self):
        """Main launcher method"""
        print("🚀 Ultimate Copilot - Universal Dashboard Launcher")
        print("=" * 55)
        
        # Initial status check
        status = self.check_system_status()
        
        # Auto-launch if everything is available
        if all(status.values()):
            print("🎉 All systems operational! Auto-launching Enhanced Integration...")
            if self.launch_enhanced_integration():
                return
        
        # Interactive mode
        while True:
            method = self.choose_dashboard()
            
            if method == "quit":
                print("👋 Goodbye!")
                break
            elif method == "launch_enhanced_integration":
                self.launch_enhanced_integration()
            elif method == "launch_api_server":
                self.launch_api_server()
            elif method == "launch_gui_dashboard":
                self.launch_gui_dashboard()
            elif method == "show_web_instructions":
                self.show_web_instructions()
            elif method == "install_dependencies":
                self.install_dependencies()
            elif method == "system_status":
                self.show_system_status()

def main():
    """Main entry point"""
    try:
        launcher = UniversalDashboardLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 Launcher stopped by user")
    except Exception as e:
        logger.error(f"Launcher failed: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
