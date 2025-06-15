"""
Frontend Agent - Handles frontend development tasks
"""

from agents.base_agent import BaseAgent
from typing import Dict
from pathlib import Path
from core.file_coordinator import safe_write_file

class FrontendAgent(BaseAgent):
    async def agent_initialize(self):
        """Initialize frontend-specific capabilities"""
        self.frameworks = ["React", "Vue.js", "Angular", "Svelte", "Next.js"]
        self.styling = ["CSS", "Sass", "Tailwind CSS", "Styled Components", "Material-UI"]
        self.tools = ["Webpack", "Vite", "TypeScript", "ESLint", "Prettier"]
    
    async def process_task(self, task: Dict, context: Dict) -> Dict:
        """Process frontend development tasks"""
        task_type = self.determine_task_type(task)
        
        if task_type == "component_development":
            return await self.develop_component(task, context)
        elif task_type == "ui_design":
            return await self.design_ui(task, context)
        elif task_type == "performance_optimization":
            return await self.optimize_frontend(task, context)
        elif task_type == "accessibility":
            return await self.implement_accessibility(task, context)
        else:
            return await self.general_frontend_task(task, context)
    
    async def develop_component(self, task: Dict, context: Dict) -> Dict:
        """Develop React components"""
        prompt = f"""
        As a senior frontend developer, create React components for:
        
        Task: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Provide:
        1. Component structure and props
        2. TypeScript interfaces
        3. Styling approach
        4. State management
        5. Complete implementation code
        
        Use React with TypeScript and modern hooks.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=1200)
        
        # Create React component file
        component_file = None
        code = self.extract_code(response)
        
        if code:
            component_file = f"frontend/components/{task.get('title', 'Component').replace(' ', '')}.tsx"
            workspace_root = Path(__file__).parent.parent
            file_path = workspace_root / component_file
            file_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Write the component code to file
            if safe_write_file(str(file_path), code, self.agent_id, priority=2):
                self.logger.info(f"📝 Created React component: {component_file}")
        
        return {
            'type': 'component_development',
            'file_created': component_file,
            'components': self.extract_components(response),
            'interfaces': self.extract_interfaces(response),
            'code': code,
            'summary': f"React components developed for {task.get('title', 'project')}"
        }
    
    async def design_ui(self, task: Dict, context: Dict) -> Dict:
        """Design user interface"""
        prompt = f"""
        As a UI/UX designer and frontend developer, design the interface for:
        
        Task: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Provide:
        1. Layout structure and wireframe description
        2. Color scheme and typography
        3. Component hierarchy
        4. User interaction flows
        5. Responsive design considerations
        
        Focus on usability and modern design principles.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=1000)
        
        return {
            'type': 'ui_design',
            'design': response,
            'layout': self.extract_layout(response),
            'styling': self.extract_styling(response),
            'summary': f"UI design created for {task.get('title', 'project')}"
        }
    
    async def optimize_frontend(self, task: Dict, context: Dict) -> Dict:
        """Optimize frontend performance"""
        prompt = f"""
        As a frontend performance engineer, optimize:
        
        Task: {task.get('title', '')}
        Issue: {task.get('description', '')}
        
        Analyze and provide:
        1. Performance bottlenecks
        2. Bundle size optimization
        3. Loading performance improvements
        4. Runtime optimization
        5. Caching strategies
        
        Focus on measurable performance gains.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'performance_optimization',
            'analysis': response,
            'optimizations': self.extract_optimizations(response),
            'metrics': self.extract_metrics(response),
            'summary': f"Frontend performance optimization for {task.get('title', 'application')}"
        }
    
    async def implement_accessibility(self, task: Dict, context: Dict) -> Dict:
        """Implement accessibility features"""
        prompt = f"""
        As an accessibility expert, implement accessibility for:
        
        Task: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Provide:
        1. ARIA labels and roles
        2. Keyboard navigation
        3. Screen reader support
        4. Color contrast compliance
        5. Semantic HTML structure
        
        Follow WCAG 2.1 AA guidelines.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'accessibility',
            'accessibility_plan': response,
            'features': self.extract_accessibility_features(response),
            'compliance': self.extract_compliance(response),
            'summary': f"Accessibility implementation for {task.get('title', 'interface')}"
        }
    
    async def general_frontend_task(self, task: Dict, context: Dict) -> Dict:
        """Handle general frontend tasks"""
        prompt = f"""
        As a senior frontend developer, help with:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Context from previous work:
        {self.format_context(context)}
        
        Provide detailed technical guidance and implementation suggestions.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=600)
        
        return {
            'type': 'general_frontend',
            'guidance': response,
            'summary': f"Frontend guidance provided for {task.get('title', 'task')}"
        }
    
    def determine_task_type(self, task: Dict) -> str:
        """Determine the type of frontend task"""
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        
        if any(word in description + title for word in ['component', 'react', 'vue', 'angular']):
            return "component_development"
        elif any(word in description + title for word in ['ui', 'design', 'interface', 'layout']):
            return "ui_design"
        elif any(word in description + title for word in ['performance', 'optimize', 'slow', 'bundle']):
            return "performance_optimization"
        elif any(word in description + title for word in ['accessibility', 'a11y', 'wcag', 'screen reader']):
            return "accessibility"
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
        """Extract component names from response"""
        components = []
        lines = response.split('\n')
        
        for line in lines:
            if 'component' in line.lower() or 'function' in line.lower():
                components.append(line.strip())
        
        return components[:10]
    
    def extract_interfaces(self, response: str) -> list:
        """Extract TypeScript interfaces from response"""
        interfaces = []
        lines = response.split('\n')
        
        for line in lines:
            if 'interface' in line or 'type' in line:
                interfaces.append(line.strip())
        
        return interfaces[:5]
    
    def extract_code(self, response: str) -> str:
        """Extract code snippets from response"""
        code_blocks = []
        in_code_block = False
        current_block = []
        
        for line in response.split('\n'):
            if '```' in line:
                if in_code_block:
                    code_blocks.append('\n'.join(current_block))
                    current_block = []
                in_code_block = not in_code_block
            elif in_code_block:
                current_block.append(line)
        
        return '\n\n'.join(code_blocks[:3])
    
    def extract_layout(self, response: str) -> list:
        """Extract layout information from response"""
        layout = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['layout', 'grid', 'flex', 'container']):
                layout.append(line.strip())
        
        return layout[:5]
    
    def extract_styling(self, response: str) -> list:
        """Extract styling information from response"""
        styling = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['color', 'font', 'style', 'css', 'theme']):
                styling.append(line.strip())
        
        return styling[:5]
    
    def extract_optimizations(self, response: str) -> list:
        """Extract optimization suggestions from response"""
        optimizations = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['optimize', 'improve', 'reduce', 'lazy']):
                optimizations.append(line.strip())
        
        return optimizations[:5]
    
    def extract_metrics(self, response: str) -> list:
        """Extract performance metrics from response"""
        metrics = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['metric', 'measure', 'score', 'time']):
                metrics.append(line.strip())
        
        return metrics[:3]
    
    def extract_accessibility_features(self, response: str) -> list:
        """Extract accessibility features from response"""
        features = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['aria', 'role', 'label', 'alt', 'tabindex']):
                features.append(line.strip())
        
        return features[:5]
    
    def extract_compliance(self, response: str) -> list:
        """Extract compliance information from response"""
        compliance = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['wcag', 'compliance', 'guideline', 'standard']):
                compliance.append(line.strip())
        
        return compliance[:3]
    
    async def agent_health_check(self):
        """Frontend-specific health check"""
        # Test frontend knowledge
        test_prompt = "What is a React component?"
        response = await self.generate_llm_response(test_prompt, max_tokens=50)
        
        if not response or len(response) < 10:
            raise Exception("Frontend agent knowledge test failed")
    
    async def agent_cleanup(self):
        """Frontend-specific cleanup"""
        # Clear any cached data or temporary files
        pass