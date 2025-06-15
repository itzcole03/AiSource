"""
Orchestrator Agent - Coordinates tasks and manages workflow
"""

from agents.base_agent import BaseAgent
from core.file_coordinator import safe_write_file
from typing import Dict, List
import datetime
import json

class OrchestratorAgent(BaseAgent):
    async def agent_initialize(self):
        """Initialize orchestrator-specific capabilities"""
        self.workflow_patterns = ["Sequential", "Parallel", "Conditional", "Loop", "Branch"]
        self.coordination_strategies = ["Priority-based", "Dependency-based", "Resource-based"]
    
    async def process_task(self, task: Dict, context: Dict) -> Dict:
        """Process orchestration and coordination tasks"""
        task_type = self.determine_task_type(task)
        
        if task_type == "task_planning":
            return await self.plan_tasks(task, context)
        elif task_type == "workflow_design":
            return await self.design_workflow(task, context)
        elif task_type == "resource_allocation":
            return await self.allocate_resources(task, context)
        elif task_type == "progress_monitoring":
            return await self.monitor_progress(task, context)
        else:
            return await self.general_orchestration_task(task, context)
    
    async def plan_tasks(self, task: Dict, context: Dict) -> Dict:
        """Plan and break down complex tasks"""
        prompt = f"""
        As a project orchestrator, break down the following into manageable tasks:
        
        Project: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Create:
        1. Task breakdown structure
        2. Dependencies between tasks
        3. Priority assignments
        4. Agent assignments
        5. Timeline estimates
        
        Consider available agents: architect, backend_dev, frontend_dev, qa_analyst.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=1200)
        
        # Create task planning files
        await self.create_planning_files(task, response)
        
        return {
            'type': 'task_planning',
            'task_breakdown': response,
            'subtasks': self.extract_subtasks(response),
            'dependencies': self.extract_dependencies(response),
            'assignments': self.extract_assignments(response),
            'summary': f"Task plan created for {task.get('title', 'project')}"
        }
    
    async def design_workflow(self, task: Dict, context: Dict) -> Dict:
        """Design workflow for complex processes"""
        prompt = f"""
        As a workflow designer, create a workflow for:
        
        Process: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Design:
        1. Workflow steps and sequence
        2. Decision points and branches
        3. Error handling and rollback
        4. Monitoring and checkpoints
        5. Success criteria
        
        Focus on efficiency and reliability.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=1000)
        
        return {
            'type': 'workflow_design',
            'workflow': response,
            'steps': self.extract_workflow_steps(response),
            'decision_points': self.extract_decision_points(response),
            'checkpoints': self.extract_checkpoints(response),
            'summary': f"Workflow designed for {task.get('title', 'process')}"
        }
    
    async def allocate_resources(self, task: Dict, context: Dict) -> Dict:
        """Allocate resources and agents to tasks"""
        prompt = f"""
        As a resource manager, allocate resources for:
        
        Project: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Consider:
        1. Agent capabilities and availability
        2. Task priorities and deadlines
        3. Resource constraints
        4. Skill matching
        5. Load balancing
        
        Available agents: architect, backend_dev, frontend_dev, qa_analyst.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'resource_allocation',
            'allocation_plan': response,
            'assignments': self.extract_resource_assignments(response),
            'priorities': self.extract_priorities(response),
            'timeline': self.extract_timeline(response),
            'summary': f"Resource allocation plan for {task.get('title', 'project')}"
        }
    
    async def monitor_progress(self, task: Dict, context: Dict) -> Dict:
        """Monitor and report on progress"""
        prompt = f"""
        As a project monitor, analyze progress for:
        
        Project: {task.get('title', '')}
        Current Status: {task.get('description', '')}
        
        Provide:
        1. Progress assessment
        2. Bottleneck identification
        3. Risk analysis
        4. Recommendations for improvement
        5. Next steps
        
        Focus on actionable insights.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'progress_monitoring',
            'progress_report': response,
            'bottlenecks': self.extract_bottlenecks(response),
            'risks': self.extract_risks(response),
            'recommendations': self.extract_recommendations(response),
            'summary': f"Progress report for {task.get('title', 'project')}"
        }
    
    async def general_orchestration_task(self, task: Dict, context: Dict) -> Dict:
        """Handle general orchestration tasks"""
        prompt = f"""
        As a project orchestrator, help coordinate:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Context from previous work:
        {self.format_context(context)}
        
        Provide coordination guidance and next steps.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=600)
        
        return {
            'type': 'general_orchestration',
            'guidance': response,
            'summary': f"Orchestration guidance for {task.get('title', 'task')}"
        }
    
    def determine_task_type(self, task: Dict) -> str:
        """Determine the type of orchestration task"""
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        
        if any(word in description + title for word in ['plan', 'breakdown', 'organize']):
            return "task_planning"
        elif any(word in description + title for word in ['workflow', 'process', 'sequence']):
            return "workflow_design"
        elif any(word in description + title for word in ['allocate', 'assign', 'resource']):
            return "resource_allocation"
        elif any(word in description + title for word in ['monitor', 'progress', 'status', 'track']):
            return "progress_monitoring"
        else:
            return "general"
    
    def format_context(self, context: Dict) -> str:
        """Format context for LLM prompt"""
        formatted = ""
        
        if context.get('similar_tasks'):
            formatted += "Similar previous tasks:\n"
            for task in context['similar_tasks'][:2]:
                formatted += f"- {task.get('task_title', 'Unknown')}: {task.get('result', {}).get('summary', 'No summary')}\n"
        
        return formatted
    
    def extract_subtasks(self, response: str) -> List[Dict]:
        """Extract subtasks from response"""
        subtasks = []
        lines = response.split('\n')
        
        for line in lines:
            if any(indicator in line for indicator in ['1.', '2.', '3.', '-', '*']) and len(line.strip()) > 5:
                # Extract task info
                task_text = line.strip()
                
                # Simple parsing for agent assignment
                agent = "orchestrator"  # default
                if "frontend" in task_text.lower():
                    agent = "frontend_dev"
                elif "backend" in task_text.lower() or "api" in task_text.lower():
                    agent = "backend_dev"
                elif "test" in task_text.lower() or "qa" in task_text.lower():
                    agent = "qa_analyst"
                elif "design" in task_text.lower() or "architect" in task_text.lower():
                    agent = "architect"
                
                subtasks.append({
                    'title': task_text,
                    'agent': agent,
                    'priority': 'medium'
                })
        
        return subtasks[:10]  # Limit to 10 subtasks
    
    def extract_dependencies(self, response: str) -> List[Dict]:
        """Extract task dependencies from response"""
        dependencies = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['depends', 'after', 'before', 'requires']):
                dependencies.append({
                    'description': line.strip(),
                    'type': 'sequential'
                })
        
        return dependencies[:5]
    
    def extract_assignments(self, response: str) -> List[Dict]:
        """Extract agent assignments from response"""
        assignments = []
        lines = response.split('\n')
        
        agents = ['architect', 'backend_dev', 'frontend_dev', 'qa_analyst']
        
        for line in lines:
            for agent in agents:
                if agent.replace('_', ' ') in line.lower() or agent in line.lower():
                    assignments.append({
                        'agent': agent,
                        'task': line.strip(),
                        'priority': 'medium'
                    })
                    break
        
        return assignments[:8]
    
    def extract_workflow_steps(self, response: str) -> List[str]:
        """Extract workflow steps from response"""
        steps = []
        lines = response.split('\n')
        
        for line in lines:
            if any(indicator in line for indicator in ['step', '1.', '2.', '3.', '-', '*']):
                steps.append(line.strip())
        
        return steps[:10]
    
    def extract_decision_points(self, response: str) -> List[str]:
        """Extract decision points from response"""
        decisions = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['if', 'decision', 'choose', 'branch']):
                decisions.append(line.strip())
        
        return decisions[:5]
    
    def extract_checkpoints(self, response: str) -> List[str]:
        """Extract checkpoints from response"""
        checkpoints = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['checkpoint', 'milestone', 'review', 'validate']):
                checkpoints.append(line.strip())
        
        return checkpoints[:5]
    
    def extract_resource_assignments(self, response: str) -> List[Dict]:
        """Extract resource assignments from response"""
        assignments = []
        lines = response.split('\n')
        
        agents = ['architect', 'backend_dev', 'frontend_dev', 'qa_analyst']
        
        for line in lines:
            for agent in agents:
                if agent.replace('_', ' ') in line.lower():
                    assignments.append({
                        'agent': agent,
                        'allocation': line.strip()
                    })
        
        return assignments[:5]
    
    def extract_priorities(self, response: str) -> List[str]:
        """Extract priorities from response"""
        priorities = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['priority', 'urgent', 'high', 'critical']):
                priorities.append(line.strip())
        
        return priorities[:5]
    
    def extract_timeline(self, response: str) -> List[str]:
        """Extract timeline information from response"""
        timeline = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['timeline', 'schedule', 'deadline', 'duration']):
                timeline.append(line.strip())
        
        return timeline[:5]
    
    def extract_bottlenecks(self, response: str) -> List[str]:
        """Extract bottlenecks from response"""
        bottlenecks = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['bottleneck', 'blocked', 'delay', 'slow']):
                bottlenecks.append(line.strip())
        
        return bottlenecks[:3]
    
    def extract_risks(self, response: str) -> List[str]:
        """Extract risks from response"""
        risks = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['risk', 'concern', 'issue', 'problem']):
                risks.append(line.strip())
        
        return risks[:5]
    
    def extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from response"""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['recommend', 'suggest', 'should', 'improve']):
                recommendations.append(line.strip())
        
        return recommendations[:5]
    
    async def agent_health_check(self):
        """Orchestrator-specific health check"""
        # Test orchestration knowledge
        test_prompt = "What is task orchestration?"
        response = await self.generate_llm_response(test_prompt, max_tokens=50)
        
        if not response or len(response) < 10:
            raise Exception("Orchestrator agent knowledge test failed")
    
    async def agent_cleanup(self):
        """Orchestrator-specific cleanup"""
        # Clear any cached workflow data
        pass
    
    async def create_planning_files(self, task: Dict, response: str):
        """Create task planning and workflow files"""
        try:
            task_title = task.get('title', 'project').replace(' ', '_').lower()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create task breakdown document
            breakdown_doc = f"""# Task Breakdown - {task.get('title', 'Project')}

## Overview
Generated on: {timestamp}
Project: {task.get('title', '')}

## Task Planning
{response}

## Subtasks
{self.format_subtasks(self.extract_subtasks(response))}

## Dependencies
{self.format_dependencies(self.extract_dependencies(response))}

## Agent Assignments
{self.format_assignments(self.extract_assignments(response))}

## Generated by OrchestratorAgent
"""
            
            # Write task breakdown document
            breakdown_file = f"agent_outputs/OrchestratorAgent/task_breakdown_{task_title}_{timestamp}.md"
            if safe_write_file(breakdown_file, breakdown_doc, self.agent_id, priority=1):
                self.logger.info(f"Task breakdown created: {breakdown_file}")
            
            # Create workflow JSON file for automation
            workflow_data = {
                "project": task.get('title', ''),
                "timestamp": timestamp,
                "subtasks": self.extract_subtasks(response),
                "dependencies": self.extract_dependencies(response),
                "assignments": self.extract_assignments(response),
                "status": "planned"
            }
            
            workflow_file = f"agent_outputs/OrchestratorAgent/workflow_{task_title}_{timestamp}.json"
            if safe_write_file(workflow_file, json.dumps(workflow_data, indent=2), self.agent_id, priority=1):
                self.logger.info(f"Workflow JSON created: {workflow_file}")
            
            # Create project timeline
            timeline_content = self.generate_timeline_content(task, response)
            timeline_file = f"agent_outputs/OrchestratorAgent/timeline_{task_title}_{timestamp}.md"
            if safe_write_file(timeline_file, timeline_content, self.agent_id, priority=1):
                self.logger.info(f"Timeline created: {timeline_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating planning files: {e}")
    
    def format_subtasks(self, subtasks: list) -> str:
        """Format subtasks into readable list"""
        if not subtasks:
            return "- No specific subtasks identified"
        return "\n".join([f"- {task}" for task in subtasks])
    
    def format_dependencies(self, dependencies: list) -> str:
        """Format dependencies into readable list"""
        if not dependencies:
            return "- No specific dependencies identified"
        return "\n".join([f"- {dep}" for dep in dependencies])
    
    def format_assignments(self, assignments: list) -> str:
        """Format agent assignments into readable list"""
        if not assignments:
            return "- No specific assignments identified"
        return "\n".join([f"- {assignment}" for assignment in assignments])
    
    def generate_timeline_content(self, task: Dict, response: str) -> str:
        """Generate project timeline content"""
        return f"""# Project Timeline - {task.get('title', 'Project')}

## Project Overview
{task.get('description', 'No description provided')}

## Estimated Timeline
Based on task analysis: {response[:300]}...

## Phases
1. **Planning Phase** (Week 1)
   - Requirements gathering
   - Architecture design
   - Task breakdown

2. **Development Phase** (Weeks 2-4)
   - Backend development
   - Frontend development
   - Integration

3. **Testing Phase** (Week 5)
   - Unit testing
   - Integration testing
   - E2E testing

4. **Deployment Phase** (Week 6)
   - Production deployment
   - Monitoring setup
   - Documentation

## Generated by OrchestratorAgent
"""