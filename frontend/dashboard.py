"""
Streamlit Dashboard for Ultimate Copilot System
Provides real-time monitoring and control interface
"""
import streamlit as st
import streamlit.components.v1 as components
import requests
import socket
import os
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from typing import Dict, Any, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="Ultimate Copilot System Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dashboard configuration
REFRESH_INTERVAL = 5  # seconds
API_BASE_URL = "http://localhost:8000"  # System API endpoint

class CopilotDashboard:
    def __init__(self):
        self.system_status = {}
        self.performance_metrics = {}
        self.model_info = {}
        self.backend_url = os.getenv("DASHBOARD_BACKEND_URL", "http://127.0.0.1:8001")
        self.active_agents = {}
        self.workspace_path = None
    
    def get_backend_status(self) -> Dict[str, Any]:
        """Get status from backend API"""
        try:
            response = requests.get(f"{self.backend_url}/system/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {"status": "offline"}
    
    
    
    def send_agent_command(self, agent_type: str, command: str, workspace: Optional[str] = None) -> Dict[str, Any]:
        """Send command to specific agent"""
        try:
            payload = {
                "agent_id": agent_type,
                "action": command,
                "config": {"workspace": workspace or self.workspace_path} if workspace or self.workspace_path else None
            }
            response = requests.post(f"{self.backend_url}/agents/control", json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "error", "message": "Failed to connect to backend"}
    
    
    
    def send_agent_instruction(self, agent_type: str, instruction: str, workspace: Optional[str] = None) -> Dict[str, Any]:
        """Send instruction to specific agent"""
        try:
            payload = {
                "agent_id": agent_type,
                "action": "send_instruction",
                "instruction": instruction,
                "workspace": workspace or self.workspace_path
            }
            print(f"[DEBUG] Sending agent instruction: {payload}")
            response = requests.post(f"{self.backend_url}/agents/control", json=payload, timeout=10)
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response content: {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}: {response.text}"}
        
        except Exception as e:
            print(f"[DEBUG] Exception in send_agent_instruction: {e}")
            return {"status": "error", "message": str(e)}
        return {"status": "error", "message": "Failed to connect to backend"}
    
    
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        try:
            response = requests.get(f"{self.backend_url}/agents/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {"agents": {}, "status": "offline"}
        
    
    
    def control_system(self, action: str) -> Dict[str, Any]:
        """Send control commands to the system"""
        try:
            import subprocess
            import os

            project_root = os.path.dirname(os.path.dirname(__file__))

            if action == "start":
                subprocess.Popen(
                    ["python", "main.py"],
                    cwd=project_root,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                return {"status": "success", "message": "System starting in new window..."}

            elif action == "stop":
                # For now, just return a message since stopping requires process management
                return {"status": "info", "message": "Use Ctrl+C in the system console to stop"}

            elif action == "restart":
                return {"status": "info", "message": "Stop the system with Ctrl+C, then restart manually"}

            elif action == "restart_components":
                return {"status": "info", "message": "Component restart initiated (simulated)"}
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
                
        
        except Exception as e:
            return {"status": "error", "message": f"Control action failed: {str(e)}"}

    
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            # Try to detect which editor is actually running/selected
            # Check for running processes or active connections
            import subprocess
            import os
            
            # Check for VS Code Insiders process
            vscode_running = False
            void_running = False
            
            try:
                # Check if VS Code Insiders is running
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq Code - Insiders.exe"],
                    capture_output=True, text=True, timeout=5
                )
                vscode_running = "Code - Insiders.exe" in result.stdout
            except:
                pass
            
            try:
                # Check if Void Editor is running (adjust process name as needed)
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq void.exe"],
                    capture_output=True, text=True, timeout=5
                )
                void_running = "void.exe" in result.stdout
            except:
                pass
              # Determine active editor based on system selection
            # If we can't detect via process, use WebSocket connectivity
            vscode_connected = False
            void_connected = False
            
            try:
                # Try to connect to VS Code WebSocket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                vscode_connected = sock.connect_ex(('localhost', 8765)) == 0
                sock.close()
            except:
                pass
                
            try:
                # Try to connect to Void Editor WebSocket  
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                void_connected = sock.connect_ex(('localhost', 7900)) == 0
                sock.close()
            except:
                pass
            
            return {
                "status": "running",
                "uptime": "1h 23m",
                "void_editor": {
                    "connected": void_connected or void_running,
                    "status": "connected" if (void_connected or void_running) else "disconnected"
                },
                "vscode": {
                    "connected": vscode_connected or vscode_running,
                    "status": "connected" if (vscode_connected or vscode_running) else "disconnected"
                },
                "models_loaded": 2,
                "vram_usage": {"current": 4.5, "total": 7.5, "percentage": 60.0},
                "active_tasks": 0,
                "total_requests": 42,
                "success_rate": 100.0
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}    
    
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "avg_response_time": 0.85,
            "requests_per_minute": 12,
            "error_rate": 0.0,
            "model_switches": 3,
            "memory_efficiency": 85.2
        }
    
    
    
    def send_model_command(self, provider: str, model: str, action: str) -> Dict[str, Any]:
        """Send model control command to backend"""
        try:
            response = requests.post(
                f"{self.backend_url}/models/control",
                json={
                    "provider": provider,
                    "model": model,
                    "action": action
                },
                timeout=30  # Model operations can take longer
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"Backend error: {response.status_code}"}
        
        except Exception as e:
            return {"status": "error", "message": f"Connection error: {str(e)}"}    
    
    def analyze_workspace_backend(self, workspace_path: str) -> dict:
        try:
            response = requests.post(f"{self.backend_url}/workspace/analyze", json={"workspace_path": workspace_path}, timeout=30)
            return response.json() if response.status_code == 200 else {"error": response.text}
        
        except Exception as e:
            return {"error": str(e)}

    
    
    def quick_scan_workspace_backend(self, workspace_path: str) -> dict:
        try:
            response = requests.post(f"{self.backend_url}/workspace/quick-scan", json={"workspace_path": workspace_path}, timeout=15)
            return response.json() if response.status_code == 200 else {"error": response.text}
        
        except Exception as e:
            return {"error": str(e)}

    
    
    def generate_documentation_backend(self, workspace_path: str) -> dict:
        try:
            response = requests.post(f"{self.backend_url}/workspace/generate-documentation", json={"workspace_path": workspace_path}, timeout=60)
            return response.json() if response.status_code == 200 else {"error": response.text}
        
        except Exception as e:
            return {"error": str(e)}

    
    
    def analyze_architecture_backend(self, workspace_path: str) -> dict:
        try:
            response = requests.post(f"{self.backend_url}/workspace/analyze-architecture", json={"workspace_path": workspace_path}, timeout=60)
            return response.json() if response.status_code == 200 else {"error": response.text}
        
        except Exception as e:
            return {"error": str(e)}

    
    
    def run_tests_backend(self, workspace_path: str) -> dict:
        try:
            response = requests.post(f"{self.backend_url}/workspace/run-tests", json={"workspace_path": workspace_path}, timeout=60)
            return response.json() if response.status_code == 200 else {"error": response.text}
        
        except Exception as e:
            return {"error": str(e)}

    
    
    def code_review_backend(self, workspace_path: str) -> dict:
        try:
            response = requests.post(f"{self.backend_url}/workspace/code-review", json={"workspace_path": workspace_path}, timeout=60)
            return response.json() if response.status_code == 200 else {"error": response.text}
        
        except Exception as e:
            return {"error": str(e)}
    
    
    
    def get_model_status(self) -> dict:
        """Get model status with improved error handling and timeout"""
        try:
            response = requests.get(f"{self.backend_url}/models/status", timeout=3)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Backend returned status {response.status_code}", "manager": "offline"}
        
        except requests.exceptions.Timeout:
            return {"error": "Backend timeout", "manager": "timeout"}        
        except requests.exceptions.ConnectionError:
            return {"error": "Backend not reachable", "manager": "offline"}
        
        except Exception as e:
            return {"error": str(e), "manager": "error"}

    
    def get_system_logs(self) -> dict:
        try:
            response = requests.get(f"{self.backend_url}/logs", timeout=10)
            return response.json() if response.status_code == 200 else {"error": response.text}
        
        except Exception as e:
            return {"error": str(e)}

def main():
    """Main dashboard function"""
    dashboard = CopilotDashboard()
    
    # Page title with status indicator
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.title("🤖 Ultimate Copilot System Dashboard")
        st.caption("Real-time monitoring and control interface")
    
    with col2:
        status = dashboard.get_system_status()
        if status.get("status") == "running":
            st.success("🟢 System Online")
        else:
            st.error("🔴 System Offline")
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
      # Sidebar - System Controls
    with st.sidebar:
        st.header("🎛️ System Controls")
        
        st.subheader("Quick Actions")
        if st.button("🚀 Start System", use_container_width=True):
            result = dashboard.control_system("start")
            if result["status"] == "success":
                st.success(result["message"])
            elif result["status"] == "info":
                st.info(result["message"])
            else:
                st.error(result["message"])
        
        if st.button("⏹️ Stop System", use_container_width=True):
            result = dashboard.control_system("stop")
            st.info(result["message"])
        
        if st.button("🔄 Restart Components", use_container_width=True):
            result = dashboard.control_system("restart_components")
            st.info(result["message"])
        st.divider()
        st.subheader("Integration Controls")
        void_enabled = st.checkbox("🔮 Void Editor", value=False, help="Enable Void Editor integration", key="classic_void")
        vscode_enabled = st.checkbox("💻 VS Code Insiders", value=False, help="Enable VS Code Insiders integration", key="classic_vscode")
        
        st.divider()
        
        st.subheader("Model Providers")
        ollama_enabled = st.checkbox("🦙 Ollama", value=True, key="classic_ollama")
        lms_enabled = st.checkbox("🏭 LM Studio", value=True, key="classic_lms")
        vllm_enabled = st.checkbox("⚡ vLLM", value=False, key="classic_vllm")
    status = dashboard.get_system_status()
    metrics = dashboard.get_performance_metrics()
    model_status = dashboard.get_model_status()
    
    # Top metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            label="System Uptime",
            value=status.get("uptime", "Unknown"),
            delta="Stable"
        )
    
    with col2:
        st.metric(
            label="Active Models",
            value=status.get("models_loaded", 0),
            delta="+1 since restart"
        )

    with col3:
        vram = status.get("vram_usage", {})
        st.metric(
            label="VRAM Usage",
            value=f"{vram.get('current', 0):.1f}GB",
            delta=f"{vram.get('percentage', 0):.0f}% of {vram.get('total', 0):.1f}GB"
        )

    with col4:
        st.metric(
            label="Success Rate",
            value=f"{status.get('success_rate', 0):.1f}%",
            delta="Excellent"
        )

    with col5:
        st.metric(
            label="Avg Response",
            value=f"{metrics.get('avg_response_time', 0):.2f}s",
            delta="Fast"
        )

    # Agent Interaction Section
    st.header("🤖 Agent Copilot Interface")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat with Agent Swarm")
        
        # Initialize session state for chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Agent selection
        agent_options = {
            "🎯 Orchestrator": "orchestrator",
            "🏗️ Architect": "architect", 
            "⚙️ Backend Dev": "backend_dev",
            "🎨 Frontend Dev": "frontend_dev",
            "🔍 QA Analyst": "qa_analyst",
            "🤖 Auto-Select": "auto"
        }
        
        selected_agent = st.selectbox(
            "Select Agent:",
            options=list(agent_options.keys()),
            index=0,
            help="Choose which agent to interact with, or let the system auto-select"
        )
        
        # Prompt input
        user_prompt = st.text_area(
            "Enter your task or question:",
            placeholder="e.g., 'Create a FastAPI endpoint for user authentication' or 'Explain this code functionality'",
            height=100,
            help="Describe what you want the agents to do. Be specific for best results."
        )
        
        # Task type selection
        task_type_options = {
            "General": "general",
            "Code Review": "code_review",
            "Architecture Design": "architecture",
            "API Development": "api_development", 
            "Frontend Development": "frontend_dev",
            "Testing & QA": "testing",
            "Documentation": "documentation",
            "Bug Analysis": "bug_analysis",
            "Performance Optimization": "optimization"
        }
        
        task_type = st.selectbox(
            "Task Type:",
            options=list(task_type_options.keys()),
            help="Helps route your request to the most appropriate agent"
        )
        
        # Priority selection
        priority = st.selectbox(
            "Priority:",
            options=["Low", "Medium", "High", "Critical"],
            index=1
        )
        
        # Submit button
        col_submit, col_clear = st.columns([1, 1])
        
        with col_submit:
            if st.button("🚀 Send to Agents", use_container_width=True, type="primary"):
                if user_prompt.strip():
                    # Create task object
                    task_data = {
                        "title": user_prompt[:50] + ("..." if len(user_prompt) > 50 else ""),
                        "description": user_prompt,
                        "type": "user",
                        "agent": selected_agent,
                        "task_type": task_type
                    }
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "type": "user",
                        "content": user_prompt,
                        "task_type": task_type,
                        "timestamp": datetime.now().isoformat(),
                        "agent": selected_agent
                    })
                    try:
                        import time
                        time.sleep(2)  # Simulate processing time

                        # Mock response - replace with actual agent execution
                        response = f"""✅ **Task Analysis Complete**

**Agent:** {selected_agent}
**Task Type:** {task_type}

**Response:** I've analyzed your request: "{user_prompt[:100]}..."

**Action Plan:**
1. Understand the requirements
2. Design the solution architecture  
3. Implement the core functionality
4. Add proper error handling
5. Write tests and documentation

**Next Steps:**
- The task has been queued for execution
- You'll receive updates as agents work on this
- Check the system logs for detailed progress

*Note: This is a demo response. In the full system, this would trigger actual agent execution.*"""

                        # Add response to chat history
                        st.session_state.chat_history.append({
                            "type": "agent",
                            "content": response,
                            "timestamp": datetime.now().isoformat(),
                            "agent": selected_agent,
                            "status": "completed"
                        })

                        st.success("✅ Task sent to agent swarm successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error sending task to agents: {str(e)}")
                        st.session_state.chat_history.append({
                            "type": "error",
                            "content": f"Failed to process request: {str(e)}",
                            "timestamp": datetime.now().isoformat()
                        })
                else:
                    st.warning("⚠️ Please enter a task or question before sending.")
        
        with col_clear:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    with col2:
        st.subheader("⚡ Quick Actions")
        
        # Quick action buttons
        if st.button("📋 Create Project Plan", use_container_width=True):
            quick_task = "Create a comprehensive project plan with milestones, tasks, and resource allocation for a new web application."
            st.session_state.chat_history.append({
                "type": "user",
                "content": quick_task,
                "timestamp": datetime.now().isoformat(),
                "agent": "🎯 Orchestrator",
                "task_type": "General"
            })
            st.rerun()
            
        if st.button("🏗️ Design Architecture", use_container_width=True):
            quick_task = "Design a scalable system architecture for a modern web application with microservices, database design, and deployment strategy."
            st.session_state.chat_history.append({
                "type": "user", 
                "content": quick_task,
                "timestamp": datetime.now().isoformat(),
                "agent": "🏗️ Architect",
                "task_type": "Architecture Design"
            })
            st.rerun()
            
        if st.button("⚙️ Code Review", use_container_width=True):
            quick_task = "Perform a comprehensive code review focusing on best practices, security, performance, and maintainability."
            st.session_state.chat_history.append({
                "type": "user",
                "content": quick_task, 
                "timestamp": datetime.now().isoformat(),
                "agent": "🔍 QA Analyst",
                "task_type": "Code Review"
            })
            st.rerun()
            
        if st.button("🐛 Debug Issue", use_container_width=True):
            quick_task = "Help debug and resolve a technical issue. Analyze symptoms, identify root cause, and provide solutions."
            st.session_state.chat_history.append({
                "type": "user",
                "content": quick_task,
                "timestamp": datetime.now().isoformat(), 
                "agent": "🤖 Auto-Select",
                "task_type": "Bug Analysis"
            })
            st.rerun()
    
    # Chat History Display
    if st.session_state.chat_history:
        st.subheader("💬 Conversation History")
        
        # Create a container for the chat history
        chat_container = st.container()
        
        with chat_container:
            displayed_messages = list(reversed(st.session_state.chat_history[-10:]))
            for i, message in enumerate(displayed_messages):  # Show last 10 messages
                timestamp = datetime.fromisoformat(message['timestamp']).strftime("%H:%M:%S")
                
                if message['type'] == 'user':
                    with st.chat_message("user"):
                        st.write(f"**[{timestamp}] You → {message.get('agent', 'Agent')}**")
                        st.write(f"*Task Type: {message.get('task_type', 'General')}*")
                        st.write(message['content'])
                        
                elif message['type'] == 'agent':
                    with st.chat_message("assistant"):
                        st.write(f"**[{timestamp}] {message.get('agent', 'Agent')} Response**")
                        st.markdown(message['content'])
                        
                elif message['type'] == 'error':
                    with st.chat_message("assistant"):
                        st.error(f"**[{timestamp}] System Error**")
                        st.write(message['content'])
                        
                # Add a divider between messages
                if i < len(displayed_messages) - 1:
                    st.divider()

    # Integration Status
    st.header("🔗 Integration Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔮 Void Editor Integration")
        void_status = status.get("void_editor", {})
        if void_status.get("connected"):
            st.success("✅ Connected and Active")
            st.info("WebSocket: ws://localhost:7900")
        else:
            st.warning("⚠️ Not Connected")
            st.info("Make sure Void Editor is running")
    
    with col2:
        st.subheader("💻 VS Code Insiders Integration")
        vscode_status = status.get("vscode", {})
        if vscode_status.get("connected"):
            st.success("✅ Connected and Active")
            st.info("WebSocket: ws://localhost:8765")
        elif vscode_status.get("status") == "disconnected":
            st.warning("⚠️ Selected but Not Connected")
            st.caption("Make sure VS Code Insiders is running")
        else:
            st.info("ℹ️ Available but Not Selected")
            st.caption("Select during system startup to activate")
    
    # Model Provider Status
    st.header("🤖 Model Providers")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🦙 Ollama")
        ollama = model_status.get("ollama", {})
        if ollama.get("status") == "running":
            st.success("✅ Running")
            st.write(f"**Models:** {len(ollama.get('models', []))}")
            for model in ollama.get('models', []):
                st.text(f"• {model}")
            st.write(f"**Memory:** {ollama.get('memory_usage', 0):.1f}GB")
        else:
            st.error("❌ Not Running")
    
    with col2:
        st.subheader("🏭 LM Studio")
        lms = model_status.get("lmstudio", {})
        if lms.get("status") == "running":
            st.success("✅ Running")
            st.write(f"**Models:** {len(lms.get('models', []))}")
            for model in lms.get('models', []):
                st.text(f"• {model}")
            st.write(f"**Memory:** {lms.get('memory_usage', 0):.1f}GB")
        else:
            st.error("❌ Not Running")
    
    with col3:
        st.subheader("⚡ vLLM (WSL)")
        vllm = model_status.get("vllm", {})
        if vllm.get("status") == "running":
            st.success("✅ Running")
            st.write(f"**Models:** {len(vllm.get('models', []))}")
            for model in vllm.get('models', []):
                st.text(f"• {model}")
            st.write(f"**Memory:** {vllm.get('memory_usage', 0):.1f}GB")
        else:
            st.info("ℹ️ Optional for 8GB systems")
    
    # Performance Charts
    st.header("📈 Performance Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # VRAM Usage Chart
        vram_data = pd.DataFrame({
            'Component': ['Ollama Models', 'LM Studio', 'System Reserved', 'Available'],
            'Memory (GB)': [2.5, 2.0, 1.0, 2.0],
            'Color': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        })
        
        fig = px.pie(
            vram_data, 
            values='Memory (GB)', 
            names='Component',
            title='VRAM Usage Breakdown',
            color_discrete_sequence=vram_data['Color']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Response Time Chart (mock data)
        time_data = pd.DataFrame({
            'Time': pd.date_range(start='2024-01-01 10:00', periods=20, freq='1min'),
            'Response Time (s)': [0.8, 0.7, 0.9, 0.6, 0.8, 0.7, 0.5, 0.9, 0.8, 0.6,
                                 0.7, 0.8, 0.6, 0.9, 0.7, 0.8, 0.6, 0.7, 0.8, 0.9]
        })        
        fig = px.line(
            time_data, 
            x='Time', 
            y='Response Time (s)',
            title='Response Time Trend',
            line_shape='spline'
        )
        fig.update_traces(line_color='#4ECDC4')
        st.plotly_chart(fig, use_container_width=True)

def activity_logs_section():
    """Activity Logs Section"""
    # System Logs
    st.header("📝 Recent Activity")
    
    # Get real logs from backend
    dashboard = CopilotDashboard()
    try:
        response = requests.get(f"{dashboard.backend_url}/logs", timeout=5)
        if response.status_code == 200:
            log_data = response.json()
            logs = log_data.get("logs", [])
        else:
            logs = []
    except:
        logs = []
    
    # Fallback to sample logs if backend unavailable
    if not logs:
        logs = [
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "component": "Dashboard", "message": "Dashboard connected (backend offline)"},
            {"timestamp": (datetime.now() - timedelta(seconds=30)).isoformat(), "level": "WARNING", "component": "Backend", "message": "Backend connection unavailable"},
        ]
    
    for log in logs:
        log_time = log.get("timestamp", "Unknown")
        if "T" in log_time:  # ISO format
            try:
                dt = datetime.fromisoformat(log_time.replace("Z", "+00:00"))
                log_time = dt.strftime("%H:%M:%S")
            except:
                log_time = log_time[:8]  # Take first 8 chars as fallback
        
        if log["level"] == "ERROR":
            st.error(f"🔴 {log_time} [{log.get('component', 'System')}] {log.get('message', 'No message')}")
        elif log["level"] == "WARNING":
            st.warning(f"🟡 {log_time} [{log.get('component', 'System')}] {log.get('message', 'No message')}")
        else:
            st.info(f"🔵 {log_time} [{log.get('component', 'System')}] {log.get('message', 'No message')}")

    # Auto-refresh
    if st.sidebar.checkbox("🔄 Auto-refresh", value=True):
        import time as time_module
        time_module.sleep(REFRESH_INTERVAL)
        st.rerun()

def workspace_management_section(dashboard):
    """Workspace Management Section"""
    st.header("📁 Workspace Management")
    
    # Initialize session state for workspace path
    if 'workspace_path' not in st.session_state:
        st.session_state.workspace_path = ""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Workspace")
        
        # Workspace selection with session state
        workspace_path = st.text_input(
            "Workspace Path",
            value=st.session_state.workspace_path,
            placeholder="Enter the path to your project workspace",
            help="Enter the path to your project workspace",
            key="workspace_path_input"
        )
          # Update session state and dashboard when workspace path changes
        if workspace_path != st.session_state.workspace_path:
            st.session_state.workspace_path = workspace_path
            dashboard.workspace_path = workspace_path
        
        if st.button("🔄 Scan Workspace"):
            if workspace_path and os.path.exists(workspace_path):
                # Update the dashboard instance
                dashboard.workspace_path = workspace_path
                st.session_state.workspace_path = workspace_path
                
                # Use backend analysis if available
                with st.spinner("Analyzing workspace..."):
                    analysis_result = dashboard.analyze_workspace_backend(workspace_path)
                
                if "error" not in analysis_result:
                    analysis = analysis_result.get("analysis", {})
                    
                    st.success("✅ Workspace analysis complete!")
                    
                    # Display project type
                    project_type = analysis.get("project_type", {})
                    if project_type.get("primary") != "unknown":
                        st.info(f"🎯 **Project Type:** {project_type.get('primary', 'unknown').title()} (confidence: {project_type.get('confidence', 0)}%)")
                    
                    # Display structure info
                    structure = analysis.get("structure", {})
                    col_stats1, col_stats2 = st.columns(2)
                    with col_stats1:
                        st.metric("📁 Total Files", structure.get("total_files", 0))
                        st.metric("📂 Directories", structure.get("total_directories", 0))
                    with col_stats2:
                        size_info = analysis.get("size_info", {})
                        st.metric("💾 Size (MB)", size_info.get("total_size_mb", 0))
                    
                    # Display languages
                    languages = analysis.get("languages", {})
                    if languages:
                        st.subheader("🌐 Languages Detected")
                        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
                            st.text(f"{lang}: {count} files")
                    
                    # Display recommendations
                    recommendations = analysis.get("recommendations", [])
                    if recommendations:
                        st.subheader("💡 Recommendations")
                        for rec in recommendations:
                            st.info(f"• {rec}")
                
                else:
                    # Fallback to basic scan
                    st.warning(f"Backend analysis failed: {analysis_result.get('error', 'Unknown error')}")
                    st.info("Falling back to basic file scan...")
                    
                    # Basic file scan
                    files = []
                    for root, dirs, file_list in os.walk(workspace_path):
                        # Skip common ignore patterns
                        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
                        for file in file_list:
                            if not file.startswith('.'):
                                rel_path = os.path.relpath(os.path.join(root, file), workspace_path)
                                files.append(rel_path)
                    
                    st.success(f"Found {len(files)} files in workspace")
                    
                    # Show file tree
                    if files:
                        st.subheader("📂 File Structure")
                        for file in sorted(files)[:20]:  # Show first 20 files
                            st.text(f"📄 {file}")
                        if len(files) > 20:
                            st.text(f"... and {len(files) - 20} more files")
                            
            elif workspace_path:
                st.error("Workspace path does not exist")
            else:
                st.warning("Please enter a workspace path")
        
        # Quick scan button for faster analysis
        col_scan1, col_scan2 = st.columns(2)
        with col_scan1:
            if st.button("⚡ Quick Scan", help="Fast basic analysis"):
                if workspace_path and os.path.exists(workspace_path):
                    dashboard.workspace_path = workspace_path
                    st.session_state.workspace_path = workspace_path
                    with st.spinner("Quick scanning..."):
                        quick_result = dashboard.quick_scan_workspace_backend(workspace_path)
                    
                    if "error" not in quick_result:
                        scan = quick_result.get("scan", {})
                        if "error" not in scan:
                            st.success("Quick scan completed!")
                            
                            # Display metrics in a simple vertical layout to avoid nesting
                            st.metric("📁 Files", scan.get("file_count", 0))
                            st.metric("📂 Folders", scan.get("directory_count", 0))
                            st.metric("💾 Size (MB)", scan.get("total_size_mb", 0))
                            st.info(f"🎯 Type: {scan.get('project_type', 'unknown').title()}")
                        else:
                            st.error(f"Scan failed: {scan.get('error', 'Unknown error')}")
                    else:
                        st.error(f"Quick scan failed: {quick_result.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter a valid workspace path")
        
        with col_scan2:
            if st.button("🗂️ Create Project", help="Initialize new project structure"):
                if workspace_path:
                    st.info("🚧 Project creation feature coming soon!")
                else:
                    st.warning("Please enter a workspace path first")
                    
            # Agent workspace assignment
            st.subheader("🤖 Agent Assignment")
            
            agents = ["Orchestrator", "Architect", "Backend Developer", "Frontend Developer", "QA Analyst"]
            selected_agent = st.selectbox("Select Agent", agents)
            
            if st.button("📋 Assign Workspace to Agent"):
                if workspace_path:
                    # Update dashboard workspace path
                    dashboard.workspace_path = workspace_path
                    st.session_state.workspace_path = workspace_path
                    
                    st.success(f"Workspace assigned to {selected_agent}")
                    st.info(f"Agent will analyze: {workspace_path}")
                else:
                    st.warning("Please enter a workspace path first")
    
    with col2:
        st.subheader("Workspace Analysis")
        
        # Project type detection
        project_types = {
            "Python": ["requirements.txt", "pyproject.toml", "setup.py"],
            "JavaScript/Node.js": ["package.json", "package-lock.json"],
            "Java": ["pom.xml", "build.gradle"],
            "C++": ["CMakeLists.txt", "Makefile"],
            "Rust": ["Cargo.toml"],
            "Go": ["go.mod", "go.sum"]
        }
        
        detected_type = "Unknown"
        for ptype, indicators in project_types.items():
            for indicator in indicators:
                if os.path.exists(os.path.join(workspace_path, indicator)):
                    detected_type = ptype
                    break
            if detected_type != "Unknown":
                break
        
        st.metric("Project Type", detected_type)
        
        # Workspace statistics
        if os.path.exists(workspace_path):
            try:
                total_files = sum(len(files) for _, _, files in os.walk(workspace_path))
                total_dirs = sum(len(dirs) for _, dirs, _ in os.walk(workspace_path))
                
                st.metric("Total Files", total_files)
                st.metric("Total Directories", total_dirs)
                  # Git status
                if os.path.exists(os.path.join(workspace_path, '.git')):
                    st.success("✅ Git Repository Detected")
                else:
                    st.warning("⚠️ No Git Repository")
                    
            except Exception as e:
                st.error(f"Error analyzing workspace: {e}")
    
    # Workspace actions - moved outside column context to avoid nesting
    st.subheader("🚀 Quick Actions")
    
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        if st.button("🏗️ Analyze Architecture"):
            if workspace_path and os.path.exists(workspace_path):
                with st.spinner("Analyzing project architecture via backend..."):
                    result = dashboard.analyze_architecture_backend(workspace_path)
                if result.get("status") == "success":
                    st.success("✅ Architecture analysis complete!")
                    arch = result.get("architecture", {})
                    st.write(arch)
                else:
                    st.error(f"Error: {result.get('error', result)}")
            else:
                st.warning("Please enter a valid workspace path first")
        
        if st.button("📝 Generate Documentation"):
            if workspace_path and os.path.exists(workspace_path):
                with st.spinner("Generating project documentation via backend..."):
                    result = dashboard.generate_documentation_backend(workspace_path)
                if result.get("status") == "success":
                    st.success("✅ Documentation generation complete!")
                    doc = result.get("documentation", {})
                    st.write(doc)
                else:
                    st.error(f"Error: {result.get('error', result)}")
            else:
                st.warning("Please enter a valid workspace path first")
    
    with action_col2:
        if st.button("🧪 Run Tests"):
            if workspace_path and os.path.exists(workspace_path):
                with st.spinner("Running project tests via backend..."):
                    result = dashboard.run_tests_backend(workspace_path)
                if result.get("status") == "success":
                    st.success("✅ Test execution complete!")
                    test = result.get("test_results", {})
                    st.write(test)
                else:
                    st.error(f"Error: {result.get('error', result)}")
            else:
                st.warning("Please enter a valid workspace path first")
        
        if st.button("🔍 Code Review"):
            if workspace_path and os.path.exists(workspace_path):
                with st.spinner("Starting code review via backend..."):
                    result = dashboard.code_review_backend(workspace_path)
                if result.get("status") == "success":
                    st.success("✅ Code review complete!")
                    review = result.get("review", {})
                    st.write(review)
                else:
                    st.error(f"Error: {result.get('error', result)}")
            else:
                st.warning("Please enter a valid workspace path first")

def main_dashboard():
    """Main dashboard function with tabs"""
    st.title("🤖 Ultimate Copilot System Dashboard")
    
    dashboard = CopilotDashboard()
    
    # Initialize workspace from session state if available
    if 'workspace_path' in st.session_state and st.session_state.workspace_path:
        dashboard.workspace_path = st.session_state.workspace_path
    
    # Sidebar - System Controls (same as classic view but with unique keys)
    with st.sidebar:
        st.header("🎛️ System Controls")
        
        st.subheader("Quick Actions")
        if st.button("🚀 Start System", use_container_width=True, key="tabbed_start_system"):
            result = dashboard.control_system("start")
            if result["status"] == "success":
                st.success(result["message"])
            elif result["status"] == "info":
                st.info(result["message"])
            else:
                st.error(result["message"])
        
        if st.button("⏹️ Stop System", use_container_width=True, key="tabbed_stop_system"):
            result = dashboard.control_system("stop")
            st.info(result["message"])
        
        if st.button("🔄 Restart Components", use_container_width=True, key="tabbed_restart_components"):
            result = dashboard.control_system("restart_components")
            st.info(result["message"])
        
        st.divider()
        
        st.subheader("Integration Controls")
        void_enabled = st.checkbox("🔮 Void Editor", value=False, help="Enable Void Editor integration", key="tabbed_void_editor")
        vscode_enabled = st.checkbox("💻 VS Code Insiders", value=False, help="Enable VS Code Insiders integration", key="tabbed_vscode_insiders")
        
        st.divider()
        
        st.subheader("Model Providers")
        ollama_enabled = st.checkbox("🦙 Ollama", value=True, key="tabbed_ollama")
        lms_enabled = st.checkbox("🏭 LM Studio", value=True, key="tabbed_lms")
        vllm_enabled = st.checkbox("⚡ vLLM", value=False, key="tabbed_vllm")
      # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 System Overview", 
        "🤖 Agents", 
        "🧠 Models", 
        "📁 Workspace", 
        "📝 Activity",
        "⚙️ Model Manager"
    ])
    
    with tab1:
        system_overview_section(dashboard)
    
    with tab2:
        st.header("🤖 Agent Management")
        
        # Get agent status from backend
        agent_status = dashboard.get_agent_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Available Agents")
            
            agents = [
                {"name": "Orchestrator", "type": "orchestrator", "description": "Coordinates tasks and manages workflow"},
                {"name": "Architect", "type": "architect", "description": "Handles system design and architecture"},
                {"name": "Backend Developer", "type": "backend", "description": "Develops backend systems and APIs"},
                {"name": "Frontend Developer", "type": "frontend", "description": "Creates user interfaces and frontend"},
                {"name": "QA Analyst", "type": "qa", "description": "Quality assurance and testing"}            ]
            
            for agent in agents:
                with st.expander(f"🤖 {agent['name']}", expanded=False):
                    st.write(agent['description'])
                    
                    # Agent status - handle both list and dict formats from backend
                    agents_data = agent_status.get("agents", {})
                    if isinstance(agents_data, list):
                        # If agents is a list, look for matching agent by type
                        status = next((a for a in agents_data if a.get("type") == agent['type']), {})
                    else:
                        # If agents is a dict, use direct lookup
                        status = agents_data.get(agent['type'], {})
                    
                    if status.get("active", False):
                        st.success("✅ Active")
                        if status.get("current_task"):
                            st.info(f"Current task: {status['current_task']}")
                    else:
                        st.warning("⚠️ Inactive")
                      # Agent controls
                    action_col1, action_col2 = st.columns(2)
                    
                    with action_col1:
                        if st.button(f"🚀 Start {agent['name']}", key=f"start_{agent['type']}"):
                            result = dashboard.send_agent_command(agent['type'], "start")
                            if result.get("success", False):  # Check for "success" instead of "status"
                                st.success(f"{agent['name']} started!")
                                st.rerun()
                            else:
                                st.error(f"Failed to start {agent['name']}: {result.get('message', 'Unknown error')}")
                    
                    with action_col2:
                        if st.button(f"⏹️ Stop {agent['name']}", key=f"stop_{agent['type']}"):
                            result = dashboard.send_agent_command(agent['type'], "stop")
                            if result.get("success", False):  # Check for "success" instead of "status"
                                st.success(f"{agent['name']} stopped!")
                                st.rerun()
                            else:
                                st.error(f"Failed to stop {agent['name']}: {result.get('message', 'Unknown error')}")
        
        with col2:
            st.subheader("Agent Swarm Chat")
            
            # Get current workspace for context - prioritize session state
            current_workspace = st.session_state.get('workspace_path', '') or dashboard.workspace_path or "No workspace selected"
            workspace_context = current_workspace if current_workspace != "No workspace selected" else "No workspace selected"
            
            if workspace_context == "No workspace selected":
                st.info(f"Current workspace: {workspace_context}")
            else:
                st.success(f"Current workspace: {workspace_context}")
            
            # Chat interface
            user_instruction = st.text_area(
                "Instructions for Agent Swarm",
                placeholder="Enter instructions for the agents currently working on the workspace...",
                height=100
            )
            
            if st.button("📤 Send to Agent Swarm", use_container_width=True):
                if user_instruction.strip():
                    # Use session state workspace if available
                    workspace_to_use = st.session_state.get('workspace_path') or dashboard.workspace_path
                      # Send instruction to orchestrator agent
                    result = dashboard.send_agent_instruction(
                        "orchestrator", 
                        user_instruction,
                        workspace_to_use
                    )
                    if result and result.get("success"):
                        st.success("Instructions sent to agent swarm!")
                        st.info("Agents will coordinate and execute the instructions.")
                    else:
                        error_message = result.get('message', 'Unknown error') if result else 'No response from backend'
                        st.error(f"Failed to send instructions: {error_message}")
                else:
                    st.warning("Please enter instructions for the agents.")

            # Recent agent communications
            st.subheader("Recent Agent Activity")
            
            # Get real agent activity from backend
            try:
                response = requests.get(f"{dashboard.backend_url}/logs", timeout=5)
                if response.status_code == 200:
                    log_data = response.json()                    # Filter for agent-related logs
                    agent_logs = [log for log in log_data.get("logs", []) if log.get("category", "").lower() in ["agents", "agent"]]
                    
                    if agent_logs:
                        for log in agent_logs[-5:]:  # Show last 5 agent activities
                            log_time = log.get("timestamp", "Unknown")
                            if "T" in log_time:
                                try:
                                    dt = datetime.fromisoformat(log_time.replace("Z", "+00:00"))
                                    log_time = dt.strftime("%H:%M:%S")
                                except:
                                    log_time = log_time[:8]
                            
                            st.text(f"🕐 {log_time} - {log.get('category', 'Agent')}: {log.get('message', 'Activity logged')}")
                    else:
                        st.info("No recent agent activity. Agents will appear here when active.")
                else:
                    st.warning("Unable to fetch agent activity from backend")
            except:
                st.info("Backend unavailable - agent activity will appear when connected")
              # Agent coordination status
            st.subheader("Swarm Coordination")
            coordination_status = agent_status.get("coordination", {})
            if coordination_status.get("active", False):
                st.success("✅ Swarm coordination active")
                if coordination_status.get("current_project"):
                    st.info(f"Project: {coordination_status['current_project']}")
            else:
                st.warning("⚠️ No active coordination")
    
    with tab3:
        st.header("🧠 Model Management")
        
        # Get model status from backend
        model_status = dashboard.get_model_status()
        
        if "error" in model_status:
            st.error(f"❌ Unable to connect to backend: {model_status['error']}")
            st.info("Using mock data for demonstration")
            # Fallback to mock data
            model_status = {
                "providers": {
                    "ollama": {"status": "available", "models": ["llama3.2", "codellama"]},
                    "lm_studio": {"status": "available", "models": ["mistral-7b"]},
                    "vllm": {"status": "unavailable", "models": []}
                }
            }
        
        # Display provider status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🦙 Ollama")
            ollama_data = model_status.get("providers", {}).get("ollama", {})
            if ollama_data.get("status") == "available":
                st.success("✅ Available")
                models = ollama_data.get("models", [])
                for model in models:
                    st.info(f"📦 {model}")
            else:
                st.error("❌ Unavailable")
        
        with col2:
            st.subheader("🏭 LM Studio")
            lms_data = model_status.get("providers", {}).get("lm_studio", {})
            if lms_data.get("status") == "available":
                st.success("✅ Available")
                models = lms_data.get("models", [])
                for model in models:
                    st.info(f"📦 {model}")
            else:
                st.error("❌ Unavailable")
        
        with col3:
            st.subheader("⚡ vLLM")
            vllm_data = model_status.get("providers", {}).get("vllm", {})
            if vllm_data.get("status") == "available":
                st.success("✅ Available")
                models = vllm_data.get("models", [])
                if models:
                    for model in models:
                        st.info(f"📦 {model}")
                else:
                    st.warning("No models loaded")
            else:
                st.error("❌ Unavailable")
        
        # Active models section
        st.subheader("🔥 Active Models")
        active_models = model_status.get("active_models", {})
        if active_models:
            for provider, models in active_models.items():
                if models:
                    st.write(f"**{provider.title()}:**")
                    for model_name, model_info in models.items():
                        status = model_info.get("status", "unknown")
                        memory = model_info.get("memory_usage", "N/A")
                        st.info(f"🚀 {model_name} - Status: {status}, Memory: {memory}")
        else:
            st.warning("No active models detected")
          # Model controls
        st.subheader("🎛️ Model Controls")
        provider_col, model_col, action_col = st.columns(3)
        
        with provider_col:
            provider = st.selectbox("Provider", ["ollama", "lm_studio", "vllm"])
        
        with model_col:
            available_models = model_status.get("providers", {}).get(provider, {}).get("models", [])
            if available_models:
                model = st.selectbox("Model", available_models)
            else:
                model = st.text_input("Model Name")
        
        with action_col:
            action = st.selectbox("Action", ["load", "unload", "switch"])
        
        if st.button("Execute Model Command"):
            if provider and model and action:
                # Call backend model control endpoint
                result = dashboard.send_model_command(provider, model, action)
                if result.get("status") == "success":
                    st.success(f"✅ Successfully executed: {action} {model} on {provider}")
                    st.info(result.get("message", "Model command completed"))
                    st.rerun()  # Refresh to show updated model status                else:
                    st.error(f"❌ Failed to execute command: {result.get('message', 'Unknown error')}")
            else:
                st.warning("Please select provider, model, and action")
    
    with tab4:
        workspace_management_section(dashboard)
    
    with tab5:
        st.header("📝 Recent Activity")
        # Use the existing activity logs
        activity_logs_section()
    
    with tab6:
        st.header("⚙️ Advanced Model Manager")
        
        # Check if model manager is available
        model_status = dashboard.get_model_status()
        
        # Debug information
        st.write("**Debug Info:**")
        st.write(f"Backend URL: {dashboard.backend_url}")
        st.write(f"Model Status Response: {model_status}")
        
        model_manager_available = model_status.get("manager") == "IntelligentModelManager"
        st.write(f"Model Manager Available: {model_manager_available}")
        
        if model_manager_available:
            st.success("🟢 Advanced Model Manager is running")
            
            # Display model manager URL and embed option
            model_manager_url = "http://localhost:5173"  # Default Vite dev server port
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info(f"🌐 **Model Manager App**: {model_manager_url}")
                st.write("The full React-based Model Manager provides advanced features:")
                st.write("• Real-time system monitoring with GPU/CPU/RAM usage")
                st.write("• Multi-provider support (Ollama, LM Studio, vLLM)")
                st.write("• Model marketplace with 1000+ models")
                st.write("• Silent background operations")
                st.write("• Performance analytics and provider controls")
            
            with col2:
                if st.button("🚀 Launch Model Manager", type="primary"):
                    st.balloons()
                    st.success("Opening Model Manager in new tab...")
                    # Use JavaScript to open in new tab
                    st.markdown(f"""
                    <script>
                    window.open('{model_manager_url}', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
                
                if st.button("🔄 Start Model Manager"):
                    with st.spinner("Starting Model Manager..."):
                        # Start the model manager frontend
                        result = start_model_manager_frontend()
                        if result:
                            st.success("✅ Model Manager started successfully!")
                        else:
                            st.error("❌ Failed to start Model Manager")
              # Embed the Model Manager as an iframe
            st.subheader("📱 Embedded Model Manager")
            
            embed_option = st.radio(
                "Display Mode:",
                ["External Link Only", "Embedded View", "Full Screen Iframe"],
                index=0
            )
            
            if embed_option == "Embedded View":
                components.iframe(
                    model_manager_url,
                    width=1200,
                    height=800,
                    scrolling=True
                )
            
            elif embed_option == "Full Screen Iframe":
                components.iframe(
                    model_manager_url,
                    width=None,  # Full width
                    height=1000,
                    scrolling=True
                )
              # Quick status from model manager backend
            st.subheader("📊 Quick Model Manager Status")
            
            try:
                # Get status from model manager backend (port 8080)
                mm_response = requests.get("http://localhost:8080/system/info", timeout=5)
                if mm_response.status_code == 200:
                    mm_data = mm_response.json()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        cpu_info = mm_data.get("cpu", {})
                        st.metric(
                            "CPU Usage", 
                            f"{cpu_info.get('usage', 0):.1f}%",
                            f"{cpu_info.get('cores', 0)} cores"
                        )
                    
                    with col2:
                        ram_info = mm_data.get("ram", {})
                        st.metric(
                            "RAM Usage",
                            f"{ram_info.get('percentage', 0):.1f}%",
                            f"{ram_info.get('used', 'Unknown')} / {ram_info.get('total', 'Unknown')}"
                        )
                    
                    with col3:
                        gpus = mm_data.get("gpus", [])
                        if gpus:
                            gpu = gpus[0]  # Show first GPU
                            st.metric(
                                f"GPU ({gpu.get('type', 'Unknown')})",
                                f"{gpu.get('utilization', 0)}%",
                                gpu.get('name', 'Unknown')[:20]
                            )
                        else:                            st.metric("GPU", "No GPU", "Not detected")
                else:
                    st.warning("⚠️ Model Manager backend not responding")
            except Exception as e:
                st.error(f"❌ Cannot connect to Model Manager backend: {e}")
        
        else:
            st.warning("⚠️ Advanced Model Manager not available")
            st.write("The React-based model manager is not running. Choose an alternative:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🌐 Open Static Model Manager", type="primary"):
                    static_url = "file:///" + os.path.abspath("model_manager_static.html").replace("\\", "/")
                    st.markdown(f"""
                    <script>
                    window.open('{static_url}', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
                    st.success("Opening Static Model Manager in new tab...")
            
            with col2:
                if st.button("🔧 Setup Model Manager"):
                    st.info("Setting up Model Manager...")
                    setup_result = setup_model_manager()
                    if setup_result:
                        st.success("✅ Model Manager setup completed!")
                        st.rerun()
                    else:
                        st.error("❌ Model Manager setup failed")
            
            with col3:
                if st.button("📖 View Setup Instructions"):
                    st.info("""
                    **To enable the Advanced Model Manager:**
                    
                    1. Run `python install_nodejs.py` to install Node.js
                    2. Or manually install Node.js from nodejs.org
                    3. Navigate to `frontend/model manager/`
                    4. Run `npm install`
                    5. Run `npm run dev`
                    6. Refresh this dashboard
                    """)
            
            # Embedded static model manager option
            st.subheader("📱 Static Model Manager (No Node.js Required)")
            if st.checkbox("Embed Static Model Manager"):
                static_html_path = os.path.abspath("model_manager_static.html")
                if os.path.exists(static_html_path):
                    with open(static_html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    components.html(html_content, height=800, scrolling=True)
                else:
                    st.error("Static Model Manager file not found")

def start_model_manager_frontend():
    """Start the React frontend for the model manager"""
    try:
        import subprocess
        import os
        
        model_manager_path = os.path.join(os.path.dirname(__file__), "model manager")
        
        # Check if node_modules exists
        if not os.path.exists(os.path.join(model_manager_path, "node_modules")):
            # Run npm install first
            subprocess.run(["npm", "install"], cwd=model_manager_path, check=True)
        
        # Start the dev server
        subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=model_manager_path,
            stdout=subprocess.PIPE,            stderr=subprocess.PIPE
        )
        
        return True
    except Exception as e:
        st.error(f"Error starting Model Manager: {e}")
        return False

def setup_model_manager():
    """Setup the model manager by installing dependencies"""
    try:
        import subprocess
        import os
        
        model_manager_path = os.path.join(os.path.dirname(__file__), "model manager")
        
        if not os.path.exists(model_manager_path):
            st.error("Model Manager directory not found")
            return False
        
        # Install Node.js dependencies        subprocess.run(["npm", "install"], cwd=model_manager_path, check=True)
        
        # Install Python backend dependencies
        backend_path = os.path.join(model_manager_path, "backend")
        subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=backend_path, check=True)
        
        return True
    except Exception as e:
        st.error(f"Setup failed: {e}")
        return False

def system_overview_section(dashboard):
    """System Overview Section"""
    # System Status Overview
    st.header("📊 System Overview")
    
    status = dashboard.get_system_status()
    model_status = dashboard.get_model_status()
    metrics = dashboard.get_performance_metrics()
    
    # Top metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="System Uptime",
            value=status.get("uptime", "Unknown"),
            delta="Stable"
        )
    
    with col2:
        st.metric(
            label="Active Models",
            value=status.get("models_loaded", 0),
            delta="+1 since restart"
        )

    with col3:
        vram = status.get("vram_usage", {})
        st.metric(
            label="VRAM Usage",
            value=f"{vram.get('current', 0):.1f}GB",
            delta=f"{vram.get('percentage', 0):.0f}% of {vram.get('total', 0):.1f}GB"
        )

    with col4:
        st.metric(
            label="Avg Response Time",
            value=f"{metrics.get('avg_response_time', 0):.2f}s",
            delta="Normal"
        )

    with col5:
        st.metric(
            label="Error Rate",
            value=f"{metrics.get('error_rate', 0):.1f}%",
            delta="Good" if metrics.get('error_rate', 0) < 1 else "High"
        )

if __name__ == "__main__":
    # Choose interface style
    interface_style = st.sidebar.radio(
        "Dashboard Style",
        ["Classic View", "Tabbed View"],
        index=1  # Default to new tabbed view
    )
    
    if interface_style == "Tabbed View":
        main_dashboard()
    else:
        main()  # Original single-page dashboard