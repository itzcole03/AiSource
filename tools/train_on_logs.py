# train_on_logs.py
# Summarizes recent swarm activity into lessons for agent intelligence updates

import json
import os
from datetime import datetime

LOGS_PATH = "data/logs/"
INTEL_PATH = "memory/agent_profiles/"
OUTPUT_PATH = "memory/agent_learning/"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def summarize_agent_log(agent_name):
    log_file = os.path.join(LOGS_PATH, f"{agent_name}_history.json")
    if not os.path.exists(log_file):
        print(f"[No log found for {agent_name}]")
        return None

    with open(log_file, "r", encoding="utf-8") as f:
        entries = json.load(f)

    completions = [e for e in entries if "result" in e and len(e["result"]) > 30]
    if not completions:
        return None

    summary = {
        "agent": agent_name,
        "total_tasks": len(completions),
        "insights": [
            f"✅ Task: {e['task']}\nSummary: {e['result'][:140]}..."
            for e in completions[-5:]
        ]
    }
    
    out_file = os.path.join(OUTPUT_PATH, f"{agent_name}_summary_{datetime.now().strftime('%Y%m%d')}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary

if __name__ == "__main__":
    agents = ["architect", "backend_dev", "frontend_dev", "qa_agent"]
    for agent in agents:
        summary = summarize_agent_log(agent)
        if summary:
            print(f"\n📘 {agent.upper()} SUMMARY:\n", json.dumps(summary, indent=2))