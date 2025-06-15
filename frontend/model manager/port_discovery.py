#!/usr/bin/env python3
"""
Port discovery utility for Model Manager
Helps frontend automatically discover the correct backend port
"""

import json
import os
from pathlib import Path

def write_port_config(port: int, base_path: str = "."):
    """Write the current port to a config file for frontend discovery"""
    config = {
        "backend_port": port,
        "backend_url": f"http://127.0.0.1:{port}",
        "timestamp": str(os.path.getmtime(__file__) if os.path.exists(__file__) else 0)
    }
    
    # Write to multiple locations for reliability
    locations = [
        os.path.join(base_path, "backend_config.json"),
        os.path.join(base_path, "..", "backend_config.json"),
        os.path.join(base_path, "..", "..", "backend_config.json")
    ]
    
    for location in locations:
        try:
            Path(location).parent.mkdir(parents=True, exist_ok=True)
            with open(location, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"📝 Wrote backend config: {os.path.abspath(location)}")
        except Exception as e:
            print(f"❌ Failed to write config to {location}: {e}")

def read_port_config(base_path: str = "."):
    """Read the current port from config file"""
    locations = [
        os.path.join(base_path, "backend_config.json"),
        os.path.join(base_path, "..", "backend_config.json"),
        os.path.join(base_path, "..", "..", "backend_config.json")
    ]
    
    for location in locations:
        try:
            if os.path.exists(location):
                with open(location, 'r') as f:
                    config = json.load(f)
                return config.get("backend_port"), config.get("backend_url")
        except Exception as e:
            print(f"❌ Failed to read config from {location}: {e}")
    
    return None, None

def find_available_port(start_port: int = 8002):
    """Find the next available port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"No available ports found starting from {start_port}")

if __name__ == "__main__":
    # Test the port discovery
    port, url = read_port_config()
    if port:
        print(f"Current backend port: {port}")
        print(f"Current backend URL: {url}")
    else:
        print("No backend config found")
