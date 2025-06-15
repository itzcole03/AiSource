#!/usr/bin/env python3
"""
Demo: Persistent Agent Intelligence Across Projects

This demonstrates how agents accumulate and apply intelligence across multiple projects,
becoming more capable and experienced over time.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
import sys

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from persistent_agent_intelligence import PersistentAgentIntelligence, ExperienceType

class MockAgent:
    """Mock agent for demonstration purposes"""
    
    def __init__(self, role: str, intelligence: PersistentAgentIntelligence):
        self.role = role
        self.intelligence = intelligence
        self.projects_worked_on = []
    
    async def work_on_project(self, project_name: str, project_context: dict, tasks: list):
        """Simulate working on a project and learning from it"""
        print(f"\n=== {self.role.upper()} working on {project_name} ===")
        
        self.projects_worked_on.append(project_name)
        
        # Get current expertise level
        expertise = self.intelligence.get_agent_expertise_summary(self.role)
        print(f"Starting expertise level: {expertise['expertise_level']} ({expertise['experience_count']} experiences)")
        
        # Work through tasks
        for task in tasks:
            await self._execute_task_with_learning(task, project_context)
        
        # Show improved expertise
        new_expertise = self.intelligence.get_agent_expertise_summary(self.role)
        print(f"Ending expertise level: {new_expertise['expertise_level']} ({new_expertise['experience_count']} experiences)")
        
        if new_expertise['experience_count'] > expertise['experience_count']:
            print(f"✓ Gained {new_expertise['experience_count'] - expertise['experience_count']} new experiences!")
    
    async def _execute_task_with_learning(self, task: dict, project_context: dict):
        """Execute a task and learn from it"""
        print(f"\n  Task: {task['description']}")
        
        # Get suggestion based on previous experience
        suggestion = self.intelligence.suggest_approach(
            agent_role=self.role,
            task_description=task['description'],
            project_context=project_context
        )
        
        if suggestion['confidence'] > 0.5:
            print(f"  💡 Applying learned approach (confidence: {suggestion['confidence']:.1%})")
            print(f"     {suggestion['suggestion'][:100]}...")
        else:
            print(f"  🆕 No relevant experience, learning new approach")
        
        # Simulate task execution and learning
        success = task.get('success', True)
        
        # Record the experience
        exp_id = self.intelligence.record_experience(
            agent_role=self.role,
            experience_type=ExperienceType(task['experience_type']),
            context=task['description'],
            solution=task['solution'],
            outcome=task['outcome'],
            project_context=project_context,
            confidence=task.get('confidence', 0.8),
            tags=set(task.get('tags', []))
        )
        
        # Update success rate for used experiences
        for used_exp_id in suggestion.get('experiences_used', []):
            self.intelligence.update_experience_success(used_exp_id, success)
        
        result_icon = "✓" if success else "✗"
        print(f"  {result_icon} {task['outcome']}")

async def simulate_multi_project_learning():
    """Simulate agents working across multiple projects and accumulating intelligence"""
    
    print("🚀 PERSISTENT AGENT INTELLIGENCE DEMONSTRATION")
    print("=" * 60)
    print("This demo shows how agents become smarter across multiple projects")
    
    # Initialize intelligence system
    intelligence = PersistentAgentIntelligence()
    
    # Create agents
    architect = MockAgent("architect", intelligence)
    developer = MockAgent("developer", intelligence)
    
    # === PROJECT 1: E-commerce API ===
    ecommerce_context = {
        "project_name": "ecommerce_api",
        "language": "python",
        "framework": "fastapi",
        "project_type": "web_api"
    }
    
    ecommerce_tasks = [
        {
            "description": "Design REST API architecture for e-commerce platform",
            "experience_type": "architecture",
            "solution": "Use microservices architecture with API Gateway, separate services for users, products, orders",
            "outcome": "Created scalable architecture supporting 10k concurrent users",
            "success": True,
            "confidence": 0.9,
            "tags": ["microservices", "api_gateway", "scalability"]
        },
        {
            "description": "Implement user authentication and authorization",
            "experience_type": "solution_pattern",
            "solution": "JWT tokens with refresh mechanism, role-based access control using decorators",
            "outcome": "Secure authentication system with 99.9% uptime",
            "success": True,
            "confidence": 0.85,
            "tags": ["jwt", "rbac", "security"]
        }
    ]
    
    developer_ecommerce_tasks = [
        {
            "description": "Implement database connection pooling for high performance",
            "experience_type": "optimization",
            "solution": "SQLAlchemy with asyncpg, connection pool size 20, proper session management",
            "outcome": "Reduced database response time by 40%",
            "success": True,
            "confidence": 0.8,
            "tags": ["database", "performance", "sqlalchemy"]
        },
        {
            "description": "Add Redis caching for frequently accessed data",
            "experience_type": "optimization",
            "solution": "Redis with automatic cache invalidation, TTL-based expiry",
            "outcome": "Improved API response time by 60%",
            "success": True,
            "confidence": 0.9,
            "tags": ["redis", "caching", "performance"]
        }
    ]
    
    await architect.work_on_project("E-commerce API", ecommerce_context, ecommerce_tasks)
    await developer.work_on_project("E-commerce API", ecommerce_context, developer_ecommerce_tasks)
    
    # === PROJECT 2: Healthcare Management System ===
    healthcare_context = {
        "project_name": "healthcare_system",
        "language": "python",
        "framework": "fastapi",
        "project_type": "healthcare_app"
    }
    
    healthcare_tasks = [
        {
            "description": "Design secure API for healthcare data with HIPAA compliance",
            "experience_type": "architecture",
            "solution": "Apply microservices pattern with enhanced security, encryption at rest and transit",
            "outcome": "HIPAA-compliant system with advanced security measures",
            "success": True,
            "confidence": 0.95,
            "tags": ["hipaa", "security", "healthcare", "encryption"]
        },
        {
            "description": "Implement role-based access for doctors, nurses, and patients",
            "experience_type": "solution_pattern",
            "solution": "Extended JWT-based RBAC with fine-grained permissions and audit logging",
            "outcome": "Comprehensive access control system with full audit trail",
            "success": True,
            "confidence": 0.9,
            "tags": ["rbac", "audit", "healthcare", "permissions"]
        }
    ]
    
    developer_healthcare_tasks = [
        {
            "description": "Optimize database for medical records retrieval",
            "experience_type": "optimization",
            "solution": "Applied connection pooling knowledge + indexed medical record queries",
            "outcome": "Fast medical record access with sub-100ms response times",
            "success": True,
            "confidence": 0.85,
            "tags": ["database", "medical_records", "indexing"]
        }
    ]
    
    await architect.work_on_project("Healthcare System", healthcare_context, healthcare_tasks)
    await developer.work_on_project("Healthcare System", healthcare_context, developer_healthcare_tasks)
    
    # === PROJECT 3: IoT Platform ===
    iot_context = {
        "project_name": "iot_platform",
        "language": "python",
        "framework": "fastapi",
        "project_type": "iot_platform"
    }
    
    iot_tasks = [
        {
            "description": "Design real-time data processing architecture for IoT sensors",
            "experience_type": "architecture",
            "solution": "Microservices with event-driven architecture, message queues for sensor data",
            "outcome": "Real-time processing of 1M+ sensor events per minute",
            "success": True,
            "confidence": 0.95,
            "tags": ["iot", "event_driven", "real_time", "message_queue"]
        }
    ]
    
    await architect.work_on_project("IoT Platform", iot_context, iot_tasks)
    
    # === SHOW ACCUMULATED INTELLIGENCE ===
    print("\n" + "=" * 60)
    print("🧠 ACCUMULATED INTELLIGENCE SUMMARY")
    print("=" * 60)
    
    for agent in [architect, developer]:
        expertise = intelligence.get_agent_expertise_summary(agent.role)
        print(f"\n{agent.role.upper()} AGENT:")
        print(f"  Expertise Level: {expertise['expertise_level']}")
        print(f"  Total Experiences: {expertise['experience_count']}")
        print(f"  Average Confidence: {expertise.get('average_confidence', 0):.1%}")
        print(f"  Average Success Rate: {expertise.get('average_success_rate', 0):.1%}")
        print(f"  Specializations: {list(expertise.get('specializations', {}).keys())}")
        print(f"  Technologies: {expertise.get('technologies', [])}")
        print(f"  Projects Worked On: {agent.projects_worked_on}")
        
        if expertise.get('most_successful_patterns'):
            print(f"  Top Successful Patterns:")
            for i, pattern in enumerate(expertise['most_successful_patterns'][:3], 1):
                print(f"    {i}. {pattern[:80]}...")
    
    # === DEMONSTRATE CROSS-PROJECT KNOWLEDGE APPLICATION ===
    print("\n" + "=" * 60)
    print("🎯 CROSS-PROJECT KNOWLEDGE APPLICATION")
    print("=" * 60)
    
    # Test suggestion for a new, similar task
    new_task_context = {
        "language": "python",
        "framework": "fastapi",
        "project_type": "fintech_api"
    }
    
    print("\nNEW PROJECT: Fintech API")
    print("Task: Implement secure authentication for financial transactions")
    
    suggestion = intelligence.suggest_approach(
        agent_role="architect",
        task_description="Implement secure authentication for financial transactions",
        project_context=new_task_context
    )
    
    print(f"\n💡 ARCHITECT'S INTELLIGENT SUGGESTION (confidence: {suggestion['confidence']:.1%}):")
    print(suggestion['suggestion'])
    
    if suggestion.get('detailed_experiences'):
        print(f"\n📚 Based on {len(suggestion['detailed_experiences'])} previous experiences:")
        for i, exp in enumerate(suggestion['detailed_experiences'][:3], 1):
            print(f"  {i}. Context: {exp['context'][:60]}...")
            print(f"     Solution: {exp['pattern'][:60]}...")
            print(f"     Success Rate: {exp['success_rate']:.1%}")
    
    print("\n✨ This demonstrates how agents become more intelligent and capable")
    print("   with each project, building compound expertise over time!")

if __name__ == "__main__":
    asyncio.run(simulate_multi_project_learning())
