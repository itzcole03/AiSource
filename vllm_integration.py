#!/usr/bin/env python3
"""
vLLM Integration Module for Ultimate Copilot Dashboard

A simplified vLLM integration that provides model discovery, status monitoring,
and basic control capabilities for the Ultimate Copilot dashboard.
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import requests

logger = logging.getLogger(__name__)

@dataclass
class VLLMModelInfo:
    """Information about a vLLM model"""
    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = "vllm"
    permission: List[Any] = field(default_factory=list)

@dataclass 
class VLLMServerStatus:
    """Status information for vLLM server"""
    is_online: bool = False
    base_url: str = "http://localhost:8000"
    models: List[VLLMModelInfo] = field(default_factory=list)
    last_check: Optional[datetime] = None
    response_time: float = 0.0
    error_message: str = ""
    
    def __post_init__(self):
        if self.last_check is None:
            self.last_check = datetime.now()

class VLLMManager:
    """Simplified vLLM manager for dashboard integration"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.status = VLLMServerStatus(base_url=base_url)
        self.logger = logging.getLogger("VLLMManager")
        
    async def check_status(self) -> VLLMServerStatus:
        """Check vLLM server status and discover models"""
        start_time = time.time()
        
        try:
            # Check if server is responding
            async with aiohttp.ClientSession() as session:
                # First try health endpoint if available
                try:
                    async with session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=3)) as response:
                        if response.status != 200:
                            self.status.is_online = False
                            return self.status
                except:
                    # Health endpoint might not exist, continue to models check
                    pass
                
                # Check models endpoint
                async with session.get(f"{self.base_url}/v1/models", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        models_data = data.get('data', [])
                        
                        # Parse models
                        models = []
                        for model_data in models_data:
                            model = VLLMModelInfo(
                                id=model_data.get('id', 'unknown'),
                                object=model_data.get('object', 'model'),
                                created=model_data.get('created', 0),
                                owned_by=model_data.get('owned_by', 'vllm'),
                                permission=model_data.get('permission', [])
                            )
                            models.append(model)
                        
                        # Update status
                        self.status.is_online = True
                        self.status.models = models
                        self.status.response_time = time.time() - start_time
                        self.status.error_message = ""
                        self.status.last_check = datetime.now()
                        
                        self.logger.info(f"vLLM server online with {len(models)} model(s)")
                        
                    else:
                        self.status.is_online = False
                        self.status.error_message = f"HTTP {response.status}"
                        
        except asyncio.TimeoutError:
            self.status.is_online = False
            self.status.error_message = "Connection timeout"
            self.logger.warning("vLLM server timeout")
            
        except Exception as e:
            self.status.is_online = False
            self.status.error_message = str(e)
            self.logger.warning(f"vLLM check failed: {e}")
        
        self.status.last_check = datetime.now()
        return self.status
    
    def check_status_sync(self) -> VLLMServerStatus:
        """Synchronous version of status check for non-async contexts"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models_data = data.get('data', [])
                
                models = []
                for model_data in models_data:
                    model = VLLMModelInfo(
                        id=model_data.get('id', 'unknown'),
                        object=model_data.get('object', 'model'),
                        created=model_data.get('created', 0),
                        owned_by=model_data.get('owned_by', 'vllm'),
                        permission=model_data.get('permission', [])
                    )
                    models.append(model)
                
                self.status.is_online = True
                self.status.models = models
                self.status.error_message = ""
                
            else:
                self.status.is_online = False
                self.status.error_message = f"HTTP {response.status_code}"
                
        except requests.RequestException as e:
            self.status.is_online = False
            self.status.error_message = str(e)
            
        self.status.last_check = datetime.now()
        return self.status
    
    async def test_model_response(self, model_id: str, test_prompt: str = "Hello") -> Dict[str, Any]:
        """Test if a specific model can respond"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": test_prompt}],
                    "max_tokens": 5,
                    "temperature": 0
                }
                
                start_time = time.time()
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_time = time.time() - start_time
                        
                        return {
                            "success": True,
                            "response_time": response_time,
                            "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                            "model": model_id
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "model": model_id
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_id
            }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get formatted data for dashboard display"""
        return {
            "status": "running" if self.status.is_online else "not_running",
            "base_url": self.base_url,
            "models": [model.id for model in self.status.models],
            "model_count": len(self.status.models),
            "last_check": self.status.last_check.isoformat() if self.status.last_check else None,
            "response_time": round(self.status.response_time * 1000, 2),  # Convert to ms
            "error_message": self.status.error_message,
            "memory_usage": 0.0  # vLLM doesn't expose memory usage easily
        }
    
    def get_models_list(self) -> List[str]:
        """Get list of available model IDs"""
        return [model.id for model in self.status.models]
    
    def is_healthy(self) -> bool:
        """Check if vLLM server is healthy"""
        return self.status.is_online and len(self.status.models) > 0

# Global instance for easy access
vllm_manager = VLLMManager()

# Convenience functions for integration
async def get_vllm_status() -> Dict[str, Any]:
    """Get current vLLM status for dashboard"""
    await vllm_manager.check_status()
    return vllm_manager.get_dashboard_data()

def get_vllm_status_sync() -> Dict[str, Any]:
    """Get current vLLM status synchronously"""
    vllm_manager.check_status_sync()
    return vllm_manager.get_dashboard_data()

async def test_vllm_connection() -> bool:
    """Test if vLLM is accessible"""
    await vllm_manager.check_status()
    return vllm_manager.is_healthy()

if __name__ == "__main__":
    # Simple test
    async def test():
        print("Testing vLLM connection...")
        status = await vllm_manager.check_status()
        print(f"Status: {'Online' if status.is_online else 'Offline'}")
        print(f"Models: {[m.id for m in status.models]}")
        
        if status.is_online and status.models:
            print("Testing model response...")
            test_result = await vllm_manager.test_model_response(status.models[0].id)
            print(f"Test result: {test_result}")
    
    asyncio.run(test())
