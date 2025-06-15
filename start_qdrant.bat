@echo off
REM Qdrant Vector Database Startup Script for Windows
REM Qdrant is needed for advanced agent memory and vector search

echo 🗃️ Starting Qdrant Vector Database...

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found. Please install Docker Desktop for Windows.
    echo 📥 Download from: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Check if Qdrant container exists
docker ps -a --format "table {{.Names}}" | findstr "qdrant" >nul 2>&1
if %errorlevel% equ 0 (
    echo 🔄 Qdrant container exists, starting...
    docker start qdrant
) else (
    echo 📦 Creating new Qdrant container...
    
    REM Create data directory
    if not exist "data\qdrant_storage" mkdir data\qdrant_storage
    
    REM Run Qdrant container
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v "%cd%\data\qdrant_storage:/qdrant/storage" qdrant/qdrant:latest
)

REM Wait for Qdrant to be ready
echo ⏳ Waiting for Qdrant to start...
timeout /t 5 /nobreak >nul

REM Check if Qdrant is responding
curl -s http://localhost:6333/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Qdrant is running successfully!
    echo 🔗 Web UI: http://localhost:6333/dashboard
    echo 🔗 API: http://localhost:6333
    echo 📊 Collections endpoint: http://localhost:6333/collections
) else (
    echo ❌ Qdrant failed to start. Check Docker logs:
    docker logs qdrant
)

pause
