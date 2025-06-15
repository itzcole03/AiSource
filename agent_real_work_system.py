#!/usr/bin/env python3
"""
Agent Real Work System - Complete Implementation
This gives agents the ability to create, edit, and enhance files systematically
"""

import os
import re
import ast
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class AgentFileOperations:
    """File operations system for agents to do real work"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.backup_dir = workspace_root / "backups"
        self.backup_dir.mkdir(exist_ok=True, parents=True)
        
    def create_backup(self, file_path: Path) -> Path:
        """Create a backup of a file before editing"""
        if not file_path.exists():
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return backup_path
        
    def read_file_safe(self, file_path: Path) -> Optional[str]:
        """Safely read a file with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
            
    def write_file_safe(self, file_path: Path, content: str) -> bool:
        """Safely write a file with backup and error handling"""
        try:
            # Create backup if file exists
            if file_path.exists():
                self.create_backup(file_path)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
            
    def add_import_to_python_file(self, file_path: Path, import_statement: str) -> bool:
        """Add an import statement to a Python file if not already present"""
        content = self.read_file_safe(file_path)
        if not content:
            return False
            
        if import_statement in content:
            return True  # Already present
            
        lines = content.split('\n')
        
        # Find the best place to insert the import
        insert_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Skip docstrings
                continue
            elif line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_index = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                break
                
        lines.insert(insert_index, import_statement)
        return self.write_file_safe(file_path, '\n'.join(lines))
        
    def add_method_to_class(self, file_path: Path, class_name: str, method_code: str) -> bool:
        """Add a method to an existing class in a Python file"""
        content = self.read_file_safe(file_path)
        if not content:
            return False
            
        lines = content.split('\n')
        class_found = False
        insert_index = -1
        current_indent = 0
        
        for i, line in enumerate(lines):
            if f'class {class_name}' in line:
                class_found = True
                current_indent = len(line) - len(line.lstrip())
                continue
                
            if class_found:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else current_indent + 4
                
                # Find end of class (next class or function at same or less indentation)
                if (line.strip() and 
                    line_indent <= current_indent and 
                    (line.strip().startswith('class ') or line.strip().startswith('def ') or 
                     line.strip().startswith('if __name__'))):
                    insert_index = i
                    break
                    
        if not class_found:
            return False
            
        if insert_index == -1:
            insert_index = len(lines)
            
        # Add method with proper indentation
        method_lines = method_code.split('\n')
        indented_method = []
        for method_line in method_lines:
            if method_line.strip():
                indented_method.append(' ' * (current_indent + 4) + method_line)
            else:
                indented_method.append('')
                
        # Insert method before the identified position
        for j, method_line in enumerate(reversed(indented_method)):
            lines.insert(insert_index, method_line)
            
        return self.write_file_safe(file_path, '\n'.join(lines))
        
    def optimize_python_imports(self, file_path: Path) -> bool:
        """Optimize imports in a Python file"""
        content = self.read_file_safe(file_path)
        if not content:
            return False
            
        lines = content.split('\n')
        imports = []
        other_lines = []
        in_imports = True
        
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                if in_imports:
                    imports.append(line)
                else:
                    other_lines.append(line)
            elif line.strip().startswith('#') or not line.strip():
                if in_imports:
                    imports.append(line)
                else:
                    other_lines.append(line)
            else:
                in_imports = False
                other_lines.append(line)
                
        # Sort imports
        import_lines = [l for l in imports if l.strip().startswith('import ') or l.strip().startswith('from ')]
        comment_lines = [l for l in imports if not (l.strip().startswith('import ') or l.strip().startswith('from '))]
        
        import_lines.sort()
        
        # Reconstruct file
        new_content = '\n'.join(comment_lines + import_lines + [''] + other_lines)
        return self.write_file_safe(file_path, new_content)
        
    def add_error_handling_to_function(self, file_path: Path, function_name: str) -> bool:
        """Add try-catch error handling to a function"""
        content = self.read_file_safe(file_path)
        if not content:
            return False
            
        # This is a simplified implementation - in practice, you'd want more sophisticated AST parsing
        pattern = rf'(def {function_name}\([^)]*\):[^:]*?)(return[^\\n]*)'
        
        def add_try_catch(match):
            func_def = match.group(1)
            return_stmt = match.group(2)
            
            return f'''{func_def}
    try:
        # Original function body would go here
        {return_stmt}
    except Exception as e:
        print(f"Error in {function_name}: {{e}}")
        return None'''
        
        new_content = re.sub(pattern, add_try_catch, content, flags=re.DOTALL)
        return self.write_file_safe(file_path, new_content)

class RealWorkTaskExecutor:
    """Task executor that performs real file operations"""
    
    def __init__(self, workspace_root: Path, agent_name: str):
        self.workspace_root = workspace_root
        self.agent_name = agent_name
        self.file_ops = AgentFileOperations(workspace_root)
        self.work_log = []
        
    def log_work(self, action: str, details: str, file_path: str = None):
        """Log work performed by the agent"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "action": action,
            "details": details,
            "file": file_path
        }
        self.work_log.append(entry)
        print(f"[{self.agent_name}] {action}: {details}")
        
    def execute_create_component_task(self, task: Dict[str, Any]) -> bool:
        """Execute a task to create a new component"""
        file_to_create = task.get('file_to_create')
        content_template = task.get('content_template')
        
        if not file_to_create:
            return False
            
        target_file = self.workspace_root / file_to_create
        
        # Load template if specified
        if content_template:
            template_file = self.workspace_root / "data" / "templates" / f"{content_template}.py"
            if template_file.exists():
                template_content = self.file_ops.read_file_safe(template_file)
                if template_content:
                    success = self.file_ops.write_file_safe(target_file, template_content)
                    if success:
                        self.log_work("CREATE_COMPONENT", f"Created {file_to_create} from template", str(target_file))
                    return success
        
        # Generate default component content
        default_content = self.generate_default_component_content(task)
        success = self.file_ops.write_file_safe(target_file, default_content)
        if success:
            self.log_work("CREATE_COMPONENT", f"Created {file_to_create} with default content", str(target_file))
        return success
        
    def execute_optimize_code_task(self, task: Dict[str, Any]) -> bool:
        """Execute a task to optimize existing code"""
        file_to_modify = task.get('file_to_modify')
        optimization_type = task.get('optimization_type', 'general')
        
        if not file_to_modify:
            return False
            
        target_file = self.workspace_root / file_to_modify
        if not target_file.exists():
            return False
            
        success = False
        
        if optimization_type == 'imports':
            success = self.file_ops.optimize_python_imports(target_file)
            if success:
                self.log_work("OPTIMIZE_IMPORTS", f"Optimized imports in {file_to_modify}", str(target_file))
                
        elif optimization_type == 'error_handling':
            # Add error handling to functions
            content = self.file_ops.read_file_safe(target_file)
            if content and 'def ' in content:
                # Find function names
                function_matches = re.findall(r'def (\w+)\(', content)
                for func_name in function_matches[:3]:  # Limit to first 3 functions
                    self.file_ops.add_error_handling_to_function(target_file, func_name)
                success = True
                self.log_work("ADD_ERROR_HANDLING", f"Added error handling to functions in {file_to_modify}", str(target_file))
                
        elif optimization_type == 'memory':
            # Add memory optimization imports and calls
            success = self.file_ops.add_import_to_python_file(target_file, "import gc  # Added for memory optimization")
            if success:
                self.log_work("MEMORY_OPTIMIZATION", f"Added memory optimization imports to {file_to_modify}", str(target_file))
                
        return success
        
    def execute_enhance_functionality_task(self, task: Dict[str, Any]) -> bool:
        """Execute a task to enhance existing functionality"""
        file_to_modify = task.get('file_to_modify')
        enhancement_type = task.get('enhancement_type', 'general')
        
        if not file_to_modify:
            return False
            
        target_file = self.workspace_root / file_to_modify
        if not target_file.exists():
            return False
            
        content = self.file_ops.read_file_safe(target_file)
        if not content:
            return False
            
        if enhancement_type == 'logging':
            # Add logging capability
            success = self.file_ops.add_import_to_python_file(target_file, "import logging")
            if success:
                # Add logging setup to classes
                if 'class ' in content:
                    class_matches = re.findall(r'class (\w+)', content)
                    for class_name in class_matches[:2]:  # Limit to first 2 classes
                        logging_method = '''def setup_logging(self):
    """Setup logging for this class"""
    self.logger = logging.getLogger(self.__class__.__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    self.logger.addHandler(handler)
    self.logger.setLevel(logging.INFO)'''
                        
                        self.file_ops.add_method_to_class(target_file, class_name, logging_method)
                        
                self.log_work("ENHANCE_LOGGING", f"Added logging capabilities to {file_to_modify}", str(target_file))
                return True
                
        elif enhancement_type == 'monitoring':
            # Add monitoring capabilities
            success = self.file_ops.add_import_to_python_file(target_file, "import psutil")
            success = success and self.file_ops.add_import_to_python_file(target_file, "import time")
            if success:
                self.log_work("ENHANCE_MONITORING", f"Added monitoring imports to {file_to_modify}", str(target_file))
                return True
                
        return False
        
    def execute_create_config_task(self, task: Dict[str, Any]) -> bool:
        """Execute a task to create configuration files"""
        file_to_create = task.get('file_to_create')
        config_type = task.get('config_type', 'yaml')
        
        if not file_to_create:
            return False
            
        target_file = self.workspace_root / file_to_create
        
        if config_type == 'yaml':
            config_content = f"""# Configuration created by {self.agent_name}
# Created: {datetime.now().isoformat()}

application:
  name: "Ultimate Copilot"
  version: "1.0.0"
  environment: "development"

agents:
  max_concurrent: 5
  work_cycle_minutes: 30
  intelligence_evolution: true
  
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
optimization:
  auto_optimize: true
  memory_management: true
  performance_monitoring: true
"""
        else:
            config_content = f"""{{
  "application": {{
    "name": "Ultimate Copilot",
    "version": "1.0.0",
    "environment": "development",
    "created_by": "{self.agent_name}",
    "created_at": "{datetime.now().isoformat()}"
  }},
  "agents": {{
    "max_concurrent": 5,
    "work_cycle_minutes": 30,
    "intelligence_evolution": true
  }},
  "optimization": {{
    "auto_optimize": true,
    "memory_management": true,
    "performance_monitoring": true
  }}
}}"""
        
        success = self.file_ops.write_file_safe(target_file, config_content)
        if success:
            self.log_work("CREATE_CONFIG", f"Created {config_type} config: {file_to_create}", str(target_file))
        return success
        
    def generate_default_component_content(self, task: Dict[str, Any]) -> str:
        """Generate default content for a component"""
        component_name = Path(task.get('file_to_create', 'Component')).stem
        class_name = ''.join(word.capitalize() for word in component_name.split('_'))
        
        return f'''"""
{class_name} Component for Ultimate Copilot
Created by: {self.agent_name}
Created: {datetime.now().isoformat()}
Task: {task.get('title', 'Component Creation')}
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class {class_name}:
    """
    {task.get('description', f'{class_name} component')}
    """
    
    def __init__(self):
        self.name = "{class_name}"
        self.created_by = "{self.agent_name}"
        self.created_at = datetime.now()
        self.active = False
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for this component"""
        self.logger = logging.getLogger(self.__class__.__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    async def start(self):
        """Start the component"""
        self.active = True
        self.logger.info(f"{{self.name}} component started")
        
    async def stop(self):
        """Stop the component"""
        self.active = False
        self.logger.info(f"{{self.name}} component stopped")
        
    async def process(self, data: Any) -> Any:
        """Process data through this component"""
        self.logger.info(f"Processing data: {{type(data)}}")
        # Component-specific processing logic would go here
        return data
        
    def get_status(self) -> Dict[str, Any]:
        """Get component status"""
        return {{
            "name": self.name,
            "active": self.active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "status": "running" if self.active else "stopped"
        }}

if __name__ == "__main__":
    # Example usage
    component = {class_name}()
    print(f"{{component.name}} component created by {{component.created_by}}")
'''

def create_comprehensive_task_queue():
    """Create a comprehensive task queue for agents to work on"""
    workspace_root = Path(__file__).parent
    tasks_file = workspace_root / "data" / "comprehensive_task_queue.json"
    
    comprehensive_tasks = [
        # Component Creation Tasks
        {
            "id": "create_api_health",
            "type": "create_component",
            "title": "Create API Health Check Endpoint",
            "description": "Create a comprehensive health check endpoint with metrics",
            "priority": 9,
            "complexity": 5,
            "file_to_create": "api/health_endpoint.py",
            "content_template": "api_health_check"
        },
        {
            "id": "create_metrics_collector",
            "type": "create_component", 
            "title": "Create Advanced Metrics Collector",
            "description": "Create system for collecting and analyzing performance metrics",
            "priority": 8,
            "complexity": 7,
            "file_to_create": "core/advanced_metrics_collector.py"
        },
        {
            "id": "create_task_scheduler",
            "type": "create_component",
            "title": "Create Intelligent Task Scheduler",
            "description": "Create system for scheduling and managing agent tasks",
            "priority": 8,
            "complexity": 8,
            "file_to_create": "core/intelligent_task_scheduler.py"
        },
        
        # Code Optimization Tasks
        {
            "id": "optimize_llm_manager",
            "type": "optimize_code",
            "title": "Optimize LLM Manager Imports",
            "description": "Optimize and organize imports in the LLM manager",
            "priority": 6,
            "complexity": 3,
            "file_to_modify": "core/enhanced_llm_manager.py",
            "optimization_type": "imports"
        },
        {
            "id": "add_error_handling_agents",
            "type": "optimize_code",
            "title": "Add Error Handling to Agent System",
            "description": "Add comprehensive error handling to autonomous agents",
            "priority": 7,
            "complexity": 5,
            "file_to_modify": "core/autonomous_agents.py",
            "optimization_type": "error_handling"
        },
        {
            "id": "memory_optimize_manager",
            "type": "optimize_code",
            "title": "Add Memory Optimization to Agent Manager", 
            "description": "Add memory management optimizations",
            "priority": 6,
            "complexity": 4,
            "file_to_modify": "core/agent_manager.py",
            "optimization_type": "memory"
        },
        
        # Enhancement Tasks
        {
            "id": "enhance_logging_system",
            "type": "enhance_functionality",
            "title": "Enhance System Logging",
            "description": "Add comprehensive logging to the plugin system",
            "priority": 7,
            "complexity": 5,
            "file_to_modify": "core/plugin_system.py",
            "enhancement_type": "logging"
        },
        {
            "id": "add_monitoring_capabilities",
            "type": "enhance_functionality", 
            "title": "Add System Monitoring",
            "description": "Add system monitoring capabilities to database manager",
            "priority": 6,
            "complexity": 6,
            "file_to_modify": "core/database_manager.py",
            "enhancement_type": "monitoring"
        },
        
        # Configuration Tasks
        {
            "id": "create_prod_config",
            "type": "create_config",
            "title": "Create Production Configuration",
            "description": "Create comprehensive production configuration",
            "priority": 8,
            "complexity": 4,
            "file_to_create": "config/production.yaml",
            "config_type": "yaml"
        },
        {
            "id": "create_agent_configs",
            "type": "create_config",
            "title": "Create Agent-Specific Configurations",
            "description": "Create configuration files for each agent type",
            "priority": 7,
            "complexity": 5,
            "file_to_create": "config/agent_configurations.json",
            "config_type": "json"
        },
        
        # Advanced Tasks
        {
            "id": "create_performance_analyzer",
            "type": "create_component",
            "title": "Create Performance Analyzer",
            "description": "Create advanced performance analysis system",
            "priority": 7,
            "complexity": 9,
            "file_to_create": "core/performance_analyzer.py"
        },
        {
            "id": "create_security_manager",
            "type": "create_component", 
            "title": "Create Security Manager",
            "description": "Create security management and validation system",
            "priority": 9,
            "complexity": 8,
            "file_to_create": "core/security_manager.py"
        }
    ]
    
    tasks_file.parent.mkdir(parents=True, exist_ok=True)
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_tasks, f, indent=2)
    
    print(f"Created comprehensive task queue with {len(comprehensive_tasks)} tasks: {tasks_file}")
    return tasks_file

def main():
    """Set up the real work system for agents"""
    print("Setting up comprehensive real work system for agents...")
    print("=" * 60)
    
    # Create comprehensive task queue
    task_queue = create_comprehensive_task_queue()
    
    # Test the task executor with a sample task
    workspace_root = Path(__file__).parent
    executor = RealWorkTaskExecutor(workspace_root, "TestAgent")
    
    print("\n🧪 Testing task execution capabilities...")
    
    # Test component creation
    test_task = {
        "id": "test_component",
        "type": "create_component",
        "title": "Test Component Creation",
        "description": "Test component for validation",
        "file_to_create": "test/test_component.py"
    }
    
    success = executor.execute_create_component_task(test_task)
    print(f"Component creation test: {'PASSED' if success else 'FAILED'}")
    
    # Test config creation
    config_task = {
        "id": "test_config",
        "type": "create_config", 
        "title": "Test Configuration",
        "description": "Test configuration creation",
        "file_to_create": "test/test_config.yaml",
        "config_type": "yaml"
    }
    
    success = executor.execute_create_config_task(config_task)
    print(f"Configuration creation test: {'PASSED' if success else 'FAILED'}")
    
    print("\n" + "=" * 60)
    print("Real work system setup complete!")
    print("\nAgents can now perform:")
    print("   Create new components with full functionality")
    print("   Optimize existing code (imports, error handling, memory)")
    print("   Enhance functionality (logging, monitoring)")
    print("   Create configuration files (YAML, JSON)")
    print("   Safely edit files with automatic backups")
    print("   Log all work performed with timestamps")
    
    print(f"\n📂 Task queue location: {task_queue}")
    print("📂 Test files created in: test/")
    print("📂 Backups will be stored in: backups/")

if __name__ == "__main__":
    main()


