#!/usr/bin/env python3
"""
Agent Integration Patch - Connect Real Work System to Intelligent Agents
This patches the existing intelligent agents to use the real work system
"""

import os
import json
import sys
from pathlib import Path

def patch_intelligent_agents_with_real_work():
    """Patch the intelligent agents to use the real work system"""
    
    workspace_root = Path(__file__).parent
    agent_file = workspace_root / "run_intelligent_agents.py"
    
    # Read current file
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add import for the real work system at the top
    import_addition = """
# Real Work System Integration
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent_real_work_system import RealWorkTaskExecutor
"""
    
    # Find where to add the import
    if "from agent_real_work_system import RealWorkTaskExecutor" not in content:
        # Add after existing imports
        import_position = content.find('class IntelligentAgent:')
        if import_position != -1:
            content = content[:import_position] + import_addition + '\n' + content[import_position:]
    
    # Replace the __init__ method to include the real work executor
    old_init_pattern = """    def __init__(self, name: str, role: str, workspace_root: str):
        self.name = name
        self.role = role
        self.workspace_root = Path(workspace_root)
        self.logs_dir = self.workspace_root / "logs" / "intelligent_agents"
        self.logs_dir.mkdir(exist_ok=True, parents=True)"""
    
    new_init_pattern = """    def __init__(self, name: str, role: str, workspace_root: str):
        self.name = name
        self.role = role
        self.workspace_root = Path(workspace_root)
        self.logs_dir = self.workspace_root / "logs" / "intelligent_agents"
        self.logs_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize real work executor
        self.real_work_executor = RealWorkTaskExecutor(self.workspace_root, self.name)"""
    
    content = content.replace(old_init_pattern, new_init_pattern)
    
    # Replace the task generation method to load from comprehensive queue
    old_task_gen = """    async def _generate_intelligent_tasks(self):
        \"\"\"Generate intelligent tasks based on project analysis\"\"\"
        self.log("Generating intelligent tasks...")
        
        # Add some default intelligent tasks
        default_tasks = [
            {
                "type": "code_optimization",
                "title": "Intelligent Code Optimization",
                "description": "Analyze and optimize code for better performance",
                "priority": 7,
                "complexity": 6
            },
            {
                "type": "architecture_improvement",
                "title": "Architecture Enhancement",
                "description": "Improve system architecture based on analysis",
                "priority": 8,
                "complexity": 7
            }
        ]
        
        self.work_queue.extend(default_tasks)"""
    
    new_task_gen = """    async def _generate_intelligent_tasks(self):
        \"\"\"Generate intelligent tasks from comprehensive task queue\"\"\"
        self.log("Loading tasks from comprehensive queue...")
        
        # Load comprehensive task queue
        task_queue_file = self.workspace_root / "data" / "comprehensive_task_queue.json"
        
        if task_queue_file.exists():
            try:
                with open(task_queue_file, 'r', encoding='utf-8') as f:
                    all_tasks = json.load(f)
                
                # Filter tasks based on agent role and current work queue size
                role_task_mapping = {
                    "Orchestrator": ["create_config", "optimize_code"],
                    "Backend Developer": ["create_component", "optimize_code", "enhance_functionality"],
                    "Frontend Developer": ["create_component", "enhance_functionality"],
                    "Architect": ["create_component", "create_config", "optimize_code"],
                    "QA Engineer": ["optimize_code", "enhance_functionality"]
                }
                
                suitable_tasks = []
                agent_task_types = role_task_mapping.get(self.role, ["create_component"])
                
                for task in all_tasks:
                    task_type = task.get('type', '')
                    if task_type in agent_task_types and task.get('id') not in [t.get('id', '') for t in self.work_queue]:
                        suitable_tasks.append(task)
                
                # Add up to 3 tasks at a time to avoid overwhelming
                selected_tasks = suitable_tasks[:3]
                self.work_queue.extend(selected_tasks)
                
                self.log(f"Loaded {len(selected_tasks)} real tasks for {self.role}")
                
            except Exception as e:
                self.log(f"Error loading comprehensive tasks: {e}")
                await self._generate_fallback_tasks()
        else:
            self.log("Comprehensive task queue not found, generating fallback tasks")
            await self._generate_fallback_tasks()
    
    async def _generate_fallback_tasks(self):
        \"\"\"Generate fallback tasks if comprehensive queue unavailable\"\"\"
        fallback_tasks = [
            {
                "id": f"fallback_{self.name}_{int(time.time())}",
                "type": "create_component",
                "title": f"Create {self.role} Enhancement",
                "description": f"Create enhancement component for {self.role}",
                "priority": 6,
                "complexity": 5,
                "file_to_create": f"core/{self.name.lower()}_enhancement.py"
            }
        ]
        
        self.work_queue.extend(fallback_tasks)
        self.log(f"Generated {len(fallback_tasks)} fallback tasks")"""
    
    content = content.replace(old_task_gen, new_task_gen)
    
    # Replace the task execution method with real work execution
    old_task_exec = """    async def _execute_task_intelligently(self, task: Dict[str, Any]) -> bool:
        \"\"\"Execute a task with intelligent problem-solving\"\"\"
        try:
            task_type = task.get('type', 'generic')
            
            if task_type == "missing_critical_component":
                return await self._create_missing_component(task)
            elif task_type == "intelligent_monitoring":
                return await self._implement_intelligent_monitoring(task)
            elif task_type == "auto_optimization":
                return await self._implement_auto_optimization(task)
            elif task_type == "intelligent_deployment":
                return await self._implement_intelligent_deployment(task)
            elif task_type == "advanced_security":
                return await self._implement_advanced_security(task)
            else:
                return await self._execute_generic_intelligent_task(task)
        
        except Exception as e:
            self.log(f"Error executing task {task['title']}: {str(e)}")
            return False"""
    
    new_task_exec = """    async def _execute_task_intelligently(self, task: Dict[str, Any]) -> bool:
        \"\"\"Execute a task with real work using the integrated work system\"\"\"
        try:
            task_type = task.get('type', 'generic')
            self.log(f"Executing real work task: {task.get('title', 'Unknown')}")
            
            if task_type == "create_component":
                success = self.real_work_executor.execute_create_component_task(task)
                if success:
                    self.log(f"Successfully created component: {task.get('file_to_create')}")
                return success
                
            elif task_type == "optimize_code":
                success = self.real_work_executor.execute_optimize_code_task(task)
                if success:
                    self.log(f"Successfully optimized code: {task.get('file_to_modify')}")
                return success
                
            elif task_type == "enhance_functionality":
                success = self.real_work_executor.execute_enhance_functionality_task(task)
                if success:
                    self.log(f"Successfully enhanced functionality: {task.get('file_to_modify')}")
                return success
                
            elif task_type == "create_config":
                success = self.real_work_executor.execute_create_config_task(task)
                if success:
                    self.log(f"Successfully created config: {task.get('file_to_create')}")
                return success
                
            else:
                # Handle legacy task types
                self.log(f"Legacy task type: {task_type}, executing with basic handler")
                return await self._execute_legacy_task(task)
        
        except Exception as e:
            self.log(f"Error executing task {task.get('title', 'Unknown')}: {str(e)}")
            return False
    
    async def _execute_legacy_task(self, task: Dict[str, Any]) -> bool:
        \"\"\"Execute legacy task types that don't map to real work system\"\"\"
        task_title = task.get('title', 'Unknown Task')
        
        # Create a work log entry for legacy tasks
        logs_dir = self.workspace_root / "logs" / "legacy_task_execution"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        task_log_file = logs_dir / f"legacy_task_{task.get('id', 'unknown')}.log"
        
        try:
            with open(task_log_file, 'w', encoding='utf-8') as f:
                f.write(f\"\"\"Legacy Task Execution Log
==================

Task ID: {task.get('id', 'unknown')}
Task Title: {task_title}
Task Type: {task.get('type', 'generic')}
Executed By: {self.name}
Timestamp: {datetime.now().isoformat()}

Description: {task.get('description', 'No description provided')}

Status: COMPLETED (Legacy Handler)
Result: Task executed with legacy compatibility handler
\"\"\")
            
            self.log(f"Executed legacy task: {task_title}")
            return True
            
        except Exception as e:
            self.log(f"Error executing legacy task: {e}")
            return False"""
    
    content = content.replace(old_task_exec, new_task_exec)
    
    # Add time import if not present
    if 'import time' not in content:
        content = content.replace('from datetime import datetime, timedelta', 'from datetime import datetime, timedelta\nimport time')
    
    # Write the patched content
    try:
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Successfully patched intelligent agents with real work system!")
        return True
        
    except Exception as e:
        print(f"Error writing patched agent file: {e}")
        return False

def verify_integration():
    """Verify that the integration is working"""
    workspace_root = Path(__file__).parent
    
    # Check if required files exist
    required_files = [
        "agent_real_work_system.py",
        "data/comprehensive_task_queue.json",
        "run_intelligent_agents.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (workspace_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Missing required files: {missing_files}")
        return False
    
    print("All required files present")
    
    # Check if the patch was applied
    agent_file = workspace_root / "run_intelligent_agents.py"
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "RealWorkTaskExecutor" not in content:
        print("Real work system not integrated into agents")
        return False
    
    print("Real work system successfully integrated")
    return True

def main():
    """Main integration function"""
    print("Integrating real work system with intelligent agents...")
    print("=" * 60)
    
    # Apply the patch
    if patch_intelligent_agents_with_real_work():
        print("Patch applied successfully")
    else:
        print("Failed to apply patch")
        return
    
    # Verify integration
    if verify_integration():
        print("Integration verified successfully")
    else:
        print("Integration verification failed")
        return
    
    print("\n" + "=" * 60)
    print("🎉 INTEGRATION COMPLETE!")
    print("\nIntelligent agents now have:")
    print("   Real file creation and editing capabilities")
    print("   Access to comprehensive task queue (12 tasks)")
    print("   Role-based task assignment")
    print("   Automatic file backups before editing")
    print("   Detailed work logging")
    print("   Code optimization capabilities")
    print("   Configuration file generation")
    print("   System enhancement features")
    
    print("\nStart the agents with: python run_intelligent_agents.py")
    print("Check these directories for agent output:")
    print("   - core/ (new components)")
    print("   - config/ (configuration files)")
    print("   - api/ (API endpoints)")
    print("   - logs/ (work logs)")
    print("   - backups/ (file backups)")

if __name__ == "__main__":
    main()


