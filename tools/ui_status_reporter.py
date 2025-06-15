# ui_status_reporter.py
# Dashboard auto-summary widget for agent swarm state

import json
from datetime import datetime

MEMORY_PATH = "memory/agent_profiles/"
LOG_PATH = "data/logs/"

def get_agent_status():
    agents = ["architect", "backend_dev", "frontend_dev", "qa_agent", "orchestrator"]
    summaries = []
    for agent in agents:
        try:
            with open(f"{MEMORY_PATH}/{agent}.json") as f:
                profile = json.load(f)
            task_count = profile.get("total_tasks", 0)
            learned = profile.get("successful_strategies", [])
            summaries.append({
                "agent": agent,
                "tasks_completed": task_count,
                "last_strategy": learned[-1] if learned else "—",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        except:
            summaries.append({"agent": agent, "error": "No profile found"})
    return summaries

if __name__ == "__main__":
    from pprint import pprint
    pprint(get_agent_status())