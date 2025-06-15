# agent_upgrade_kit.py
# Drop this into your root directory and import where needed.

import json
import os
from datetime import datetime
from core.advanced_memory_manager import retrieve_top_memories_by_agent, update_agent_learning_profile
from persistent_agent_intelligence import load_agent_intelligence_profile
from utils.llm import call_llm  # Your existing LLM wrapper

# Path to your memory folder and agent configs
MEMORY_PATH = "data/memory"
PROFILES_PATH = "memory/agent_profiles"

# --- SMART PROMPT FORMATTING ---
def format_prompt(agent_name, task_description, top_memories, agent_experience):
    prompt = f"""
You are {agent_name}, a senior-level AI developer agent.
You follow the best practices in clean code, modular architecture, and testing.
Your task: {task_description}

Relevant knowledge from memory:
{chr(10).join([f"- {m}" for m in top_memories])}

Your recent experience includes:
{chr(10).join([f"• {s}" for s in agent_experience.get('successful_strategies', [])[-3:]])}

Respond with high-quality, production-ready code.
"""
    return prompt.strip()

# --- TASK EXECUTION WRAPPER ---
def run_agent_task(agent_name, task_description):
    print(f"[Swarm] Assigning task to {agent_name}: {task_description}")

    top_memories = retrieve_top_memories_by_agent(agent_name, top_n=3)
    agent_experience = load_agent_intelligence_profile(agent_name)
    prompt = format_prompt(agent_name, task_description, top_memories, agent_experience)

    result = call_llm(prompt, model=agent_experience.get("preferred_model", "deepseek-coder"))
    
    if "error" in result.lower():
        print(f"⚠️ {agent_name} failed initial attempt. Retrying with memory emphasis...")
        retry_prompt = prompt + "\n\nPrevious attempt failed. Review your past strategy and try again more thoroughly."
        result = call_llm(retry_prompt, model="codellama:7b")

    # Log learning
    update_agent_learning_profile(agent_name, {
        "task": task_description,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })

    return result

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    task = "Generate a FastAPI route for /status that returns current memory stats."
    output = run_agent_task("backend_dev", task)
    print("\n✅ Final Output:\n", output)