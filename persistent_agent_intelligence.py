#!/usr/bin/env python3
"""
Persistent Agent Intelligence System

This system enables agents to accumulate knowledge, patterns, and expertise
across all projects they work on, creating truly intelligent and experienced agents.
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import sqlite3
import pickle
from pathlib import Path

class ExperienceType(Enum):
    SOLUTION_PATTERN = "solution_pattern"
    ERROR_RESOLUTION = "error_resolution"
    OPTIMIZATION = "optimization"
    WORKFLOW = "workflow"
    ARCHITECTURE = "architecture"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    INTEGRATION = "integration"

@dataclass
class Experience:
    """Represents a learned experience from a project"""
    id: str
    agent_role: str
    experience_type: ExperienceType
    context: str  # What situation/problem this applies to
    solution: str  # What the agent did/learned
    outcome: str  # What was the result
    confidence: float  # How confident the agent is in this experience (0-1)
    project_context: Dict[str, Any]  # Programming language, framework, etc.
    timestamp: datetime
    usage_count: int = 0
    success_rate: float = 1.0
    tags: Set[str] = field(default_factory=set)

@dataclass
class ProjectLearning:
    """Learning accumulated from a specific project"""
    project_id: str
    workspace_path: str
    technologies: Set[str]
    patterns_discovered: List[str]
    challenges_overcome: List[str]
    successful_strategies: List[str]
    timestamp: datetime

class PersistentAgentIntelligence:
    """
    Manages persistent intelligence across all agent sessions and projects
    """
    
    def __init__(self, intelligence_dir: str = None):
        # Use a global intelligence directory that persists across workspaces
        if intelligence_dir is None:
            home_dir = Path.home()
            self.intelligence_dir = home_dir / ".ultimate_copilot" / "agent_intelligence"
        else:
            self.intelligence_dir = Path(intelligence_dir)
        
        self.intelligence_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database for persistent storage
        self.db_path = self.intelligence_dir / "agent_intelligence.db"
        self._init_database()
        
        # In-memory cache for faster access
        self.experience_cache: Dict[str, List[Experience]] = {}
        self.project_patterns: Dict[str, List[str]] = {}
        
        # Load existing intelligence
        self._load_intelligence()
    
    def _init_database(self):
        """Initialize SQLite database for persistent storage"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Experiences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiences (
                id TEXT PRIMARY KEY,
                agent_role TEXT NOT NULL,
                experience_type TEXT NOT NULL,
                context TEXT NOT NULL,
                solution TEXT NOT NULL,
                outcome TEXT NOT NULL,
                confidence REAL NOT NULL,
                project_context TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                tags TEXT DEFAULT ''
            )
        """)
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                workspace_path TEXT NOT NULL,
                technologies TEXT NOT NULL,
                patterns_discovered TEXT NOT NULL,
                challenges_overcome TEXT NOT NULL,
                successful_strategies TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Agent performance tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_performance (
                agent_role TEXT NOT NULL,
                project_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                avg_completion_time REAL DEFAULT 0.0,
                last_updated TEXT NOT NULL,
                PRIMARY KEY (agent_role, project_id, task_type)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_intelligence(self):
        """Load existing intelligence from database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Load experiences
        cursor.execute("SELECT * FROM experiences")
        for row in cursor.fetchall():
            exp = Experience(
                id=row[0],
                agent_role=row[1],
                experience_type=ExperienceType(row[2]),
                context=row[3],
                solution=row[4],
                outcome=row[5],
                confidence=row[6],
                project_context=json.loads(row[7]),
                timestamp=datetime.fromisoformat(row[8]),
                usage_count=row[9],
                success_rate=row[10],
                tags=set(row[11].split(',')) if row[11] else set()
            )
            
            if exp.agent_role not in self.experience_cache:
                self.experience_cache[exp.agent_role] = []
            self.experience_cache[exp.agent_role].append(exp)
        
        conn.close()
    
    def record_experience(self, agent_role: str, experience_type: ExperienceType, 
                         context: str, solution: str, outcome: str, 
                         project_context: Dict[str, Any], confidence: float = 0.8,
                         tags: Set[str] = None) -> str:
        """Record a new experience for an agent"""
        
        # Create unique ID based on content
        content_hash = hashlib.md5(f"{agent_role}:{context}:{solution}".encode()).hexdigest()
        exp_id = f"{agent_role}_{experience_type.value}_{content_hash[:8]}"
        
        experience = Experience(
            id=exp_id,
            agent_role=agent_role,
            experience_type=experience_type,
            context=context,
            solution=solution,
            outcome=outcome,
            confidence=confidence,
            project_context=project_context,
            timestamp=datetime.now(),
            tags=tags or set()
        )
        
        # Save to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO experiences 
            (id, agent_role, experience_type, context, solution, outcome, 
             confidence, project_context, timestamp, usage_count, success_rate, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            experience.id, experience.agent_role, experience.experience_type.value,
            experience.context, experience.solution, experience.outcome,
            experience.confidence, json.dumps(experience.project_context),
            experience.timestamp.isoformat(), experience.usage_count,
            experience.success_rate, ','.join(experience.tags)
        ))
        
        conn.commit()
        conn.close()
        
        # Update cache
        if agent_role not in self.experience_cache:
            self.experience_cache[agent_role] = []
        self.experience_cache[agent_role].append(experience)
        
        return exp_id
    
    def get_relevant_experiences(self, agent_role: str, context: str, 
                               experience_types: List[ExperienceType] = None,
                               project_context: Dict[str, Any] = None,
                               limit: int = 10) -> List[Experience]:
        """Get relevant experiences for a given context"""
        
        experiences = self.experience_cache.get(agent_role, [])
        
        if not experiences:
            return []
        
        # Filter by experience type if specified
        if experience_types:
            experiences = [exp for exp in experiences if exp.experience_type in experience_types]
        
        # Score experiences by relevance
        scored_experiences = []
        context_words = set(context.lower().split())
        
        for exp in experiences:
            score = 0.0
            
            # Context similarity
            exp_context_words = set(exp.context.lower().split())
            context_overlap = len(context_words.intersection(exp_context_words))
            score += context_overlap * 2.0
            
            # Project context similarity
            if project_context and exp.project_context:
                for key, value in project_context.items():
                    if key in exp.project_context and exp.project_context[key] == value:
                        score += 3.0
            
            # Confidence and success rate
            score += exp.confidence * 2.0
            score += exp.success_rate * 2.0
            
            # Usage frequency (popular solutions)
            score += min(exp.usage_count * 0.1, 2.0)
            
            # Recency bonus
            days_old = (datetime.now() - exp.timestamp).days
            recency_bonus = max(0, 2.0 - (days_old * 0.01))
            score += recency_bonus
            
            scored_experiences.append((score, exp))
        
        # Sort by score and return top results
        scored_experiences.sort(key=lambda x: x[0], reverse=True)
        return [exp for score, exp in scored_experiences[:limit]]
    
    def record_project_completion(self, project_id: str, workspace_path: str,
                                technologies: Set[str], patterns_discovered: List[str],
                                challenges_overcome: List[str], 
                                successful_strategies: List[str]):
        """Record completion of a project with learnings"""
        
        project_learning = ProjectLearning(
            project_id=project_id,
            workspace_path=workspace_path,
            technologies=technologies,
            patterns_discovered=patterns_discovered,
            challenges_overcome=challenges_overcome,
            successful_strategies=successful_strategies,
            timestamp=datetime.now()
        )
        
        # Save to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO projects 
            (project_id, workspace_path, technologies, patterns_discovered,
             challenges_overcome, successful_strategies, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_learning.project_id, project_learning.workspace_path,
            json.dumps(list(project_learning.technologies)),
            json.dumps(project_learning.patterns_discovered),
            json.dumps(project_learning.challenges_overcome),
            json.dumps(project_learning.successful_strategies),
            project_learning.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def update_experience_success(self, experience_id: str, was_successful: bool):
        """Update the success rate of an experience based on usage outcome"""
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get current stats
        cursor.execute("SELECT usage_count, success_rate FROM experiences WHERE id = ?", (experience_id,))
        result = cursor.fetchone()
        
        if result:
            usage_count, success_rate = result
            
            # Calculate new success rate
            total_successes = success_rate * usage_count
            new_usage_count = usage_count + 1
            
            if was_successful:
                total_successes += 1
            
            new_success_rate = total_successes / new_usage_count
            
            # Update database
            cursor.execute("""
                UPDATE experiences 
                SET usage_count = ?, success_rate = ?
                WHERE id = ?
            """, (new_usage_count, new_success_rate, experience_id))
            
            conn.commit()
        
        conn.close()
    
    def get_agent_expertise_summary(self, agent_role: str) -> Dict[str, Any]:
        """Get a summary of an agent's accumulated expertise"""
        
        experiences = self.experience_cache.get(agent_role, [])
        
        if not experiences:
            return {"expertise_level": "novice", "experience_count": 0}
        
        # Calculate expertise metrics
        total_experiences = len(experiences)
        avg_confidence = sum(exp.confidence for exp in experiences) / total_experiences
        avg_success_rate = sum(exp.success_rate for exp in experiences) / total_experiences
        total_usage = sum(exp.usage_count for exp in experiences)
        
        # Categorize experience types
        type_counts = {}
        for exp in experiences:
            exp_type = exp.experience_type.value
            type_counts[exp_type] = type_counts.get(exp_type, 0) + 1
        
        # Extract technologies/domains
        technologies = set()
        for exp in experiences:
            if 'language' in exp.project_context:
                technologies.add(exp.project_context['language'])
            if 'framework' in exp.project_context:
                technologies.add(exp.project_context['framework'])
        
        # Determine expertise level
        if total_experiences < 10:
            expertise_level = "novice"
        elif total_experiences < 50:
            expertise_level = "intermediate"
        elif total_experiences < 200:
            expertise_level = "advanced"
        else:
            expertise_level = "expert"
        
        return {
            "expertise_level": expertise_level,
            "experience_count": total_experiences,
            "average_confidence": avg_confidence,
            "average_success_rate": avg_success_rate,
            "total_usage": total_usage,
            "specializations": type_counts,
            "technologies": list(technologies),
            "most_successful_patterns": [
                exp.solution for exp in sorted(experiences, key=lambda x: x.success_rate, reverse=True)[:5]
            ]
        }
    
    def suggest_approach(self, agent_role: str, task_description: str, 
                        project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest an approach based on accumulated experience"""
        
        relevant_experiences = self.get_relevant_experiences(
            agent_role, task_description, project_context=project_context, limit=5
        )
        
        if not relevant_experiences:
            return {
                "suggestion": "No relevant experience found. Proceed with standard approach.",
                "confidence": 0.3,
                "experiences_used": []
            }
        
        # Combine experiences into a suggestion
        suggestions = []
        total_confidence = 0.0
        
        for exp in relevant_experiences:
            suggestions.append({
                "pattern": exp.solution,
                "context": exp.context,
                "outcome": exp.outcome,
                "confidence": exp.confidence,
                "success_rate": exp.success_rate
            })
            total_confidence += exp.confidence * exp.success_rate
        
        avg_confidence = total_confidence / len(relevant_experiences)
        
        # Generate combined approach
        approach_elements = []
        for exp in relevant_experiences[:3]:  # Top 3 most relevant
            approach_elements.append(f"- {exp.solution} (based on: {exp.context})")
        
        combined_suggestion = "Based on previous experience:\n" + "\n".join(approach_elements)
        
        return {
            "suggestion": combined_suggestion,
            "confidence": avg_confidence,
            "experiences_used": [exp.id for exp in relevant_experiences],
            "detailed_experiences": suggestions
        }
    
    def export_intelligence(self, export_path: str):
        """Export agent intelligence for backup or sharing"""
        export_data = {
            "experiences": {},
            "projects": [],
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Export experiences
        for agent_role, experiences in self.experience_cache.items():
            export_data["experiences"][agent_role] = [
                asdict(exp) for exp in experiences
            ]
        
        # Export projects from database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects")
        
        for row in cursor.fetchall():
            export_data["projects"].append({
                "project_id": row[0],
                "workspace_path": row[1],
                "technologies": json.loads(row[2]),
                "patterns_discovered": json.loads(row[3]),
                "challenges_overcome": json.loads(row[4]),
                "successful_strategies": json.loads(row[5]),
                "timestamp": row[6]
            })
        
        conn.close()
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)

def test_persistent_intelligence():
    """Test the persistent intelligence system"""
    print("Testing Persistent Agent Intelligence System...")
    
    intelligence = PersistentAgentIntelligence()
    
    # Record some test experiences
    project_context = {
        "language": "python",
        "framework": "fastapi",
        "project_type": "web_api"
    }
    
    # Architect experience
    arch_exp_id = intelligence.record_experience(
        agent_role="architect",
        experience_type=ExperienceType.ARCHITECTURE,
        context="Designing REST API with authentication",
        solution="Use JWT tokens with refresh mechanism, implement middleware for route protection",
        outcome="Successfully implemented secure API with 99.9% uptime",
        project_context=project_context,
        confidence=0.9,
        tags={"api", "security", "jwt"}
    )
    
    # Developer experience
    dev_exp_id = intelligence.record_experience(
        agent_role="developer",
        experience_type=ExperienceType.SOLUTION_PATTERN,
        context="Implementing database connection pooling in FastAPI",
        solution="Use SQLAlchemy with connection pooling, implement proper session management",
        outcome="Reduced database connection overhead by 40%",
        project_context=project_context,
        confidence=0.85,
        tags={"database", "performance", "sqlalchemy"}
    )
    
    print(f"✓ Recorded architect experience: {arch_exp_id}")
    print(f"✓ Recorded developer experience: {dev_exp_id}")
    
    # Test getting relevant experiences
    relevant = intelligence.get_relevant_experiences(
        agent_role="architect",
        context="Building secure web API",
        project_context=project_context
    )
    
    print(f"✓ Found {len(relevant)} relevant experiences for architect")
    
    # Test suggestion system
    suggestion = intelligence.suggest_approach(
        agent_role="developer",
        task_description="Need to optimize database performance",
        project_context=project_context
    )
    
    print(f"✓ Generated suggestion with confidence: {suggestion['confidence']:.2f}")
    print(f"Suggestion: {suggestion['suggestion']}")
    
    # Test expertise summary
    expertise = intelligence.get_agent_expertise_summary("architect")
    print(f"✓ Architect expertise level: {expertise['expertise_level']}")
    print(f"Experience count: {expertise['experience_count']}")
    
    return True

if __name__ == "__main__":
    test_persistent_intelligence()
