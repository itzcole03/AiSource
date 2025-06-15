# Ultimate Copilot System - API Reference

## 🚀 Overview

The Ultimate Copilot System provides multiple APIs for integration and extensibility:

1. **REST API** - HTTP endpoints for external integrations
2. **WebSocket API** - Real-time communication with editors
3. **Python API** - Direct integration for Python applications
4. **Plugin API** - Extension development interface

## 🌐 REST API

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
```http
# Bearer token authentication
Authorization: Bearer your-api-token
```

### Core Endpoints

#### System Status
```http
GET /status
```
**Response:**
```json
{
  "status": "running",
  "version": "1.0.0",
  "uptime": 3600,
  "vram_usage": 75.2,
  "active_agents": 3,
  "models_loaded": ["llama3.2:3b", "codellama:7b"]
}
```

#### Agent Chat
```http
POST /agents/{agent_type}/chat
```
**Parameters:**
- `agent_type`: orchestrator, architect, backend, frontend, qa

**Request:**
```json
{
  "message": "Create a REST API endpoint for user management",
  "context": {
    "project_type": "python-fastapi",
    "files": ["main.py", "models.py"],
    "preferences": {
      "style": "async",
      "database": "postgresql"
    }
  },
  "stream": true
}
```

**Response:**
```json
{
  "id": "chat-123",
  "agent": "backend",
  "response": "I'll help you create a REST API endpoint...",
  "code_suggestions": [
    {
      "file": "routes/users.py",
      "content": "from fastapi import APIRouter...",
      "type": "create"
    }
  ],
  "metadata": {
    "model_used": "codellama:7b",
    "processing_time": 2.3,
    "tokens_used": 150
  }
}
```

#### File Operations
```http
POST /files/analyze
```
**Request:**
```json
{
  "file_path": "/path/to/file.py",
  "analysis_type": "code_review",
  "options": {
    "include_suggestions": true,
    "check_performance": true,
    "security_scan": true
  }
}
```

#### Model Management
```http
GET /models
POST /models/{model_name}/load
DELETE /models/{model_name}/unload
GET /models/stats
```

#### VRAM Monitoring
```http
GET /vram/usage
GET /vram/history
POST /vram/optimize
```

### WebSocket API

#### Connection
```javascript
const ws = new WebSocket('ws://localhost:8765/ws');
```

#### Message Format
```json
{
  "type": "message_type",
  "id": "unique-id",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {}
}
```

#### Message Types

##### File Synchronization
```json
{
  "type": "file_sync",
  "id": "sync-123",
  "data": {
    "action": "update",
    "file_path": "/workspace/main.py",
    "content": "print('Hello World')",
    "cursor_position": 15,
    "selection": {"start": 0, "end": 15}
  }
}
```

##### AI Assistance Request
```json
{
  "type": "ai_request",
  "id": "ai-456",
  "data": {
    "agent": "backend",
    "request": "Explain this function",
    "context": {
      "code": "def process_data(data): ...",
      "language": "python",
      "file_path": "/workspace/utils.py"
    }
  }
}
```

##### Real-time Notifications
```json
{
  "type": "notification",
  "id": "notif-789",
  "data": {
    "level": "info",
    "message": "Model codellama:7b loaded successfully",
    "category": "model_management"
  }
}
```

## 🐍 Python API

### Core System Access
```python
from core.enhanced_system_manager import EnhancedSystemManager
from agents.orchestrator_agent import OrchestratorAgent

# Initialize system
system = EnhancedSystemManager()
await system.initialize()

# Get orchestrator
orchestrator = system.get_agent('orchestrator')

# Send request
response = await orchestrator.process_request(
    message="Create a new FastAPI endpoint",
    context={
        "project_type": "python-web",
        "framework": "fastapi"
    }
)
```

### Agent Direct Access
```python
from agents.backend_agent import BackendAgent

# Create agent instance
agent = BackendAgent()
await agent.initialize()

# Process request
result = await agent.process_request(
    request="Generate a database model for users",
    context={
        "orm": "sqlalchemy",
        "database": "postgresql"
    }
)

print(result.code_suggestions)
print(result.explanation)
```

### LLM Manager
```python
from core.enhanced_llm_manager import EnhancedLLMManager

# Initialize LLM manager
llm_manager = EnhancedLLMManager()
await llm_manager.initialize()

# Get response from specific model
response = await llm_manager.get_response(
    prompt="Explain async/await in Python",
    model="codellama:7b",
    provider="ollama"
)

# Auto-select best model
response = await llm_manager.get_best_response(
    prompt="Design a microservices architecture",
    task_type="architecture",
    complexity="high"
)
```

### VRAM Manager
```python
from core.vram_manager import VRAMManager

# Monitor VRAM
vram = VRAMManager()

# Get current usage
usage = vram.get_usage_percentage()
available = vram.get_available_memory()

# Check if model can be loaded
can_load = vram.can_load_model("codellama:13b")

# Force cleanup if needed
if usage > 85:
    vram.cleanup_models()
```

### Memory Manager
```python
from core.advanced_memory_manager import AdvancedMemoryManager

# Initialize memory
memory = AdvancedMemoryManager()
await memory.initialize()

# Store conversation
await memory.store_conversation(
    session_id="user-123",
    messages=[
        {"role": "user", "content": "How do I create a REST API?"},
        {"role": "assistant", "content": "Here's how to create a REST API..."}
    ]
)

# Search similar conversations
similar = await memory.search_similar(
    query="REST API creation",
    limit=5
)
```

## 🔌 Plugin API

### Plugin Structure
```python
from core.plugin_system import BasePlugin

class MyCustomPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="my-plugin",
            version="1.0.0",
            description="Custom functionality"
        )
    
    async def initialize(self):
        """Initialize plugin resources"""
        pass
    
    async def process_request(self, request):
        """Handle plugin-specific requests"""
        return {"result": "processed"}
    
    def get_endpoints(self):
        """Return REST endpoints"""
        return [
            {
                "path": "/plugins/my-plugin/action",
                "method": "POST",
                "handler": self.handle_action
            }
        ]
    
    async def handle_action(self, request):
        """Handle custom endpoint"""
        return {"status": "success"}
```

### Plugin Registration
```python
# plugins/my_plugin/__init__.py
from .main import MyCustomPlugin

def register_plugin():
    return MyCustomPlugin()
```

### Plugin Manifest
```json
{
  "name": "my-custom-plugin",
  "version": "1.0.0",
  "description": "Custom plugin for Ultimate Copilot",
  "author": "Your Name",
  "license": "MIT",
  "main": "main.py",
  "dependencies": [
    "requests>=2.31.0"
  ],
  "permissions": [
    "file_access",
    "network_access",
    "model_access"
  ],
  "endpoints": [
    "/plugins/my-plugin/*"
  ],
  "hooks": [
    "before_agent_request",
    "after_model_load"
  ]
}
```

## 🎯 Integration Examples

### VS Code Extension
```typescript
import * as vscode from 'vscode';

class UltimateCopilotClient {
    private ws: WebSocket;
    
    constructor() {
        this.ws = new WebSocket('ws://localhost:8765/ws');
        this.setupEventHandlers();
    }
    
    async getCodeSuggestion(code: string, context: any) {
        return new Promise((resolve) => {
            const request = {
                type: 'ai_request',
                id: Date.now().toString(),
                data: {
                    agent: 'backend',
                    request: 'improve this code',
                    context: { code, ...context }
                }
            };
            
            this.ws.send(JSON.stringify(request));
            
            this.ws.onmessage = (event) => {
                const response = JSON.parse(event.data);
                if (response.id === request.id) {
                    resolve(response.data);
                }
            };
        });
    }
}
```

### Void Editor Integration
```javascript
class VoidCopilotIntegration {
    constructor() {
        this.connect();
    }
    
    connect() {
        this.socket = new WebSocket('ws://localhost:8765/ws');
        
        this.socket.onopen = () => {
            console.log('Connected to Ultimate Copilot');
            this.registerEditor();
        };
        
        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
    }
    
    registerEditor() {
        this.send({
            type: 'editor_register',
            data: {
                editor: 'void',
                version: '1.0.0',
                capabilities: ['file_sync', 'ai_assistance']
            }
        });
    }
    
    syncFile(filePath, content) {
        this.send({
            type: 'file_sync',
            data: {
                action: 'update',
                file_path: filePath,
                content: content
            }
        });
    }
}
```

### CLI Tool
```bash
# ultimatecopilot CLI
ultimatecopilot chat "How do I optimize this code?"
ultimatecopilot analyze file.py --agent backend
ultimatecopilot models list
ultimatecopilot vram status
ultimatecopilot start --config custom.yaml
```

```python
# CLI implementation
import click
import asyncio
from core.enhanced_system_manager import EnhancedSystemManager

@click.group()
def cli():
    """Ultimate Copilot CLI"""
    pass

@cli.command()
@click.argument('message')
@click.option('--agent', default='orchestrator')
async def chat(message, agent):
    """Chat with an agent"""
    system = EnhancedSystemManager()
    await system.initialize()
    
    agent_instance = system.get_agent(agent)
    response = await agent_instance.process_request(message)
    
    click.echo(response.content)

if __name__ == '__main__':
    cli()
```

## 📊 Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VRAM_INSUFFICIENT",
    "message": "Not enough VRAM to load model",
    "details": {
      "required_vram": "8GB",
      "available_vram": "6.2GB",
      "suggested_action": "unload_models"
    },
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Error Codes
- `VRAM_INSUFFICIENT` - Not enough VRAM for operation
- `MODEL_NOT_FOUND` - Requested model not available
- `AGENT_BUSY` - Agent is processing another request
- `INVALID_REQUEST` - Request format is invalid
- `PROVIDER_UNAVAILABLE` - LLM provider is not accessible
- `CONFIG_ERROR` - Configuration file error
- `PERMISSION_DENIED` - Insufficient permissions
- `RATE_LIMITED` - Too many requests

## 🔒 Security

### API Authentication
```python
# Generate API token
from utils.auth import generate_api_token

token = generate_api_token(
    user_id="user-123",
    permissions=["chat", "file_read", "model_access"],
    expires_in=3600  # 1 hour
)
```

### Request Validation
```python
# Validate requests
from utils.validation import validate_request

@validate_request({
    "message": {"type": "string", "max_length": 10000},
    "agent": {"type": "string", "enum": ["orchestrator", "backend", "frontend"]},
    "context": {"type": "object", "optional": True}
})
async def chat_endpoint(request):
    # Process validated request
    pass
```

### Rate Limiting
```yaml
# config/system_config.yaml
security:
  rate_limiting:
    enabled: true
    requests_per_minute: 60
    burst_limit: 10
  
  api_keys:
    required: true
    expiration: 3600
```

## 📚 SDKs and Libraries

### Python SDK
```bash
pip install ultimate-copilot-sdk
```

```python
from ultimate_copilot import Client

client = Client(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Chat with agent
response = await client.chat(
    agent="backend",
    message="Create a user model"
)

# File operations
analysis = await client.analyze_file("main.py")
```

### Node.js SDK
```bash
npm install ultimate-copilot-js
```

```javascript
const { UltimateCopilot } = require('ultimate-copilot-js');

const client = new UltimateCopilot({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key'
});

// Chat with agent
const response = await client.chat({
    agent: 'frontend',
    message: 'Create a React component'
});
```

This API reference provides comprehensive documentation for integrating with the Ultimate Copilot System. For more examples and detailed implementation guides, see the `examples/` directory in the repository.
