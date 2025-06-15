"""
Simple Agent Implementations for Quick Testing
These work without full infrastructure dependencies
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    from core.mock_managers import MockLLMManager, MockMemoryManager
except ImportError:
    # Create simple mock classes if the module doesn't exist
    class MockLLMManager:
        async def generate_response(self, agent_type, prompt):
            return f"Mock response for {agent_type}: {prompt[:100]}..."
    
    class MockMemoryManager:
        async def store_task_result(self, task, result):
            pass
        
        async def retrieve_similar_tasks(self, description, limit=3):
            return []

class SimpleBaseAgent:
    """Simplified base agent that works immediately"""
    
    def __init__(self, agent_id: str = "agent"):
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        self.status = "initializing"
        self.llm_manager = MockLLMManager()
        self.memory_manager = MockMemoryManager()
        
        # Setup work logging
        self.work_log_dir = Path("logs/agents")
        self.work_log_dir.mkdir(parents=True, exist_ok=True)
        self.work_log_file = self.work_log_dir / f"{agent_id}_work.log"
        
    async def log_work(self, work_type: str, details: str, files_analyzed=None):
        """Log detailed work to agent-specific file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"""
{'='*60}
TIMESTAMP: {timestamp}
AGENT: {self.agent_id.upper()}
WORK TYPE: {work_type}
{'='*60}

{details}

"""
        
        if files_analyzed:
            log_entry += f"\nFILES ANALYZED:\n"
            for file in files_analyzed:
                log_entry += f"  - {file}\n"
        
        log_entry += f"\n{'='*60}\n\n"
        
        try:
            with open(self.work_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            self.logger.warning(f"Could not write to work log: {e}")
    
    async def process_task(self, task: Dict[str, Any], context: Dict[str, Any]):
        """Basic task processing"""
        task_type = task.get("type", "unknown")
        workspace = task.get("workspace", os.getcwd())
        
        self.logger.info(f"Processing {task_type} task")
        
        # Simple mock processing
        result = {
            "agent": self.agent_id,
            "task_type": task_type,
            "workspace": workspace,
            "summary": f"Completed {task_type} analysis",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        await self.log_work(task_type, f"Processed task in {workspace}")
        
        return result

class SimpleOrchestratorAgent(SimpleBaseAgent):
    """Simple orchestrator for coordination"""
    
    def __init__(self):
        super().__init__("orchestrator")
        
    async def process_task(self, task: Dict[str, Any], context: Dict[str, Any]):
        self.logger.info("Orchestrator analyzing workspace and creating plan...")
        
        workspace = task.get("workspace", os.getcwd())
        
        # Basic file analysis
        files = list(Path(workspace).glob("*.py"))
        
        result = {
            "agent": "orchestrator",
            "summary": f"Analyzed workspace with {len(files)} Python files",
            "plan": f"Coordinate development across {len(files)} files",
            "recommendations": [
                "Continue with backend optimization",
                "Enhance agent communication",
                "Improve error handling"
            ]
        }
        
        await self.log_work("orchestration", f"Created plan for {len(files)} files")
        
        return result

class SimpleArchitectAgent(SimpleBaseAgent):
    """Simple architect for system design"""
    
    def __init__(self):
        super().__init__("architect")
        
    async def process_task(self, task: Dict[str, Any], context: Dict[str, Any]):
        self.logger.info("Architect analyzing system architecture...")
        
        workspace = task.get("workspace", os.getcwd())
        
        result = {
            "agent": "architect",
            "summary": "Analyzed system architecture and design patterns",
            "plan": "Architecture analysis completed with recommendations for improvement"
        }
        
        await self.log_work("architecture", "Completed architectural analysis")
        
        return result

class SimpleBackendAgent(SimpleBaseAgent):
    """Simple backend developer"""
    
    def __init__(self):
        super().__init__("backend")
        
    async def process_task(self, task: Dict[str, Any], context: Dict[str, Any]):
        self.logger.info("Backend agent analyzing code quality...")
        
        result = {
            "agent": "backend",
            "summary": "Analyzed backend code for optimizations and improvements",
            "plan": "Backend analysis completed with performance recommendations"
        }
        
        await self.log_work("backend_analysis", "Completed backend code analysis")
        
        return result

class SimpleFrontendAgent(SimpleBaseAgent):
    """Simple frontend developer"""
    
    def __init__(self):
        super().__init__("frontend")
        
    async def process_task(self, task: Dict[str, Any], context: Dict[str, Any]):
        self.logger.info("Frontend agent analyzing UI/UX...")
        
        result = {
            "agent": "frontend",
            "summary": "Analyzed frontend components and user experience",
            "plan": "Frontend analysis completed with UI/UX recommendations"
        }
        
        await self.log_work("frontend_analysis", "Completed frontend analysis")
        
        return result

class SimpleQAAgent(SimpleBaseAgent):
    """Simple QA agent"""
    
    def __init__(self):
        super().__init__("qa")
        
    async def process_task(self, task: Dict[str, Any], context: Dict[str, Any]):
        self.logger.info("QA agent performing quality analysis...")
        
        result = {
            "agent": "qa",
            "summary": "Performed comprehensive quality analysis and testing review",
            "plan": "QA analysis completed with quality improvement recommendations"
        }
        
        await self.log_work("qa_analysis", "Completed quality assurance analysis")
        
        return result
