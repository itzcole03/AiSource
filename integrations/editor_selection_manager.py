"""EditorSelectionManager — Detects active editor + workspace and prepares swarm context"""

import logging
import os
from typing import Dict

class EditorSelectionManager:
    def __init__(self, config: Dict, void_integration: bool = True):
        self.config = config
        self.void_integration = void_integration
        self.logger = logging.getLogger("EditorSelectionManager")

    async def initialize(self):
        self.logger.info("Detecting active editor and workspace...")
        editor = self._detect_editor()
        workspace = self._detect_workspace()

        self.logger.info(f"Editor Detected: {editor}")
        self.logger.info(f"Workspace: {workspace}")

        self.config["editor"] = editor
        self.config["workspace"] = workspace

    def _detect_editor(self) -> str:
        if self.void_integration:
            return "Void"
        # Check for VS Code Insiders
        if "VSCODE_IPC_HOOK" in os.environ:
            return "VSCode Insiders"
        return "Unknown"

    def _detect_workspace(self) -> str:
        # Assume current working directory is root workspace
        return os.getcwd()

    async def shutdown(self):
        self.logger.info("Editor manager cleanup complete.")
