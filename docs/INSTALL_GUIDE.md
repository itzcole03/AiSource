# Ultimate Copilot System - Clean Installation Guide

## 📁 Project Structure

The Ultimate Copilot System has been organized into a clean, modular structure:

```
ultimate_copilot/
├── main.py                 # Primary system launcher
├── main_hybrid.py          # Hybrid system with CodeGPT integration
├── start_dashboard.py      # Dashboard launcher
├── start.bat              # Windows launcher with menu
├── requirements.txt       # Python dependencies
├── README.md             # Main documentation
│
├── core/                  # Core system components
│   ├── enhanced_system_manager.py    # Central orchestration
│   ├── enhanced_llm_manager.py       # Multi-provider LLM management
│   ├── advanced_memory_manager.py    # Vector memory with Qdrant
│   ├── agent_manager.py              # Agent lifecycle management
│   ├── vram_manager.py               # 8GB VRAM optimization
│   └── plugin_system.py              # Plugin architecture
│
├── agents/                # AI Agent implementations
│   ├── base_agent.py               # Foundation agent class
│   ├── orchestrator_agent.py       # Task coordination
│   ├── architect_agent.py          # System architecture
│   ├── backend_agent.py            # Backend development
│   ├── frontend_agent.py           # Frontend development
│   └── qa_agent.py                 # Quality assurance
│
├── integrations/          # Editor and platform integrations
│   ├── vscode_integration.py       # VS Code/Insiders support
│   ├── void_integration.py         # Void Editor integration
│   └── codegpt_bridge.py           # CodeGPT platform bridge
│
├── config/                # Configuration files
│   ├── system_config.yaml          # Main system settings
│   ├── hybrid_config.yaml          # Hybrid system settings
│   └── models_config.yaml          # Model configurations
│
├── frontend/              # User interfaces
│   └── dashboard.py               # Streamlit monitoring dashboard
│
├── utils/                 # Utility functions
│   ├── logger.py                  # Logging configuration
│   └── config.py                  # Configuration management
│
├── docs/                  # Documentation
│   ├── UPDATED_RECOMMENDATION.md   # Latest strategy recommendation
│   ├── FINAL_IMPLEMENTATION_SUMMARY.md
│   └── CODEGPT_VS_CUSTOM_ANALYSIS.md
│
├── logs/                  # System logs (auto-created)
└── memory/                # Persistent memory (auto-created)
```

## 🚀 Quick Start

### Method 1: Use the Launcher (Recommended)
1. Navigate to the `ultimate_copilot` directory
2. Double-click `start.bat` (Windows) or run it from command line
3. Choose option 1 for the main system

### Method 2: Direct Python Execution
```bash
cd ultimate_copilot
pip install -r requirements.txt
python main.py
```

### Method 3: With Dashboard
```bash
cd ultimate_copilot
pip install -r requirements.txt
python start.bat  # Choose option 2
# Or manually:
python start_dashboard.py &
python main.py
```

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **Memory**: 8GB+ RAM (optimized for 8GB VRAM systems)
- **OS**: Windows 10/11 (primary), Linux/macOS (supported)
- **Optional**: Ollama, LM Studio, or vLLM for local models

## 📋 Dependencies

All dependencies are listed in `requirements.txt`:

```
fastapi>=0.104.0
uvicorn>=0.24.0
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
pyyaml>=6.0
python-dotenv>=1.0.0
huggingface-hub>=0.17.0
sentence-transformers>=2.2.0
aiohttp>=3.9.0
requests>=2.31.0
qdrant-client>=1.6.0
aiofiles>=23.2.1
watchdog>=3.0.0
websockets>=11.0.2
psutil>=5.9.0
gputil>=1.4.0
```

## 🎯 Key Features

### ✅ **Unlimited Local Usage**
- No subscription fees or usage limits
- Supports Ollama, LM Studio, vLLM
- Cloud provider fallbacks (OpenAI, Anthropic, Google)

### ✅ **8GB VRAM Optimization**
- Intelligent model rotation
- Memory-aware task scheduling
- Aggressive cleanup strategies
- Performance monitoring

### ✅ **Multi-Agent Orchestration**
- Task decomposition and delegation
- Inter-agent communication
- Workflow automation
- Progress tracking

### ✅ **Editor Integration**
- Void Editor prioritization
- VS Code Insiders swarm automation
- Real-time file synchronization
- Advanced debugging support

### ✅ **Real-time Monitoring**
- Streamlit dashboard
- Performance metrics
- System health monitoring
- Resource utilization tracking

## 🔄 Migration from Original Structure

If you have files in the original scattered structure, you can:

1. **Use the new clean structure**: Recommended for new setups
2. **Gradually migrate**: Copy important configs and customizations
3. **Dual setup**: Keep both for testing and comparison

## 💡 Usage Tips

### For Development Work
- Use the main system (`main.py`) for unlimited local execution
- Access dashboard at `http://localhost:8501` for monitoring
- Customize agents in the `agents/` directory

### For CodeGPT Integration (Optional)
- Set `CODEGPT_API_KEY` and `CODEGPT_ORG_ID` environment variables
- Use `main_hybrid.py` for hybrid execution
- Note: Requires paid CodeGPT subscription for meaningful usage

### For Configuration
- Edit `config/system_config.yaml` for main settings
- Edit `config/hybrid_config.yaml` for CodeGPT integration
- All configs support environment variable substitution

## 🛟 Troubleshooting

### Common Issues
1. **Import errors**: Ensure you're running from the `ultimate_copilot` directory
2. **Missing packages**: Run `pip install -r requirements.txt`
3. **Permission errors**: Run as administrator on Windows if needed
4. **Port conflicts**: Dashboard uses port 8501, system APIs use 8000

### Getting Help
- Check the `logs/` directory for detailed error information
- Use the system status option in `start.bat` for diagnostics
- Review documentation in the `docs/` directory

---

**The Ultimate Copilot System provides enterprise-grade AI development assistance with unlimited local usage, advanced multi-agent orchestration, and seamless editor integration - all without subscription costs.**
