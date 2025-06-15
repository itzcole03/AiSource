"""
CodeGPT Integration Bridge for Ultimate Copilot System
Enables hybrid approach leveraging both CodeGPT agents and our custom orchestration
"""

import asyncio
import logging
import json
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime

class CodeGPTBridge:
    """Bridge to integrate CodeGPT agents with our orchestration system"""
    
    def __init__(self, api_key: str, org_id: str):
        self.api_key = api_key
        self.org_id = org_id
        self.base_url = "https://api.codegpt.co/v1"
        self.logger = logging.getLogger("CodeGPTBridge")
        
        # Track CodeGPT agents
        self.codegpt_agents = {}
        self.session = None
    
    async def initialize(self):
        """Initialize the CodeGPT bridge"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        # Load available CodeGPT agents
        await self.load_available_agents()
        
        self.logger.info(f"CodeGPT Bridge initialized with {len(self.codegpt_agents)} agents")
    
    async def load_available_agents(self):
        """Load list of available CodeGPT agents"""
        try:
            url = f"{self.base_url}/agents"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    for agent in data.get('agents', []):
                        self.codegpt_agents[agent['id']] = {
                            'name': agent['name'],
                            'description': agent.get('description', ''),
                            'capabilities': agent.get('capabilities', []),
                            'model': agent.get('model', 'unknown')
                        }
                else:
                    self.logger.warning(f"Failed to load CodeGPT agents: {response.status}")
        except Exception as e:
            self.logger.error(f"Error loading CodeGPT agents: {e}")
    
    async def chat_completion(self, agent_id: str, messages: List[Dict], **kwargs) -> Dict:
        """Send chat completion request to CodeGPT agent"""
        try:
            url = f"{self.base_url}/chat/completions"
            payload = {
                "agent_id": agent_id,
                "messages": messages,
                "stream": kwargs.get('stream', False),
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 1000)
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'content': result.get('choices', [{}])[0].get('message', {}).get('content', ''),
                        'usage': result.get('usage', {}),
                        'model': result.get('model', 'unknown')
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'error': f"HTTP {response.status}: {error_text}"
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_codegpt_task(self, agent_id: str, task: Dict) -> Dict:
        """Execute a task using a CodeGPT agent"""
        task_prompt = self.format_task_prompt(task)
        
        messages = [
            {"role": "user", "content": task_prompt}
        ]
        
        result = await self.chat_completion(agent_id, messages)
        
        return {
            'type': 'codegpt_response',
            'agent_id': agent_id,
            'task_id': task.get('id'),
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def format_task_prompt(self, task: Dict) -> str:
        """Format task for CodeGPT agent consumption"""
        prompt = f"Task: {task.get('title', 'Untitled')}\n"
        prompt += f"Description: {task.get('description', '')}\n"
        
        if task.get('context'):
            prompt += f"Context: {task.get('context')}\n"
        
        if task.get('requirements'):
            prompt += f"Requirements: {task.get('requirements')}\n"
        
        if task.get('files'):
            prompt += f"Related files: {', '.join(task.get('files', []))}\n"
        
        return prompt
    
    async def close(self):
        """Close the bridge connection"""
        if self.session:
            await self.session.close()


class HybridAgentManager:
    """Manages both custom agents and CodeGPT agents in a unified way"""
    
    def __init__(self, custom_agent_manager, codegpt_bridge: CodeGPTBridge):
        self.custom_agent_manager = custom_agent_manager
        self.codegpt_bridge = codegpt_bridge
        self.logger = logging.getLogger("HybridAgentManager")
        
        # Agent routing configuration
        self.agent_routing = {
            # Tasks best handled by CodeGPT
            'code_review': 'codegpt',
            'documentation': 'codegpt',
            'quick_questions': 'codegpt',
            'syntax_help': 'codegpt',
            
            # Tasks best handled by custom agents
            'project_orchestration': 'custom',
            'multi_agent_coordination': 'custom',
            'system_integration': 'custom',
            'workflow_automation': 'custom',
            'vram_optimization': 'custom'
        }
        
        # Preferred CodeGPT agents for different task types
        self.codegpt_agent_preferences = {
            'code_review': 'coding-expert-agent-id',
            'documentation': 'docs-writer-agent-id',
            'quick_questions': 'general-assistant-agent-id'
        }
    
    async def initialize(self):
        """Initialize the hybrid manager"""
        await self.codegpt_bridge.initialize()
        self.logger.info("Hybrid Agent Manager initialized")
    
    async def execute_task(self, task: Dict) -> Dict:
        """Route and execute task using appropriate agent system"""
        task_type = self.determine_task_type(task)
        routing = self.agent_routing.get(task_type, 'custom')
        
        if routing == 'codegpt':
            return await self.execute_codegpt_task(task, task_type)
        else:
            return await self.execute_custom_task(task)
    
    async def execute_codegpt_task(self, task: Dict, task_type: str) -> Dict:
        """Execute task using CodeGPT agent"""
        agent_id = self.codegpt_agent_preferences.get(task_type)
        
        if not agent_id:
            # Fallback to custom system if no CodeGPT agent configured
            return await self.execute_custom_task(task)
        
        self.logger.info(f"Executing task {task.get('id')} with CodeGPT agent {agent_id}")
        return await self.codegpt_bridge.execute_codegpt_task(agent_id, task)
    
    async def execute_custom_task(self, task: Dict) -> Dict:
        """Execute task using custom agent system"""
        self.logger.info(f"Executing task {task.get('id')} with custom agents")
        return await self.custom_agent_manager.execute_task(task)
    
    def determine_task_type(self, task: Dict) -> str:
        """Determine the type of task for routing purposes"""
        title = task.get('title', '').lower()
        description = task.get('description', '').lower()
        
        # Simple keyword-based classification
        if any(keyword in title + description for keyword in ['review', 'check', 'analyze']):
            return 'code_review'
        elif any(keyword in title + description for keyword in ['document', 'readme', 'docs']):
            return 'documentation'
        elif any(keyword in title + description for keyword in ['orchestrate', 'coordinate', 'manage']):
            return 'project_orchestration'
        elif any(keyword in title + description for keyword in ['workflow', 'automation', 'pipeline']):
            return 'workflow_automation'
        else:
            return 'general'
    
    async def get_agent_status(self) -> Dict:
        """Get status of all agents (custom and CodeGPT)"""
        custom_status = await self.custom_agent_manager.get_agent_status()
        
        codegpt_status = {
            'available_agents': len(self.codegpt_bridge.codegpt_agents),
            'agents': list(self.codegpt_bridge.codegpt_agents.keys())
        }
        
        return {
            'custom_agents': custom_status,
            'codegpt_agents': codegpt_status,
            'routing_config': self.agent_routing
        }
    
    async def close(self):
        """Close the hybrid manager"""
        await self.codegpt_bridge.close()
