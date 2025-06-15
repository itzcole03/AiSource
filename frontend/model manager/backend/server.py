"""
Backend service for the Unified Model Manager
Handles system-level operations like starting/stopping providers and system monitoring
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
import aiohttp
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Network optimization settings
NETWORK_TIMEOUT = 2  # Reduced timeout for faster response
MAX_RETRIES = 1
CACHE_DURATION = 5  # Cache system info for 5 seconds
REQUEST_POOL_SIZE = 5

# System cache for improved performance
SYSTEM_CACHE = {
    "data": None,
    "last_update": 0,
    "cache_duration": CACHE_DURATION
}

app = FastAPI(title="Unified Model Manager Backend", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
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

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize HTTP client on startup"""
    global http_client
    timeout = httpx.Timeout(NETWORK_TIMEOUT, connect=NETWORK_TIMEOUT)
    http_client = httpx.AsyncClient(
        timeout=timeout,
        limits=httpx.Limits(max_connections=REQUEST_POOL_SIZE)
    )
    logger.info("HTTP client initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup HTTP client on shutdown"""
    global http_client
    if http_client:
        await http_client.aclose()
    logger.info("HTTP client closed")

# Optimized network functions
async def make_request_with_retry(url: str, max_retries: int = MAX_RETRIES) -> Optional[Dict]:
    """Make HTTP request with retry logic and timeout"""
    global http_client
    
    for attempt in range(max_retries + 1):
        try:
            response = await http_client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Request to {url} returned {response.status_code}")
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"Failed to connect to {url} after {max_retries + 1} attempts: {e}")
            else:
                logger.debug(f"Attempt {attempt + 1} failed for {url}: {e}")
            await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
    
    return None

@lru_cache(maxsize=128)
def get_cached_system_info() -> Dict:
    """Get cached system information to reduce repeated calls"""
    current_time = time.time()
    
    if (SYSTEM_CACHE["data"] is None or 
        current_time - SYSTEM_CACHE["last_update"] > SYSTEM_CACHE["cache_duration"]):
        
        # Update cache
        SYSTEM_CACHE["data"] = get_system_info_internal()
        SYSTEM_CACHE["last_update"] = current_time
    
    return SYSTEM_CACHE["data"]

def get_system_info_internal() -> Dict:
    """Internal function to get fresh system information"""
    try:
        # CPU info
        cpu_info = {
            "cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "usage": psutil.cpu_percent(interval=1)
        }
        
        # RAM info
        ram = psutil.virtual_memory()
        ram_info = {
            "total": f"{ram.total / (1024**3):.1f} GB",
            "used": f"{ram.used / (1024**3):.1f} GB",
            "available": f"{ram.available / (1024**3):.1f} GB",
            "percentage": ram.percent
        }
        
        # Basic system info without async calls (simplified for internal use)
        system_data = {
            "cpu": cpu_info,
            "ram": ram_info,
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "timestamp": time.time()
        }
        
        return system_data
        
    except Exception as e:
        logger.error(f"Failed to get system info: {str(e)}")
        return {
            "cpu": {"cores": 0, "physical_cores": 0, "usage": 0},
            "ram": {"total": "0 GB", "used": "0 GB", "available": "0 GB", "percentage": 0},
            "platform": {"system": "unknown", "release": "unknown"},
            "timestamp": time.time(),
            "error": str(e)
        }

@app.get("/")
async def root():
    return {
        "message": "Unified Model Manager Backend", 
        "version": "1.0.0",
        "status": "running",
        "providers": list(PROVIDER_PATHS.keys())
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/system/info")
async def get_system_info():
    """Get comprehensive system information including CPU, RAM, and GPU usage"""
    try:
        current_time = time.time()
        
        # Use cached data if less than 2 seconds old
        if SYSTEM_CACHE["data"] and (current_time - SYSTEM_CACHE["last_update"]) < 2:
            return SYSTEM_CACHE["data"]
        
        # CPU info
        cpu_info = {
            "cores": psutil.cpu_count(logical=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "usage": psutil.cpu_percent(interval=1)
        }
        
        # RAM info
        ram = psutil.virtual_memory()
        ram_info = {
            "total": f"{ram.total / (1024**3):.1f} GB",
            "used": f"{ram.used / (1024**3):.1f} GB",
            "available": f"{ram.available / (1024**3):.1f} GB",
            "percentage": ram.percent
        }
        
        # GPU info
        gpu_info = await get_gpu_info()
        
        # Provider status
        provider_status = await get_provider_status()
        
        # Disk info
        disk_info = get_disk_info()
        
        system_data = {
            "cpu": cpu_info,
            "ram": ram_info,
            "gpus": gpu_info,
            "providers": provider_status,
            "disk": disk_info,
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "timestamp": current_time
        }
        
        # Update cache
        SYSTEM_CACHE["data"] = system_data
        SYSTEM_CACHE["last_update"] = current_time
        
        return system_data
        
    except Exception as e:
        logger.error(f"Failed to get system info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")

async def get_gpu_info():
    """Get detailed GPU information"""
    gpus = []
    
    try:
        # Try NVIDIA GPU detection first
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu", 
             "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 6:
                        gpus.append({
                            "name": parts[0],
                            "memory": f"{parts[2]} MB / {parts[1]} MB used",
                            "utilization": int(parts[4]) if parts[4].isdigit() else 0,
                            "temperature": f"{parts[5]}°C" if parts[5].isdigit() else "N/A",
                            "type": "NVIDIA"
                        })
        
        # If no NVIDIA GPUs found, try AMD detection
        if not gpus:
            try:
                # Try AMD GPU detection (Windows)
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ["wmic", "path", "win32_VideoController", "get", "name,AdapterRAM", "/format:csv"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')[1:]  # Skip header
                        for line in lines:
                            if line.strip() and ',' in line:
                                parts = line.split(',')
                                if len(parts) >= 3 and parts[2].strip():
                                    name = parts[2].strip()
                                    if 'AMD' in name or 'Radeon' in name or 'Ryzen' in name:
                                        ram_bytes = parts[1].strip() if parts[1].strip().isdigit() else "0"
                                        ram_mb = int(ram_bytes) // (1024 * 1024) if ram_bytes.isdigit() else 0
                                        
                                        gpus.append({
                                            "name": name,
                                            "memory": f"{ram_mb} MB" if ram_mb > 0 else "Shared System RAM",
                                            "utilization": 0,  # Can't get real-time utilization easily
                                            "temperature": "N/A",
                                            "type": "AMD"
                                        })
            except Exception as e:
                logger.warning(f"AMD GPU detection failed: {e}")
        
        # Fallback for integrated graphics
        if not gpus:
            gpus.append({
                "name": "AMD Ryzen 9 3900X (Integrated Graphics)",
                "memory": "Shared System RAM",
                "utilization": 0,
                "temperature": "N/A",
                "type": "Integrated"
            })
                
    except Exception as e:
        logger.error(f"GPU detection error: {e}")
        gpus.append({
            "name": "GPU Detection Failed",
            "memory": "Unknown",
            "utilization": 0,
            "temperature": "N/A",
            "type": "Unknown"
        })
    
    return gpus

def get_disk_info():
    """Get disk usage information"""
    try:
        if platform.system() == "Windows":
            disk_usage = psutil.disk_usage('C:')
        else:
            disk_usage = psutil.disk_usage('/')
        
        return {
            "total": f"{disk_usage.total / (1024**3):.1f} GB",
            "used": f"{disk_usage.used / (1024**3):.1f} GB",
            "free": f"{disk_usage.free / (1024**3):.1f} GB",
            "percentage": (disk_usage.used / disk_usage.total) * 100
        }
    except Exception as e:
        logger.error(f"Disk info error: {e}")
        return {
            "total": "Unknown",
            "used": "Unknown", 
            "free": "Unknown",
            "percentage": 0
        }

@app.get("/providers/status")
async def get_provider_status():
    """Check installation and running status of all providers"""
    status = {}
    
    for provider, path in PROVIDER_PATHS.items():
        if provider == "vllm":
            # Special handling for vLLM in WSL
            status[provider] = await check_vllm_status()
        else:
            status[provider] = {
                "installed": os.path.exists(path) if path != "wsl" else True,
                "running": await is_provider_running(provider),
                "path": path
            }
    
    return status

async def check_vllm_status():
    """Check vLLM status in WSL"""
    try:
        # Check if WSL is available
        result = subprocess.run(["wsl", "--status"], capture_output=True, text=True, timeout=5)
        wsl_available = result.returncode == 0
        
        if not wsl_available:
            return {"installed": False, "running": False, "path": "WSL not available"}
        
        # Check if vLLM is running (check port 8000)
        try:
            response = requests.get("http://localhost:8000/health", timeout=3)
            running = response.status_code == 200
        except:
            running = False
        
        return {
            "installed": True,  # Assume installed in Ubuntu as mentioned
            "running": running,
            "path": "Ubuntu/WSL"
        }
    except Exception as e:
        logger.error(f"vLLM status check failed: {e}")
        return {"installed": False, "running": False, "path": "WSL check failed"}

async def is_provider_running(provider: str) -> bool:
    """Check if a provider process is running"""
    if provider == "lmstudio":
        # Check if LM Studio is running (port 1234)
        return await check_port(1234)
    elif provider == "ollama":
        # Check if Ollama is running (port 11434)
        return await check_port(11434)
    return False

async def check_port(port: int) -> bool:
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"Port check failed for {port}: {e}")
        return False

@app.post("/providers/{provider}/start")
async def start_provider(provider: str):
    """Start a provider service"""
    if provider not in PROVIDER_PATHS:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    try:
        if provider == "lmstudio":
            return await start_lmstudio()
        elif provider == "ollama":
            return await start_ollama()
        elif provider == "vllm":
            return await start_vllm()
        else:
            raise HTTPException(status_code=400, detail="Unknown provider")
    except Exception as e:
        logger.error(f"Failed to start {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/providers/{provider}/stop")
async def stop_provider(provider: str):
    """Stop a provider service"""
    if provider not in PROVIDER_PATHS:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    try:
        if provider == "lmstudio":
            return await stop_lmstudio()
        elif provider == "ollama":
            return await stop_ollama()
        elif provider == "vllm":
            return await stop_vllm()
        else:
            raise HTTPException(status_code=400, detail="Unknown provider")
    except Exception as e:
        logger.error(f"Failed to stop {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def start_lmstudio():
    """Start LM Studio"""
    try:
        if await is_provider_running("lmstudio"):
            return {"status": "already_running", "message": "LM Studio is already running"}
        
        if not os.path.exists(PROVIDER_PATHS["lmstudio"]):
            return {"status": "error", "message": "LM Studio not found at expected path"}
        
        process = subprocess.Popen([PROVIDER_PATHS["lmstudio"]], shell=True)
        PROVIDER_PROCESSES["lmstudio"] = process
        
        # Wait a bit for startup
        await asyncio.sleep(3)
        
        return {"status": "started", "message": "LM Studio started successfully"}
    except Exception as e:
        logger.error(f"Failed to start LM Studio: {e}")
        return {"status": "error", "message": f"Failed to start LM Studio: {str(e)}"}

async def start_ollama():
    """Start Ollama"""
    try:
        if await is_provider_running("ollama"):
            return {"status": "already_running", "message": "Ollama is already running"}
        
        if not os.path.exists(PROVIDER_PATHS["ollama"]):
            return {"status": "error", "message": "Ollama not found at expected path"}
        
        # Start Ollama serve
        process = subprocess.Popen([PROVIDER_PATHS["ollama"], "serve"], shell=True)
        PROVIDER_PROCESSES["ollama"] = process
        
        # Wait a bit for startup
        await asyncio.sleep(3)
        
        return {"status": "started", "message": "Ollama started successfully"}
    except Exception as e:
        logger.error(f"Failed to start Ollama: {e}")
        return {"status": "error", "message": f"Failed to start Ollama: {str(e)}"}

async def start_vllm():
    """Start vLLM via Windows batch script"""
    try:
        script_path = r"c:\Users\bcmad\OneDrive\Desktop\full model gui app\project\project\scripts\vllm_windows_launcher_advanced.bat"
        
        if not os.path.exists(script_path):
            return {"status": "error", "message": "vLLM launcher script not found"}
        
        # Start the vLLM launcher
        process = subprocess.Popen([script_path], shell=True)
        PROVIDER_PROCESSES["vllm"] = process
        
        return {"status": "started", "message": "vLLM launcher started"}
    except Exception as e:
        logger.error(f"Failed to start vLLM: {e}")
        return {"status": "error", "message": f"Failed to start vLLM: {str(e)}"}

async def stop_lmstudio():
    """Stop LM Studio"""
    try:
        # Kill LM Studio processes
        killed_count = 0
        for process in psutil.process_iter(['pid', 'name']):
            try:
                if 'LM Studio' in process.info['name'] or 'lmstudio' in process.info['name'].lower():
                    process.terminate()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if "lmstudio" in PROVIDER_PROCESSES:
            PROVIDER_PROCESSES["lmstudio"].terminate()
            del PROVIDER_PROCESSES["lmstudio"]
        
        return {"status": "stopped", "message": f"LM Studio stopped ({killed_count} processes terminated)"}
    except Exception as e:
        logger.error(f"Failed to stop LM Studio: {e}")
        return {"status": "error", "message": f"Failed to stop LM Studio: {str(e)}"}

async def stop_ollama():
    """Stop Ollama"""
    try:
        # Kill Ollama processes
        killed_count = 0
        for process in psutil.process_iter(['pid', 'name']):
            try:
                if 'ollama' in process.info['name'].lower():
                    process.terminate()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if "ollama" in PROVIDER_PROCESSES:
            PROVIDER_PROCESSES["ollama"].terminate()
            del PROVIDER_PROCESSES["ollama"]
        
        return {"status": "stopped", "message": f"Ollama stopped ({killed_count} processes terminated)"}
    except Exception as e:
        logger.error(f"Failed to stop Ollama: {e}")
        return {"status": "error", "message": f"Failed to stop Ollama: {str(e)}"}

async def stop_vllm():
    """Stop vLLM"""
    try:
        # Stop vLLM via WSL
        result = subprocess.run(["wsl", "bash", "-c", "pkill -f vllm"], timeout=10)
        
        if "vllm" in PROVIDER_PROCESSES:
            PROVIDER_PROCESSES["vllm"].terminate()
            del PROVIDER_PROCESSES["vllm"]
        
        return {"status": "stopped", "message": "vLLM stopped"}
    except Exception as e:
        logger.error(f"Failed to stop vLLM: {e}")
        return {"status": "error", "message": f"Failed to stop vLLM: {str(e)}"}

@app.get("/providers/{provider}/models")
async def get_provider_models(provider: str):
    """Get models from a specific provider (proxy to avoid CORS)"""
    if provider == "lmstudio":
        try:
            # Proxy request to LM Studio API
            response = requests.get("http://localhost:1234/v1/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Transform to our model format
                models = []
                for model in data.get('data', []):
                    models.append({
                        "id": model.get('id', 'unknown'),
                        "name": model.get('id', 'unknown'),
                        "provider": "lmstudio",
                        "size": "Unknown",
                        "format": "GGUF",
                        "status": "available",
                        "port": 1234
                    })
                return {"models": models}
            else:
                raise HTTPException(status_code=response.status_code, detail="LM Studio API error")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"Cannot connect to LM Studio: {str(e)}")
    elif provider == "ollama":
        try:
            # Proxy request to Ollama API
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get('models', []):
                    models.append({
                        "id": model.get('name', 'unknown'),
                        "name": model.get('name', 'unknown'),
                        "provider": "ollama",
                        "size": f"{model.get('size', 0) / (1024**3):.1f} GB" if model.get('size') else "Unknown",
                        "format": model.get('details', {}).get('format', 'GGUF'),
                        "status": "available",
                        "port": 11434
                    })
                return {"models": models}
            else:
                raise HTTPException(status_code=response.status_code, detail="Ollama API error")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"Cannot connect to Ollama: {str(e)}")
    elif provider == "vllm":
        try:
            # Proxy request to vLLM API
            response = requests.get("http://localhost:8000/v1/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get('data', []):
                    models.append({
                        "id": model.get('id', 'unknown'),
                        "name": model.get('id', 'unknown'),
                        "provider": "vllm",
                        "size": "Unknown",
                        "format": "HuggingFace",
                        "status": "running",
                        "port": 8000
                    })
                return {"models": models}
            else:
                raise HTTPException(status_code=response.status_code, detail="vLLM API error")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"Cannot connect to vLLM: {str(e)}")
    else:
        raise HTTPException(status_code=404, detail="Provider not supported")

@app.get("/system/processes")
async def get_system_processes():
    """Get information about running processes related to AI providers"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'cmdline']):
            try:
                name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
                
                if any(provider in name or provider in cmdline for provider in ['ollama', 'lmstudio', 'vllm', 'python']):
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_mb": proc.info['memory_info'].rss / (1024 * 1024),
                        "cmdline": ' '.join(proc.info['cmdline'][:3]) if proc.info['cmdline'] else ''
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {"processes": processes}
    except Exception as e:
        logger.error(f"Failed to get processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def find_available_port(start_port: int = 8080, max_attempts: int = 20) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('127.0.0.1', port))
                logger.info(f"🔍 Found available port: {port}")
                return port
        except OSError as e:
            logger.debug(f"🔍 Port {port} is busy, trying next...")
            continue
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Add command line argument parsing
    parser = argparse.ArgumentParser(description="Unified Model Manager Backend")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    args = parser.parse_args()
    
    logger.info("Starting Unified Model Manager Backend...")
    logger.info(f"System: {platform.system()} {platform.release()}")
    logger.info(f"CPU Cores: {psutil.cpu_count()}")
    logger.info(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    
    # Find available port automatically
    try:
        # Always use the find_available_port function to ensure we get a working port
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
            
        logger.info(f"🚀 Starting server on http://{args.host}:{port}")
        logger.info("💡 Press Ctrl+C to stop the server")
        
        uvicorn.run(app, host=args.host, port=port, log_level="info")
            
    except RuntimeError as e:
        logger.error(f"❌ Error: {e}")
        logger.error("Please free up some ports and try again.")
        exit(1)
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        exit(1)