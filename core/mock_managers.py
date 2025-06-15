"""
Simple Mock LLM Manager for quick agent testing
This allows agents to run without full LLM infrastructure
"""

import asyncio
import logging
from typing import Dict, Any

class MockLLMManager:
    """Mock LLM Manager that provides simulated responses"""
    
    def __init__(self):
        self.logger = logging.getLogger("MockLLM")
        
    async def initialize(self):
        """Mock initialization"""
        self.logger.info("Mock LLM Manager initialized")
        
    async def generate_response(self, model: str = "mock", prompt: str = "", **kwargs) -> Dict[str, Any]:
        """Generate a mock response based on the prompt"""
        
        # Simulate thinking time
        await asyncio.sleep(0.1)
        
        # Generate context-aware mock responses
        if "architect" in prompt.lower() or "architecture" in prompt.lower():
            content = """
            ## Architecture Analysis
            
            Based on the workspace analysis, I recommend:
            
            1. **Code Structure**: The project follows a modular agent-based architecture
            2. **Improvements Needed**: 
               - Add proper error handling
               - Implement better logging
               - Add configuration validation
            3. **Next Steps**: Focus on core functionality first, then optimize
            """
            
        elif "backend" in prompt.lower() or "api" in prompt.lower():
            content = """
            ## Backend Analysis
            
            Current backend status:
            
            1. **FastAPI Framework**: Good choice for async operations
            2. **Agent Communication**: Needs better message passing
            3. **Recommendations**:
               - Add proper API endpoints
               - Implement health checks
               - Add request/response validation
            """
            
        elif "frontend" in prompt.lower() or "ui" in prompt.lower():
            content = """
            ## Frontend Analysis
            
            UI/UX Assessment:
            
            1. **Current State**: Basic command-line interface
            2. **Improvements**:
               - Add web dashboard
               - Real-time agent status display
               - Interactive task management
            3. **Technology**: Consider Streamlit or FastAPI + React
            """
            
        elif "qa" in prompt.lower() or "quality" in prompt.lower():
            content = """
            ## Quality Analysis
            
            Code quality assessment:
            
            1. **Test Coverage**: Currently minimal - needs improvement
            2. **Code Quality**: Good structure, needs better error handling
            3. **Recommendations**:
               - Add unit tests for agents
               - Implement integration tests
               - Add code quality metrics
            """
            
        elif "orchestrat" in prompt.lower() or "plan" in prompt.lower():
            content = """
            ## Task Orchestration Plan
            
            Analyzing workspace for autonomous improvement:
            
            1. **Immediate Tasks**:
               - Verify agent functionality
               - Test communication between agents
               - Identify critical missing components
            
            2. **Agent Assignments**:
               - Architect: Review code structure
               - Backend: Optimize core systems
               - Frontend: Improve user interface
               - QA: Test and validate changes
            
            3. **Success Metrics**:
               - All agents operational
               - Basic functionality working
               - Ready for self-improvement
            """
            
        else:
            # Generic response
            content = f"""
            ## Analysis Complete
            
            Processed request: {prompt[:100]}...
            
            **Summary**: Mock response generated for development testing.
            
            **Recommendations**:
            1. Continue with agent development
            2. Test core functionality
            3. Implement real LLM when ready
            
            **Status**: Ready for next task
            """
        
        return {
            "content": content,
            "model": model,
            "tokens_used": len(prompt.split()) + len(content.split()),
            "status": "success"
        }
    
    async def health_check(self):
        """Mock health check"""
        return {"status": "healthy", "provider": "mock"}
    
    async def shutdown(self):
        """Mock shutdown"""
        self.logger.info("🔮 Mock LLM Manager shutdown")


class MockMemoryManager:
    """Mock Memory Manager for agent history"""
    
    def __init__(self):
        self.logger = logging.getLogger("MockMemory")
        self.memories = []
        
    async def initialize(self):
        """Mock initialization"""
        self.logger.info("🧠 Mock Memory Manager initialized")
        
    async def get_agent_history(self, agent_id: str):
        """Get mock agent history"""
        return []
    
    async def store_task_result(self, task: Dict, result: Dict):
        """Store mock task result"""
        self.memories.append({
            "task": task,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        })
        
    async def retrieve_similar_tasks(self, description: str, limit: int = 3):
        """Retrieve mock similar tasks"""
        return self.memories[-limit:] if self.memories else []
    
    async def shutdown(self):
        """Mock shutdown"""
        self.logger.info("🧠 Mock Memory Manager shutdown")
