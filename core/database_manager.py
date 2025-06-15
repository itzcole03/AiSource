"""
Database Manager for Ultimate Copilot
Handles connections to PostgreSQL database with all schemas
"""

import asyncpg
import asyncio
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or "postgresql://localhost/ultimate_copilot"
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(self.connection_string)
            await self.create_tables()
            logger.info("Database manager initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    async def create_tables(self):
        """Create all tables from schema files"""
        schema_dir = Path("database/schemas")
        if not schema_dir.exists():
            return
            
        async with self.pool.acquire() as conn:
            for schema_file in schema_dir.glob("*.sql"):
                try:
                    schema_sql = schema_file.read_text()
                    await conn.execute(schema_sql)
                    logger.info(f"Created tables from {schema_file.name}")
                except Exception as e:
                    logger.error(f"Failed to create tables from {schema_file.name}: {e}")
    
    async def execute_query(self, query: str, *args) -> List[Dict]:
        """Execute a query and return results"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def execute_command(self, command: str, *args) -> str:
        """Execute a command (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as conn:
            result = await conn.execute(command, *args)
            return result
    
    async def get_agent_tasks(self, agent_id: str = None) -> List[Dict]:
        """Get tasks for agents"""
        if agent_id:
            query = "SELECT * FROM agent_tasks WHERE agent_id = $1 ORDER BY created_at DESC"
            return await self.execute_query(query, agent_id)
        else:
            query = "SELECT * FROM agent_tasks ORDER BY created_at DESC"
            return await self.execute_query(query)
    
    async def create_agent_task(self, agent_id: str, task_type: str, description: str, metadata: Dict = None) -> str:
        """Create a new agent task"""
        command = """
            INSERT INTO agent_tasks (agent_id, task_type, description, metadata, status)
            VALUES ($1, $2, $3, $4, 'pending')
            RETURNING id
        """
        result = await self.execute_query(command, agent_id, task_type, description, metadata or {})
        return result[0]['id'] if result else None
    
    async def update_task_status(self, task_id: str, status: str, result: Dict = None):
        """Update task status"""
        command = """
            UPDATE agent_tasks 
            SET status = $2, result = $3, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """
        await self.execute_command(command, task_id, status, result or {})
    
    async def log_system_metric(self, metric_name: str, value: float, metadata: Dict = None):
        """Log system metric"""
        command = """
            INSERT INTO system_metrics (metric_name, value, metadata)
            VALUES ($1, $2, $3)
        """
        await self.execute_command(command, metric_name, value, metadata or {})
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

async def get_database() -> DatabaseManager:
    """Get database manager instance"""
    if not db_manager.pool:
        await db_manager.initialize()
    return db_manager
