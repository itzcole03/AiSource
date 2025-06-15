# real_time_diff_learner.py
# Watches file diffs and creates learning entries for the agent responsible

import os
import json
from datetime import datetime
from difflib import unified_diff

MEMORY_PATH = "memory/agent_learning/"
CODE_DIR = "workspace/codebase"
DIFF_LOG = "data/diff_history.json"

os.makedirs(MEMORY_PATH, exist_ok=True)

def learn_from_diff(agent_name, old_file_path, new_file_path):
    try:
        with open(old_file_path, "r") as f_old, open(new_file_path, "r") as f_new:
            old_lines = f_old.readlines()
            new_lines = f_new.readlines()

        diff = list(unified_diff(old_lines, new_lines, fromfile=old_file_path, tofile=new_file_path))
        if len(diff) < 3:
            return "No meaningful diff."

        entry = {
            "agent": agent_name,
            "file": os.path.basename(new_file_path),
            "diff_preview": diff[:20],
            "timestamp": datetime.now().isoformat()
        }

        with open(DIFF_LOG, "a", encoding="utf-8") as f:
            json.dump(entry, f)
            f.write(",\n")

        return f"✅ Learned from {old_file_path} → {new_file_path}"

    except Exception as e:
        return f"❌ Diff learning failed: {e}"

# Example:
if __name__ == "__main__":
    result = learn_from_diff("backend_dev", "temp/back_before.py", "temp/back_after.py")
    print(result)