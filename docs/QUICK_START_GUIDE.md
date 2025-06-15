# Ultimate Copilot System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
# Navigate to the project directory
cd ultimate_copilot

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Configure the System
```bash
# Copy example configurations
copy config\system_config.yaml.example config\system_config.yaml
copy config\hybrid_config.yaml.example config\hybrid_config.yaml

# Edit configurations as needed (optional for basic usage)
```

### Step 3: Choose Your Launch Method

#### Option A: Simple Start (Recommended for First Time)
```bash
# Windows
start.bat

# Or directly with Python
python main.py
```

#### Option B: With Dashboard Monitoring
```bash
# Start dashboard first (opens in browser)
python start_dashboard.py

# In another terminal, start the main system
python main.py
```

#### Option C: Hybrid Mode (CodeGPT + Custom Agents)
```bash
# Set CodeGPT credentials (optional)
set CODEGPT_API_KEY=your_key_here
set CODEGPT_ORG_ID=your_org_id_here

# Start hybrid system
python main_hybrid.py
```

### Step 4: Verify Installation

1. **Check System Status**: Look for "System Online" messages in the console
2. **Access Dashboard**: Open http://localhost:8501 in your browser (if started)
3. **Test Local Models**: System will automatically detect Ollama/LM Studio if running

## 🎯 What You Get Out of the Box

### ✅ Immediate Features
- **Multi-Agent Orchestration**: 5 specialized AI agents ready to work
- **8GB VRAM Optimization**: Intelligent model management for resource-constrained systems
- **Local Model Support**: Works with Ollama, LM Studio, vLLM
- **Real-time Monitoring**: Dashboard showing system performance and agent status
- **Void Editor Integration**: Priority integration for advanced development workflows

### 🔧 System Requirements Met
- **No Subscription Costs**: Unlimited local execution
- **Resource Efficient**: Optimized for 8GB VRAM systems
- **Cross-Platform**: Windows (primary), Linux, macOS support
- **Extensible**: Plugin architecture for custom agents and integrations

## 🛠️ Common First-Time Setup

### If You Have Ollama Installed
```bash
# The system will automatically detect and use your Ollama models
# Recommended models for best performance:
ollama pull llama3
ollama pull codellama
ollama pull mistral
```

### If You Have LM Studio
```bash
# Make sure LM Studio is running on localhost:1234
# The system will automatically detect available models
```

### If You Want Cloud Fallbacks
```bash
# Set API keys for cloud providers (optional)
set OPENAI_API_KEY=your_openai_key
set ANTHROPIC_API_KEY=your_anthropic_key
```

## 📊 Verify Everything is Working

### Check 1: System Status
Look for these messages in the console:
```
[INFO] Enhanced Ultimate Copilot System started successfully
[INFO] Void Editor integration active (Priority 1)
[INFO] Enhanced Agent Manager initialized with VRAM optimization
```

### Check 2: Dashboard Access
1. Open http://localhost:8501
2. Should see "System Online" status
3. VRAM usage should show current models loaded

### Check 3: Agent Status
In the dashboard, verify:
- **Active Models**: 1-2 models loaded
- **VRAM Usage**: Under 80% for optimal performance
- **Integration Status**: Void Editor connection status

## 🎉 You're Ready!

Your Ultimate Copilot System is now running with:
- **Unlimited AI Usage**: No subscription fees or request limits
- **Intelligent Resource Management**: Optimized for your hardware
- **Advanced Agent Coordination**: Multi-agent workflows ready
- **Editor Integration**: Seamless development environment support

## 🔄 Next Steps

1. **Explore the Dashboard**: Monitor system performance and agent activity
2. **Try Agent Tasks**: Use the orchestrator to coordinate complex workflows
3. **Configure Integrations**: Set up Void Editor or VS Code Insiders integration
4. **Customize Agents**: Add your own specialized agents using the plugin system

## 🆘 Need Help?

- **Logs**: Check `logs/system.log` for detailed information
- **Status**: Use `start.bat` option 5 to check system status
- **Documentation**: See `docs/` directory for detailed guides
- **Configuration**: Review example config files for customization options

---

**Welcome to the Ultimate Copilot System - Your unlimited AI development assistant!**