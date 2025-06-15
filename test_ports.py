#!/usr/bin/env python3
"""
Port Testing Utility

Tests port availability and conflict resolution for the dashboard system.
"""

import socket
import sys
from typing import Optional, List

def check_port_in_use(port: int, host: str = '127.0.0.1') -> bool:
    """Check if a port is in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0  # Port is in use
    except Exception as e:
        print(f"Error checking port {port}: {e}")
        return False

def find_available_port(start_port: int = 8501, max_attempts: int = 10, host: str = '127.0.0.1') -> Optional[int]:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if not check_port_in_use(port, host):
            return port
    return None

def test_port_range(start_port: int, end_port: int, host: str = '127.0.0.1') -> List[int]:
    """Test a range of ports and return available ones"""
    available_ports = []
    for port in range(start_port, end_port + 1):
        if not check_port_in_use(port, host):
            available_ports.append(port)
    return available_ports

def main():
    print("🔍 Ultimate Copilot Port Testing Utility")
    print("=" * 50)
    
    # Test default dashboard ports
    frontend_port = 8501
    backend_port = 8001
    
    print(f"\n📊 Testing default ports:")
    print(f"Frontend port {frontend_port}: {'❌ IN USE' if check_port_in_use(frontend_port) else '✅ AVAILABLE'}")
    print(f"Backend port {backend_port}: {'❌ IN USE' if check_port_in_use(backend_port) else '✅ AVAILABLE'}")
    
    # Find alternative ports if needed
    if check_port_in_use(frontend_port):
        alt_frontend = find_available_port(frontend_port + 1)
        if alt_frontend:
            print(f"📋 Alternative frontend port: {alt_frontend}")
        else:
            print("⚠️ No alternative frontend port found in range")
    
    if check_port_in_use(backend_port):
        alt_backend = find_available_port(backend_port + 1)
        if alt_backend:
            print(f"📋 Alternative backend port: {alt_backend}")
        else:
            print("⚠️ No alternative backend port found in range")
    
    # Test port range for Streamlit (common range)
    print(f"\n📊 Testing Streamlit port range (8501-8510):")
    streamlit_ports = test_port_range(8501, 8510)
    if streamlit_ports:
        print(f"✅ Available Streamlit ports: {', '.join(map(str, streamlit_ports))}")
    else:
        print("❌ No available Streamlit ports in range")
    
    # Test port range for APIs (common range)
    print(f"\n📊 Testing API port range (8000-8010):")
    api_ports = test_port_range(8000, 8010)
    if api_ports:
        print(f"✅ Available API ports: {', '.join(map(str, api_ports))}")
    else:
        print("❌ No available API ports in range")
    
    # Interactive port testing
    print(f"\n🔧 Interactive port testing:")
    try:
        while True:
            port_input = input("Enter port to test (or 'quit' to exit): ")
            if port_input.lower() in ['quit', 'exit', 'q']:
                break
            
            try:
                port = int(port_input)
                if 1 <= port <= 65535:
                    status = check_port_in_use(port)
                    print(f"Port {port}: {'❌ IN USE' if status else '✅ AVAILABLE'}")
                else:
                    print("❌ Port must be between 1 and 65535")
            except ValueError:
                print("❌ Please enter a valid port number")
    
    except KeyboardInterrupt:
        print("\n\n👋 Port testing completed")

if __name__ == "__main__":
    main()
