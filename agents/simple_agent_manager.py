import json
import logging
from datetime import datetime
import os

class SimpleAgentManager:
    def __init__(self):
        self.agents = {
            "orchestrator": {"status": "idle", "last_active": None},
            "architect": {"status": "idle", "last_active": None}, 
            "backend": {"status": "idle", "last_active": None},
            "frontend": {"status": "idle", "last_active": None},
            "qa": {"status": "idle", "last_active": None}
        }
        self.workspace_path = None
        self.instruction_log = []
        
    def send_instruction(self, instruction, workspace_path=None):
        try:
            if workspace_path:
                self.workspace_path = workspace_path
                
            # Log the instruction
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "instruction": instruction,
                "workspace": workspace_path or self.workspace_path,
                "status": "received"
            }
            self.instruction_log.append(log_entry)
            
            # For now, just log to file
            log_file = "agent_instructions.log"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{log_entry['timestamp']}: {instruction}\n")
                if workspace_path:
                    f.write(f"  Workspace: {workspace_path}\n")
                f.write("---\n")
                
            return {"success": True, "message": f"Instruction logged: {instruction[:50]}..."}
            
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_agent_status(self):
        return {
            "agents": self.agents,
            "workspace": self.workspace_path,
            "recent_instructions": self.instruction_log[-5:] if self.instruction_log else []
        }
    
    def update_agent_status(self, agent_type, status):
        if agent_type in self.agents:
            self.agents[agent_type]["status"] = status
            self.agents[agent_type]["last_active"] = datetime.now().isoformat()