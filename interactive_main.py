#!/usr/bin/env python3
"""
Interactive Ultimate Copilot System
Provides a command-line interface for the running system
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.enhanced_system_manager import EnhancedSystemManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/interactive_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("InteractiveMain")

class InteractiveCopilot:
    def __init__(self):
        self.system_manager = None
        self.running = False
        
    async def initialize(self):
        """Initialize the system"""
        print("=" * 70)
        print("  ULTIMATE COPILOT - INTERACTIVE MODE")
        print("=" * 70)
        print("")
        print(" [MODE] Interactive command-line interface")
        print(" [VRAM] 8GB VRAM optimized")
        print(" [LLM] Multi-provider LLM support")
        print("")
        
        self.system_manager = EnhancedSystemManager(
            config_path="config/system_config.yaml",
            models_config_path="config/models_config.yaml",
            void_integration=False
        )
        
        await self.system_manager.initialize()
        self.running = True
        
    async def run_interactive_loop(self):
        """Run the interactive command loop"""
        print("\n" + "=" * 50)
        print("SYSTEM READY - Interactive Mode")
        print("=" * 50)
        print("Available commands:")
        print("  help     - Show this help")
        print("  status   - Show system status")
        print("  prompt   - Send a prompt to the agent system")
        print("  analyze  - Analyze current workspace")
        print("  config   - Show current configuration")
        print("  quit     - Exit the system")
        print("=" * 50)
        
        while self.running:
            try:
                # Get user input
                command = input("\nCopilot> ").strip().lower()
                
                if not command:
                    continue
                    
                await self.handle_command(command)
                
            except KeyboardInterrupt:
                print("\nReceived Ctrl+C, shutting down...")
                break
            except EOFError:
                print("\nReceived EOF, shutting down...")
                break
            except Exception as e:
                print(f"Error processing command: {e}")
                
    async def handle_command(self, command: str):
        """Handle user commands"""
        parts = command.split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "help":
            await self.cmd_help()
        elif cmd == "status":
            await self.cmd_status()
        elif cmd == "prompt":
            await self.cmd_prompt(args)
        elif cmd == "analyze":
            await self.cmd_analyze()
        elif cmd == "config":
            await self.cmd_config()
        elif cmd in ["quit", "exit", "q"]:
            self.running = False
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")
            
    async def cmd_help(self):
        """Show help"""
        print("\nUltimate Copilot Interactive Commands:")
        print("  help                    - Show this help")
        print("  status                  - Show system status and metrics")
        print("  prompt <text>           - Send a prompt to the agent system")
        print("  analyze                 - Analyze current workspace")
        print("  config                  - Show current system configuration")
        print("  quit/exit/q             - Exit the system")
        print("\nExamples:")
        print("  prompt Create a Python web app")
        print("  prompt Review my code for bugs")
        print("  analyze")
        
    async def cmd_status(self):
        """Show system status"""
        print("\n" + "=" * 40)
        print("SYSTEM STATUS")
        print("=" * 40)
        
        if self.system_manager:
            print(f"System Manager: Running")
            print(f"LLM Manager: {getattr(self.system_manager.llm_manager, 'initialized', 'Unknown')}")
            print(f"Agent Manager: {len(getattr(self.system_manager.agent_manager, 'agents', {})) if self.system_manager.agent_manager else 0} agents")
            print(f"Memory Manager: {getattr(self.system_manager.memory_manager, 'initialized', 'Unknown')}")
            print(f"Plugin Manager: {len(getattr(self.system_manager.plugin_manager, 'registered_plugins', {})) if self.system_manager.plugin_manager else 0} plugins")
        else:
            print("System Manager: Not initialized")
            
        print("=" * 40)
        
    async def cmd_prompt(self, args):
        """Handle user prompt"""
        if not args:
            prompt_text = input("Enter your prompt: ").strip()
        else:
            prompt_text = " ".join(args)
            
        if not prompt_text:
            print("No prompt provided.")
            return
            
        print(f"\nProcessing prompt: {prompt_text}")
        print("=" * 50)
        
        try:
            if self.system_manager and self.system_manager.agent_manager:
                await self.system_manager.agent_manager.dispatch_prompt(prompt_text)
            else:
                print("Agent manager not available")
        except Exception as e:
            print(f"Error processing prompt: {e}")
            
    async def cmd_analyze(self):
        """Analyze workspace"""
        print("\nAnalyzing workspace...")
        print("=" * 30)
        
        try:
            if self.system_manager and self.system_manager.agent_manager:
                await self.system_manager.agent_manager.auto_execute_workspace_plan()
            else:
                print("Agent manager not available")
        except Exception as e:
            print(f"Error analyzing workspace: {e}")
            
    async def cmd_config(self):
        """Show configuration"""
        print("\n" + "=" * 40)
        print("SYSTEM CONFIGURATION")
        print("=" * 40)
        
        if self.system_manager:
            print("Config file: config/system_config.yaml")
            print("Models config: config/models_config.yaml")
            print(f"Void integration: {self.system_manager.void_integration}")
            
            if hasattr(self.system_manager, 'config'):
                print(f"System config keys: {list(self.system_manager.config.keys())}")
            if hasattr(self.system_manager, 'models_config'):
                print(f"Models config keys: {list(self.system_manager.models_config.keys())}")
        else:
            print("System not initialized")
            
        print("=" * 40)
        
    async def shutdown(self):
        """Shutdown the system"""
        if self.system_manager:
            logger.info("Shutting down Interactive Ultimate Copilot System...")
            await self.system_manager.shutdown()
            logger.info("Shutdown complete")

async def main():
    """Main entry point"""
    copilot = InteractiveCopilot()
    
    try:
        await copilot.initialize()
        await copilot.run_interactive_loop()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Interactive system error: {e}")
    finally:
        await copilot.shutdown()

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
