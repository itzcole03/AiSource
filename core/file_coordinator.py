"""
Advanced File Coordination System
Prevents multiple agents from editing the same file simultaneously using file locking,
queuing, and collaborative coordination.
"""

import os
import time
import threading
import json
from pathlib import Path
from typing import Dict, Set, Optional, Any, List
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import logging

# Windows-compatible file locking (fcntl not available on Windows)
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

@dataclass
class FileOperation:
    """Represents a file operation request"""
    agent_id: str
    file_path: str
    operation_type: str  # 'read', 'write', 'create', 'delete'
    priority: int = 1  # Higher number = higher priority
    timestamp: Optional[datetime] = None
    content: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class FileCoordinator:
    """
    Advanced file coordination system that prevents conflicts between agents.
    Features:
    - File locking with timeouts
    - Operation queuing and prioritization
    - Conflict detection and resolution
    - Collaborative editing support
    - Deadlock prevention
    """
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.locks: Dict[str, threading.Lock] = {}
        self.active_operations: Dict[str, FileOperation] = {}
        self.operation_queue: List[FileOperation] = []
        self.file_versions: Dict[str, int] = {}
        self.coordination_lock = threading.Lock()
        self.max_lock_timeout = 30  # seconds
        self.queue_check_interval = 0.1  # seconds
        
        # Create coordination directory
        self.coordination_dir = self.workspace_root / ".file_coordination"
        self.coordination_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger("FileCoordinator")
    
    def _get_lock_file(self, file_path: str) -> Path:
        """Get the lock file path for a given file"""
        normalized_path = str(Path(file_path)).replace(os.sep, "_").replace(":", "")
        return self.coordination_dir / f"{normalized_path}.lock"
    
    def _get_queue_file(self, file_path: str) -> Path:
        """Get the queue file path for a given file"""
        normalized_path = str(Path(file_path)).replace(os.sep, "_").replace(":", "")
        return self.coordination_dir / f"{normalized_path}.queue"
    
    def _is_file_locked(self, file_path: str) -> bool:
        """Check if a file is currently locked"""
        lock_file = self._get_lock_file(file_path)
        if not lock_file.exists():
            return False
        
        try:
            # Check if lock is stale (older than max timeout)
            lock_time = datetime.fromtimestamp(lock_file.stat().st_mtime)
            if datetime.now() - lock_time > timedelta(seconds=self.max_lock_timeout * 2):
                lock_file.unlink()  # Remove stale lock
                return False
            return True
        except:
            return False
    
    def _create_lock(self, file_path: str, agent_id: str) -> bool:
        """Create a lock for a file"""
        lock_file = self._get_lock_file(file_path)
        try:
            if lock_file.exists():
                return False
            
            lock_data = {
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "file_path": file_path
            }
            
            with open(lock_file, 'w') as f:
                json.dump(lock_data, f)
            
            return True
        except:
            return False
    
    def _remove_lock(self, file_path: str, agent_id: str) -> bool:
        """Remove a lock for a file"""
        lock_file = self._get_lock_file(file_path)
        try:
            if not lock_file.exists():
                return True
            
            # Verify ownership
            with open(lock_file, 'r') as f:
                lock_data = json.load(f)
            
            if lock_data.get("agent_id") == agent_id:
                lock_file.unlink()
                return True
            
            return False
        except:
            return False
    
    def _add_to_queue(self, operation: FileOperation):
        """Add an operation to the queue"""
        queue_file = self._get_queue_file(operation.file_path)
        
        try:
            # Load existing queue
            queue_data = []
            if queue_file.exists():
                with open(queue_file, 'r') as f:
                    queue_data = json.load(f)
              # Add new operation
            op_data = {
                "agent_id": operation.agent_id,
                "operation_type": operation.operation_type,
                "priority": operation.priority,
                "timestamp": operation.timestamp.isoformat() if operation.timestamp else datetime.now().isoformat(),
                "content": operation.content
            }
            queue_data.append(op_data)
            
            # Sort by priority and timestamp
            queue_data.sort(key=lambda x: (-x["priority"], x["timestamp"]))
            
            # Save queue
            with open(queue_file, 'w') as f:
                json.dump(queue_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to add to queue: {e}")
    
    def _get_next_operation(self, file_path: str) -> Optional[Dict]:
        """Get the next operation from the queue"""
        queue_file = self._get_queue_file(file_path)
        
        try:
            if not queue_file.exists():
                return None
            
            with open(queue_file, 'r') as f:
                queue_data = json.load(f)
            
            if not queue_data:
                return None
              # Get highest priority operation
            next_op = queue_data.pop(0)
            
            # Update queue file
            with open(queue_file, 'w') as f:
                json.dump(queue_data, f, indent=2)
            
            return next_op
            
        except Exception as e:
            self.logger.error(f"Failed to get next operation: {e}")
            return None
    
    @contextmanager
    def acquire_file_lock(self, file_path: str, agent_id: str, operation_type: str = "write", 
                         timeout: Optional[float] = None, priority: int = 1):
        """
        Context manager for acquiring file locks with timeout and queuing
        
        Args:
            file_path: Path to the file to lock
            agent_id: ID of the agent requesting the lock
            operation_type: Type of operation (read, write, create, delete)
            timeout: Maximum time to wait for lock (default: max_lock_timeout)
            priority: Priority of the operation (higher = more important)
        """
        if timeout is None:
            timeout = self.max_lock_timeout
        
        file_path = str(Path(file_path).resolve())
        lock_acquired = False
        start_time = time.time()
        
        try:
            # Try to acquire lock immediately
            if not self._is_file_locked(file_path):
                if self._create_lock(file_path, agent_id):
                    lock_acquired = True
                    self.logger.info(f"Agent {agent_id} acquired lock for {file_path}")
                    yield
                    return
            
            # If immediate lock failed, add to queue and wait
            operation = FileOperation(
                agent_id=agent_id,
                file_path=file_path,
                operation_type=operation_type,
                priority=priority
            )
            
            self._add_to_queue(operation)
            self.logger.info(f"Agent {agent_id} queued for {file_path} (priority: {priority})")
            
            # Wait for our turn
            while time.time() - start_time < timeout:
                if not self._is_file_locked(file_path):
                    next_op = self._get_next_operation(file_path)
                    if next_op and next_op["agent_id"] == agent_id:
                        if self._create_lock(file_path, agent_id):
                            lock_acquired = True
                            self.logger.info(f"Agent {agent_id} acquired queued lock for {file_path}")
                            yield
                            return
                
                time.sleep(self.queue_check_interval)
            
            # Timeout reached
            raise TimeoutError(f"Could not acquire lock for {file_path} within {timeout} seconds")
            
        finally:
            if lock_acquired:
                self._remove_lock(file_path, agent_id)
                self.logger.info(f"Agent {agent_id} released lock for {file_path}")
    
    def safe_write_file(self, file_path: str, content: str, agent_id: str, 
                       encoding: str = "utf-8", priority: int = 1) -> bool:
        """
        Safely write to a file with locking and coordination
        
        Args:
            file_path: Path to the file
            content: Content to write
            agent_id: ID of the agent performing the write
            encoding: File encoding
            priority: Operation priority
            
        Returns:
            True if successful, False otherwise
        """
        try:
            full_path = Path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self.acquire_file_lock(str(full_path), agent_id, "write", priority=priority):
                # Check if file changed while waiting
                current_version = self.file_versions.get(str(full_path), 0)
                
                with open(full_path, 'w', encoding=encoding) as f:
                    f.write(content)
                
                # Update version
                self.file_versions[str(full_path)] = current_version + 1
                
                self.logger.info(f"Agent {agent_id} successfully wrote to {file_path}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to write file {file_path}: {e}")
            return False
    
    def safe_read_file(self, file_path: str, agent_id: str, 
                      encoding: str = "utf-8") -> Optional[str]:
        """
        Safely read from a file (shared lock for reads)
        
        Args:
            file_path: Path to the file
            agent_id: ID of the agent performing the read
            encoding: File encoding
            
        Returns:
            File content or None if failed
        """
        try:
            full_path = Path(file_path)
            if not full_path.exists():
                return None
            
            # Reads don't need exclusive locks but should respect write locks
            if self._is_file_locked(str(full_path)):
                # Wait briefly for write to complete
                time.sleep(0.1)
            
            with open(full_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            self.logger.debug(f"Agent {agent_id} read from {file_path}")
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            return None
    
    def check_file_conflicts(self, file_path: str) -> Dict[str, Any]:
        """
        Check for potential conflicts on a file
        
        Returns:
            Dictionary with conflict information
        """
        file_path = str(Path(file_path).resolve())
        
        return {
            "is_locked": self._is_file_locked(file_path),
            "lock_info": self._get_lock_info(file_path),
            "queue_length": self._get_queue_length(file_path),
            "version": self.file_versions.get(file_path, 0)
        }
    
    def _get_lock_info(self, file_path: str) -> Optional[Dict]:
        """Get information about the current lock"""
        lock_file = self._get_lock_file(file_path)
        try:
            if lock_file.exists():
                with open(lock_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return None
    
    def _get_queue_length(self, file_path: str) -> int:
        """Get the number of operations queued for a file"""
        queue_file = self._get_queue_file(file_path)
        try:
            if queue_file.exists():
                with open(queue_file, 'r') as f:
                    queue_data = json.load(f)
                return len(queue_data)
        except:
            pass
        return 0
    
    def force_unlock(self, file_path: str, admin_agent_id: str = "admin") -> bool:
        """
        Force unlock a file (emergency use only)
        
        Args:
            file_path: Path to the file
            admin_agent_id: ID of admin agent performing the unlock
            
        Returns:
            True if successful
        """
        try:
            lock_file = self._get_lock_file(file_path)
            if lock_file.exists():
                lock_file.unlink()
            
            self.logger.warning(f"Admin {admin_agent_id} force-unlocked {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to force unlock {file_path}: {e}")
            return False
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get statistics about file coordination"""
        lock_files = list(self.coordination_dir.glob("*.lock"))
        queue_files = list(self.coordination_dir.glob("*.queue"))
        
        total_queued = 0
        for queue_file in queue_files:
            try:
                with open(queue_file, 'r') as f:
                    queue_data = json.load(f)
                total_queued += len(queue_data)
            except:
                pass
        
        return {
            "active_locks": len(lock_files),
            "total_queued_operations": total_queued,
            "tracked_files": len(self.file_versions),
            "coordination_dir": str(self.coordination_dir)
        }


# Global coordinator instance
_coordinator = None

def get_file_coordinator(workspace_root: Optional[str] = None) -> FileCoordinator:
    """Get the global file coordinator instance"""
    global _coordinator
    
    if _coordinator is None:
        if workspace_root is None:
            workspace_root = os.getcwd()
        _coordinator = FileCoordinator(workspace_root)
    
    return _coordinator

def safe_write_file(file_path: str, content: str, agent_id: str, **kwargs) -> bool:
    """Convenience function for safe file writing"""
    coordinator = get_file_coordinator()
    return coordinator.safe_write_file(file_path, content, agent_id, **kwargs)

def safe_read_file(file_path: str, agent_id: str, **kwargs) -> Optional[str]:
    """Convenience function for safe file reading"""
    coordinator = get_file_coordinator()
    return coordinator.safe_read_file(file_path, agent_id, **kwargs)

@contextmanager
def file_lock(file_path: str, agent_id: str, **kwargs):
    """Convenience context manager for file locking"""
    coordinator = get_file_coordinator()
    with coordinator.acquire_file_lock(file_path, agent_id, **kwargs):
        yield
