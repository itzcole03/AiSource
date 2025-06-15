"""
Architect Agent - Handles system design and architecture tasks
"""

from agents.base_agent import BaseAgent
from core.file_coordinator import safe_write_file
from typing import Dict
import datetime

class ArchitectAgent(BaseAgent):
    async def agent_initialize(self):
        """Initialize architect-specific capabilities"""
        self.design_patterns = [
            "MVC", "MVP", "MVVM", "Microservices", "Event-Driven",
            "Layered Architecture", "Clean Architecture", "Hexagonal"
        ]
        
        self.technologies = [
            "React", "Node.js", "Python", "FastAPI", "PostgreSQL",
            "Redis", "Docker", "Kubernetes", "AWS", "Azure"
        ]
    
    async def process_task(self, task: Dict, context: Dict) -> Dict:
        """Process architecture-related tasks"""
        task_type = self.determine_task_type(task)
        
        if task_type == "system_design":
            return await self.design_system(task, context)
        elif task_type == "architecture_review":
            return await self.review_architecture(task, context)
        elif task_type == "technology_selection":
            return await self.select_technologies(task, context)
        else:
            return await self.general_architecture_task(task, context)
    
    async def design_system(self, task: Dict, context: Dict) -> Dict:
        """Design a system architecture"""
        prompt = f"""
        As a senior software architect, design a system architecture for the following requirements:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Consider:
        - Scalability requirements
        - Performance needs
        - Security considerations
        - Maintainability
        - Technology constraints
        
        Provide:
        1. High-level architecture diagram description
        2. Component breakdown
        3. Technology recommendations
        4. Data flow description
        5. Deployment strategy
        
        Format your response as a structured design document.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=1000)
        
        # Create architecture documentation files
        await self.create_architecture_files(task, response)
        
        return {
            'type': 'system_design',
            'architecture': response,
            'components': self.extract_components(response),
            'technologies': self.extract_technologies(response),
            'summary': f"System architecture designed for {task.get('title', 'project')}"
        }
    
    async def review_architecture(self, task: Dict, context: Dict) -> Dict:
        """Review existing architecture"""
        prompt = f"""
        As a senior software architect, review the following architecture:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Previous similar work:
        {self.format_context(context)}
        
        Provide:
        1. Architecture strengths
        2. Potential issues and risks
        3. Improvement recommendations
        4. Scalability assessment
        5. Security considerations
        
        Focus on practical, actionable feedback.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'architecture_review',
            'review': response,
            'recommendations': self.extract_recommendations(response),
            'risk_level': self.assess_risk_level(response),
            'summary': f"Architecture review completed for {task.get('title', 'project')}"
        }
    
    async def select_technologies(self, task: Dict, context: Dict) -> Dict:
        """Select appropriate technologies"""
        prompt = f"""
        As a technology architect, recommend the best technology stack for:
        
        Task: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Consider:
        - Project requirements and constraints
        - Team expertise
        - Scalability needs
        - Maintenance overhead
        - Community support
        - Long-term viability
        
        Recommend:
        1. Frontend technologies
        2. Backend technologies
        3. Database solutions
        4. Infrastructure tools
        5. Development tools
        
        Justify each recommendation.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'technology_selection',
            'recommendations': response,
            'tech_stack': self.extract_tech_stack(response),
            'justification': self.extract_justification(response),
            'summary': f"Technology stack recommended for {task.get('title', 'project')}"
        }
    
    async def general_architecture_task(self, task: Dict, context: Dict) -> Dict:
        """Handle general architecture tasks"""
        prompt = f"""
        As a senior software architect, help with the following:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Context from previous work:
        {self.format_context(context)}
        
        Provide detailed, actionable guidance based on architectural best practices.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=600)
        
        return {
            'type': 'general_architecture',
            'guidance': response,
            'summary': f"Architectural guidance provided for {task.get('title', 'task')}"
        }
    
    def determine_task_type(self, task: Dict) -> str:
        """Determine the type of architecture task"""
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        
        if any(word in description + title for word in ['design', 'architecture', 'system']):
            return "system_design"
        elif any(word in description + title for word in ['review', 'audit', 'assess']):
            return "architecture_review"
        elif any(word in description + title for word in ['technology', 'tech', 'stack', 'tool']):
            return "technology_selection"
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
    
    def extract_components(self, response: str) -> list:
        """Extract system components from response"""
        # Simple extraction - in practice, this would be more sophisticated
        components = []
        lines = response.split('\n')
        
        for line in lines:
            if 'component' in line.lower() or 'service' in line.lower():
                components.append(line.strip())
        
        return components[:10]  # Limit to 10 components
    
    def extract_technologies(self, response: str) -> list:
        """Extract recommended technologies"""
        found_techs = []
        response_lower = response.lower()
        
        for tech in self.technologies:
            if tech.lower() in response_lower:
                found_techs.append(tech)
        
        return found_techs
    
    def extract_recommendations(self, response: str) -> list:
        """Extract recommendations from review"""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['recommend', 'suggest', 'should', 'improve']):
                recommendations.append(line.strip())
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def assess_risk_level(self, response: str) -> str:
        """Assess risk level from review"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['critical', 'severe', 'major']):
            return "high"
        elif any(word in response_lower for word in ['moderate', 'medium', 'concern']):
            return "medium"
        else:
            return "low"
    
    def extract_tech_stack(self, response: str) -> Dict:
        """Extract technology stack recommendations"""
        return {
            'frontend': self.extract_category_techs(response, 'frontend'),
            'backend': self.extract_category_techs(response, 'backend'),
            'database': self.extract_category_techs(response, 'database'),
            'infrastructure': self.extract_category_techs(response, 'infrastructure')
        }
    
    def extract_category_techs(self, response: str, category: str) -> list:
        """Extract technologies for a specific category"""
        found_techs = []
        lines = response.split('\n')
        
        in_category = False
        for line in lines:
            if category.lower() in line.lower():
                in_category = True
                continue
            
            if in_category and line.strip():
                for tech in self.technologies:
                    if tech.lower() in line.lower():
                        found_techs.append(tech)
                
                # Stop at next category or empty line
                if any(cat in line.lower() for cat in ['frontend', 'backend', 'database', 'infrastructure']) and category.lower() not in line.lower():
                    break
        
        return found_techs[:3]  # Limit to 3 per category
    
    def extract_justification(self, response: str) -> str:
        """Extract justification for recommendations"""
        lines = response.split('\n')
        justification_lines = []
        
        for line in lines:
            if any(word in line.lower() for word in ['because', 'since', 'due to', 'reason']):
                justification_lines.append(line.strip())
        
        return '\n'.join(justification_lines[:3])  # Top 3 justifications
    
    async def agent_health_check(self):
        """Architect-specific health check"""
        # Test design pattern knowledge
        test_prompt = "What is the MVC pattern?"
        response = await self.generate_llm_response(test_prompt, max_tokens=50)
        
        if not response or len(response) < 10:
            raise Exception("Architect agent knowledge test failed")
    
    async def agent_cleanup(self):
        """Architect-specific cleanup"""
        # Clear any cached design patterns or temporary data
        pass
    
    async def create_architecture_files(self, task: Dict, response: str):
        """Create architecture documentation files"""
        try:
            task_title = task.get('title', 'project').replace(' ', '_').lower()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create architecture overview document
            architecture_doc = f"""# Architecture Design - {task.get('title', 'Project')}

## Overview
Generated on: {timestamp}
Task: {task.get('title', '')}

## Architecture Description
{response}

## Components
{self.format_components_list(self.extract_components(response))}

## Technology Stack
{self.format_tech_stack_simple(self.extract_technologies(response))}

## Generated by ArchitectAgent
"""
            
            # Write architecture document
            arch_file = f"agent_outputs/ArchitectAgent/architecture_{task_title}_{timestamp}.md"
            if safe_write_file(arch_file, architecture_doc, self.agent_id, priority=2):
                self.logger.info(f"Architecture document created: {arch_file}")
            
            # Create a system diagram file (PlantUML/Mermaid)
            diagram_content = self.generate_diagram_content(response, task)
            diagram_file = f"agent_outputs/ArchitectAgent/diagram_{task_title}_{timestamp}.md"
            if safe_write_file(diagram_file, diagram_content, self.agent_id, priority=2):
                self.logger.info(f"Diagram file created: {diagram_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating architecture files: {e}")
    
    def format_components_list(self, components: list) -> str:
        """Format components into a readable list"""
        if not components:
            return "- No specific components identified"
        return "\n".join([f"- {comp}" for comp in components])
    
    def format_tech_stack_simple(self, tech_list: list) -> str:
        """Format technology list into readable format"""
        if not tech_list:
            return "- No specific technologies identified"
        return "\n".join([f"- {tech}" for tech in tech_list])
    
    def generate_diagram_content(self, response: str, task: Dict) -> str:
        """Generate system diagram content"""
        return f"""# System Diagram - {task.get('title', 'Project')}

## Mermaid Diagram
```mermaid
graph TD
    A[User Interface] --> B[Application Layer]
    B --> C[Business Logic]
    C --> D[Data Layer]
    D --> E[Database]
    
    F[External APIs] --> B
    G[Authentication] --> B
    H[Caching] --> C
```

## Architecture Overview
Based on the analysis: {response[:200]}...

## Component Relationships
- Frontend communicates with Backend API
- Backend processes business logic
- Data layer handles persistence
- External integrations via API gateway

Generated by ArchitectAgent
"""