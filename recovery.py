#!/usr/bin/env python3
"""
Recovery Script - Get Ultimate Copilot Unstuck
Diagnoses and fixes common issues automatically
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger("Recovery")

def check_environment():
    """Check if the environment is set up correctly"""
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    
    # Check directories
    required_dirs = ['core', 'agents', 'logs', 'config']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            issues.append(f"Missing directory: {dir_name}")
    
    # Check key files
    key_files = [
        'core/simple_agents.py',
        'run_overnight.py',
        'demo.py',
        'requirements.txt'
    ]
    for file_name in key_files:
        if not os.path.exists(file_name):
            issues.append(f"Missing file: {file_name}")
    
    return issues

def fix_logs_directory():
    """Ensure logs directory structure exists"""
    log_dirs = ['logs', 'logs/agents']
    for dir_path in log_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created/verified: {dir_path}")

def test_agent_imports():
    """Test if agent imports work"""
    try:
        sys.path.insert(0, '.')
        from core.simple_agents import SimpleOrchestratorAgent, SimpleArchitectAgent
        logger.info("✓ Agent imports successful")
        return True
    except Exception as e:
        logger.error(f"✗ Agent import failed: {e}")
        return False

async def test_agent_functionality():
    """Test if agents can actually run"""
    try:
        sys.path.insert(0, '.')
        from core.simple_agents import SimpleOrchestratorAgent
        
        agent = SimpleOrchestratorAgent()
        await agent.agent_initialize()
        
        task = {'type': 'recovery_test', 'workspace': os.getcwd()}
        result = await agent.process_task(task, {})
        
        logger.info(f"✓ Agent test successful: {result['status']}")
        return True
    except Exception as e:
        logger.error(f"✗ Agent test failed: {e}")
        return False

def clean_corrupted_logs():
    """Clean up any corrupted log files"""
    log_dir = Path("logs")
    if log_dir.exists():
        for log_file in log_dir.rglob("*.log"):
            try:
                # Test if log file can be read
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if len(content) > 10000000:  # > 10MB
                    logger.info(f"Truncating large log file: {log_file}")
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write("Log file truncated by recovery script\n")
            except Exception as e:
                logger.warning(f"Issue with log file {log_file}: {e}")

def show_status_summary():
    """Show current system status"""
    print("\n" + "="*50)
    print("  ULTIMATE COPILOT STATUS SUMMARY")
    print("="*50)
    
    # Check if overnight operation is running
    if os.path.exists("logs/overnight_operation.log"):
        try:
            with open("logs/overnight_operation.log", 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    print(f"Last overnight log: {last_line}")
        except:
            print("Overnight log: Unable to read")
    
    # Check agent logs
    agent_dir = Path("logs/agents")
    if agent_dir.exists():
        agent_logs = list(agent_dir.glob("*.log"))
        print(f"Agent logs found: {len(agent_logs)}")
        
        for log_file in agent_logs[:3]:  # Show first 3
            try:
                size = log_file.stat().st_size
                print(f"  - {log_file.name}: {size} bytes")
            except:
                print(f"  - {log_file.name}: Unable to check")
    
    print("="*50)

async def main():
    """Main recovery function"""
    print("ULTIMATE COPILOT RECOVERY SCRIPT")
    print("=" * 40)
    
    # Step 1: Check environment
    logger.info("Step 1: Checking environment...")
    issues = check_environment()
    if issues:
        logger.error("Environment issues found:")
        for issue in issues:
            logger.error(f"  - {issue}")
        logger.info("Please fix these issues before continuing")
        return False
    else:
        logger.info("✓ Environment checks passed")
    
    # Step 2: Fix logs
    logger.info("Step 2: Setting up logs directory...")
    fix_logs_directory()
    
    # Step 3: Clean corrupted logs
    logger.info("Step 3: Cleaning up logs...")
    clean_corrupted_logs()
    
    # Step 4: Test imports
    logger.info("Step 4: Testing agent imports...")
    if not test_agent_imports():
        logger.error("Cannot proceed without working agent imports")
        return False
    
    # Step 5: Test functionality
    logger.info("Step 5: Testing agent functionality...")
    if not await test_agent_functionality():
        logger.error("Agent functionality test failed")
        return False
    
    # Step 6: Show status
    logger.info("Step 6: System status...")
    show_status_summary()
    
    logger.info("✓ Recovery completed successfully!")
    logger.info("System should now be ready for autonomous operation")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 RECOVERY SUCCESSFUL!")
        print("You can now run:")
        print("  - python demo.py (for testing)")
        print("  - python run_overnight.py (for autonomous operation)")
        print("  - start_overnight.bat (Windows batch script)")
    else:
        print("\nRECOVERY FAILED")
        print("Please check the error messages above and fix manually")
    
    input("\nPress Enter to exit...")


