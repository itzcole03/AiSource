#!/usr/bin/env python3
"""
Ultimate Copilot System - VOID INTEGRATION PRIORITY
Optimized for 8GB VRAM with Void Editor as primary integration
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

# Configure logging with UTF-8 encoding for Windows
import sys
from typing import List

log_handlers: List[logging.Handler] = [
    logging.FileHandler('logs/void_enhanced_system.log', encoding='utf-8')
]

# Add console handler with appropriate encoding
if sys.platform.startswith('win'):
    # Windows console handler with fallback encoding
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(name)s: %(message)s'))
    log_handlers.append(console_handler)
else:
    log_handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(name)s: %(message)s',
    handlers=log_handlers
)

logger = logging.getLogger("VoidEnhancedMain")

async def main():
    """Main entry point for Enhanced Ultimate Copilot System with user editor choice"""    
    print("="*70)
    print("  ULTIMATE COPILOT SYSTEM - MULTI-EDITOR SUPPORT")
    print("="*70)
    print("")
    print(" [EDITORS] Void Editor & VS Code Insiders: Choose your preference")
    print(" [VRAM] 8GB VRAM optimized")
    print(" [LLM] Multi-provider LLM support")
    print("")
    
    system_manager = None
    
    try:
        logger.info("[START] Starting Enhanced Ultimate Copilot System...")
          # Initialize system with user editor selection (not forced to Void)
        system_manager = EnhancedSystemManager(
            config_path="config/system_config.yaml",
            models_config_path="config/models_config.yaml", 
            void_integration=False  # Allow user choice between editors
        )        
        # Initialize and start the system
        await system_manager.initialize()
        await system_manager.start()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        
    except Exception as e:
        logger.error(f"Void enhanced system error: {e}")
        
    finally:
        if system_manager:
            logger.info("Shutting down Void-Enhanced Ultimate Copilot System...")
            await system_manager.shutdown()
            logger.info("[OK] Void enhanced system shutdown complete")

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Run the enhanced system
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


