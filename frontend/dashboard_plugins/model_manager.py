#!/usr/bin/env python3
"""
Model Manager Plugin

Provides model provider management and control for the Ultimate Copilot Dashboard.
"""

import asyncio
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_plugin import StreamlitPlugin

class ModelManagerPlugin(StreamlitPlugin):
    """Model management and provider control plugin"""
    
    def __init__(self, name: str = "model_manager", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.supported_providers = ["ollama", "lmstudio", "vllm", "openai"]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            "name": "Model Manager",
            "version": "2.0.0",
            "description": "Model provider management and control",
            "author": "Ultimate Copilot",
            "capabilities": [
                "provider_status",
                "model_listing",
                "model_loading",
                "provider_control"
            ]
        }
    
    async def update_data(self) -> Dict[str, Any]:
        """Update model management data"""
        try:
            # Get model status from API
            model_status = await self.fetch_api_data("/models/status")
            
            # Store in cache
            if model_status:
                self.cache_data("model_status", model_status)
            
            return {"model_status": model_status}
            
        except Exception as e:
            self.log_error(f"Failed to update model data: {e}")
            return {"error": str(e)}
    
    def render(self, container) -> None:
        """Render model management UI"""
        with container:
            self.render_header("Model Management", "🤖")
            
            # Get cached data
            model_status = self.get_cached_data("model_status", 30)
            
            if not model_status:
                st.error("Unable to fetch model status")
                return
            
            # Provider overview
            self.render_provider_overview(model_status)
            
            # Model details
            self.render_model_details(model_status)
            
            # Model controls
            self.render_model_controls()
    
    def render_provider_overview(self, model_status: Dict[str, Any]) -> None:
        """Render provider status overview"""
        st.subheader("Provider Status")
        
        # Provider status cards
        providers = []
        for provider_name in self.supported_providers:
            provider_data = model_status.get(provider_name, {})
            status = provider_data.get("status", "unknown")
            models_count = len(provider_data.get("models", []))
            memory_usage = provider_data.get("memory_usage", 0)
            
            providers.append({
                "Provider": provider_name.title(),
                "Status": status,
                "Models": models_count,
                "Memory (GB)": f"{memory_usage:.1f}"
            })
        
        # Display as metrics
        cols = st.columns(len(self.supported_providers))
        for i, provider in enumerate(providers):
            with cols[i]:
                status = provider["Status"]
                if status == "running":
                    st.success(f"🟢 {provider['Provider']}")
                elif status == "not_running":
                    st.error(f"🔴 {provider['Provider']}")
                else:
                    st.warning(f"🟡 {provider['Provider']}")
                
                st.metric("Models", provider["Models"])
                st.metric("Memory", provider["Memory (GB)"])
        
        # Provider table
        st.markdown("**Provider Details**")
        df = pd.DataFrame(providers)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    def render_model_details(self, model_status: Dict[str, Any]) -> None:
        """Render detailed model information"""
        st.subheader("Model Details")
        
        # Provider selection
        available_providers = [p for p in self.supported_providers 
                             if p in model_status and model_status[p].get("status") == "running"]
        
        if not available_providers:
            st.warning("No providers are currently running")
            return
        
        selected_provider = st.selectbox("Select Provider", available_providers)
        
        if selected_provider:
            provider_data = model_status[selected_provider]
            models = provider_data.get("models", [])
            
            if models:
                st.markdown(f"**{selected_provider.title()} Models**")
                
                # Model information
                model_data = []
                for model in models:
                    if isinstance(model, str):
                        model_data.append({
                            "Model": model,
                            "Status": "Available",
                            "Size": "Unknown"
                        })
                    elif isinstance(model, dict):
                        model_data.append({
                            "Model": model.get("name", "Unknown"),
                            "Status": model.get("status", "Unknown"),
                            "Size": model.get("size", "Unknown")
                        })
                
                if model_data:
                    df = pd.DataFrame(model_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info(f"No models found for {selected_provider}")
    
    def render_model_controls(self) -> None:
        """Render model control interface"""
        st.subheader("Model Controls")
        
        with st.expander("Load/Unload Models"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Load Model**")
                provider = st.selectbox("Provider", self.supported_providers, key="load_provider")
                model_name = st.text_input("Model Name", key="load_model")
                
                if st.button("Load Model", use_container_width=True):
                    if provider and model_name:
                        result = asyncio.run(self.send_api_command("/models/control", {
                            "provider": provider,
                            "model": model_name,
                            "action": "load"
                        }))
                        if result and result.get("status") == "success":
                            st.success(f"Loading {model_name} on {provider}")
                        else:
                            st.error("Failed to load model")
                    else:
                        st.error("Please specify provider and model name")
            
            with col2:
                st.markdown("**Unload Model**")
                provider = st.selectbox("Provider", self.supported_providers, key="unload_provider")
                model_name = st.text_input("Model Name", key="unload_model")
                
                if st.button("Unload Model", use_container_width=True):
                    if provider and model_name:
                        result = asyncio.run(self.send_api_command("/models/control", {
                            "provider": provider,
                            "model": model_name,
                            "action": "unload"
                        }))
                        if result and result.get("status") == "success":
                            st.success(f"Unloading {model_name} from {provider}")
                        else:
                            st.error("Failed to unload model")
                    else:
                        st.error("Please specify provider and model name")
        
        with st.expander("Provider Controls"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Start Provider**")
                start_provider = st.selectbox("Provider", self.supported_providers, key="start_provider")
                if st.button("Start Provider", use_container_width=True):
                    st.info(f"Starting {start_provider} (manual start required)")
            
            with col2:
                st.markdown("**Stop Provider**")
                stop_provider = st.selectbox("Provider", self.supported_providers, key="stop_provider")
                if st.button("Stop Provider", use_container_width=True):
                    st.warning(f"Stopping {stop_provider} (manual stop required)")
            
            with col3:
                st.markdown("**Refresh Status**")
                st.write("")  # Spacing
                if st.button("Refresh All", use_container_width=True):
                    self._data_cache.clear()
                    st.rerun()
        
        # Quick model selection
        st.subheader("Quick Model Selection")
        
        # Common models for quick access
        common_models = {
            "ollama": ["llama3.2:3b", "phi:2.7b", "codellama:7b"],
            "lmstudio": ["phi-2", "llama-2-7b-chat", "code-llama-7b"],
            "vllm": ["microsoft/phi-2", "meta-llama/Llama-2-7b-chat-hf"]
        }
        
        for provider, models in common_models.items():
            with st.expander(f"Common {provider.title()} Models"):
                cols = st.columns(len(models))
                for i, model in enumerate(models):
                    with cols[i]:
                        if st.button(f"Load {model}", key=f"quick_{provider}_{model}"):
                            result = asyncio.run(self.send_api_command("/models/control", {
                                "provider": provider,
                                "model": model,
                                "action": "load"
                            }))
                            if result and result.get("status") == "success":
                                st.success(f"Loading {model}")
                            else:
                                st.error("Failed to load model")
    
    def get_provider_health(self, provider_data: Dict[str, Any]) -> str:
        """Get provider health status"""
        status = provider_data.get("status", "unknown")
        models = provider_data.get("models", [])
        
        if status == "running" and models:
            return "healthy"
        elif status == "running":
            return "running_no_models"
        elif status == "not_running":
            return "offline"
        else:
            return "unknown"
