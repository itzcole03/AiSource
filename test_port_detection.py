#!/usr/bin/env python3
"""
Test port detection for Model Manager Backend
"""
import socket
import time

def find_available_port(start_port: int = 8080, max_attempts: int = 20) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('127.0.0.1', port))
                print(f"✅ Found available port: {port}")
                return port
        except OSError as e:
            print(f"❌ Port {port} is busy")
            continue
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")

def test_port(host: str, port: int) -> bool:
    """Test if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False

if __name__ == "__main__":
    print("🔍 Testing port detection...")
    
    # Test specific ports
    test_ports = [8080, 8081, 8082, 8083, 8084]
    
    for port in test_ports:
        available = test_port('127.0.0.1', port)
        status = "✅ Available" if available else "❌ Busy"
        print(f"Port {port}: {status}")
    
    print("\n🔍 Finding next available port from 8080...")
    try:
        available_port = find_available_port(8080)
        print(f"✅ Found port: {available_port}")
    except RuntimeError as e:
        print(f"❌ Error: {e}")
