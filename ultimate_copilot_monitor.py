#!/usr/bin/env python3
"""
Ultimate Copilot Status Monitor

A simplified status monitor for the Ultimate Copilot system
that provides real-time system information in console mode.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import time
from pathlib import Path

class UltimateCopilotMonitor:
    """
    Simplified monitor for the Ultimate Copilot system
    """
    
    def __init__(self):
        # Core components
        self.memory_manager = None
        self.unified_intelligence = None
        self.orchestrator = None
        self.completion_system = None
        
        # Monitor state
        self.system_status = {}
        self.refresh_interval = 5  # seconds
        self.running = True
        
        # Setup logging
        self.logger = logging.getLogger("Monitor")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def initialize(self):
        """Initialize all system components"""
        try:
            self.logger.info("Initializing Ultimate Copilot Monitor...")
            
            # Initialize memory manager
            from fixed_memory_manager import MemoryAwareModelManager
            self.memory_manager = MemoryAwareModelManager()
            await self.memory_manager.initialize()
            
            # Initialize unified intelligence
            from unified_model_intelligence import UnifiedModelIntelligence
            self.unified_intelligence = UnifiedModelIntelligence(self.memory_manager)
            
            # Initialize orchestrator
            from intelligent_agent_orchestrator_fixed import IntelligentAgentOrchestrator
            self.orchestrator = IntelligentAgentOrchestrator()
            await self.orchestrator.initialize()
            
            # Initialize completion system
            from ultimate_ai_completion import UltimateAICompletion
            self.completion_system = UltimateAICompletion()
            await self.completion_system.initialize()
            
            self.logger.info("Ultimate Copilot Monitor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize monitor: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def update_status(self):
        """Update system status"""
        try:
            # Collect status from all components
            status = {
                "timestamp": datetime.now().isoformat(),
                "memory_manager": {},
                "unified_intelligence": {},
                "orchestrator": {},
                "completion_system": {}
            }
            
            # Memory manager status
            if self.memory_manager:
                try:
                    memory_status = await self.memory_manager.get_memory_status()
                    status["memory_manager"] = memory_status
                except Exception as e:
                    status["memory_manager"] = {"error": str(e)}
            
            # Unified intelligence status
            if self.unified_intelligence:
                try:
                    ui_status = await self.unified_intelligence.get_system_status()
                    status["unified_intelligence"] = ui_status
                except Exception as e:
                    status["unified_intelligence"] = {"error": str(e)}
            
            # Orchestrator status
            if self.orchestrator:
                try:
                    status["orchestrator"] = {
                        "active_workflows": len(self.orchestrator.active_workflows),
                        "agent_pool_size": len(self.orchestrator.agent_pool),
                        "execution_results": len(self.orchestrator.execution_results)
                    }
                except Exception as e:
                    status["orchestrator"] = {"error": str(e)}
            
            # Completion system status
            if self.completion_system:
                try:
                    comp_status = await self.completion_system.get_system_status()
                    status["completion_system"] = comp_status["completion_system"]
                except Exception as e:
                    status["completion_system"] = {"error": str(e)}
            
            self.system_status = status
            
        except Exception as e:
            self.logger.error(f"Status update failed: {e}")
    
    def format_status_summary(self) -> str:
        """Format system status summary"""
        if not self.system_status:
            return "No status data available"
        
        summary = []
        summary.append(f"Last Updated: {self.system_status.get('timestamp', 'Unknown')}")
        summary.append("")
        
        # Memory status
        memory = self.system_status.get('memory_manager', {})
        if memory and 'error' not in memory:
            summary.append("MEMORY MANAGER:")
            summary.append(f"  VRAM Usage: {memory.get('current_usage_mb', 0)}MB / {memory.get('max_vram_mb', 0)}MB")
            summary.append(f"  Loaded Models: {len(memory.get('loaded_models', []))}")
            summary.append(f"  Available Models: {len(memory.get('available_models', []))}")
        else:
            summary.append("MEMORY MANAGER: Error or unavailable")
        
        summary.append("")
        
        # Unified intelligence
        ui = self.system_status.get('unified_intelligence', {})
        if ui and 'error' not in ui:
            summary.append("MODEL INTELLIGENCE:")
            summary.append(f"  Active Allocations: {ui.get('active_allocations', 0)}")
            summary.append(f"  Total Agents: {ui.get('total_agents', 0)}")
        else:
            summary.append("MODEL INTELLIGENCE: Error or unavailable")
        
        summary.append("")
        
        # Orchestrator
        orch = self.system_status.get('orchestrator', {})
        if orch and 'error' not in orch:
            summary.append("ORCHESTRATOR:")
            summary.append(f"  Active Workflows: {orch.get('active_workflows', 0)}")
            summary.append(f"  Agent Pool Size: {orch.get('agent_pool_size', 0)}")
        else:
            summary.append("ORCHESTRATOR: Error or unavailable")
        
        summary.append("")
        
        # Completion system
        comp = self.system_status.get('completion_system', {})
        if comp and 'error' not in comp:
            summary.append("COMPLETION SYSTEM:")
            summary.append(f"  Active Requests: {comp.get('active_requests', 0)}")
            summary.append(f"  Total Completions: {comp.get('total_completions', 0)}")
            
            metrics = comp.get('performance_metrics', {})
            if metrics:
                summary.append(f"  Average Quality: {metrics.get('average_quality', 0):.1f}/10")
                summary.append(f"  Average Time: {metrics.get('average_processing_time', 0):.1f}s")
        else:
            summary.append("COMPLETION SYSTEM: Error or unavailable")
        
        return "\n".join(summary)
    
    def show_models(self):
        """Show models in console"""
        memory = self.system_status.get('memory_manager', {})
        available_models = memory.get('available_models', {})
        
        if not available_models:
            print("No models available")
            return
        
        print("\nAvailable Models:")
        print(f"{'Provider':<12} {'Model ID':<30} {'Status':<10} {'VRAM':<8}")
        print("-" * 65)
        
        for model_key, model_info in available_models.items():
            status = "Loaded" if model_info.get('is_loaded', False) else "Available"
            model_id = model_info.get('model_id', model_key)
            if len(model_id) > 30:
                model_id = model_id[:27] + "..."
            
            print(f"{model_info.get('provider', 'Unknown'):<12} "
                  f"{model_id:<30} "
                  f"{status:<10} "
                  f"{model_info.get('estimated_vram_mb', 0)}MB")
    
    def show_agents(self):
        """Show agents in console"""
        if not self.orchestrator or not hasattr(self.orchestrator, 'agent_pool'):
            print("No agent information available")
            return
        
        print("\nActive Agents:")
        print(f"{'Agent ID':<20} {'Role':<15} {'Status':<10}")
        print("-" * 50)
        
        for agent_id, agent_info in self.orchestrator.agent_pool.items():
            if isinstance(agent_info, dict):
                print(f"{agent_id:<20} "
                      f"{agent_info.get('role', 'Unknown'):<15} "
                      f"{agent_info.get('status', 'Unknown'):<10}")
    
    def show_completions(self):
        """Show completions in console"""
        if not self.completion_system or not hasattr(self.completion_system, 'completion_history'):
            print("No completion history available")
            return
        
        recent = self.completion_system.completion_history[-10:]  # Last 10
        
        if not recent:
            print("No recent completions")
            return
        
        print("\nRecent Completions:")
        print(f"{'Request ID':<25} {'Quality':<8} {'Time':<8} {'Status':<8}")
        print("-" * 55)
        
        for completion in recent:
            status = "Success" if completion.success else "Failed"
            request_id = completion.request_id
            if len(request_id) > 25:
                request_id = request_id[:22] + "..."
            
            print(f"{request_id:<25} "
                  f"{completion.quality_score:.1f}/10   "
                  f"{completion.processing_time:.1f}s     "
                  f"{status:<8}")
    
    def save_report(self):
        """Save system report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"monitor_report_{timestamp}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": self.system_status,
                "monitor_config": {
                    "refresh_interval": self.refresh_interval
                }
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"System report saved to {report_file}")
                
        except Exception as e:
            print(f"Failed to save report: {e}")
    
    async def run_monitor(self):
        """Run the monitor in interactive console mode"""
        print("=== Ultimate Copilot System Monitor ===")
        print("Commands: r=refresh, m=models, a=agents, c=completions, s=save, q=quit")
        
        while self.running:
            try:
                # Update status
                await self.update_status()
                
                # Clear screen and show status
                print("\n" + "="*70)
                print(f"System Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*70)
                print(self.format_status_summary())
                print("\n" + "-"*70)
                print("Commands: r=refresh, m=models, a=agents, c=completions, s=save, q=quit")
                
                # Wait for command or auto-refresh
                try:
                    import select
                    import sys
                    
                    # Check if input is available (non-blocking)
                    if sys.stdin in select.select([sys.stdin], [], [], 1.0)[0]:
                        command = input("\nEnter command (or wait for auto-refresh): ").lower().strip()
                    else:
                        command = 'r'  # Auto-refresh
                except:
                    # Fallback for Windows
                    try:
                        command = input("\nEnter command: ").lower().strip()
                    except:
                        command = 'r'
                
                if command == 'q':
                    self.running = False
                elif command == 'r':
                    continue  # Refresh (default action)
                elif command == 'm':
                    self.show_models()
                    input("\nPress Enter to continue...")
                elif command == 'a':
                    self.show_agents()
                    input("\nPress Enter to continue...")
                elif command == 'c':
                    self.show_completions()
                    input("\nPress Enter to continue...")
                elif command == 's':
                    self.save_report()
                    input("\nPress Enter to continue...")
                else:
                    print(f"Unknown command: {command}")
                    await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(2)
        
        print("\nMonitor stopped.")

async def run_monitor():
    """Run the Ultimate Copilot Monitor"""
    monitor = UltimateCopilotMonitor()
    
    # Initialize
    success = await monitor.initialize()
    if not success:
        print("Failed to initialize monitor")
        return False
    
    print("Monitor initialized successfully")
    
    # Run monitor
    await monitor.run_monitor()
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(run_monitor())
    except KeyboardInterrupt:
        print("\nMonitor stopped by user")
    except Exception as e:
        print(f"Monitor error: {e}")
        import traceback
        traceback.print_exc()
