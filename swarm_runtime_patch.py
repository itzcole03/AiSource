# PATCHED: run_swarm.py or orchestrator integration
# Integrates Agent Upgrade Kit into swarm runtime logic

from agent_upgrade_kit import run_agent_task

# Assuming you have a central dispatcher or task loop in your orchestrator
# Replace or patch into existing agent task assignment block:

def dispatch_task(agent_name, task_description):
    print(f"[Swarm Dispatch] Task: {task_description} → {agent_name}")
    try:
        result = run_agent_task(agent_name, task_description)
        print("[Agent Result]:\n", result)
        return result
    except Exception as e:
        print(f"[ERROR] Agent {agent_name} failed task with exception: {e}")
        return None

# Example swarm runner integration:
if __name__ == "__main__":
    test_tasks = [
        ("architect", "Create an architecture overview markdown for this project"),
        ("backend_dev", "Refactor the memory_manager to use LRU caching"),
        ("qa_agent", "Generate test coverage for agent_real_work_system.py")
    ]

    for agent, task in test_tasks:
        dispatch_task(agent, task)