"""EnhancedLLMManager — Routes tasks to best available LLM based on role and resource"""

import logging
from typing import Dict

class EnhancedLLMManager:
    def __init__(self, models_config: Dict):
        self.models_config = models_config
        self.logger = logging.getLogger("EnhancedLLMManager")
        self.model_map = {}

    async def initialize(self):
        self.logger.info("Initializing LLM Manager...")
        self._route_models()

    def _route_models(self):
        for role, conf in self.models_config.get("agents", {}).items():
            primary = conf.get("primary_models", [])
            fallback = conf.get("fallback_models", [])
            self.model_map[role] = primary[0] if primary else (fallback[0] if fallback else "default-model")
            self.logger.info(f"Role {role} -> Model: {self.model_map[role]}")

    def get_model_for_role(self, role: str) -> str:
        return self.model_map.get(role, "default-model")

    async def shutdown(self):
        self.logger.info("LLM Manager shutdown complete.")
