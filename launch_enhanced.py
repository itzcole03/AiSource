#!/usr/bin/env python3
"""
Ultimate Copilot - Enhanced Launcher with Memory, Models, and Real Intelligence
Complete autonomous agent system with production capabilities
"""

import asyncio
import subprocess
import sys
import time
import requests
import logging
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.real_llm_manager import RealLLMManager
from core.advanced_memory_manager import AdvancedMemoryManager
from core.file_coordinator import FileCoordinator
from agents.architect_agent import ArchitectAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.qa_agent import QAAgent
from agents.orchestrator_agent import OrchestratorAgent

def check_service(url: str, name: str) -> bool:
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False

def start_qdrant():
    """Start Qdrant vector database"""
    print("🗃️ Starting Qdrant Vector Database...")
    
    # Check if already running
    if check_service("http://localhost:6333/health", "Qdrant"):
        print("Qdrant already running")
        return True
    
    try:
        # Try to start existing container first
        result = subprocess.run(["docker", "start", "qdrant"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            # Create new container
            print("📦 Creating new Qdrant container...")
            data_dir = Path("data/qdrant_storage")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            subprocess.run([
                "docker", "run", "-d",
                "--name", "qdrant",
                "-p", "6333:6333",
                "-p", "6334:6334", 
                "-v", f"{data_dir.absolute()}:/qdrant/storage",
                "qdrant/qdrant:latest"
            ], check=True)
        
        # Wait for Qdrant to be ready
        print("⏳ Waiting for Qdrant to start...")
        for i in range(30):
            if check_service("http://localhost:6333/health", "Qdrant"):
                print("Qdrant started successfully!")
                print("🔗 Web UI: http://localhost:6333/dashboard")
                return True
            time.sleep(1)
        
        print("Qdrant failed to start within 30 seconds")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Qdrant: {e}")
        return False
    except FileNotFoundError:
        print("Docker not found. Please install Docker first.")
        return False

def check_models():
    """Check which model endpoints are available"""
    endpoints = {
        "Ollama": "http://127.0.0.1:11434",
        "vLLM": "http://localhost:8000", 
        "LM Studio": "http://localhost:1234"
    }
    
    available = []
    for name, url in endpoints.items():
        if check_service(url, name):
            available.append(name)
            print(f"{name} available at {url}")
        else:
            print(f"{name} not available at {url}")
    
    return available

async def start_enhanced_agents(duration_hours: float = 1.0):
    """Start enhanced intelligent agents with critical thinking"""
    print(f"\nStarting Enhanced Agents with Critical Thinking for {duration_hours} hours...")
    
    try:
        # Run the enhanced agents with thinking capabilities
        process = subprocess.Popen([
            sys.executable, "run_intelligent_model_agents.py", 
            "--duration", str(duration_hours)
        ])
        
        print("Enhanced agents launched successfully!")
        print("Monitor logs in: logs/intelligent_model_agents/")
        print("Features: Intelligence persistence, critical thinking, real model selection")
        
        return process
        
    except Exception as e:
        print(f"Error starting enhanced agents: {e}")
        return None

def main():
    """Enhanced startup sequence"""
    print("Ultimate Copilot - Enhanced AI System with Intelligence Persistence")
    print("=" * 70)
    
    # Step 1: Start Qdrant for advanced memory
    print("🗃️ STEP 1: Vector Database (Qdrant)")
    qdrant_success = start_qdrant()
    if qdrant_success:
        print("Qdrant running - Advanced memory features enabled")
    else:
        print("Qdrant failed - Using basic memory (limited features)")
    
    # Step 2: Check AI model endpoints
    print("\nSTEP 2: AI Model Detection")
    available_models = check_models()
    
    if not available_models:
        print("No AI models detected. Starting models recommended:")
        print("  • Ollama: ollama serve")
        print("  • vLLM: ./start_vllm_cpu.sh")
        print("  • LM Studio: Start the application")
    else:
        print(f"Found {len(available_models)} model endpoints - Real intelligence enabled!")
    
    # Step 3: Install dependencies
    print("\n📦 STEP 3: Dependencies") 
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("Python dependencies ready")
    except subprocess.CalledProcessError:
        print("Some dependencies missing - agents may have limited functionality")
    
    # Step 4: Agent configuration
    print("\nSTEP 4: Enhanced Agent Launch")
    duration = float(input("⏰ Agent runtime hours (default 1.0): ") or "1.0")
    
    print("\nLAUNCHING ENHANCED FEATURES:")
    print("  Intelligence Persistence (agents remember across restarts)")
    print("  Critical Thinking (reasoning about improvements)")
    print("  Real Model Selection (based on task and availability)")
    print("  Adaptive Behavior (intelligence affects actual performance)")
    print("  Collaborative Memory (agents share insights)")
    
    # Launch enhanced agents
    try:
        process = asyncio.run(start_enhanced_agents(duration))
        
        if process:
            print(f"\nEnhanced agents running! Press Ctrl+C to stop.")
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\nStopping agents...")
                process.terminate()
                
    except Exception as e:
        print(f"Launch failed: {e}")

if __name__ == "__main__":
    main()


