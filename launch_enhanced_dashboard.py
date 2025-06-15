#!/usr/bin/env python3
"""
Enhanced Dashboard Launcher

Launches the consolidated dashboard with proper integration to the enhanced agent system.
Handles dependency checking, environment setup, and graceful fallbacks.
"""

import sys
import os
import logging
import asyncio
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DashboardLauncher")

def check_dependencies():
    """Check if required dependencies are available"""
    missing = []
    
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter (GUI)")
    
    # Check for enhanced agent system
    try:
        from working_agent_upgrade import WorkingAgentUpgrade
        logger.info("✅ Enhanced agent system available")
    except ImportError:
        logger.warning("⚠️ Enhanced agent system not available")
      # Check for simple agents fallback
    try:
        # Check if simple_agents_fixed exists and is importable
        simple_agents_path = Path(__file__).parent / "core" / "simple_agents_fixed.py"
        if simple_agents_path.exists():
            logger.info("✅ Simple agents fallback (fixed) available")
        else:
            logger.info("✅ Simple agents system available")
    except Exception:
        missing.append("agent system")
    
    return missing

def main():
    """Main launcher function"""
    logger.info("🚀 Starting Enhanced Dashboard Launcher...")
    
    # Check project structure
    project_root = Path(__file__).parent
    if not (project_root / "working_agent_upgrade.py").exists():
        logger.error("Enhanced agent system not found. Please ensure working_agent_upgrade.py exists.")
        return False
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        logger.warning(f"Missing dependencies: {', '.join(missing_deps)}")
        logger.info("Dashboard will run with available features only")
    
    try:
        # Import and launch consolidated dashboard
        from consolidated_dashboard import ConsolidatedDashboard
        
        logger.info("✅ Launching Consolidated Dashboard...")
        dashboard = ConsolidatedDashboard()
        dashboard.run()
        
    except ImportError as e:
        logger.error(f"Failed to import dashboard: {e}")
        logger.info("Attempting to launch fallback dashboard...")
        
        # Try alternative dashboards
        fallback_dashboards = [
            "simple_dashboard_v2.py",
            "enhanced_dashboard.py",
            "ultimate_dashboard_v2.py"
        ]
        
        for dashboard_file in fallback_dashboards:
            dashboard_path = project_root / dashboard_file
            if dashboard_path.exists():
                logger.info(f"Launching fallback: {dashboard_file}")
                try:
                    subprocess.run([sys.executable, str(dashboard_path)], check=True)
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"Fallback {dashboard_file} failed: {e}")
                    continue
        
        logger.error("All dashboard options failed")
        return False
    
    except Exception as e:
        logger.error(f"Dashboard launch failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        logger.error("Dashboard launcher failed")
        input("Press Enter to exit...")
        sys.exit(1)
