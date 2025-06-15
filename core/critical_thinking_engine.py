#!/usr/bin/env python3
"""
Critical Thinking Engine for Intelligent Agents
Makes agents reason about improvements rather than just checking off tasks
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CriticalThinkingEngine:
    """Enables agents to think critically about their work and find improvements"""
    
    def __init__(self, agent_name: str, agent_role: str):
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.thinking_history = []
    
    async def analyze_completion_quality(self, task: Dict[str, Any], result: str) -> Dict[str, Any]:
        """Critically analyze if a completed task actually meets quality standards"""
        
        analysis = {
            "quality_score": 0.0,
            "concerns": [],
            "improvement_opportunities": [],
            "refinement_needed": False,
            "next_actions": []
        }
        
        # Check for common quality issues
        concerns = []
        improvements = []
        
        # Code quality checks
        if task.get("type") == "create_component" and result:
            if len(result) < 100:
                concerns.append("Implementation seems too brief - might be incomplete")
                improvements.append("Expand implementation with proper error handling and documentation")
            
            if "TODO" in result or "FIXME" in result:
                concerns.append("Contains TODO/FIXME comments indicating incomplete work")
                improvements.append("Complete all TODO items and remove placeholder code")
            
            if "def " not in result and "class " not in result:
                concerns.append("No clear functions or classes defined - might not be functional")
                improvements.append("Add proper function/class structure with clear interfaces")
            
            if '"""' not in result and "'''" not in result:
                concerns.append("Missing docstrings - code lacks documentation")
                improvements.append("Add comprehensive docstrings for all functions and classes")
        
        # Configuration quality checks
        elif task.get("type") == "create_config":
            if len(result) < 50:
                concerns.append("Configuration seems minimal - might be missing important settings")
                improvements.append("Review and add comprehensive configuration options")
        
        # General quality assessment
        quality_score = max(0.0, 1.0 - (len(concerns) * 0.2))
        
        analysis.update({
            "quality_score": quality_score,
            "concerns": concerns,
            "improvement_opportunities": improvements,
            "refinement_needed": quality_score < 0.7,
            "next_actions": self._generate_next_actions(task, concerns, improvements)
        })
        
        # Store thinking for learning
        self.thinking_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": task.get("title", "Unknown"),
            "analysis": analysis
        })
        
        return analysis
    
    def _generate_next_actions(self, task: Dict[str, Any], concerns: List[str], 
                             improvements: List[str]) -> List[str]:
        """Generate specific next actions based on critical analysis"""
        actions = []
        
        if concerns:
            actions.append(f"Review and address {len(concerns)} quality concerns")
        
        if improvements:
            actions.append(f"Implement {len(improvements)} improvement opportunities")
            
        # Role-specific next actions
        if self.agent_role == "Backend Developer":
            actions.extend([
                "Add comprehensive error handling and logging",
                "Consider performance optimization opportunities",
                "Ensure proper database integration if applicable"
            ])
        elif self.agent_role == "Frontend Developer":
            actions.extend([
                "Enhance user experience and accessibility",
                "Optimize for responsiveness and performance",
                "Consider component reusability"
            ])
        elif self.agent_role == "QA Analyst":
            actions.extend([
                "Design comprehensive test scenarios",
                "Identify edge cases and error conditions",
                "Validate integration points"
            ])
        elif self.agent_role == "Architect":
            actions.extend([
                "Evaluate system scalability and maintainability",
                "Review architectural patterns and best practices",
                "Consider future extension points"
            ])
        
        return actions[:5]  # Limit to most important actions
    
    async def reason_about_enhancement_opportunities(self, current_state: str, 
                                                   intelligence_level: float) -> Dict[str, Any]:
        """Reason about potential enhancements to existing work"""
        
        reasoning = {
            "enhancement_potential": 0.0,
            "specific_opportunities": [],
            "implementation_strategy": [],
            "priority_ranking": []
        }
        
        # Intelligence-based reasoning depth
        reasoning_depth = min(10, max(3, int(intelligence_level * 1.5)))
        
        opportunities = []
        
        # Look for enhancement patterns
        enhancement_patterns = [
            {
                "pattern": "missing error handling",
                "opportunity": "Add comprehensive error handling and logging",
                "priority": "high"
            },
            {
                "pattern": "no tests",
                "opportunity": "Implement automated testing suite",
                "priority": "high"
            },
            {
                "pattern": "hardcoded values",
                "opportunity": "Extract configuration and make values configurable", 
                "priority": "medium"
            },
            {
                "pattern": "single responsibility violation",
                "opportunity": "Refactor into smaller, focused components",
                "priority": "medium"
            },
            {
                "pattern": "no documentation",
                "opportunity": "Add comprehensive documentation and examples",
                "priority": "medium"
            },
            {
                "pattern": "performance bottlenecks",
                "opportunity": "Optimize for better performance and scalability",
                "priority": "low"
            }
        ]
        
        # Simulate pattern detection (in real implementation, would analyze actual code)
        for pattern in enhancement_patterns[:reasoning_depth]:
            opportunities.append({
                "type": "enhancement",
                "description": pattern["opportunity"],
                "priority": pattern["priority"],
                "estimated_effort": self._estimate_effort(pattern["priority"], intelligence_level)
            })
        
        reasoning.update({
            "enhancement_potential": min(1.0, len(opportunities) * 0.15),
            "specific_opportunities": opportunities,
            "implementation_strategy": self._create_implementation_strategy(opportunities),
            "priority_ranking": sorted(opportunities, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)
        })
        
        return reasoning
    
    def _estimate_effort(self, priority: str, intelligence_level: float) -> str:
        """Estimate effort required based on priority and agent intelligence"""
        base_efforts = {
            "high": ["medium", "large"],
            "medium": ["small", "medium"], 
            "low": ["small", "small"]
        }
        
        efforts = base_efforts.get(priority, ["medium"])
        
        # Higher intelligence can tackle larger efforts more easily
        if intelligence_level >= 8.0:
            return efforts[0]  # Optimistic estimate
        elif intelligence_level >= 6.0:
            return efforts[0] if len(efforts) == 1 else efforts[1]  # Balanced
        else:
            return efforts[-1]  # Conservative estimate
    
    def _create_implementation_strategy(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """Create a strategic implementation plan"""
        strategy = []
        
        high_priority = [op for op in opportunities if op["priority"] == "high"]
        medium_priority = [op for op in opportunities if op["priority"] == "medium"]
        
        if high_priority:
            strategy.append(f"Phase 1: Address {len(high_priority)} critical improvements first")
        
        if medium_priority:
            strategy.append(f"Phase 2: Implement {len(medium_priority)} optimization enhancements")
        
        strategy.extend([
            "Phase 3: Validate improvements with testing",
            "Phase 4: Document changes and update examples",
            "Phase 5: Monitor performance and gather feedback"
        ])
        
        return strategy[:4]  # Keep strategy concise
    
    async def should_continue_working(self, task: Dict[str, Any], current_result: str, 
                                    intelligence_level: float) -> Dict[str, Any]:
        """Determine if agent should continue refining work or move to next task"""
        
        quality_analysis = await self.analyze_completion_quality(task, current_result)
        enhancement_reasoning = await self.reason_about_enhancement_opportunities(current_result, intelligence_level)
        
        # Decision logic based on intelligence and quality
        continue_working = False
        reasoning = []
        
        if quality_analysis["quality_score"] < 0.6:
            continue_working = True
            reasoning.append("Quality score below acceptable threshold")
        
        if intelligence_level >= 7.0 and enhancement_reasoning["enhancement_potential"] > 0.5:
            continue_working = True
            reasoning.append("High intelligence level detected significant enhancement opportunities")
        
        if len(quality_analysis["concerns"]) > 2:
            continue_working = True
            reasoning.append("Multiple quality concerns need addressing")
        
        # But don't get stuck in perfectionism
        if intelligence_level < 5.0 and quality_analysis["quality_score"] > 0.7:
            continue_working = False
            reasoning.append("Adequate quality achieved for current intelligence level")
        
        return {
            "continue_working": continue_working,
            "reasoning": reasoning,
            "recommended_actions": quality_analysis["next_actions"][:3],
            "quality_assessment": quality_analysis,
            "enhancement_opportunities": enhancement_reasoning
        }
    
    def get_thinking_summary(self) -> Dict[str, Any]:
        """Get summary of agent's critical thinking patterns"""
        if not self.thinking_history:
            return {"total_analyses": 0, "average_quality": 0.0, "common_concerns": []}
        
        total_analyses = len(self.thinking_history)
        avg_quality = sum(t["analysis"]["quality_score"] for t in self.thinking_history) / total_analyses
        
        # Find common concern patterns
        all_concerns = []
        for thinking in self.thinking_history:
            all_concerns.extend(thinking["analysis"]["concerns"])
        
        concern_counts = {}
        for concern in all_concerns:
            key = concern.split(" - ")[0]  # Get main concern type
            concern_counts[key] = concern_counts.get(key, 0) + 1
        
        common_concerns = sorted(concern_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_analyses": total_analyses,
            "average_quality": avg_quality,
            "common_concerns": [concern[0] for concern in common_concerns],
            "improvement_trend": self._calculate_improvement_trend()
        }
    
    def _calculate_improvement_trend(self) -> str:
        """Calculate if agent is improving over time"""
        if len(self.thinking_history) < 3:
            return "insufficient_data"
        
        recent_quality = sum(t["analysis"]["quality_score"] for t in self.thinking_history[-3:]) / 3
        earlier_quality = sum(t["analysis"]["quality_score"] for t in self.thinking_history[:3]) / 3
        
        if recent_quality > earlier_quality + 0.1:
            return "improving"
        elif recent_quality < earlier_quality - 0.1:
            return "declining"
        else:
            return "stable"
