# Ultimate Copilot - Startup Options Guide

## 🚀 Available Batch Files

### Quick Start Options

#### 1. `quick_launch.bat` - Fastest Start
```cmd
quick_launch.bat
```
- **Best for**: Quick access to the universal launcher
- **What it does**: 
  - Checks dependencies
  - Installs missing packages automatically
  - Launches the universal dashboard launcher with menu options
- **Time**: ~5 seconds

#### 2. `start_everything.bat` - Complete System
```cmd
start_everything.bat
```
- **Best for**: Full system startup with all interfaces
- **What it does**:
  - Starts API server on port 8001
  - Opens console dashboard
  - Opens GUI dashboard  
  - Opens universal launcher
  - Opens web interfaces in browser
- **Time**: ~15 seconds

### Advanced Options

#### 3. `start_enhanced_system.bat` - Interactive Menu
```cmd
start_enhanced_system.bat
```
- **Best for**: Choosing specific services to start
- **Features**:
  - Interactive menu with 9 options
  - Selective service startup
  - Dependency management
  - System status checks
- **Options**:
  1. Quick Start - Universal Launcher
  2. Full System - All Services  
  3. API Server Only
  4. Console Dashboard Only
  5. GUI Dashboard Only
  6. Web Interface Setup
  7. Development Mode (All + Logs)
  8. System Status Check
  9. Install/Update Dependencies

#### 4. `developer_tools.bat` - Development Environment
```cmd
developer_tools.bat
```
- **Best for**: Developers and advanced users
- **Features**:
  - Development mode with debug logging
  - Integration testing
  - Performance monitoring
  - System health checks
  - Log viewing
  - Code quality checks
  - Backup utilities
- **Options**:
  1. Start All Services (Dev Mode)
  2. Run Integration Tests
  3. Check System Health
  4. View Logs & Diagnostics
  5. Performance Test
  6. Reset System State
  7. Dependency Analysis
  8. Code Quality Check
  9. Backup Current State

## 🎯 Which One Should You Use?

### For Regular Use:
- **New users**: `start_everything.bat` - Gets everything running immediately
- **Quick access**: `quick_launch.bat` - Fast universal launcher
- **Specific needs**: `start_enhanced_system.bat` - Choose what you need

### For Development:
- **Development work**: `developer_tools.bat` - Full dev environment
- **Testing**: `start_enhanced_system.bat` → Option 7 (Development Mode)
- **Debugging**: `developer_tools.bat` → Options 3-4 (Health & Logs)

## 📊 Services Overview

When fully started, you'll have access to:

### 🌐 Web Interfaces
- **API Documentation**: http://127.0.0.1:8001/docs
- **Enhanced Dashboard**: enhanced_dashboard.html
- **API Health Check**: http://127.0.0.1:8001/health

### 💻 Desktop Interfaces  
- **Console Dashboard**: Interactive command-line interface
- **GUI Dashboard**: Tkinter-based desktop application
- **Universal Launcher**: Menu-driven launcher system

### 🔧 Background Services
- **FastAPI Server**: REST API on port 8001
- **Agent System**: Enhanced memory-aware agents
- **Status Monitor**: Real-time system monitoring

## ⚡ Quick Commands

### Start Everything (Recommended for most users):
```cmd
start_everything.bat
```

### Quick Access Menu:
```cmd
quick_launch.bat
```

### Development Environment:
```cmd
developer_tools.bat
```

### Custom Setup:
```cmd
start_enhanced_system.bat
```

## 🛠️ Troubleshooting

### If services don't start:
1. Run `start_enhanced_system.bat` → Option 9 (Install Dependencies)
2. Check `developer_tools.bat` → Option 3 (System Health)
3. View logs with `developer_tools.bat` → Option 4 (View Logs)

### Common issues:
- **Port 8001 in use**: Close other applications or restart computer
- **Import errors**: Run dependency installation
- **GUI doesn't open**: Check if tkinter is available

### System Requirements:
- Python 3.8+
- Windows PowerShell
- 4GB+ RAM recommended  
- Internet connection for initial setup

## 📱 Interface Features

### Universal Launcher
- Auto-detects available components
- Smart dependency management
- Graceful fallbacks when components unavailable
- Interactive menu system

### API Server
- FastAPI with auto-generated documentation
- Real-time agent status monitoring
- RESTful endpoints for all operations
- Health checks and diagnostics

### Console Dashboard
- Real-time command interface
- Agent memory management
- Task execution and history
- System status monitoring

### GUI Dashboard
- Modern Tkinter interface
- Visual system status
- Point-and-click operation
- Integrated controls

## 🔄 Updates and Maintenance

### Regular maintenance:
```cmd
developer_tools.bat → Option 7 (Dependency Analysis)
developer_tools.bat → Option 9 (Backup Current State)
```

### Performance monitoring:
```cmd
developer_tools.bat → Option 5 (Performance Test)
```

### System cleanup:
```cmd
developer_tools.bat → Option 6 (Reset System State)
```

---

**Need help?** Run any `.bat` file and follow the on-screen instructions. All interfaces include built-in help and status information.
