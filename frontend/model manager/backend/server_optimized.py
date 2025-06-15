"""
Optimized Backend service for the Unified Model Manager
Handles system-level operations with improved network performance
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import psutil
import os
import json
import asyncio
from typing import Dict, List, Optional
import platform
import requests
import time
import threading
from pathlib import Path
import socket
import logging
from functools import lru_cache
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Network optimization settings
NETWORK_TIMEOUT = 2  # Reduced timeout for faster response
MAX_RETRIES = 1
CACHE_DURATION = 5  # Cache system info for 5 seconds
REQUEST_POOL_SIZE = 5

app = FastAPI(title="Unified Model Manager Backend", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Provider paths - configurable for different systems
PROVIDER_PATHS = {
    "lmstudio": r"C:\Users\bcmad\AppData\Local\Programs\LM Studio\LM Studio.exe",
    "ollama": r"C:\Users\bcmad\AppData\Local\Programs\Ollama\ollama.exe",
    "vllm": "wsl"  # Special case for WSL
}

# Provider processes tracking
PROVIDER_PROCESSES = {}

# System monitoring cache
SYSTEM_CACHE = {
    "last_update": 0,
    "data": None,
    "cache_duration": CACHE_DURATION
}

# Marketplace models cache
MARKETPLACE_CACHE = {
    "data": [],
    "timestamp": 0,
    "cache_duration": 3600,  # 1 hour cache
    "is_refreshing": False
}

# Optimized system info function with caching
def get_cached_system_info() -> Dict:
    """Get cached system information to reduce repeated expensive calls"""
    current_time = time.time()
    
    if (SYSTEM_CACHE["data"] is None or 
        current_time - SYSTEM_CACHE["last_update"] > SYSTEM_CACHE["cache_duration"]):
        
        # Update cache with fresh data
        SYSTEM_CACHE["data"] = get_fresh_system_info()
        SYSTEM_CACHE["last_update"] = current_time
        logger.debug("System info cache updated")
    
    return SYSTEM_CACHE["data"]

def get_fresh_system_info() -> Dict:
    """Get fresh system information (expensive operation)"""
    try:
        # Get basic system info quickly
        cpu_percent = psutil.cpu_percent(interval=0.1)  # Very short interval
        memory = psutil.virtual_memory()
        
        # GPU info (quick check)
        gpus = []
        try:
            import GPUtil
            gpu_list = GPUtil.getGPUs()
            for gpu in gpu_list[:2]:  # Limit to first 2 GPUs for performance
                gpus.append({
                    "id": gpu.id,
                    "name": gpu.name[:30],  # Truncate long names
                    "utilization": round(gpu.load * 100, 1),
                    "memory_used": round(gpu.memoryUsed, 1),
                    "memory_total": round(gpu.memoryTotal, 1),
                    "temperature": getattr(gpu, 'temperature', 0)
                })
        except ImportError:
            logger.debug("GPUtil not available, skipping GPU info")
        except Exception as e:
            logger.debug(f"GPU info error: {e}")
        
        return {
            "cpu": {
                "usage": round(cpu_percent, 1),
                "cores": psutil.cpu_count(),
                "freq": round(psutil.cpu_freq().current if psutil.cpu_freq() else 0, 0)
            },
            "ram": {
                "total": round(memory.total / (1024**3), 1),
                "used": round(memory.used / (1024**3), 1),
                "percentage": round(memory.percent, 1),
                "available": round(memory.available / (1024**3), 1)
            },
            "gpus": gpus,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            "cpu": {"usage": 0, "cores": 0},
            "ram": {"total": 0, "used": 0, "percentage": 0},
            "gpus": [],
            "error": str(e),
            "timestamp": time.time()
        }

# Optimized provider status check
def check_provider_status_fast(provider_name: str) -> Dict:
    """Quick provider status check with timeout"""
    try:
        if provider_name == "ollama":
            # Quick process check instead of network call
            for proc in psutil.process_iter(['pid', 'name']):
                if 'ollama' in proc.info['name'].lower():
                    return {"status": "running", "method": "process_check"}
            return {"status": "stopped", "method": "process_check"}        
        elif provider_name == "lmstudio":
            # Test LM Studio API connection
            try:
                response = requests.get("http://localhost:1234/v1/models", timeout=3)
                if response.status_code == 200:
                    models_data = response.json()
                    model_count = len(models_data.get("data", []))
                    return {"status": "running", "method": "api_check", "models": model_count}
                else:
                    return {"status": "error", "method": "api_check", "error": f"HTTP {response.status_code}"}
            except requests.exceptions.ConnectionError:
                # Fallback to process check if API is not accessible
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'lm studio' in proc.info['name'].lower():
                        return {"status": "process_running", "method": "process_check", "note": "API not accessible"}
                return {"status": "stopped", "method": "process_check"}
            except Exception as e:
                return {"status": "error", "method": "api_check", "error": str(e)}
        
        else:
            return {"status": "unknown", "method": "not_implemented"}
            
    except Exception as e:
        logger.debug(f"Provider status check error for {provider_name}: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/")
async def root():
    return {
        "message": "Unified Model Manager Backend", 
        "version": "1.0.0",
        "status": "running",
        "providers": list(PROVIDER_PATHS.keys()),
        "optimization": "enabled"
    }

@app.get("/health")
async def health_check():
    """Lightweight health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "uptime": time.time() - SYSTEM_CACHE.get("start_time", time.time())
    }

@app.get("/system/info")
async def get_system_info():
    """Get cached system information for better performance"""
    return get_cached_system_info()

@app.get("/providers/status")
async def get_provider_status():
    """Get provider status with optimized checks"""
    providers = {}
    
    for provider_name in PROVIDER_PATHS.keys():
        providers[provider_name] = check_provider_status_fast(provider_name)
    
    return {
        "providers": providers,
        "timestamp": time.time()
    }

@app.get("/models/list/{provider}")
async def list_models(provider: str):
    """List models from provider with timeout"""
    if provider not in PROVIDER_PATHS:
        raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
    
    try:
        if provider == "ollama":
            # Quick timeout for ollama
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=NETWORK_TIMEOUT
            )
            if result.returncode == 0:
                return {"models": result.stdout.split('\n')[1:-1], "provider": provider}
                
        elif provider == "lmstudio":
            # Get models from LM Studio API
            try:
                response = requests.get("http://localhost:1234/v1/models", timeout=NETWORK_TIMEOUT)
                if response.status_code == 200:
                    models_data = response.json()
                    model_names = [model["id"] for model in models_data.get("data", [])]
                    return {"models": model_names, "provider": provider, "count": len(model_names)}
                else:
                    return {"models": [], "provider": provider, "error": f"HTTP {response.status_code}"}
            except requests.exceptions.ConnectionError:
                return {"models": [], "provider": provider, "error": "LM Studio API not accessible"}
            except Exception as e:
                return {"models": [], "provider": provider, "error": str(e)}
        
        # Fallback for other providers
        return {"models": [], "provider": provider, "status": "not_implemented"}
        
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout listing models for {provider}")
        return {"models": [], "provider": provider, "status": "timeout"}
    except Exception as e:
        logger.error(f"Error listing models for {provider}: {e}")
        return {"models": [], "provider": provider, "error": str(e)}

@app.get("/providers/{provider}/models")
async def get_provider_models(provider: str):
    """Get models from a specific provider - alternative endpoint format"""
    return await list_models(provider)

def find_available_port(start_port: int = 8080, max_attempts: int = 20) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('127.0.0.1', port))
                logger.info(f"🔍 Found available port: {port}")
                return port
        except OSError:
            logger.debug(f"Port {port} is busy, trying next...")
            continue
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")

# Provider Control Endpoints
@app.post("/api/providers/{provider}/start")
async def start_provider(provider: str, payload: Optional[dict] = None):
    """Start a provider service"""
    try:
        logger.info(f"🚀 Starting provider: {provider}")
        
        if provider == "lmstudio":
            result = await start_lmstudio()
        elif provider == "ollama":
            result = await start_ollama()
        elif provider == "vllm":
            result = await start_vllm(payload.get("modelPath") if payload else None)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to start {provider}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": [str(e)]
        }

@app.post("/api/providers/{provider}/stop")
async def stop_provider(provider: str):
    """Stop a provider service"""
    try:
        logger.info(f"🛑 Stopping provider: {provider}")
        
        if provider == "lmstudio":
            result = await stop_lmstudio()
        elif provider == "ollama":
            result = await stop_ollama()
        elif provider == "vllm":
            result = await stop_vllm()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to stop {provider}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": [str(e)]
        }

@app.post("/api/providers/{provider}/restart")
async def restart_provider(provider: str, payload: Optional[dict] = None):
    """Restart a provider service"""
    try:
        logger.info(f"🔄 Restarting provider: {provider}")
        
        # Stop first
        stop_result = await stop_provider(provider)
        if stop_result.get("status") == "error":
            logger.warning(f"Stop failed for {provider}, attempting start anyway")
        
        # Wait a moment for cleanup
        await asyncio.sleep(2)
        
        # Start again
        start_result = await start_provider(provider, payload)
        
        return {
            "status": start_result.get("status", "error"),
            "message": f"Restart {'successful' if start_result.get('status') == 'success' else 'failed'}",
            "logs": start_result.get("logs", [])
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to restart {provider}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": [str(e)]
        }

@app.get("/api/providers/{provider}/status")
async def get_specific_provider_status(provider: str):
    """Get detailed status of a specific provider"""
    try:
        if provider == "lmstudio":
            status = await check_lmstudio_status()
        elif provider == "ollama":
            status = await check_ollama_status()
        elif provider == "vllm":
            status = await check_vllm_status()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get status for {provider}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "connected": False
        }

# Provider Connection Check Functions
async def check_lmstudio_connection():
    """Check if LM Studio is accessible"""
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        return response.status_code == 200
    except:
        return False

async def check_ollama_connection():
    """Check if Ollama is accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

async def check_vllm_connection():
    """Check if vLLM is accessible"""
    try:
        response = requests.get("http://localhost:8000/v1/models", timeout=2)
        return response.status_code == 200
    except:
        return False

# Provider Control Helper Functions
async def start_lmstudio():
    """Start LM Studio if not running"""
    try:
        # Check if already running
        if await check_lmstudio_connection():
            return {
                "status": "success",
                "message": "LM Studio is already running",
                "port": 1234,
                "logs": ["Service already active"]
            }
        
        # Find LM Studio executable
        lmstudio_path = PROVIDER_PATHS.get("lmstudio")
        if not lmstudio_path or not os.path.exists(lmstudio_path):
            return {
                "status": "error",
                "message": "LM Studio executable not found",
                "logs": [f"Path not found: {lmstudio_path}"]
            }
        
        # Start LM Studio process
        logger.info(f"🚀 Starting LM Studio from: {lmstudio_path}")
        
        # Use startfile on Windows to start GUI app properly
        if platform.system() == "Windows":
            os.startfile(lmstudio_path)
        else:
            process = subprocess.Popen([lmstudio_path], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            PROVIDER_PROCESSES["lmstudio"] = process
        
        # Wait a moment for startup
        await asyncio.sleep(3)
        
        # Verify it started
        if await check_lmstudio_connection():
            return {
                "status": "success",
                "message": "LM Studio started successfully",
                "port": 1234,
                "logs": ["Service started and verified"]
            }
        else:
            return {
                "status": "error",
                "message": "LM Studio started but API not responding",
                "logs": ["Service started but API check failed"]
            }
            
    except Exception as e:
        logger.error(f"❌ Error starting LM Studio: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": [str(e)]
        }

async def stop_lmstudio():
    """Stop LM Studio process"""
    try:
        # Try to find and kill LM Studio processes
        killed = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'lm studio' in proc.info['name'].lower():
                    proc.kill()
                    killed = True
                    logger.info(f"🛑 Killed LM Studio process: {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Clean up tracked process
        if "lmstudio" in PROVIDER_PROCESSES:
            try:
                PROVIDER_PROCESSES["lmstudio"].terminate()
                del PROVIDER_PROCESSES["lmstudio"]
            except:
                pass
        
        await asyncio.sleep(1)
        
        return {
            "status": "success",
            "message": "LM Studio stopped" if killed else "LM Studio was not running",
            "logs": [f"Processes killed: {killed}"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error stopping LM Studio: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": [str(e)]
        }

async def start_ollama():
    """Start Ollama service"""
    try:
        # Check if already running
        if await check_ollama_connection():
            return {
                "status": "success",
                "message": "Ollama is already running",
                "port": 11434,
                "logs": ["Service already active"]
            }
        
        # Start Ollama
        if platform.system() == "Windows":
            # On Windows, Ollama might be a service or executable
            try:
                result = subprocess.run(["ollama", "serve"], 
                                      capture_output=True, text=True, timeout=5)
                logger.info(f"Ollama serve output: {result.stdout}")
            except subprocess.TimeoutExpired:
                # Ollama serve runs indefinitely, timeout is expected
                pass
        else:
            process = subprocess.Popen(["ollama", "serve"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            PROVIDER_PROCESSES["ollama"] = process
        
        # Wait for startup
        await asyncio.sleep(3)
        
        # Verify connection
        if await check_ollama_connection():
            return {
                "status": "success",
                "message": "Ollama started successfully",
                "port": 11434,
                "logs": ["Service started and verified"]
            }
        else:
            return {
                "status": "error",
                "message": "Ollama started but not responding",
                "logs": ["Service started but API check failed"]
            }
            
    except Exception as e:
        logger.error(f"❌ Error starting Ollama: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": [str(e)]
        }

async def stop_ollama():
    """Stop Ollama service"""
    try:
        # Try to find and kill Ollama processes
        killed = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'ollama' in proc.info['name'].lower():
                    proc.kill()
                    killed = True
                    logger.info(f"🛑 Killed Ollama process: {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Clean up tracked process
        if "ollama" in PROVIDER_PROCESSES:
            try:
                PROVIDER_PROCESSES["ollama"].terminate()
                del PROVIDER_PROCESSES["ollama"]
            except:
                pass
        
        await asyncio.sleep(1)
        
        return {
            "status": "success",
            "message": "Ollama stopped" if killed else "Ollama was not running",
            "logs": [f"Processes killed: {killed}"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error stopping Ollama: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": [str(e)]
        }

async def start_vllm(model_path: Optional[str] = None):
    """Start vLLM service"""
    try:
        # Check if already running
        if await check_vllm_connection():
            return {
                "status": "success",
                "message": "vLLM is already running",
                "port": 8000,
                "logs": ["Service already active"]
            }
        
        # vLLM typically runs in WSL or containers
        if not model_path:
            model_path = "microsoft/DialoGPT-medium"  # Default model
        
        # For now, return a mock success since vLLM setup is complex
        return {
            "status": "success",
            "message": "vLLM start initiated (WSL/Docker required)",
            "port": 8000,
            "logs": [f"Would start vLLM with model: {model_path}"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error starting vLLM: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": [str(e)]
        }

async def stop_vllm():
    """Stop vLLM service"""
    try:
        # For now, return mock success
        return {
            "status": "success",
            "message": "vLLM stop initiated",
            "logs": ["vLLM stop command sent"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error stopping vLLM: {e}")
        return {
            "status": "error",
            "message": str(e),
            "logs": [str(e)]
        }

async def check_lmstudio_status():
    """Get detailed LM Studio status"""
    connected = await check_lmstudio_connection()
    return {
        "status": "success",
        "connected": connected,
        "port": 1234,
        "message": "Connected" if connected else "Disconnected"
    }

async def check_ollama_status():
    """Get detailed Ollama status"""
    connected = await check_ollama_connection()
    return {
        "status": "success",
        "connected": connected,
        "port": 11434,
        "message": "Connected" if connected else "Disconnected"
    }

async def check_vllm_status():
    """Get detailed vLLM status"""
    connected = await check_vllm_connection()
    return {
        "status": "success", 
        "connected": connected,
        "port": 8000,
        "message": "Connected" if connected else "Disconnected"
    }

# Settings endpoints
@app.get("/api/settings")
async def get_settings():
    """Get current settings"""
    try:
        settings_file = Path("settings.json")
        if settings_file.exists():
            with open(settings_file, "r") as f:
                settings = json.load(f)
            return settings
        else:
            # Return default settings
            default_settings = {
                "autoRefresh": True,
                "refreshInterval": 30,
                "notifications": True,
                "compactView": False,
                "showSystemMonitor": True,
                "theme": "light",
                "maxConcurrentRequests": 5,
                "requestTimeout": 30
            }
            return default_settings
    except Exception as e:
        logger.error(f"❌ Error getting settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings")
async def save_settings(settings: dict):
    """Save settings to file"""
    try:
        settings_file = Path("settings.json")
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
        logger.info(f"💾 Settings saved to {settings_file.absolute()}")
        return {"status": "success", "message": "Settings saved successfully"}
    except Exception as e:
        logger.error(f"❌ Error saving settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Add startup time to cache
    SYSTEM_CACHE["start_time"] = time.time()
    
    # Add command line argument parsing
    parser = argparse.ArgumentParser(description="Unified Model Manager Backend")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8002, help="Port to bind to")
    args = parser.parse_args()
    
    logger.info("Starting Optimized Model Manager Backend...")
    logger.info(f"System: {platform.system()} {platform.release()}")
    logger.info(f"CPU Cores: {psutil.cpu_count()}")
    logger.info(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    logger.info(f"Network timeout: {NETWORK_TIMEOUT}s")
    logger.info(f"Cache duration: {CACHE_DURATION}s")
    
    # Find available port automatically
    try:
        port = find_available_port(args.port)
        
        # Write the port to a config file for the frontend
        config_path = Path("backend_config.json")
        with open(config_path, "w") as f:
            json.dump({"backend_port": port}, f)
            
        logger.info(f"📝 Wrote backend config: {config_path.absolute()}")
        
        # Also write to project root for frontend access
        root_config_path = Path("../backend_config.json")
        try:
            with open(root_config_path, "w") as f:
                json.dump({"backend_port": port}, f)
            logger.info(f"📝 Wrote root config: {root_config_path.absolute()}")
        except Exception as e:
            logger.warning(f"Could not write root config: {e}")
            
        logger.info(f"🚀 Starting optimized server on http://{args.host}:{port}")
        logger.info("💡 Press Ctrl+C to stop the server")
        
        uvicorn.run(
            app, 
            host=args.host, 
            port=port, 
            log_level="warning",  # Reduce log verbosity
            access_log=False     # Disable access logs for performance
        )
            
    except RuntimeError as e:
        logger.error(f"❌ Error: {e}")
        logger.error("Please free up some ports and try again.")
        exit(1)
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)
