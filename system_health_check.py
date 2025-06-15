#!/usr/bin/env python3
"""
Ultimate Copilot System Health Checker
Verifies all components are properly configured and optimized
"""

import asyncio
import sys
import os
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_python_environment():
    """Check Python version and dependencies"""
    print("🐍 Checking Python Environment...")
    
    # Python version
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - requires 3.8+")
        return False
    
    # Check critical dependencies
    required_packages = [
        'asyncio', 'aiohttp', 'fastapi', 'streamlit', 
        'plotly', 'pandas', 'pyyaml', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_gpu_resources():
    """Check GPU and VRAM availability"""
    print("\n🎮 Checking GPU Resources...")
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            max_vram = 0
            for i, line in enumerate(lines):
                total, used, free = map(float, line.split(', '))
                total_gb = total / 1024
                used_gb = used / 1024
                free_gb = free / 1024
                utilization = (used / total) * 100
                max_vram = max(max_vram, total_gb)
                
                print(f"✅ GPU {i}: {total_gb:.1f}GB total, {free_gb:.1f}GB free ({utilization:.1f}% used)")
                
                if total_gb >= 8:
                    print(f"✅ GPU {i}: Excellent for all models")
                elif total_gb >= 6:
                    print(f"⚠️ GPU {i}: Good for medium models")
                elif total_gb >= 4:
                    print(f"⚠️ GPU {i}: Limited to small models")
                else:
                    print(f"❌ GPU {i}: Insufficient VRAM")
                      return max_vram >= 4  # Minimum viable
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️ NVIDIA GPU not detected - will use CPU models")
        return True  # CPU mode is acceptable
    
    return True

def check_llm_providers():
    """Check availability of LLM providers"""
    print("\n🧠 Checking LLM Providers...")
    
    providers = {
        'Ollama': 'http://localhost:11434/api/tags',
        'LM Studio': 'http://localhost:1234/v1/models',
        'vLLM': 'http://localhost:8000/v1/models'
    }
    
    available_providers = []
    
    for name, url in providers.items():
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"✅ {name}: Available")
                if name == 'Ollama':
                    try:
                        models = response.json().get('models', [])
                        print(f"   - {len(models)} models available")
                    except:
                        pass
                elif name in ['LM Studio', 'vLLM']:
                    try:
                        models = response.json().get('data', [])
                        print(f"   - {len(models)} models loaded")
                    except:
                        pass
                available_providers.append(name)
            else:
                print(f"❌ {name}: Not running (HTTP {response.status_code})")
        except requests.exceptions.RequestException:
            print(f"❌ {name}: Not available")
    
    if not available_providers:
        print("\n⚠️ No LLM providers available!")
        print("Please install and start at least one:")
        print("- Ollama: https://ollama.ai/ (Recommended)")
        print("- LM Studio: https://lmstudio.ai/")
        return False
    
    return True

def check_configuration():
    """Check system configuration files"""
    print("\n⚙️ Checking Configuration...")
    
    config_files = {
        'config/system_config.yaml': 'System configuration',
        'config/models_config.yaml': 'Models configuration'
    }
    
    all_good = True
    
    for file_path, description in config_files.items():
        if Path(file_path).exists():
            print(f"✅ {description}: {file_path}")
            
            # Validate YAML syntax
            try:
                if file_path.endswith('.yaml'):
                    import yaml
                    with open(file_path, 'r') as f:
                        yaml.safe_load(f)
                    print(f"   - Valid YAML syntax")
                elif file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        json.load(f)
                    print(f"   - Valid JSON syntax")
            except Exception as e:
                print(f"   ❌ Syntax error: {e}")
                all_good = False
                
        else:
            print(f"❌ {description}: Missing {file_path}")
            if file_path.endswith('.example'):
                example_file = file_path + '.example'
                if Path(example_file).exists():
                    print(f"   ℹ️ Copy from {example_file}")
            all_good = False
    
    return all_good

async def check_system_performance():
    """Check system performance and optimization"""
    print("\n⚡ Checking System Performance...")
    
    try:
        # Import VRAM manager
        from core.vram_manager import VRAMManager
        
        vram_manager = VRAMManager()
        optimization_info = await vram_manager.optimize_for_system()
        
        print(f"✅ VRAM Optimization: {optimization_info['optimization_level']}")
        print(f"✅ Detected VRAM: {optimization_info['detected_vram_gb']:.1f}GB")
        print(f"✅ Configured Max: {optimization_info['configured_max_gb']:.1f}GB")
        print(f"✅ Concurrent Models: {optimization_info['concurrent_model_limit']}")
        print(f"✅ Recommended Models: {len(optimization_info['recommended_models'])}")
        
        # Show top recommended models
        top_models = optimization_info['recommended_models'][:5]
        for model in top_models:
            size = vram_manager.model_sizes.get(model, 0)
            print(f"   - {model} ({size:.1f}GB)")
            
        return True
        
    except Exception as e:
        print(f"❌ Performance check failed: {e}")
        return False

def check_file_structure():
    """Check essential file structure"""
    print("\n📁 Checking File Structure...")
    
    essential_dirs = [
        'core', 'agents', 'config', 'frontend', 
        'integrations', 'utils'
    ]
    
    essential_files = [
        'main.py', 'requirements.txt',
        'core/enhanced_system_manager.py',
        'core/vram_manager.py',
        'agents/base_agent.py',
        'frontend/dashboard.py'
    ]
    
    all_good = True
    
    for directory in essential_dirs:
        if Path(directory).exists():
            print(f"✅ Directory: {directory}/")
        else:
            print(f"❌ Directory: {directory}/ - missing")
            all_good = False
    
    for file_path in essential_files:
        if Path(file_path).exists():
            print(f"✅ File: {file_path}")
        else:
            print(f"❌ File: {file_path} - missing")
            all_good = False
    
    # Create logs directory if missing
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
        print("✅ Created logs/ directory")
    
    return all_good

def generate_optimization_report():
    """Generate optimization recommendations"""
    print("\n📋 Optimization Recommendations:")
    print("=" * 50)
    
    # GPU-based recommendations
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            vram_mb = int(result.stdout.strip())
            vram_gb = vram_mb / 1024
            
            if vram_gb >= 16:
                print("🎯 High-end GPU detected:")
                print("   - Enable multiple concurrent models")
                print("   - Use largest available models")
                print("   - Consider enabling vLLM for maximum performance")
            elif vram_gb >= 8:
                print("🎯 8GB GPU optimization (Current focus):")
                print("   - Use intelligent model rotation")
                print("   - Limit to 1-2 concurrent models")
                print("   - Prefer 7B parameter models or smaller")
            elif vram_gb >= 4:
                print("🎯 Low VRAM optimization:")
                print("   - Use small models only (3B parameters or less)")
                print("   - Enable aggressive memory cleanup")
                print("   - Consider CPU-only mode for complex tasks")
            else:
                print("🎯 CPU-only mode recommended:")
                print("   - Use CPU-optimized models")
                print("   - Enable cloud fallbacks")
                print("   - Focus on smaller, efficient models")
        else:
            print("🎯 No GPU detected - CPU optimization:")
            print("   - Use CPU-optimized models only")
            print("   - Enable cloud API fallbacks")
            print("   - Optimize for response time over model size")
            
    except:
        print("🎯 Unable to detect GPU - assuming CPU mode")
    
    print("\n💡 General Recommendations:")
    print("   - Start with Ollama for easiest setup")
    print("   - Use dashboard for real-time monitoring")
    print("   - Enable cloud fallbacks for critical tasks")
    print("   - Configure your preferred editor integration")

async def main():
    """Main system health check"""
    print("🔍 Ultimate Copilot System Health Check")
    print("=" * 50)
    
    checks = [
        ("Python Environment", check_python_environment()),
        ("GPU Resources", check_gpu_resources()),
        ("LLM Providers", check_llm_providers()),
        ("Configuration", check_configuration()),
        ("File Structure", check_file_structure())
    ]
    
    # Run async performance check
    print("\n⚡ Running performance check...")
    performance_ok = await check_system_performance()
    checks.append(("System Performance", performance_ok))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 SYSTEM HEALTH SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    total = len(checks)
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Health: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 System is fully optimized and ready!")
        print("Run 'python main.py' or use 'ultimate_start.bat' to start")
    elif passed >= total * 0.8:
        print("\n⚠️ System is mostly ready with minor issues")
        print("Address the failed checks for optimal performance")
    else:
        print("\n❌ System needs attention before use")
        print("Please resolve the failed checks")
    
    generate_optimization_report()
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nHealth check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        sys.exit(1)
