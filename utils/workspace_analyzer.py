"""
Advanced Workspace Analyzer
Provides detailed analysis of project workspaces for the Ultimate Copilot system.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class WorkspaceAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger("WorkspaceAnalyzer")
        
    def analyze_workspace(self, workspace_path: str) -> Dict[str, Any]:
        """Comprehensive workspace analysis"""
        if not os.path.exists(workspace_path):
            return {"error": "Workspace path does not exist"}
            
        analysis = {
            "path": workspace_path,
            "timestamp": str(os.path.getctime(workspace_path)),
            "project_type": self._detect_project_type(workspace_path),
            "structure": self._analyze_structure(workspace_path),
            "dependencies": self._analyze_dependencies(workspace_path),
            "size_info": self._get_size_info(workspace_path),
            "languages": self._detect_languages(workspace_path),
            "recommendations": []
        }
        
        analysis["recommendations"] = self._generate_recommendations(analysis)
        return analysis
    
    def _detect_project_type(self, workspace_path: str) -> Dict[str, Any]:
        """Detect project type based on files and structure"""
        project_types = {
            "python": {
                "files": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
                "extensions": [".py"],
                "confidence": 0
            },
            "javascript": {
                "files": ["package.json", "package-lock.json", "yarn.lock"],
                "extensions": [".js", ".jsx", ".ts", ".tsx"],
                "confidence": 0
            },
            "react": {
                "files": ["package.json"],
                "dependencies": ["react", "react-dom"],
                "confidence": 0
            },
            "docker": {
                "files": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
                "confidence": 0
            }
        }
        
        # Check files and calculate confidence
        for project_type, criteria in project_types.items():
            for file in criteria.get("files", []):
                if os.path.exists(os.path.join(workspace_path, file)):
                    project_types[project_type]["confidence"] += 30
                    
        # Check for extensions
        for root, dirs, files in os.walk(workspace_path):
            if any(ignore in root for ignore in ['.git', 'node_modules', '__pycache__', '.venv']):
                continue
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                for project_type, criteria in project_types.items():
                    if ext in criteria.get("extensions", []):
                        project_types[project_type]["confidence"] += 5
        
        # Find most likely project type
        best_match = max(project_types.items(), key=lambda x: x[1]["confidence"])
        
        return {
            "primary": best_match[0] if best_match[1]["confidence"] > 0 else "unknown",
            "confidence": best_match[1]["confidence"],
            "all_matches": {k: v["confidence"] for k, v in project_types.items() if v["confidence"] > 0}
        }
    
    def _analyze_structure(self, workspace_path: str) -> Dict[str, Any]:
        """Analyze directory structure"""
        structure = {
            "total_files": 0,
            "total_directories": 0,
            "file_types": {},
            "large_files": []
        }
        
        for root, dirs, files in os.walk(workspace_path):
            structure["total_directories"] += len(dirs)
            structure["total_files"] += len(files)
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                else:
                    structure["file_types"]["no_extension"] = structure["file_types"].get("no_extension", 0) + 1
                
                # Check file size
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    if size > 10 * 1024 * 1024:  # Files larger than 10MB
                        rel_path = os.path.relpath(file_path, workspace_path)
                        structure["large_files"].append({
                            "path": rel_path,
                            "size_mb": round(size / (1024 * 1024), 2)
                        })
                except OSError:
                    pass
        
        return structure
    
    def _analyze_dependencies(self, workspace_path: str) -> Dict[str, Any]:
        """Analyze project dependencies"""
        dependencies = {}
        
        # Python dependencies
        requirements_files = ["requirements.txt", "requirements-dev.txt", "requirements-prod.txt"]
        for req_file in requirements_files:
            req_path = os.path.join(workspace_path, req_file)
            if os.path.exists(req_path):
                try:
                    with open(req_path, 'r') as f:
                        deps = []
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                deps.append(line.split('==')[0].split('>=')[0].split('<=')[0])
                        dependencies[req_file] = deps
                except Exception:
                    pass
        
        # Node.js dependencies
        package_json_path = os.path.join(workspace_path, "package.json")
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    dependencies["package.json"] = {
                        "dependencies": list(package_data.get("dependencies", {}).keys()),
                        "devDependencies": list(package_data.get("devDependencies", {}).keys())
                    }
            except Exception:
                pass
        
        return dependencies
    
    def _get_size_info(self, workspace_path: str) -> Dict[str, Any]:
        """Get workspace size information"""
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(workspace_path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    size = os.path.getsize(file_path)
                    total_size += size
                    file_count += 1
                except OSError:
                    pass
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count
        }
    
    def _detect_languages(self, workspace_path: str) -> Dict[str, int]:
        """Detect programming languages used"""
        language_extensions = {
            "Python": [".py", ".pyw", ".pyx"],
            "JavaScript": [".js", ".jsx"],
            "TypeScript": [".ts", ".tsx"],
            "HTML": [".html", ".htm"],
            "CSS": [".css", ".scss", ".sass", ".less"],
            "JSON": [".json"],
            "YAML": [".yml", ".yaml"],
            "XML": [".xml"],
            "Markdown": [".md", ".markdown"]
        }
        
        language_counts = {}
        
        for root, dirs, files in os.walk(workspace_path):
            if any(ignore in root for ignore in ['.git', 'node_modules', '__pycache__', '.venv']):
                continue
                
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                for language, extensions in language_extensions.items():
                    if ext in extensions:
                        language_counts[language] = language_counts.get(language, 0) + 1
        
        return language_counts
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        project_type = analysis.get("project_type", {}).get("primary", "unknown")
        structure = analysis.get("structure", {})
        
        # Large files recommendation
        large_files = structure.get("large_files", [])
        if large_files:
            recommendations.append(f"Found {len(large_files)} large files - consider optimization")
        
        # Project-specific recommendations
        if project_type == "python":
            if "requirements.txt" not in str(analysis.get("dependencies", {})):
                recommendations.append("Consider creating a requirements.txt file for Python dependencies")
        elif project_type == "javascript":
            try:
                gitignore_exists = os.path.exists(os.path.join(analysis["path"], ".gitignore"))
                if not gitignore_exists:
                    recommendations.append("Consider adding a .gitignore file for Node.js projects")
            except Exception:
                pass
        
        return recommendations

    def quick_scan(self, workspace_path: str) -> Dict[str, Any]:
        """Quick workspace scan for basic info"""
        if not os.path.exists(workspace_path):
            return {"error": "Workspace path does not exist"}
        
        file_count = 0
        dir_count = 0
        size = 0
        
        try:
            for root, dirs, files in os.walk(workspace_path):
                dir_count += len(dirs)
                file_count += len(files)
                for file in files:
                    try:
                        size += os.path.getsize(os.path.join(root, file))
                    except OSError:
                        pass
        except Exception as e:
            return {"error": str(e)}
        
        return {
            "path": workspace_path,
            "file_count": file_count,
            "directory_count": dir_count,
            "total_size_mb": round(size / (1024 * 1024), 2),
            "project_type": self._detect_project_type(workspace_path)["primary"]
        }
