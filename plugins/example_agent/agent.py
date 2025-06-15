"""
Example Custom Agent Plugin
"""

from agents.base_agent import BaseAgent
from typing import Dict

class ExampleAgent(BaseAgent):
    async def agent_initialize(self):
        """Initialize example agent"""
        self.example_setting = self.config.get('example_setting', 'default_value')
        self.enable_feature = self.config.get('enable_feature', True)
        
        self.capabilities = ['example_task', 'demo_functionality']
        
        self.logger.info(f"Example agent initialized with setting: {self.example_setting}")
    
    async def process_task(self, task: Dict, context: Dict) -> Dict:
        """Process tasks for example agent"""
        task_type = self.determine_task_type(task)
        
        if task_type == "example_task":
            return await self.handle_example_task(task, context)
        elif task_type == "demo_functionality":
            return await self.handle_demo_functionality(task, context)
        else:
            return await self.general_example_task(task, context)
    
    async def handle_example_task(self, task: Dict, context: Dict) -> Dict:
        """Handle example task type"""
        prompt = f"""
        As an example agent, process the following task:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Provide a helpful response demonstrating custom agent capabilities.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=500)
        
        return {
            'type': 'example_task',
            'response': response,
            'agent_setting': self.example_setting,
            'feature_enabled': self.enable_feature,
            'success': True,
            'summary': f"Example task completed: {task.get('title', 'Unknown')}"
        }
    
    async def handle_demo_functionality(self, task: Dict, context: Dict) -> Dict:
        """Handle demo functionality"""
        return {
            'type': 'demo_functionality',
            'message': 'Demo functionality executed successfully',
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'summary': 'Demo functionality completed'
        }
    
    async def general_example_task(self, task: Dict, context: Dict) -> Dict:
        """Handle general example tasks"""
        prompt = f"""
        As a custom example agent, help with:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Provide guidance using custom agent capabilities.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=400)
        
        return {
            'type': 'general_example',
            'guidance': response,
            'success': True,
            'summary': f"General example task completed: {task.get('title', 'task')}"
        }
    
    def determine_task_type(self, task: Dict) -> str:
        """Determine task type for example agent"""
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        
        if any(word in description + title for word in ['example', 'test', 'demo']):
            return "example_task"
        elif any(word in description + title for word in ['demo', 'functionality', 'feature']):
            return "demo_functionality"
        else:
            return "general"
    
    async def agent_health_check(self):
        """Example agent health check"""
        test_prompt = "Hello from example agent"
        response = await self.generate_llm_response(test_prompt, max_tokens=10)
        
        if not response or len(response) < 5:
            raise Exception("Example agent health check failed")
    
    async def agent_cleanup(self):
        """Example agent cleanup"""
        self.logger.info("Example agent cleanup completed")
