import socket

def test_port_detection():
    print("Testing port detection...")
    
    def find_available_port(start_port: int = 8080, max_attempts: int = 5) -> int:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(('0.0.0.0', port))
                    print(f"✅ Port {port} is available")
                    return port
            except OSError as e:
                print(f"❌ Port {port} is busy: {e}")
                continue
        raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts}")
    
    try:
        port = find_available_port(8080)
        print(f"Selected port: {port}")
    except RuntimeError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_port_detection()
