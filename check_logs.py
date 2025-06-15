#!/usr/bin/env python3
"""
Check logs for agent activity
"""
import requests
import json

def check_logs():
    try:
        response = requests.get("http://127.0.0.1:8001/logs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logs = data.get("logs", [])
            
            print("All logs:")
            for log in logs:
                print(f"  {log.get('timestamp', '')[:19]} [{log.get('category', 'unknown')}] {log.get('message', '')}")
            
            print("\nAgent-related logs:")
            agent_logs = [log for log in logs if log.get("category", "").lower() in ["agents", "agent"]]
            for log in agent_logs:
                print(f"  {log.get('timestamp', '')[:19]}: {log.get('message', '')}")
                
            if not agent_logs:
                print("  No agent logs found")
                
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_logs()
