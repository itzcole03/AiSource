# tools/gpt_override.py
# Plug-and-play GPT-4 lead agent proxy

import os
import requests
import json
from core.advanced_memory_manager import summarize_recent_activity

GPT_API_KEY = os.getenv("OPENAI_API_KEY")  # or hardcode temporarily
GPT_MODEL = "gpt-4"
GPT_ENDPOINT = "https://api.openai.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {GPT_API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = """
You are the Lead Developer overseeing an AI swarm. Your job is to review current project state, recent issues, and instruct agents to complete tasks in elite engineering quality. Prioritize test coverage, documentation, and modular design. Respond only with JSON task instructions.
"""

# Generate lead plan
def lead_dev_plan(project_summary: str):
    payload = {
        "model": GPT_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": project_summary}
        ],
        "temperature": 0.3
    }
    try:
        response = requests.post(GPT_ENDPOINT, headers=headers, json=payload)
        data = response.json()
        plan = data['choices'][0]['message']['content']
        return plan
    except Exception as e:
        print("[GPT Override Error]", e)
        return None

# Example usage:
if __name__ == "__main__":
    summary = summarize_recent_activity(limit=5)
    plan = lead_dev_plan(summary)
    print("\n🧠 Lead Dev Plan:\n", plan)