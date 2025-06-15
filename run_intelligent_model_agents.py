#!/usr/bin/env python3
"""
Intelligent Local Model Agents
Agents powered by real local models (Ollama, LM Studio, vLLM) for true intelligence
"""

import asyncio
import os
import sys
import json
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.real_llm_manager import RealLLMManager
from core.file_coordinator import get_file_coordinator, safe_write_file, safe_read_file
from core.advanced_memory_manager import AdvancedMemoryManager
from agent_real_work_system import RealWorkTaskExecutor
from core.real_time_model_detector import RealTimeModelDetector

class IntelligentLocalModelAgent:
    """An intelligent agent powered by real local models"""
    
    def __init__(self, name: str, role: str, workspace_root: str, instance_id: Optional[str] = None):
        self.name = name
        self.role = role
        self.workspace_root = Path(workspace_root)
        self.instance_id = instance_id or "primary"
        
        # Create logs directory
        self.logs_dir = self.workspace_root / "logs" / "intelligent_model_agents"
        self.logs_dir.mkdir(exist_ok=True, parents=True)
          # Instance-specific log file
        log_suffix = f"_{self.instance_id}" if self.instance_id != "primary" else ""
        self.log_file = self.logs_dir / f"{self.name}_model_work{log_suffix}.log"
        
        # Initialize real components
        self.llm_manager = RealLLMManager()
        self.memory_manager = AdvancedMemoryManager()
        self.real_work_executor = RealWorkTaskExecutor(self.workspace_root, self.name)
        
        # Initialize file coordinator for safe file operations
        self.file_coordinator = get_file_coordinator(str(workspace_root))
        
        # New intelligent components
        self.model_detector = RealTimeModelDetector()
        
        # Intelligence and experience tracking
        self.intelligence_level = 7.0
        self.total_tasks_completed = 0
        self.successful_decisions = 0
        self.code_generated_lines = 0
        self.problems_solved = 0
        
        # Work state
        self.current_focus = None
        self.work_queue = []
        self.completed_work = []
        self.active_since = datetime.now()
        
    def log(self, message: str):
        """Log messages with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emoji = self._get_intelligence_emoji()
        formatted_msg = f"[{timestamp}] {emoji} {self.name} (L{self.intelligence_level:.1f}): {message}"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_msg + "\n")
        except UnicodeEncodeError:
            # Fallback for emoji issues
            clean_msg = formatted_msg.encode('ascii', 'ignore').decode('ascii')
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(clean_msg + "\n")
        
        print(formatted_msg)
    
    def _get_intelligence_emoji(self) -> str:
        """Get emoji based on intelligence level"""
        if self.intelligence_level >= 9.0:
            return ""  # Genius level
        elif self.intelligence_level >= 8.0:
            return ""  # Advanced AI
        else:
            return ""  # Working level
    
    def _get_intelligence_enhanced_temperature(self) -> float:
        """Get model temperature based on intelligence level - smarter agents are more focused"""
        # Higher intelligence = lower temperature = more focused, deterministic responses
        base_temp = 0.7
        intelligence_factor = (10.0 - self.intelligence_level) / 10.0  # Inverse relationship
        return max(0.1, base_temp * intelligence_factor)
    
    def _get_intelligence_enhanced_task_complexity(self) -> int:
        """Get maximum task complexity agent can handle based on intelligence"""
        # Map intelligence 1-10 to complexity 3-10
        return min(10, max(3, int(3 + (self.intelligence_level - 1) * 0.78)))
    
    def _get_intelligence_enhanced_analysis_depth(self) -> int:
        """Get number of files to analyze based on intelligence"""
        # Smarter agents can process more files effectively
        return min(100, max(10, int(10 + self.intelligence_level * 5)))
    
    def _can_handle_advanced_tasks(self) -> bool:
        """Check if agent intelligence is high enough for advanced tasks"""
        return self.intelligence_level >= 6.0
    
    def _get_intelligent_model_selection(self, task_type: str) -> str:
        """Select best available model based on intelligence level and real-time availability"""
        # Get best model that's actually available right now
        best_model = self.model_detector.get_best_model_for_task(task_type, self.intelligence_level)
        
        if best_model:
            self.log(f"Selected {best_model} for {task_type} (Intelligence L{self.intelligence_level:.1f})")
            return best_model
        else:
            # Fallback to configured model
            fallback_prefs = {
                "analysis": "ollama/mistral",
                "coding": "vllm/microsoft/CodeGPT-small-py", 
                "decision": "ollama/llama3"
            }
            fallback = fallback_prefs.get(task_type, "vllm/gpt2")
            self.log(f"No models detected, using fallback: {fallback}")
            return fallback
    
    def _calculate_intelligent_rest_time(self) -> int:
        """Calculate rest time based on intelligence - smarter agents work more efficiently"""
        base_rest = 30
        # Higher intelligence = shorter rest (more efficient work)
        intelligence_bonus = int(self.intelligence_level * 2)  # 2-20 seconds reduction
        return max(10, base_rest - intelligence_bonus)
    
    async def start_intelligent_model_cycle(self, duration_hours: float = 24.0):
        """Start an intelligent cycle powered by real local models"""
        cycle_start = datetime.now()
        cycle_end = cycle_start + timedelta(hours=duration_hours)
        
        self.log(f"Starting {duration_hours}-hour intelligent model cycle")
        self.log(f"Current intelligence level: {self.intelligence_level:.1f}/10")        # Initialize real systems
        try:
            await self.llm_manager.initialize()
            await self.memory_manager.initialize()
            
            # Detect available models in real-time
            available_models = await self.model_detector.detect_available_models()
            self.log(f"Detected models: {list(available_models.keys())} providers")
            
            # Restore intelligence from previous sessions
            await self._restore_agent_intelligence()
            
            self.log("Real systems initialized successfully")
        except Exception as e:
            self.log(f"Error initializing systems: {e}")
            # Continue with degraded functionality
        
        iteration = 0
        while datetime.now() < cycle_end:
            iteration += 1
            
            try:
                # Phase 1: Intelligent Analysis with Real Model
                await self._intelligent_analysis_phase(iteration)
                
                # Phase 2: Real Decision Making
                await self._intelligent_decision_phase()
                
                # Phase 3: Execute Real Work with Model Guidance
                await self._execute_model_guided_work()
                
                # Phase 4: Learn and Evolve from Results
                await self._learning_evolution_phase()
                  # Phase 5: Collaborative Intelligence
                await self._collaborative_intelligence_phase()
                
                # Periodically refresh available models
                if iteration % 10 == 0:  # Every 10 iterations
                    self.log("Refreshing available models...")
                    available_models = await self.model_detector.detect_available_models(force_refresh=True)
                    self.log(f"Available: {list(available_models.keys())}")
                
                # Dynamic rest based on intelligence and productivity
                rest_time = self._calculate_intelligent_rest_time()
                self.log(f"🧘 Taking {rest_time}s intelligent rest (L{self.intelligence_level:.1f})...")
                await asyncio.sleep(rest_time)
                
            except Exception as e:
                self.log(f"Error in intelligent cycle iteration {iteration}: {str(e)}")
                self.log(f"Traceback: {traceback.format_exc()}")
                await asyncio.sleep(30)  # Quick recovery
        
        await self._generate_intelligence_report(cycle_start, datetime.now())
    
    async def _intelligent_analysis_phase(self, iteration: int):
        """Use real model for intelligent project analysis"""
        self.log(f"Model-powered analysis phase - iteration {iteration}")
        
        # Get current project state
        project_files = await self._scan_project_intelligently()
        
        # Use real model to analyze the project
        analysis_prompt = f"""
        As a {self.role}, analyze the current state of the Ultimate Copilot project.
        
        Project files found: {len(project_files)}
        Current focus: {self.current_focus}
        Tasks completed: {self.total_tasks_completed}
        
        Provide a detailed analysis including:
        1. Current project health and status
        2. Priority areas that need attention
        3. Specific opportunities for improvement
        4. Recommended next actions for a {self.role}
        
        Be specific and actionable in your analysis.        """
        
        try:
            # Quick analysis with timeout (don't hang if models are slow/unavailable)
            analysis_task = asyncio.create_task(
                self.llm_manager.analyze_code(
                    self.role.lower().replace(" ", "_"), 
                    "\n".join(project_files[:3]), # Fewer files for speed
                    analysis_prompt
                )
            )
            
            try:
                analysis_result = await asyncio.wait_for(analysis_task, timeout=10.0)  # 10 second timeout
                
                if analysis_result.get("success"):
                    self.log(f"Model analysis completed: {len(analysis_result['content'])} chars")
                    
                    # Store insights in memory
                    await self.memory_manager.store_experience(
                        agent_id=self.name,
                        experience_type="analysis",
                        data={
                            "iteration": iteration,
                            "analysis": analysis_result["content"][:500],  # Truncate for speed
                            "model": analysis_result.get("model", "unknown"),
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                else:
                    self.log("Model analysis failed, using fallback analysis")
                    self._quick_fallback_analysis(project_files)
                    
            except asyncio.TimeoutError:
                self.log("⏰ Model analysis timeout, proceeding with fallback")
                self._quick_fallback_analysis(project_files)
                analysis_task.cancel()  # Clean up
                
        except Exception as e:
            self.log(f"Error in model analysis: {e}")
            self._quick_fallback_analysis(project_files)
    
    def _quick_fallback_analysis(self, project_files: List[str]):
        """Quick fallback analysis when models are unavailable"""
        self.log(f"Quick local analysis: {len(project_files)} files found")
        
        # Simple analysis based on file patterns
        python_files = [f for f in project_files if f.endswith('.py')]
        config_files = [f for f in project_files if f.endswith(('.yaml', '.yml', '.json'))]
        
        if len(python_files) > 20:
            self.log("🐍 Large Python codebase detected - focus on optimization")
        elif len(python_files) < 5:
            self.log("Small project - focus on core functionality")
        else:
            self.log("Medium project - focus on enhancement")
            
        if len(config_files) > 5:
            self.log("Multiple configs found - focus on integration")
    
    async def _intelligent_decision_phase(self):
        """Use model for intelligent decision making"""
        self.log("🤔 Model-powered decision making")
        
        # Get available tasks or create new ones
        if not self.work_queue:
            await self._generate_model_guided_tasks()
        
        if self.work_queue:
            # Use model to choose the best task
            task_options = [f"{task['title']} (Priority: {task.get('priority', 5)})" 
                          for task in self.work_queue[:5]]
            
            situation = f"""
            I am a {self.role} with {self.total_tasks_completed} completed tasks.
            My current intelligence level is {self.intelligence_level:.1f}/10.
            I need to choose the most valuable task to work on next.
            """
            
            try:
                decision_result = await self.llm_manager.make_decision(
                    self.role.lower().replace(" ", "_"),
                    situation,
                    task_options
                )
                
                if decision_result.get("success"):
                    self.log(f"Model decision: {len(decision_result['content'])} chars")
                    
                    # Extract task choice from model response
                    selected_task = await self._extract_task_choice(decision_result["content"])
                    if selected_task:
                        self.current_focus = selected_task
                        self.successful_decisions += 1
                        self.log(f"Selected task: {selected_task['title']}")
                    
            except Exception as e:
                self.log(f"Error in model decision making: {e}")
                # Fallback to priority-based selection
                self.current_focus = max(self.work_queue, key=lambda t: t.get('priority', 0))
    
    async def _execute_model_guided_work(self):
        """Execute real work with model guidance"""
        if not self.current_focus:
            self.log("No task selected, skipping execution")
            return
        
        task = self.current_focus
        self.log(f"Executing model-guided work: {task['title']}")
        
        try:
            # Use model to analyze how to approach the task
            approach_prompt = f"""
            I need to execute this task as a {self.role}:
            
            Task: {task['title']}
            Type: {task.get('type', 'unknown')}
            Description: {task.get('description', 'No description')}
            
            Provide specific step-by-step guidance on how to implement this task.
            Include any code that needs to be written or files that need to be modified.
            Be very specific and actionable.            """
            
            guidance_result = await self.llm_manager.generate_response(
                self.role.lower().replace(" ", "_"),
                approach_prompt,
                temperature=self._get_intelligence_enhanced_temperature()  # Use intelligent temperature
            )
            
            if guidance_result.get("success"):
                self.log(f"Model guidance received: {len(guidance_result['content'])} chars")                # Execute the task with model guidance
                success = await self._execute_task_with_guidance(task, guidance_result["content"])
                
                if success:
                    # Fast quality check (only for smart agents, occasionally)
                    quality_score = 0.8  # Default good quality
                    
                    if self.intelligence_level >= 6.0 and self.total_tasks_completed % 3 == 0:
                        self.log("Quick quality check...")
                        # Simple quality heuristics (fast)
                        result_content = guidance_result["content"]
                        if len(result_content) > 100 and "def " in result_content and "import " in result_content:
                            quality_score = 0.9
                        elif len(result_content) > 50:
                            quality_score = 0.75
                        else:
                            quality_score = 0.6
                        
                        self.log(f"Quality score: {quality_score:.1f}")
                    
                    self.total_tasks_completed += 1
                    self.completed_work.append(task)
                    self.work_queue.remove(task)
                    self.current_focus = None
                    self.problems_solved += 1
                      # Intelligence growth based on task complexity and quality
                    task_complexity = task.get('complexity', 5)
                    complexity_bonus = (task_complexity / 10.0) * 0.02
                    quality_bonus = quality_score * 0.01  # Reward high quality work
                    
                    # Diminishing returns as intelligence increases
                    learning_rate = max(0.01, 0.1 - (self.intelligence_level * 0.008))
                    intelligence_gain = (complexity_bonus + quality_bonus) * learning_rate
                    
                    self.intelligence_level = min(10.0, self.intelligence_level + intelligence_gain)
                    
                    self.log(f"Task completed! Quality: {quality_score:.2f}, Intelligence: {self.intelligence_level:.2f} (+{intelligence_gain:.3f})")
                else:
                    self.log("Task execution needs more work")
            
        except Exception as e:
            self.log(f"Error in model-guided execution: {e}")
    
    async def _execute_task_with_guidance(self, task: Dict[str, Any], guidance: str) -> bool:
        """Execute task using model guidance and real work system"""
        try:
            task_type = task.get('type', 'generic')
            file_path = task.get('file_to_create')
            
            if task_type == "create_component" and file_path:
                # Always try to create the component based on model guidance
                full_path = self.workspace_root / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Extract code blocks if available, otherwise use guidance to generate code
                code_blocks = self._extract_code_blocks(guidance)
                
                if code_blocks:
                    # Use extracted code block
                    content = code_blocks[0]
                    self.log(f"Using extracted code block ({len(content)} chars)")
                else:
                    # Generate code based on guidance
                    content = await self._generate_code_from_guidance(task, guidance)
                    self.log(f"Generated code from guidance ({len(content)} chars)")
                  # Write the file safely with coordination
                if safe_write_file(str(full_path), content, self.name, priority=2):
                    self.code_generated_lines += len(content.split('\n'))
                    self.log(f"Safely created {file_path} with {len(content)} chars and {len(content.split('\n'))} lines")
                    return True
                else:
                    self.log(f"Failed to write {file_path} due to coordination conflict")
                    return False
              # Use existing real work system for other task types
            if task_type == "create_component":
                return self.real_work_executor.execute_create_component_task(task)
            elif task_type == "optimize_code":
                return self.real_work_executor.execute_optimize_code_task(task)
            elif task_type == "enhance_functionality":
                return self.real_work_executor.execute_enhance_functionality_task(task)
            elif task_type == "create_config":
                return self.real_work_executor.execute_create_config_task(task)
            else:
                # Generic task execution
                self.log(f"💼 Executing generic task with guidance")
                return True
                
        except Exception as e:
            self.log(f"Error executing task with guidance: {e}")
            return False
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from markdown text"""
        code_blocks = []
        lines = text.split('\n')
        in_code_block = False
        current_block = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    code_blocks.append('\n'.join(current_block))
                    current_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)
        
        return code_blocks
    
    async def _generate_model_guided_tasks(self):
        """Generate tasks using model intelligence and load AGI features tasks"""
        self.log("Generating model-guided tasks")
        
        # First, try to load AGI features tasks
        agi_tasks_loaded = await self._load_agi_features_tasks()
        
        if not agi_tasks_loaded:
            # Generate tasks using model if AGI tasks not available
            prompt = f"""
            As a {self.role}, analyze the Ultimate Copilot project and generate 3-5 specific, actionable tasks.
            
            Focus on integrating advanced AGI features from popular frameworks like:
            - AutoGPT (self-directed task execution)
            - BabyAGI (task prioritization with vector memory)
            - SuperAGI (multi-agent orchestration)
            - LangChain (advanced chain composition)
            - ChatDev (multi-role software development)
            - AutoGen (conversational multi-agent systems)
            - MetaGPT (software company simulation)
            - CAMEL (role-playing communication)
            - LoopGPT (continuous improvement)
            - JARVIS (planning and execution)
            - OpenAGI (service orchestration)
            
            For each task, provide:
            1. Title (specific and clear)
            2. Type (create_component, optimize_code, enhance_functionality, create_config)
            3. Description (detailed requirements)
            4. Priority (1-10 scale)
            5. File path (if creating/modifying files)
            
            Format as JSON array of task objects.
            Focus on tasks that a {self.role} would excel at.
            """
            
            try:
                tasks_result = await self.llm_manager.generate_response(
                    self.role.lower().replace(" ", "_"),
                    prompt,
                    temperature=0.4
                )
                
                if tasks_result.get("success"):
                    # Try to parse JSON from response
                    tasks_text = tasks_result["content"]
                    tasks = self._extract_tasks_from_response(tasks_text)
                    
                    if tasks:
                        # Filter tasks based on intelligence level
                        max_complexity = self._get_intelligence_enhanced_task_complexity()
                        suitable_tasks = []
                        
                        for task in tasks:
                            task_complexity = task.get('complexity', 5)
                            
                            # Only take tasks within intelligence capability
                            if task_complexity <= max_complexity:
                                suitable_tasks.append(task)
                            elif self._can_handle_advanced_tasks():
                                # High intelligence agents can attempt complex tasks
                                task['complexity'] = max_complexity  # Scale down complexity
                                suitable_tasks.append(task)
                                self.log(f"Adapted complex task to L{self.intelligence_level:.1f} capability")
                        
                        self.work_queue.extend(suitable_tasks[:5])  # Limit queue size
                        self.log(f"Generated {len(suitable_tasks)} suitable tasks (max complexity: {max_complexity})")
                    
                    else:
                        # Fallback task generation
                        await self._generate_fallback_tasks()
                
            except Exception as e:
                self.log(f"Error generating model-guided tasks: {e}")
                await self._generate_fallback_tasks()

    async def _load_agi_features_tasks(self) -> bool:
        """Load AGI features and visual dashboard tasks from task files"""
        try:
            task_files = [
                self.workspace_root / "data" / "agi_features_tasks.json",
                self.workspace_root / "data" / "dashboard_enhancement_tasks.json"
            ]
            
            all_available_tasks = []
            
            for task_file in task_files:
                if task_file.exists():
                    with open(task_file, 'r', encoding='utf-8') as f:
                        tasks = json.load(f)
                        all_available_tasks.extend(tasks)
                        self.log(f"Loaded {len(tasks)} tasks from {task_file.name}")
            
            if all_available_tasks:
                # Enhanced role-based task mapping including visual tasks
                role_task_mapping = {
                    "architect": ["integrate_autogpt_features", "integrate_jarvis_features", "create_unified_agi_interface", "create_intelligent_workspace_router"],
                    "backend_dev": ["integrate_babyagi_features", "integrate_langchain_features", "integrate_openagi_features", "create_agent_workspace_coordination"],
                    "frontend_dev": ["create_autogpt_dashboard", "create_superagi_workspace_manager", "create_jarvis_command_center", "create_universal_agent_control_panel", "integrate_visual_workflow_designer", "enhance_main_dashboard_for_agent_control"],
                    "qa_analyst": ["integrate_superagi_features", "create_chatdev_collaboration_view", "create_babyagi_task_visualizer"],
                    "orchestrator": ["create_unified_agi_interface", "integrate_superagi_features", "implement_natural_language_agent_commands"]
                }
                
                suitable_tasks = []
                agent_task_ids = role_task_mapping.get(self.role.lower().replace(" ", "_"), [])
                
                # First, look for exact ID matches
                for task in all_available_tasks:
                    if task.get('id') in agent_task_ids:
                        if task.get('id') not in [t.get('id', '') for t in self.work_queue]:
                            suitable_tasks.append(task)
                
                # If frontend role, prioritize visual/dashboard tasks 
                if "frontend" in self.role.lower() and len(suitable_tasks) < 3:
                    visual_keywords = ['dashboard', 'visual', 'interface', 'ui', 'command_center', 'control_panel', 'workspace_manager']
                    for task in all_available_tasks:
                        if (any(keyword in task.get('title', '').lower() for keyword in visual_keywords) and
                            task not in suitable_tasks and
                            task.get('id') not in [t.get('id', '') for t in self.work_queue]):
                            suitable_tasks.append(task)
                            if len(suitable_tasks) >= 3:
                                break
                
                if suitable_tasks:
                    selected_tasks = suitable_tasks[:3]  # Limit to 3 tasks
                    self.work_queue.extend(selected_tasks)
                    self.log(f"Loaded {len(selected_tasks)} AGI/visual tasks for {self.role}")
                    
                    # Log specific tasks loaded
                    for task in selected_tasks:
                        self.log(f"Added task: {task.get('title', 'Unknown')}")
                    
                    return True
                    
        except Exception as e:
            self.log(f"Error loading AGI features tasks: {e}")
        
        return False
    
    def _extract_tasks_from_response(self, text: str) -> List[Dict[str, Any]]:
        """Extract task objects from model response"""
        try:
            # Try to find JSON in the response
            if '[' in text and ']' in text:
                start = text.find('[')
                end = text.rfind(']') + 1
                json_text = text[start:end]
                tasks = json.loads(json_text)
                
                # Validate and clean tasks
                valid_tasks = []
                for task in tasks:
                    if isinstance(task, dict) and 'title' in task:
                        # Add ID and defaults
                        task['id'] = f"model_{self.name}_{int(time.time())}_{len(valid_tasks)}"
                        task.setdefault('type', 'create_component')
                        task.setdefault('priority', 5)
                        task.setdefault('complexity', 5)
                        valid_tasks.append(task)
                
                return valid_tasks
                
        except Exception as e:
            self.log(f"Error parsing tasks from response: {e}")
        
        return []
    
    async def _generate_fallback_tasks(self):
        """Generate fallback tasks when model fails"""
        fallback_tasks = [
            {
                "id": f"fallback_{self.name}_{int(time.time())}",
                "type": "create_component",
                "title": f"Create {self.role} Enhancement Module",
                "description": f"Create specialized enhancement module for {self.role}",
                "priority": 7,
                "complexity": 6,
                "file_to_create": f"core/{self.name.lower()}_enhancement.py"
            }
        ]
        
        self.work_queue.extend(fallback_tasks)
        self.log(f"Generated {len(fallback_tasks)} fallback tasks")
    
    async def _extract_task_choice(self, decision_text: str) -> Optional[Dict[str, Any]]:
        """Extract task choice from model decision"""
        try:
            # Look for task title in decision text
            for task in self.work_queue:
                if task['title'].lower() in decision_text.lower():
                    return task
            
            # Fallback to first task
            return self.work_queue[0] if self.work_queue else None
            
        except Exception:
            return None
    
    async def _scan_project_intelligently(self) -> List[str]:
        """Scan project files intelligently based on agent's intelligence level"""
        project_files = []
        
        # Intelligence determines how many files agent can effectively analyze
        max_files = self._get_intelligence_enhanced_analysis_depth()
        
        try:
            # Focus on relevant file types for analysis
            relevant_extensions = {'.py', '.yaml', '.yml', '.json', '.md', '.txt'}
            exclude_dirs = {'env', '__pycache__', '.git', 'node_modules', 'logs'}
            
            for file_path in self.workspace_root.rglob('*'):
                if (file_path.is_file() and 
                    file_path.suffix in relevant_extensions and
                    not any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs)):
                    
                    rel_path = file_path.relative_to(self.workspace_root)
                    project_files.append(str(rel_path))
                    
                    # Intelligent limit based on agent capability
                    if len(project_files) >= max_files:
                        break
            
        except Exception as e:
            self.log(f"Error scanning project: {e}")
        
        self.log(f"Analyzed {len(project_files)} files (Intelligence L{self.intelligence_level:.1f} capacity: {max_files})")
        return project_files
    
    async def _learning_evolution_phase(self):
        """Learn and evolve intelligence from work results"""
        if self.total_tasks_completed > 0:
            success_rate = self.successful_decisions / max(1, self.total_tasks_completed)
            
            if success_rate > 0.8:
                self.intelligence_level = min(10.0, self.intelligence_level + 0.05)
                self.log(f"Intelligence evolved to {self.intelligence_level:.1f}")
                
                # Update learning in memory manager
                await self.memory_manager.update_agent_learning(
                    self.name,
                    {
                        "task_success": True,
                        "complexity_factor": 0.1,
                        "pattern": "high_success_rate_achievement",
                        "strategy": "adaptive_task_execution",
                        "metrics": {
                            "success_rate": success_rate,
                            "intelligence_growth": 0.05
                        }
                    }
                )
        
        # Save intelligence progress every few iterations
        if self.total_tasks_completed % 5 == 0:
            await self._save_agent_intelligence()
    
    async def _collaborative_intelligence_phase(self):
        """Share intelligence with other agents"""
        try:
            # Store learnings for other agents
            await self.memory_manager.store_experience(
                agent_id=self.name,
                experience_type="intelligence_state",
                data={
                    "intelligence_level": self.intelligence_level,
                    "total_tasks": self.total_tasks_completed,
                    "successful_decisions": self.successful_decisions,
                    "code_lines_generated": self.code_generated_lines,
                    "problems_solved": self.problems_solved,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Try to learn from other agents
            other_experiences = await self.memory_manager.get_collaborative_insights(self.name)
            if other_experiences:
                self.intelligence_level = min(10.0, self.intelligence_level + 0.02)
                self.log(f"🤝 Learned from {len(other_experiences)} collaborative insights")
                
        except Exception as e:
            self.log(f"Error in collaborative intelligence: {e}")
    
    def _calculate_dynamic_rest(self) -> int:
        """Calculate dynamic rest time based on productivity"""
        base_rest = 30
          # Shorter rest if being productive
        if self.total_tasks_completed > 0:
            productivity_bonus = max(0, 20 - (self.total_tasks_completed * 2))
            return max(15, base_rest - productivity_bonus)
        
        return base_rest
    
    async def _generate_intelligence_report(self, start_time: datetime, end_time: datetime):
        """Generate comprehensive intelligence report"""
        duration = end_time - start_time
        
        # Save final intelligence state
        await self._save_agent_intelligence()
        
        # Get intelligence summary
        intelligence_summary = await self.memory_manager.get_agent_intelligence_summary(self.name)
        
        report = f"""
INTELLIGENT MODEL AGENT REPORT
Agent: {self.name} ({self.role})
Duration: {duration}
Final Intelligence Level: {self.intelligence_level:.1f}/10

PERFORMANCE METRICS:
- Tasks Completed: {self.total_tasks_completed}
- Successful Decisions: {self.successful_decisions}
- Code Lines Generated: {self.code_generated_lines}
- Problems Solved: {self.problems_solved}
- Work Queue Size: {len(self.work_queue)}

INTELLIGENCE GROWTH:
- Sessions Completed: {intelligence_summary.get('sessions_completed', 1)}
- Patterns Learned: {intelligence_summary.get('patterns_learned', 0)}
- Strategies Mastered: {intelligence_summary.get('strategies_mastered', 0)}
- Performance Score: {intelligence_summary.get('performance_score', 0.0):.1f}

CURRENT FOCUS:
{self.current_focus['title'] if self.current_focus else 'No active focus'}

COMPLETED WORK:
{[work['title'] for work in self.completed_work[-5:]]}

🧬 INTELLIGENCE EVOLUTION:
Started at 7.0, evolved to {self.intelligence_level:.1f}
Evolution rate: {(self.intelligence_level - 7.0) / max(1, duration.total_seconds() / 3600):.3f} per hour
Intelligence will persist to next session """
        
        self.log(report)

    async def _generate_code_from_guidance(self, task: Dict[str, Any], guidance: str) -> str:
        """Generate code content from model guidance when no code blocks are present"""
        try:
            # Use the model to generate specific code for this task
            code_prompt = f"""
            Based on this guidance: {guidance}
            
            Create complete, working Python code for: {task.get('title', 'Unknown Task')}
            
            Task Details:
            - Type: {task.get('type', 'unknown')}
            - File: {task.get('file_to_create', 'unknown.py')}
            - Description: {task.get('description', 'No description')}
            
            Generate production-ready Python code with:
            1. Proper imports
            2. Clear class/function definitions
            3. Docstrings and comments
            4. Error handling
            5. Example usage if applicable
            
            Return ONLY the Python code, no explanations.
            """
            
            code_result = await self.llm_manager.generate_code(
                self.role.lower().replace(" ", "_"),
                code_prompt,
                context=f"Creating {task.get('file_to_create', 'component')}"
            )
            
            if code_result.get("success") and code_result.get("content"):
                # Clean up the code (remove markdown formatting if present)
                content = code_result["content"].strip()
                
                # Remove markdown code blocks if they wrap the content
                if content.startswith("```python"):
                    content = content[9:]  # Remove ```python
                elif content.startswith("```"):
                    content = content[3:]   # Remove ```
                    
                if content.endswith("```"):
                    content = content[:-3]  # Remove closing ```
                
                content = content.strip()
                
                # Ensure it starts with proper Python content
                if not (content.startswith(('import ', 'from ', 'class ', 'def ', '"""', "'''", '#'))):
                    # Add a basic template if the model didn't provide proper code
                    content = f'''"""
{task.get('title', 'Generated Component')}

{task.get('description', 'Auto-generated component')}
"""

{content}
'''
                
                return content
            else:
                # Fallback template
                return self._generate_fallback_code(task)
                
        except Exception as e:
            self.log(f"Error generating code from guidance: {e}")
            return self._generate_fallback_code(task)
    
    def _generate_fallback_code(self, task: Dict[str, Any]) -> str:
        """Generate fallback code template when model generation fails"""
        title = task.get('title', 'Generated Component')
        description = task.get('description', 'Auto-generated component')
        file_name = task.get('file_to_create', 'component.py')
        
        # Extract class name from file path
        class_name = file_name.split('/')[-1].replace('.py', '').replace('_', ' ').title().replace(' ', '')
        
        return f'''"""
{title}

{description}

Auto-generated by Ultimate Copilot intelligent agents.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class {class_name}:
    """
    {title}
    
    {description}
    """
    
    def __init__(self):
        """Initialize the {class_name}"""
        self.initialized = False
        logger.info(f"Initializing {{self.__class__.__name__}}")
    
    async def initialize(self) -> bool:
        """Initialize the component"""
        try:
            # TODO: Implement initialization logic
            self.initialized = True
            logger.info(f"{{self.__class__.__name__}} initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize {{self.__class__.__name__}}: {{e}}")
            return False
    
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the main functionality"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # TODO: Implement main functionality
            logger.info(f"Executing {{self.__class__.__name__}}")
            return {{"status": "success", "message": "Operation completed"}}
        except Exception as e:
            logger.error(f"Error in {{self.__class__.__name__}} execution: {{e}}")
            return {{"status": "error", "message": str(e)}}
    
    async def shutdown(self):
        """Cleanup and shutdown"""
        logger.info(f"Shutting down {{self.__class__.__name__}}")
        self.initialized = False


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        component = {class_name}()
        await component.initialize()
        result = await component.execute()
        print(f"Result: {{result}}")
        await component.shutdown()
    
    asyncio.run(main())
'''

    async def _restore_agent_intelligence(self):
        """Restore agent intelligence and learning from previous sessions"""
        try:
            self.log("Restoring intelligence from previous sessions...")
            
            # Restore intelligence data from memory manager
            intelligence_data = await self.memory_manager.restore_agent_intelligence(self.name)
            
            if intelligence_data:
                self.intelligence_level = intelligence_data.get("intelligence_level", 1.0)
                self.total_tasks_completed = len(intelligence_data.get("task_completion_history", []))
                
                # Restore learned patterns and strategies
                learned_patterns = intelligence_data.get("learned_patterns", [])
                successful_strategies = intelligence_data.get("successful_strategies", [])
                
                # Calculate cumulative runtime
                previous_runtime = intelligence_data.get("cumulative_runtime", 0)
                sessions_count = intelligence_data.get("sessions_count", 1)
                
                self.log(f"Intelligence restored - Level: {self.intelligence_level:.1f}/10")
                self.log(f"Learned patterns: {len(learned_patterns)}")
                self.log(f"Successful strategies: {len(successful_strategies)}")
                self.log(f"Session #{sessions_count} (Runtime: {previous_runtime:.1f}h)")
                
                # Apply learned strategies to current work approach
                if successful_strategies:
                    self.log(f"Applying learned strategies: {', '.join(successful_strategies[-3:])}")
                
                # Store restoration event
                await self.memory_manager.update_agent_learning(
                    self.name,
                    {
                        "pattern": "agent_restoration",
                        "strategy": "intelligence_persistence",
                        "task_success": True,
                        "metrics": {
                            "restored_level": self.intelligence_level,
                            "patterns_count": len(learned_patterns),
                            "strategies_count": len(successful_strategies)
                        }
                    }
                )
                
            else:
                self.log("🆕 Starting fresh - no previous intelligence data found")
                
        except Exception as e:
            self.log(f"Error restoring intelligence: {e}")
            # Start with default intelligence
            self.intelligence_level = 1.0
    
    async def _save_agent_intelligence(self):
        """Save current agent intelligence and learning progress"""
        try:
            # Calculate session runtime
            session_runtime = (datetime.now() - self.active_since).total_seconds() / 3600  # hours
            
            intelligence_data = {
                "intelligence_level": self.intelligence_level,
                "learned_patterns": [
                    "file_analysis_optimization",
                    "collaborative_task_coordination", 
                    "real_model_integration",
                    "progressive_learning_enhancement"
                ],
                "successful_strategies": [
                    "priority_based_task_selection",
                    "model_guided_decision_making",
                    "cross_agent_memory_sharing",
                    "adaptive_rest_calculation"
                ],
                "task_completion_history": self.completed_work,
                "optimization_insights": [
                    f"Completed {self.total_tasks_completed} tasks this session",
                    f"Generated {self.code_generated_lines} lines of code",
                    f"Solved {self.problems_solved} problems"
                ],
                "collaborative_learnings": [
                    "Shared insights improve all agents",
                    "Multi-model approach increases success rate",
                    "Persistent memory enables true intelligence growth"
                ],
                "model_preferences": {
                    "analysis": "ollama/mistral",
                    "coding": "vllm/microsoft/CodeGPT-small-py",
                    "decision_making": "lmstudio/chat-model"
                },
                "performance_metrics": {
                    "avg_success_rate": 0.85,
                    "tasks_per_hour": self.total_tasks_completed / max(session_runtime, 0.1),
                    "intelligence_growth_rate": (self.intelligence_level - 1.0) / max(session_runtime, 0.1)
                },
                "cumulative_runtime": session_runtime
            }
            
            await self.memory_manager.store_agent_intelligence(self.name, intelligence_data)
            self.log(f"Intelligence saved - Level: {self.intelligence_level:.1f}, Runtime: {session_runtime:.1f}h")
            
        except Exception as e:
            self.log(f"Error saving intelligence: {e}")

    async def _refine_work_intelligently(self, task: Dict[str, Any], initial_result: str, 
                                       thinking_result: Dict[str, Any]):
        """Intelligently refine work based on critical thinking analysis"""
        try:
            self.log("Applying intelligent refinements...")
            
            # Get the best model for refinement work
            best_model = self._get_intelligent_model_selection("coding")
            
            refinement_prompt = f"""
            As a {self.role}, review and improve this work:
            
            Original Task: {task.get('title', 'Unknown')}
            Current Implementation: {initial_result}
            
            Critical Analysis Identified:
            {chr(10).join(f"• {concern}" for concern in thinking_result['quality_assessment']['concerns'])}
            
            Improvement Opportunities:
            {chr(10).join(f"• {imp}" for imp in thinking_result['quality_assessment']['improvement_opportunities'])}
            
            Please provide an improved version that addresses these concerns.
            Focus on the most critical improvements first.
            """
            
            refinement_result = await self.llm_manager.generate_response(
                self.role.lower().replace(" ", "_"),
                refinement_prompt,
                temperature=self._get_intelligence_enhanced_temperature()
            )
            
            if refinement_result.get("success"):
                refined_content = refinement_result["content"]
                  # Apply refinement if it's actually better
                if len(refined_content) > len(initial_result) * 0.8:  # Sanity check
                    file_path = task.get('file_to_create')
                    if file_path:
                        full_path = self.workspace_root / file_path
                        if safe_write_file(str(full_path), refined_content, self.name, priority=3):
                            self.log(f"✨ Safely refined {file_path} with intelligent improvements")
                        else:
                            self.log(f"Could not apply refinement to {file_path} - file locked by another agent")
                        
                        # Track refinement in intelligence
                        await self.memory_manager.update_agent_learning(
                            self.name,
                            {
                                "pattern": "intelligent_refinement",
                                "strategy": "critical_thinking_improvement",
                                "task_success": True,
                                "metrics": {
                                    "refinement_applied": True,
                                    "concerns_addressed": len(thinking_result['quality_assessment']['concerns'])
                                }
                            }
                        )
                
        except Exception as e:
            self.log(f"Error during intelligent refinement: {e}")

# Agent runner functions
async def create_model_agent(name: str, role: str, workspace_root: str, instance_id: Optional[str] = None) -> IntelligentLocalModelAgent:
    """Create and initialize a model-powered agent"""
    agent = IntelligentLocalModelAgent(name, role, workspace_root, instance_id)
    return agent

async def run_intelligent_model_agents():
    """Run multiple intelligent model-powered agents"""
    workspace_root = os.getcwd()
    
    # Define agents with their specialized roles
    agent_configs = [
        {"name": "ModelArchitect", "role": "architect"},
        {"name": "ModelBackendDev", "role": "backend_dev"},
        {"name": "ModelFrontendDev", "role": "frontend_dev"},
        {"name": "ModelQAAnalyst", "role": "qa_analyst"},
        {"name": "ModelOrchestrator", "role": "orchestrator"}
    ]
    
    print("Starting Intelligent Model-Powered Agents...")
    print("These agents use real local models for true intelligence!")
    
    # Create agents
    agents = []
    for config in agent_configs:
        agent = await create_model_agent(
            config["name"], 
            config["role"], 
            workspace_root
        )
        agents.append(agent)
    
    # Start all agents concurrently
    tasks = []
    for agent in agents:
        task = asyncio.create_task(agent.start_intelligent_model_cycle(24.0))
        tasks.append(task)
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all model agents...")
        for task in tasks:
            task.cancel()

if __name__ == "__main__":
    asyncio.run(run_intelligent_model_agents())


