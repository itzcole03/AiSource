"""
Ultimate Copilot Integration Script
Integrates all newly built components into the main application
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.enhanced_llm_manager import EnhancedLLMManager
from core.advanced_memory_manager import AdvancedMemoryManager
from core.enhanced_system_manager import EnhancedSystemManager

class AppIntegrator:
    """Integrates all newly built components into the main app"""
    
    def __init__(self):
        self.logger = logging.getLogger("AppIntegrator")
        self.setup_logging()
        
    def setup_logging(self):
        """Setup integration logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        
    async def check_component_integrity(self):
        """Check all generated components for integrity"""
        self.logger.info("Checking component integrity...")
        
        components = {
            "Database Schemas": [
                "database/schemas/agent_tasks.sql",
                "database/schemas/system_metrics.sql", 
                "database/schemas/user_preferences.sql"
            ],
            "API Endpoints": [
                "api/agent_control.py",
                "api/task_management.py",
                "api/system_monitoring.py"
            ],
            "UI Components": [
                "frontend/components/AgentStatusDashboard.tsx",
                "frontend/components/TaskCreationForm.tsx",
                "frontend/components/SystemLogsViewer.tsx"
            ]
        }
        
        all_good = True
        for category, files in components.items():
            self.logger.info(f"Checking {category}...")
            for file_path in files:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    self.logger.info(f"  ✓ {file_path} ({file_size} bytes)")
                else:
                    self.logger.error(f"  ✗ {file_path} MISSING")
                    all_good = False
                    
        return all_good
        
    async def create_integration_config(self):
        """Create configuration for integrating new components"""
        config = {
            "databases": {
                "schemas_dir": "database/schemas",
                "connection_string": "sqlite:///ultimate_copilot.db"
            },
            "apis": {
                "endpoints_dir": "api",
                "base_url": "http://localhost:8000/api"
            },
            "frontend": {
                "components_dir": "frontend/components",
                "build_dir": "frontend/dist"
            }
        }
        
        # Write integration config
        import json
        with open("config/integration_config.json", "w") as f:
            json.dump(config, f, indent=2)
            
        self.logger.info("Created integration configuration")
        return config
        
    async def setup_database_integration(self):
        """Setup database schema integration"""
        self.logger.info("Setting up database integration...")
        
        # Create database initialization script
        init_script = """
#!/usr/bin/env python3
\"\"\"
Database Initialization Script
Sets up all schemas for Ultimate Copilot
\"\"\"

import sqlite3
import os
from pathlib import Path

def initialize_database():
    # Create database directory
    os.makedirs("data/database", exist_ok=True)
    
    # Connect to database
    db_path = "data/database/ultimate_copilot.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute schema files
    schema_dir = Path("database/schemas")
    for schema_file in schema_dir.glob("*.sql"):
        print(f"Executing schema: {schema_file}")
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
            # Convert PostgreSQL to SQLite (basic conversion)
            schema_sql = schema_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
            schema_sql = schema_sql.replace("JSONB", "TEXT")
            schema_sql = schema_sql.replace("CURRENT_TIMESTAMP", "datetime('now')")
            cursor.executescript(schema_sql)
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    initialize_database()
"""
        
        with open("setup_database.py", "w") as f:
            f.write(init_script)
            
        self.logger.info("Created database setup script")
        
    async def setup_api_integration(self):
        """Setup API endpoint integration"""
        self.logger.info("Setting up API integration...")
        
        # Create main API router
        api_router = """
from fastapi import FastAPI, APIRouter
from api.agent_control import app as agent_control_app
from api.task_management import app as task_management_app
from api.system_monitoring import app as system_monitoring_app

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all API modules
api_router.mount("/agent-control", agent_control_app)
api_router.mount("/task-management", task_management_app)
api_router.mount("/system-monitoring", system_monitoring_app)

def setup_api_routes(app: FastAPI):
    \"\"\"Setup all API routes in the main FastAPI app\"\"\"
    app.include_router(api_router)
    return app
"""
        
        with open("api/__init__.py", "w") as f:
            f.write(api_router)
            
        self.logger.info("Created API integration module")
        
    async def setup_frontend_integration(self):
        """Setup frontend component integration"""
        self.logger.info("Setting up frontend integration...")
        
        # Create component index
        component_index = """
// Ultimate Copilot Component Exports
// Auto-generated component integration

export { AgentStatusDashboard } from './AgentStatusDashboard';
export { TaskCreationForm } from './TaskCreationForm';
export { SystemLogsViewer } from './SystemLogsViewer';

// Main dashboard layout that combines all components
export { default as MainDashboard } from './MainDashboard';
"""
        
        with open("frontend/components/index.ts", "w") as f:
            f.write(component_index)
            
        # Create main dashboard layout
        main_dashboard = """
import React from 'react';
import { AgentStatusDashboard } from './AgentStatusDashboard';
import { TaskCreationForm } from './TaskCreationForm';
import { SystemLogsViewer } from './SystemLogsViewer';

export default function MainDashboard() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
      <div className="col-span-1 lg:col-span-2">
        <h1 className="text-3xl font-bold mb-6">Ultimate Copilot Dashboard</h1>
      </div>
      
      <div className="space-y-6">
        <AgentStatusDashboard />
        <TaskCreationForm />
      </div>
      
      <div>
        <SystemLogsViewer />
      </div>
    </div>
  );
}
"""
        
        with open("frontend/components/MainDashboard.tsx", "w") as f:
            f.write(main_dashboard)
            
        self.logger.info("Created frontend integration components")
        
    async def create_integration_test(self):
        """Create integration test script"""
        test_script = """
#!/usr/bin/env python3
\"\"\"
Integration Test Script
Tests all newly integrated components
\"\"\"

import asyncio
import logging
import requests
import sqlite3
from pathlib import Path

async def test_database_integration():
    \"\"\"Test database schema integration\"\"\"
    print("Testing database integration...")
    
    db_path = "data/database/ultimate_copilot.db"
    if not Path(db_path).exists():
        print("  Running database setup...")
        import subprocess
        subprocess.run(["python", "setup_database.py"])
    
    # Test database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Test each table
    tables = ["agent_tasks_schema", "system_metrics_schema", "user_preferences_schema"]
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table}: {count} records")
        except Exception as e:
            print(f"  ✗ {table}: {e}")
    
    conn.close()

async def test_api_integration():
    \"\"\"Test API endpoint integration\"\"\"
    print("Testing API integration...")
    
    # Test imports
    try:
        from api.agent_control import app as agent_control_app
        from api.task_management import app as task_management_app
        from api.system_monitoring import app as system_monitoring_app
        print("  ✓ All API modules imported successfully")
    except Exception as e:
        print(f"  ✗ API import error: {e}")

async def test_frontend_integration():
    \"\"\"Test frontend component integration\"\"\"
    print("Testing frontend integration...")
    
    components = [
        "frontend/components/AgentStatusDashboard.tsx",
        "frontend/components/TaskCreationForm.tsx", 
        "frontend/components/SystemLogsViewer.tsx",
        "frontend/components/MainDashboard.tsx",
        "frontend/components/index.ts"
    ]
    
    for component in components:
        if Path(component).exists():
            print(f"  ✓ {component}")
        else:
            print(f"  ✗ {component} missing")

async def main():
    print("=" * 60)
    print("ULTIMATE COPILOT INTEGRATION TEST")
    print("=" * 60)
    
    await test_database_integration()
    print()
    await test_api_integration()
    print()
    await test_frontend_integration()
    
    print()
    print("Integration test complete!")

if __name__ == "__main__":
    asyncio.run(main())
"""
        
        with open("test_integration.py", "w") as f:
            f.write(test_script)
            
        self.logger.info("Created integration test script")
        
    async def run_full_integration(self):
        """Run the complete integration process"""
        self.logger.info("="*60)
        self.logger.info("ULTIMATE COPILOT COMPONENT INTEGRATION")
        self.logger.info("="*60)
        
        # Step 1: Check component integrity
        if not await self.check_component_integrity():
            self.logger.error("Component integrity check failed!")
            return False
            
        # Step 2: Create integration config
        await self.create_integration_config()
        
        # Step 3: Setup database integration
        await self.setup_database_integration()
        
        # Step 4: Setup API integration
        await self.setup_api_integration()
        
        # Step 5: Setup frontend integration
        await self.setup_frontend_integration()
        
        # Step 6: Create integration test
        await self.create_integration_test()
        
        self.logger.info("="*60)
        self.logger.info("INTEGRATION COMPLETE!")
        self.logger.info("="*60)
        self.logger.info("")
        self.logger.info("Next steps:")
        self.logger.info("1. Run: python setup_database.py")
        self.logger.info("2. Run: python test_integration.py")
        self.logger.info("3. Start main app: python main.py")
        self.logger.info("")
        
        return True

async def main():
    """Main integration function"""
    integrator = AppIntegrator()
    success = await integrator.run_full_integration()
    
    if success:
        print("✓ Integration completed successfully!")
        return 0
    else:
        print("✗ Integration failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
