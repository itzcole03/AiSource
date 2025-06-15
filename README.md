# Hybrid Ultimate Copilot System

A revolutionary AI-powered development assistant that combines the best of custom agent orchestration with CodeGPT's platform capabilities.

## 🌟 Key Features

### Hybrid Architecture
- **Custom Agents**: Advanced multi-agent orchestration for complex workflows
- **CodeGPT Integration**: Leverage CodeGPT's mature platform for simple tasks
- **Intelligent Routing**: Automatically routes tasks to the best agent system
- **8GB VRAM Optimization**: Designed for resource-constrained environments

### Multi-Agent Coordination
- **Orchestrator Agent**: Manages complex project workflows
- **Specialized Agents**: Architect, Backend Dev, Frontend Dev, QA Analyst
- **Task Delegation**: Intelligent task breakdown and assignment
- **Progress Monitoring**: Real-time project tracking and coordination

### Editor Integrations
- **Void Editor Priority**: Primary integration for advanced development
- **VS Code Insiders**: Swarm automation and lead developer mode
- **CodeGPT Extension**: Seamless integration with CodeGPT platform

### Advanced Features
- **Real-time Dashboard**: Monitor system performance and agent status
- **Memory Management**: Persistent knowledge across sessions
- **Model Optimization**: Dynamic model switching for optimal performance
- **Plugin Architecture**: Extensible system with custom plugins

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- 8GB+ RAM (optimized for 8GB VRAM systems)
- Windows 10/11 (primary), Linux/macOS (supported)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ultimate-copilot-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the system**
   ```bash
   # Copy and edit configuration files
   copy config\system_config.yaml.example config\system_config.yaml
   copy config\hybrid_config.yaml.example config\hybrid_config.yaml
   ```

4. **Set up CodeGPT integration (optional)**
   ```bash
   # Set environment variables
   set CODEGPT_API_KEY=your_api_key_here
   set CODEGPT_ORG_ID=your_org_id_here
   ```

### Launch Options

#### Option 1: Hybrid System (Recommended)
```bash
# Windows
start_hybrid_system.bat

# Or directly with Python
python main_hybrid.py
```

#### Option 2: Custom Agents Only
```bash
python main_void_priority.py
```

#### Option 3: With Dashboard
```bash
# Start dashboard first
python start_dashboard.py

# Then start the main system
python main_hybrid.py
```

## 🤖 Agent Types

### Custom Agents
- **Orchestrator**: Coordinates complex workflows and manages task delegation
- **Architect**: Designs system architecture and technical specifications
- **Backend Developer**: Handles server-side development and APIs
- **Frontend Developer**: Manages UI/UX and client-side implementation
- **QA Analyst**: Performs testing, quality assurance, and code review

### CodeGPT Agents
- **Code Reviewer**: Specialized in code quality analysis and security
- **Documentation Writer**: Expert at creating technical documentation
- **Q&A Assistant**: Quick answers and explanations for development questions

## 🔧 Configuration

### Hybrid Configuration (`config/hybrid_config.yaml`)

```yaml
# CodeGPT Integration
codegpt:
  enabled: true
  api_key: "${CODEGPT_API_KEY}"
  org_id: "${CODEGPT_ORG_ID}"

# Task Routing
routing:
  codegpt_tasks:
    - "code_review"
    - "documentation"
    - "quick_questions"
  
  custom_tasks:
    - "project_orchestration"
    - "workflow_automation"
    - "system_integration"

# Editor Integrations
integration:
  void_editor:
    enabled: true
    priority: 1
  vscode_insiders:
    enabled: true
    swarm_mode: true
```

### System Configuration (`config/system_config.yaml`)

```yaml
# LLM Providers
llm_providers:
  ollama:
    enabled: true
    base_url: "http://localhost:11434"
  
  lm_studio:
    enabled: true
    base_url: "http://localhost:1234"

# Memory Management
memory:
  provider: "qdrant"
  host: "localhost"
  port: 6333

# VRAM Optimization
vram:
  max_usage_gb: 7.5
  enable_model_rotation: true
  aggressive_cleanup: true
```

## 📊 Dashboard

Access the real-time dashboard at `http://localhost:8501` to monitor:

- System performance metrics
- Agent status and workload
- Task execution history
- Resource utilization
- Integration status

## 🔌 Integrations

### Void Editor
- Primary development environment integration
- Real-time file synchronization
- Advanced project management
- Custom workflow automation

### VS Code Insiders
- Swarm automation capabilities
- Lead developer mode
- Advanced debugging integration
- Multi-project coordination

### CodeGPT Platform
- Agent marketplace access
- Enterprise-grade security
- Advanced AI model access
- Community-driven agents

## 🛠️ Development

### Adding Custom Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods: `agent_initialize`, `process_task`
3. Register agent in `agent_manager.py`
4. Update routing configuration

### Creating CodeGPT Agents

1. Access CodeGPT Studio
2. Create specialized agent with custom instructions
3. Add agent ID to `hybrid_config.yaml`
4. Configure routing rules

### Plugin Development

See `docs/PLUGIN_DEVELOPMENT.md` for detailed plugin development guide.

## 📈 Performance Optimization

### 8GB VRAM Systems
- Automatic model rotation
- Memory-aware task scheduling
- Intelligent resource allocation
- Performance monitoring and alerts

### Scaling Considerations
- Horizontal agent scaling
- Load balancing across providers
- Distributed memory management
- Performance profiling and optimization

## 🔒 Security

- Environment variable configuration
- Secure API key management
- Local model execution
- Zero data retention options
- SOC2 Type II compliance (CodeGPT)

## 🐛 Troubleshooting

### Common Issues

1. **CodeGPT API Connection Failed**
   - Verify API key and org ID
   - Check network connectivity
   - Ensure sufficient API quotas

2. **High VRAM Usage**
   - Enable aggressive cleanup
   - Reduce concurrent model loading
   - Configure model rotation

3. **Integration Not Working**
   - Check editor installation
   - Verify configuration files
   - Review log files in `logs/` directory

### Debug Mode
```bash
# Enable debug logging
set LOG_LEVEL=DEBUG
python main_hybrid.py
```

## 📚 Documentation

- [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- CodeGPT platform for AI agent infrastructure
- Ollama for local model execution
- Qdrant for vector database capabilities
- VS Code and Void Editor teams for integration support

---

**Hybrid Ultimate Copilot System** - Where custom orchestration meets platform excellence.
