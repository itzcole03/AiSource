"""
Advanced Memory Manager

This module provides a shared memory system for the agent swarm with
vector-based retrieval and cross-agent knowledge sharing.
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class AdvancedMemoryManager:
    """Advanced memory manager with vector-based retrieval"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.memory_path = Path(self.config.get("memory_path", "data/memory"))
        self.vector_db = None
        self.memory_cache = {}
        self.initialized = False
        self.embedding_model = None
        self.memory_lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """Initialize the memory manager"""
        logger.info("Initializing Advanced Memory Manager")
        
        # Set start time for uptime tracking
        self._start_time = time.time()
        
        # Create memory directory if it doesn't exist
        os.makedirs(self.memory_path, exist_ok=True)
        
        # Initialize vector database
        await self.initialize_vector_db()
        
        # Load existing memories
        await self.load_memories()
        
        self.initialized = True
        logger.info("Advanced Memory Manager initialized")
        return True
    
    async def initialize_vector_db(self) -> None:
        """Initialize the vector database"""
        try:
            # Try to import Qdrant
            from qdrant_client import QdrantClient
            from qdrant_client.http import models
            
            # Initialize Qdrant client
            self.vector_db = QdrantClient(
                url=self.config.get("qdrant_url", "http://localhost:6333")
            )
            
            # Check if collection exists, create if not
            collections = self.vector_db.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if "agent_memory" not in collection_names:
                # Create collection
                self.vector_db.create_collection(
                    collection_name="agent_memory",
                    vectors_config=models.VectorParams(
                        size=384,  # Default embedding size
                        distance=models.Distance.COSINE
                    )
                )
                
            logger.info("Vector database initialized")
            
        except ImportError:
            logger.warning("Qdrant client not available, using fallback memory system")
            self.vector_db = None
            
        except Exception as e:
            logger.error(f"Error initializing vector database: {e}")
            self.vector_db = None
    
    async def load_memories(self) -> None:
        """Load existing memories from disk"""
        try:
            memory_file = self.memory_path / "memories.json"
            if memory_file.exists():
                with open(memory_file, "r") as f:
                    self.memory_cache = json.load(f)
                logger.info(f"Loaded {len(self.memory_cache)} memories from disk")
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
            self.memory_cache = {}
    
    async def save_memories(self) -> None:
        """Save memories to disk"""
        try:
            memory_file = self.memory_path / "memories.json"
            with open(memory_file, "w") as f:
                json.dump(self.memory_cache, f)
            logger.info(f"Saved {len(self.memory_cache)} memories to disk")
        except Exception as e:
            logger.error(f"Error saving memories: {e}")
    
    async def add_memory(self, memory_item: Dict[str, Any]) -> str:
        """Add a memory item to the shared memory"""
        if not self.initialized:
            logger.warning("Memory manager not initialized")
            return ""
        
        async with self.memory_lock:
            try:
                # Generate memory ID if not provided
                memory_id = memory_item.get("id", f"mem_{int(time.time() * 1000)}")
                
                # Add timestamp if not provided
                if "timestamp" not in memory_item:
                    memory_item["timestamp"] = time.time()
                
                # Add to memory cache
                self.memory_cache[memory_id] = memory_item
                
                # Add to vector database if available
                if self.vector_db and "content" in memory_item:
                    await self.add_to_vector_db(memory_id, memory_item)
                
                # Save memories periodically
                # In a real implementation, you might want to do this less frequently
                await self.save_memories()
                
                return memory_id
                
            except Exception as e:
                logger.error(f"Error adding memory: {e}")
                return ""
    
    async def add_to_vector_db(self, memory_id: str, memory_item: Dict[str, Any]) -> None:
        """Add a memory item to the vector database"""
        if not self.vector_db:
            return
        
        try:
            # Generate embedding
            embedding = await self.generate_embedding(memory_item["content"])
            
            # Add to vector database
            from qdrant_client.http import models
            
            self.vector_db.upsert(
                collection_name="agent_memory",
                points=[
                    models.PointStruct(
                        id=memory_id,
                        vector=embedding,
                        payload=memory_item
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"Error adding to vector database: {e}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # In a real implementation, you would use a proper embedding model
        # For simplicity, we'll just use a mock implementation
        
        # Try to use sentence-transformers if available
        try:
            if not self.embedding_model:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            embedding = self.embedding_model.encode(text).tolist()
            return embedding
            
        except ImportError:
            # Fallback to a simple mock embedding
            import hashlib
            hash_value = hashlib.md5(text.encode()).digest()
            # Convert to a list of 384 float values between -1 and 1
            return [(b / 128.0) - 1.0 for b in hash_value] + [0.0] * (384 - len(hash_value))
    
    async def query_memory(self, query: str, context: Dict[str, Any] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Query the shared memory"""
        if not self.initialized:
            logger.warning("Memory manager not initialized")
            return []
        
        try:
            # If vector database is available, use it for semantic search
            if self.vector_db:
                return await self.query_vector_db(query, context, limit)
            
            # Otherwise, fall back to simple keyword search
            return await self.query_keyword(query, context, limit)
            
        except Exception as e:
            logger.error(f"Error querying memory: {e}")
            return []
    
    async def query_vector_db(self, query: str, context: Dict[str, Any] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Query the vector database"""
        try:
            # Generate embedding for query
            query_embedding = await self.generate_embedding(query)
            
            # Search vector database
            search_results = self.vector_db.search(
                collection_name="agent_memory",
                query_vector=query_embedding,
                limit=limit
            )
            
            # Extract results
            results = []
            for hit in search_results:
                memory_item = hit.payload
                memory_item["score"] = hit.score
                results.append(memory_item)
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying vector database: {e}")
            return []
    
    async def query_keyword(self, query: str, context: Dict[str, Any] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Query using simple keyword matching"""
        results = []
        query_lower = query.lower()
        
        # Simple keyword search
        for memory_id, memory_item in self.memory_cache.items():
            if "content" in memory_item:
                content_lower = memory_item["content"].lower()
                if query_lower in content_lower:
                    # Calculate a simple score based on frequency
                    score = content_lower.count(query_lower) / len(content_lower)
                    result = memory_item.copy()
                    result["score"] = score
                    results.append(result)
        
        # Sort by score and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory item"""
        return self.memory_cache.get(memory_id)
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update a memory item"""
        if not self.initialized:
            logger.warning("Memory manager not initialized")
            return False
        
        async with self.memory_lock:
            if memory_id not in self.memory_cache:
                logger.warning(f"Memory {memory_id} not found")
                return False
            
            try:
                # Update memory item
                memory_item = self.memory_cache[memory_id]
                for key, value in updates.items():
                    memory_item[key] = value
                
                # Update vector database if content changed
                if self.vector_db and "content" in updates:
                    await self.add_to_vector_db(memory_id, memory_item)
                
                # Save memories
                await self.save_memories()
                
                return True
                
            except Exception as e:
                logger.error(f"Error updating memory: {e}")
                return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item"""
        if not self.initialized:
            logger.warning("Memory manager not initialized")
            return False
        
        async with self.memory_lock:
            if memory_id not in self.memory_cache:
                logger.warning(f"Memory {memory_id} not found")
                return False
            
            try:
                # Remove from memory cache
                del self.memory_cache[memory_id]
                
                # Remove from vector database
                if self.vector_db:
                    self.vector_db.delete(
                        collection_name="agent_memory",
                        points_selector=[memory_id]
                    )
                
                # Save memories
                await self.save_memories()
                
                return True
                
            except Exception as e:
                logger.error(f"Error deleting memory: {e}")
                return False
    
    async def get_agent_context(self, agent_id: str, task_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get context for a specific agent"""
        if not self.initialized:
            logger.warning("Memory manager not initialized")
            return {}
        
        try:
            # Get agent-specific memories from regular memory cache
            agent_memories = []
            for memory_id, memory_item in self.memory_cache.items():
                # Skip the experiences list (handled separately)
                if memory_id == "experiences" or not isinstance(memory_item, dict):
                    continue
                if memory_item.get("agent_id") == agent_id:
                    agent_memories.append(memory_item)
            
            # Get agent-specific experiences
            agent_experiences = []
            if "experiences" in self.memory_cache and isinstance(self.memory_cache["experiences"], list):
                for experience in self.memory_cache["experiences"]:
                    if isinstance(experience, dict) and experience.get("agent_id") == agent_id:
                        agent_experiences.append(experience)
            
            # Sort by timestamp (newest first)
            agent_memories.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            agent_experiences.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            
            # Get task-specific memories if task context provided
            task_memories = []
            if task_context:
                task_type = task_context.get("task_type")
                if task_type:
                    # Query for relevant memories
                    task_memories = await self.query_memory(task_type, task_context, limit=10)
            
            return {
                "agent_memories": agent_memories[:10],  # Limit to 10 most recent
                "agent_experiences": agent_experiences[:10],  # Limit to 10 most recent
                "task_memories": task_memories,
                "task_context": task_context or {}
            }
            
        except Exception as e:
            logger.error(f"Error getting agent context: {e}")
            return {}
    
    async def share_memory(self, memory_id: str, target_agents: List[str]) -> bool:
        """Share a memory with specific agents"""
        if not self.initialized:
            logger.warning("Memory manager not initialized")
            return False
        
        if memory_id not in self.memory_cache:
            logger.warning(f"Memory {memory_id} not found")
            return False
        
        try:
            memory_item = self.memory_cache[memory_id]
            
            # Add target agents to the memory item
            if "shared_with" not in memory_item:
                memory_item["shared_with"] = []
                
            memory_item["shared_with"].extend(target_agents)
            memory_item["shared_with"] = list(set(memory_item["shared_with"]))  # Remove duplicates
            
            # Save memories
            await self.save_memories()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sharing memory: {e}")
            return False
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the memory manager"""
        try:
            metrics = {
                "initialized": self.initialized,
                "total_memories": len(self.memory_cache),
                "memory_path": str(self.memory_path),
                "vector_db_available": self.vector_db is not None,
                "memory_usage_mb": self._get_memory_usage(),
                "uptime_seconds": self._get_uptime()
            }
            
            # Add vector DB specific metrics if available
            if self.vector_db:
                try:
                    collections = await asyncio.to_thread(self.vector_db.get_collections)
                    collection_info = collections.collections
                    metrics["vector_collections"] = len(collection_info)
                    
                    # Get collection stats if agent_memory exists
                    for collection in collection_info:
                        if collection.name == "agent_memory":
                            metrics["vector_count"] = collection.points_count
                            break
                    else:
                        metrics["vector_count"] = 0
                        
                except Exception as e:
                    metrics["vector_db_error"] = str(e)
                    metrics["vector_collections"] = 0
                    metrics["vector_count"] = 0
            else:
                metrics["vector_collections"] = 0
                metrics["vector_count"] = 0
            
            # Memory distribution by agent
            agent_memory_count = {}
            for memory_item in self.memory_cache.values():
                agent_id = memory_item.get("agent_id", "unknown")
                agent_memory_count[agent_id] = agent_memory_count.get(agent_id, 0) + 1
            
            metrics["memory_by_agent"] = agent_memory_count
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting memory performance metrics: {e}")
            return {
                "error": str(e),
                "initialized": False,
                "total_memories": 0,
                "memory_usage_mb": 0,
                "uptime_seconds": 0
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the memory manager"""
        try:
            health_status = {
                "status": "healthy",
                "components": {},
                "issues": []
            }
            
            # Check initialization
            if not self.initialized:
                health_status["status"] = "unhealthy"
                health_status["issues"].append("Memory manager not initialized")
                return health_status
            
            # Check memory directory
            if not self.memory_path.exists():
                health_status["issues"].append("Memory directory does not exist")
                health_status["components"]["filesystem"] = {"status": "unhealthy", "message": "Memory directory missing"}
            else:
                health_status["components"]["filesystem"] = {"status": "healthy", "message": "Memory directory accessible"}
            
            # Check vector database
            if self.vector_db:
                try:
                    # Test vector DB connection
                    collections = await asyncio.to_thread(self.vector_db.get_collections)
                    health_status["components"]["vector_db"] = {
                        "status": "healthy", 
                        "message": f"Connected with {len(collections.collections)} collections"
                    }
                except Exception as e:
                    health_status["issues"].append(f"Vector database error: {e}")
                    health_status["components"]["vector_db"] = {
                        "status": "unhealthy", 
                        "error": str(e)
                    }
            else:
                health_status["components"]["vector_db"] = {
                    "status": "disabled", 
                    "message": "Vector database not configured"
                }
            
            # Check memory cache
            try:
                # Try to perform a basic operation
                test_memory_id = f"health_check_{int(time.time())}"
                test_memory = {
                    "content": "Health check test memory",
                    "agent_id": "health_check",
                    "timestamp": time.time(),
                    "metadata": {"test": True}
                }
                
                # Test store and retrieve
                success = await self.store_memory(test_memory_id, test_memory)
                if success:
                    retrieved = await self.get_memory(test_memory_id)
                    if retrieved:
                        # Clean up test memory
                        await self.delete_memory(test_memory_id)
                        health_status["components"]["memory_operations"] = {
                            "status": "healthy",
                            "message": "Memory operations working correctly"
                        }
                    else:
                        health_status["issues"].append("Memory retrieval failed")
                        health_status["components"]["memory_operations"] = {
                            "status": "unhealthy",
                            "message": "Memory retrieval failed"
                        }
                else:
                    health_status["issues"].append("Memory storage failed")
                    health_status["components"]["memory_operations"] = {
                        "status": "unhealthy",
                        "message": "Memory storage failed"
                    }
                    
            except Exception as e:
                health_status["issues"].append(f"Memory operations error: {e}")
                health_status["components"]["memory_operations"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            
            # Determine overall status
            if health_status["issues"]:
                unhealthy_components = [
                    comp for comp in health_status["components"].values() 
                    if comp["status"] == "unhealthy"
                ]
                if unhealthy_components:
                    health_status["status"] = "unhealthy"
                else:
                    health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error during memory health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "components": {},
                "issues": [f"Health check failed: {e}"]
            }
    
    async def restart(self) -> Dict[str, Any]:
        """Restart the memory manager"""
        try:
            logger.info("Restarting Advanced Memory Manager")
            
            # Shutdown current instance
            await self.shutdown()
            
            # Clear state
            self.memory_cache = {}
            self.vector_db = None
            self.initialized = False
            
            # Reinitialize
            success = await self.initialize()
            
            if success:
                logger.info("Advanced Memory Manager restarted successfully")
                return {
                    "status": "success",
                    "message": "Memory Manager restarted successfully",
                    "timestamp": time.time()
                }
            else:
                logger.error("Failed to restart Advanced Memory Manager")
                return {
                    "status": "error",
                    "message": "Failed to restart Memory Manager",
                    "timestamp": time.time()
                }
                
        except Exception as e:
            logger.error(f"Error restarting Memory Manager: {e}")
            return {
                "status": "error",
                "message": f"Failed to restart Memory Manager: {e}",
                "timestamp": time.time()
            }
    
    def _get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
        except Exception:
            return 0.0
    
    def _get_uptime(self) -> float:
        """Get uptime in seconds"""
        try:
            if not hasattr(self, '_start_time'):
                self._start_time = time.time()
            return time.time() - self._start_time
        except Exception:
            return 0.0

    async def shutdown(self) -> None:
        """Shutdown the memory manager"""
        logger.info("Shutting down Advanced Memory Manager")
        
        # Save memories
        await self.save_memories()
        
        # Close vector database connection
        if hasattr(self, 'vector_db') and self.vector_db:
            try:
                # Some clients might have a close method
                if hasattr(self.vector_db, 'close'):
                    self.vector_db.close()
            except:
                pass
            
        self.initialized = False

    async def store_experience(self, agent_id: str, task: Dict[str, Any], result: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store agent experience for collaborative learning"""
        try:
            async with self.memory_lock:
                # Create experience entry
                experience = {
                    "agent_id": agent_id,
                    "experience_type": "task_completion",
                    "data": {
                        "task": task,
                        "result": result,
                        "metadata": metadata or {}
                    },
                    "timestamp": time.time(),
                    "id": f"{agent_id}_task_completion_{int(time.time())}"
                }
                
                # Store in memory cache
                if "experiences" not in self.memory_cache:
                    self.memory_cache["experiences"] = []
                
                self.memory_cache["experiences"].append(experience)
                
                # Save to file
                experiences_file = self.memory_path / "agent_experiences.json"
                with open(experiences_file, 'w', encoding='utf-8') as f:
                    json.dump(self.memory_cache["experiences"], f, indent=2)
                
                logger.debug(f"Stored experience for {agent_id}: task_completion")
                return True
                
        except Exception as e:
            logger.error(f"Error storing experience: {e}")
            return False
    
    async def get_collaborative_insights(self, requesting_agent: str) -> List[Dict[str, Any]]:
        """Get collaborative insights from other agents"""
        try:
            insights = []
            
            # Load experiences if not in cache
            if "experiences" not in self.memory_cache:
                experiences_file = self.memory_path / "agent_experiences.json"
                if experiences_file.exists():
                    with open(experiences_file, 'r', encoding='utf-8') as f:
                        self.memory_cache["experiences"] = json.load(f)
                else:
                    self.memory_cache["experiences"] = []
            
            # Get recent experiences from other agents
            current_time = time.time()
            for exp in self.memory_cache["experiences"]:
                # Skip own experiences
                if exp["agent_id"] == requesting_agent:
                    continue
                
                # Only get recent experiences (last hour)
                if current_time - exp["timestamp"] < 3600:
                    insights.append({
                        "source_agent": exp["agent_id"],
                        "type": exp["experience_type"],
                        "data": exp["data"],
                        "age_minutes": (current_time - exp["timestamp"]) / 60
                    })
            
            # Sort by recency
            insights.sort(key=lambda x: x["age_minutes"])
            
            logger.debug(f"Retrieved {len(insights)} collaborative insights for {requesting_agent}")
            return insights[:10]  # Return top 10 most recent
            
        except Exception as e:
            logger.error(f"Error getting collaborative insights: {e}")
            return []
    
    async def store_agent_state(self, agent_id: str, state_data: Dict[str, Any]) -> bool:
        """Store current agent state for coordination"""
        try:
            async with self.memory_lock:
                # Create agent states section if needed
                if "agent_states" not in self.memory_cache:
                    self.memory_cache["agent_states"] = {}
                
                # Store current state
                self.memory_cache["agent_states"][agent_id] = {
                    "state": state_data,
                    "timestamp": time.time(),
                    "last_update": time.time()
                }
                
                # Save to file
                states_file = self.memory_path / "agent_states.json"
                with open(states_file, 'w', encoding='utf-8') as f:
                    json.dump(self.memory_cache["agent_states"], f, indent=2)
                
                return True
                
        except Exception as e:
            logger.error(f"Error storing agent state: {e}")
            return False
    
    async def get_other_agent_states(self, requesting_agent: str) -> Dict[str, Any]:
        """Get states of other agents for coordination"""
        try:
            # Load states if not in cache
            if "agent_states" not in self.memory_cache:
                states_file = self.memory_path / "agent_states.json"
                if states_file.exists():
                    with open(states_file, 'r', encoding='utf-8') as f:
                        self.memory_cache["agent_states"] = json.load(f)
                else:
                    self.memory_cache["agent_states"] = {}
            
            # Return other agents' states
            other_states = {}
            current_time = time.time()
            
            for agent_id, state_info in self.memory_cache["agent_states"].items():
                if agent_id != requesting_agent:
                    # Only include recent states (last 10 minutes)
                    if current_time - state_info["timestamp"] < 600:
                        other_states[agent_id] = state_info["state"]
            
            return other_states
            
        except Exception as e:
            logger.error(f"Error getting other agent states: {e}")
            return {}

    async def store_agent_intelligence(self, agent_id: str, intelligence_data: Dict[str, Any]) -> bool:
        """Store agent intelligence level and learning progress"""
        try:
            async with self.memory_lock:
                # Create intelligence tracking section if needed
                if "agent_intelligence" not in self.memory_cache:
                    self.memory_cache["agent_intelligence"] = {}
                
                # Store intelligence data
                self.memory_cache["agent_intelligence"][agent_id] = {
                    "intelligence_level": intelligence_data.get("intelligence_level", 1.0),
                    "learned_patterns": intelligence_data.get("learned_patterns", []),
                    "successful_strategies": intelligence_data.get("successful_strategies", []),
                    "task_completion_history": intelligence_data.get("task_completion_history", []),
                    "optimization_insights": intelligence_data.get("optimization_insights", []),
                    "collaborative_learnings": intelligence_data.get("collaborative_learnings", []),
                    "model_preferences": intelligence_data.get("model_preferences", {}),
                    "performance_metrics": intelligence_data.get("performance_metrics", {}),
                    "timestamp": time.time(),
                    "last_update": time.time(),
                    "sessions_count": intelligence_data.get("sessions_count", 1),
                    "cumulative_runtime": intelligence_data.get("cumulative_runtime", 0)
                }
                
                # Save to dedicated intelligence file
                intelligence_file = self.memory_path / "agent_intelligence.json"
                with open(intelligence_file, 'w', encoding='utf-8') as f:
                    json.dump(self.memory_cache["agent_intelligence"], f, indent=2)
                
                logger.info(f"Stored intelligence data for {agent_id} - Level: {intelligence_data.get('intelligence_level', 1.0)}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing agent intelligence: {e}")
            return False
    
    async def restore_agent_intelligence(self, agent_id: str) -> Dict[str, Any]:
        """Restore agent intelligence and learning progress from previous sessions"""
        try:
            # Load intelligence data if not in cache
            if "agent_intelligence" not in self.memory_cache:
                intelligence_file = self.memory_path / "agent_intelligence.json"
                if intelligence_file.exists():
                    with open(intelligence_file, 'r', encoding='utf-8') as f:
                        self.memory_cache["agent_intelligence"] = json.load(f)
                        logger.info(f"Loaded intelligence data from {intelligence_file}")
                else:
                    self.memory_cache["agent_intelligence"] = {}
                    logger.info("No existing intelligence data found, starting fresh")
            
            # Get agent's intelligence data or create default
            if agent_id in self.memory_cache["agent_intelligence"]:
                intelligence_data = self.memory_cache["agent_intelligence"][agent_id].copy()
                
                # Increment session count
                intelligence_data["sessions_count"] = intelligence_data.get("sessions_count", 0) + 1
                intelligence_data["last_session_start"] = time.time()
                
                logger.info(f"Restored intelligence for {agent_id} - Level: {intelligence_data.get('intelligence_level', 1.0)}, Session: {intelligence_data['sessions_count']}")
                return intelligence_data
            else:
                # Create default intelligence data for new agent
                default_intelligence = {
                    "intelligence_level": 1.0,
                    "learned_patterns": [],
                    "successful_strategies": [],
                    "task_completion_history": [],
                    "optimization_insights": [],
                    "collaborative_learnings": [],
                    "model_preferences": {},
                    "performance_metrics": {},
                    "sessions_count": 1,
                    "cumulative_runtime": 0,
                    "last_session_start": time.time()
                }
                
                logger.info(f"Created new intelligence profile for {agent_id}")
                return default_intelligence
                
        except Exception as e:
            logger.error(f"Error restoring agent intelligence: {e}")
            return {
                "intelligence_level": 1.0,
                "learned_patterns": [],
                "successful_strategies": [],
                "task_completion_history": [],
                "optimization_insights": [],
                "collaborative_learnings": [],
                "model_preferences": {},
                "performance_metrics": {},
                "sessions_count": 1,
                "cumulative_runtime": 0,
                "last_session_start": time.time()
            }
    
    async def update_agent_learning(self, agent_id: str, learning_data: Dict[str, Any]) -> bool:
        """Update agent learning progress and intelligence"""
        try:
            async with self.memory_lock:
                if "agent_intelligence" not in self.memory_cache:
                    self.memory_cache["agent_intelligence"] = {}
                
                if agent_id not in self.memory_cache["agent_intelligence"]:
                    self.memory_cache["agent_intelligence"][agent_id] = await self.restore_agent_intelligence(agent_id)
                
                agent_intel = self.memory_cache["agent_intelligence"][agent_id]
                
                # Update intelligence level based on successful completions
                if learning_data.get("task_success", False):
                    current_level = agent_intel.get("intelligence_level", 1.0)
                    learning_boost = learning_data.get("complexity_factor", 0.1) * 0.05
                    agent_intel["intelligence_level"] = min(10.0, current_level + learning_boost)
                
                # Add learned patterns
                if "pattern" in learning_data:
                    patterns = agent_intel.get("learned_patterns", [])
                    if learning_data["pattern"] not in patterns:
                        patterns.append(learning_data["pattern"])
                        agent_intel["learned_patterns"] = patterns[-50:]  # Keep last 50
                
                # Add successful strategies
                if "strategy" in learning_data:
                    strategies = agent_intel.get("successful_strategies", [])
                    if learning_data["strategy"] not in strategies:
                        strategies.append(learning_data["strategy"])
                        agent_intel["successful_strategies"] = strategies[-30:]  # Keep last 30
                
                # Update performance metrics
                if "metrics" in learning_data:
                    agent_intel["performance_metrics"].update(learning_data["metrics"])
                
                # Update collaborative learnings
                if "collaboration" in learning_data:
                    collaborations = agent_intel.get("collaborative_learnings", [])
                    collaborations.append({
                        "learning": learning_data["collaboration"],
                        "timestamp": time.time()
                    })
                    agent_intel["collaborative_learnings"] = collaborations[-20:]  # Keep last 20
                
                # Update task completion history
                if "task_result" in learning_data:
                    history = agent_intel.get("task_completion_history", [])
                    history.append({
                        "task": learning_data["task_result"],
                        "success": learning_data.get("task_success", False),
                        "timestamp": time.time()
                    })
                    agent_intel["task_completion_history"] = history[-100:]  # Keep last 100
                
                agent_intel["last_update"] = time.time()
                
                # Save updated intelligence
                await self.store_agent_intelligence(agent_id, agent_intel)
                
                logger.debug(f"Updated learning for {agent_id} - New level: {agent_intel['intelligence_level']:.2f}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating agent learning: {e}")
            return False
    
    async def get_agent_intelligence_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get a summary of agent's intelligence and learning progress"""
        try:
            if "agent_intelligence" not in self.memory_cache:
                await self.restore_agent_intelligence(agent_id)
            
            if agent_id in self.memory_cache.get("agent_intelligence", {}):
                intel_data = self.memory_cache["agent_intelligence"][agent_id]
                
                return {
                    "agent_id": agent_id,
                    "intelligence_level": intel_data.get("intelligence_level", 1.0),
                    "sessions_completed": intel_data.get("sessions_count", 1),
                    "patterns_learned": len(intel_data.get("learned_patterns", [])),
                    "strategies_mastered": len(intel_data.get("successful_strategies", [])),
                    "tasks_completed": len(intel_data.get("task_completion_history", [])),
                    "collaborations": len(intel_data.get("collaborative_learnings", [])),
                    "cumulative_runtime": intel_data.get("cumulative_runtime", 0),
                    "last_active": intel_data.get("last_update", 0),
                    "performance_score": intel_data.get("performance_metrics", {}).get("avg_success_rate", 0.0)
                }
            else:
                return {
                    "agent_id": agent_id,
                    "intelligence_level": 1.0,
                    "sessions_completed": 0,
                    "patterns_learned": 0,
                    "strategies_mastered": 0,
                    "tasks_completed": 0,
                    "collaborations": 0,
                    "cumulative_runtime": 0,
                    "last_active": 0,
                    "performance_score": 0.0
                }
                
        except Exception as e:
            logger.error(f"Error getting intelligence summary: {e}")
            return {}