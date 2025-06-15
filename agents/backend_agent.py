"""
Backend Agent - Handles backend development tasks
"""

from agents.base_agent import BaseAgent
from typing import Dict
from pathlib import Path
from core.file_coordinator import safe_write_file

class BackendAgent(BaseAgent):
    async def agent_initialize(self):
        """Initialize backend-specific capabilities"""
        self.frameworks = ["FastAPI", "Django", "Flask", "Express.js", "Spring Boot"]
        self.databases = ["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite"]
        self.patterns = ["REST", "GraphQL", "Microservices", "Event-Driven", "CQRS"]
    
    async def process_task(self, task: Dict, context: Dict) -> Dict:
        """Process backend development tasks"""
        task_type = self.determine_task_type(task)
        
        if task_type == "api_development":
            return await self.develop_api(task, context)
        elif task_type == "database_design":
            return await self.design_database(task, context)
        elif task_type == "performance_optimization":
            return await self.optimize_performance(task, context)
        elif task_type == "security_implementation":
            return await self.implement_security(task, context)
        else:
            return await self.general_backend_task(task, context)
    
    async def develop_api(self, task: Dict, context: Dict) -> Dict:
        """Develop API endpoints"""
        prompt = f"""
        As a senior backend developer, create API endpoints for:
        
        Task: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Provide:
        1. API endpoint definitions (REST)
        2. Request/response schemas
        3. Error handling
        4. Authentication requirements
        5. Sample implementation code
        
        Use FastAPI/Python for implementation.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=1200)
        
        # Extract code from response and create actual files
        code = self.extract_code(response)
        api_file = None
        
        if code:
            # Create API file
            api_file = f"api/{task.get('title', 'api').lower().replace(' ', '_')}.py"
            workspace_root = Path(__file__).parent.parent  # Go up to workspace root
            file_path = workspace_root / api_file
            file_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Write the API code to file
            if safe_write_file(str(file_path), code, self.agent_id, priority=2):
                self.logger.info(f"📝 Created API file: {api_file}")
            
        return {
            'type': 'api_development',
            'file_created': api_file,
            'endpoints': self.extract_endpoints(response),
            'schemas': self.extract_schemas(response),
            'code': code,
            'summary': f"API endpoints developed for {task.get('title', 'project')}"
        }
    
    async def design_database(self, task: Dict, context: Dict) -> Dict:
        """Design database schema"""
        prompt = f"""
        As a database architect, design a database schema for:
        
        Task: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Provide:
        1. Table definitions with relationships
        2. Indexes for performance
        3. Constraints and validations
        4. Migration scripts
        5. Sample queries
        
        Use PostgreSQL syntax.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=1000)
        
        # Create database schema file
        sql_file = None
        if response:
            sql_file = f"database/{task.get('title', 'schema').lower().replace(' ', '_')}.sql"
            workspace_root = Path(__file__).parent.parent
            file_path = workspace_root / sql_file
            file_path.parent.mkdir(exist_ok=True, parents=True)
            
            # Write the SQL schema to file
            if safe_write_file(str(file_path), response, self.agent_id, priority=2):
                self.logger.info(f"📝 Created database schema: {sql_file}")
        
        return {
            'type': 'database_design',
            'file_created': sql_file,
            'schema': response,
            'tables': self.extract_tables(response),
            'relationships': self.extract_relationships(response),
            'summary': f"Database schema designed for {task.get('title', 'project')}"
        }
    
    async def optimize_performance(self, task: Dict, context: Dict) -> Dict:
        """Optimize backend performance"""
        prompt = f"""
        As a performance engineer, optimize the following:
        
        Task: {task.get('title', '')}
        Issue: {task.get('description', '')}
        
        Analyze and provide:
        1. Performance bottlenecks identification
        2. Optimization strategies
        3. Caching recommendations
        4. Database query optimization
        5. Code improvements
        
        Focus on practical, measurable improvements.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'performance_optimization',
            'analysis': response,
            'optimizations': self.extract_optimizations(response),
            'metrics': self.extract_metrics(response),
            'summary': f"Performance optimization plan for {task.get('title', 'system')}"
        }
    
    async def implement_security(self, task: Dict, context: Dict) -> Dict:
        """Implement security measures"""
        prompt = f"""
        As a security engineer, implement security for:
        
        Task: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Provide:
        1. Authentication implementation
        2. Authorization strategies
        3. Input validation
        4. Security headers
        5. Vulnerability prevention
        
        Use industry best practices.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'security_implementation',
            'security_plan': response,
            'measures': self.extract_security_measures(response),
            'vulnerabilities': self.extract_vulnerabilities(response),
            'summary': f"Security implementation for {task.get('title', 'system')}"
        }
    
    async def general_backend_task(self, task: Dict, context: Dict) -> Dict:
        """Handle general backend tasks"""
        prompt = f"""
        As a senior backend developer, help with:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Context from previous work:
        {self.format_context(context)}
        
        Provide detailed technical guidance and implementation suggestions.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=600)
        
        return {
            'type': 'general_backend',
            'guidance': response,
            'summary': f"Backend guidance provided for {task.get('title', 'task')}"
        }
    
    def determine_task_type(self, task: Dict) -> str:
        """Determine the type of backend task"""
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        
        if any(word in description + title for word in ['api', 'endpoint', 'rest', 'graphql']):
            return "api_development"
        elif any(word in description + title for word in ['database', 'schema', 'table', 'sql']):
            return "database_design"
        elif any(word in description + title for word in ['performance', 'optimize', 'slow', 'speed']):
            return "performance_optimization"
        elif any(word in description + title for word in ['security', 'auth', 'login', 'permission']):
            return "security_implementation"
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
    
    def extract_endpoints(self, response: str) -> list:
        """Extract API endpoints from response"""
        endpoints = []
        lines = response.split('\n')
        
        for line in lines:
            if any(method in line.upper() for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']):
                endpoints.append(line.strip())
        
        return endpoints[:10]
    
    def extract_schemas(self, response: str) -> list:
        """Extract data schemas from response"""
        schemas = []
        lines = response.split('\n')
        
        for line in lines:
            if 'schema' in line.lower() or 'model' in line.lower():
                schemas.append(line.strip())
        
        return schemas[:5]
    
    def extract_code(self, response: str) -> str:
        """Extract code snippets from response"""
        # Look for code blocks
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
        
        return '\n\n'.join(code_blocks[:3])  # Return first 3 code blocks
    
    def extract_tables(self, response: str) -> list:
        """Extract database tables from response"""
        tables = []
        lines = response.split('\n')
        
        for line in lines:
            if 'CREATE TABLE' in line.upper() or 'table' in line.lower():
                tables.append(line.strip())
        
        return tables[:10]
    
    def extract_relationships(self, response: str) -> list:
        """Extract database relationships from response"""
        relationships = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['foreign key', 'references', 'relationship']):
                relationships.append(line.strip())
        
        return relationships[:5]
    
    def extract_optimizations(self, response: str) -> list:
        """Extract optimization suggestions from response"""
        optimizations = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['optimize', 'improve', 'cache', 'index']):
                optimizations.append(line.strip())
        
        return optimizations[:5]
    
    def extract_metrics(self, response: str) -> list:
        """Extract performance metrics from response"""
        metrics = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['metric', 'measure', 'benchmark', 'time']):
                metrics.append(line.strip())
        
        return metrics[:3]
    
    def extract_security_measures(self, response: str) -> list:
        """Extract security measures from response"""
        measures = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['auth', 'encrypt', 'validate', 'secure']):
                measures.append(line.strip())
        
        return measures[:5]
    
    def extract_vulnerabilities(self, response: str) -> list:
        """Extract vulnerability information from response"""
        vulnerabilities = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['vulnerability', 'attack', 'exploit', 'risk']):
                vulnerabilities.append(line.strip())
        
        return vulnerabilities[:3]
    
    async def agent_health_check(self):
        """Backend-specific health check"""
        # Test backend knowledge
        test_prompt = "What is a REST API?"
        response = await self.generate_llm_response(test_prompt, max_tokens=50)
        
        if not response or len(response) < 10:
            raise Exception("Backend agent knowledge test failed")
    
    async def agent_cleanup(self):
        """Backend-specific cleanup"""
        # Clear any cached data or temporary files
        pass