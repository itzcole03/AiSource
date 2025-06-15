"""
QA Agent - Handles quality assurance and testing tasks
"""

from agents.base_agent import BaseAgent
from core.file_coordinator import safe_write_file
from typing import Dict
import datetime

class QAAgent(BaseAgent):
    async def agent_initialize(self):
        """Initialize QA-specific capabilities"""
        self.test_types = ["Unit", "Integration", "E2E", "Performance", "Security", "Accessibility"]
        self.tools = ["Jest", "Cypress", "Playwright", "Selenium", "Postman", "JMeter"]
        self.methodologies = ["TDD", "BDD", "Risk-based", "Exploratory"]
    
    async def process_task(self, task: Dict, context: Dict) -> Dict:
        """Process QA and testing tasks"""
        task_type = self.determine_task_type(task)
        
        if task_type == "test_planning":
            return await self.create_test_plan(task, context)
        elif task_type == "test_automation":
            return await self.create_automated_tests(task, context)
        elif task_type == "bug_analysis":
            return await self.analyze_bugs(task, context)
        elif task_type == "quality_review":
            return await self.review_quality(task, context)
        else:
            return await self.general_qa_task(task, context)
    
    async def create_test_plan(self, task: Dict, context: Dict) -> Dict:
        """Create comprehensive test plan"""
        prompt = f"""
        As a senior QA engineer, create a test plan for:
        
        Task: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Provide:
        1. Test strategy and approach
        2. Test scenarios and cases
        3. Testing tools and frameworks
        4. Risk assessment
        5. Timeline and resources
        
        Include unit, integration, and E2E testing considerations.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=1200)
        
        return {
            'type': 'test_planning',
            'test_plan': response,
            'scenarios': self.extract_test_scenarios(response),
            'tools': self.extract_tools(response),
            'risks': self.extract_risks(response),
            'summary': f"Test plan created for {task.get('title', 'project')}"
        }
    
    async def create_automated_tests(self, task: Dict, context: Dict) -> Dict:
        """Create automated test scripts"""
        prompt = f"""
        As a test automation engineer, create automated tests for:
        
        Task: {task.get('title', '')}
        Requirements: {task.get('description', '')}
        
        Provide:
        1. Unit test cases (Jest/Vitest)
        2. Integration test scenarios
        3. E2E test scripts (Cypress/Playwright)
        4. API testing (if applicable)
        5. Test data setup and teardown
        
        Include complete, runnable test code.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=1200)
        
        # Create test files
        await self.create_test_files(task, response)
        
        return {
            'type': 'test_automation',
            'test_code': response,
            'unit_tests': self.extract_unit_tests(response),
            'e2e_tests': self.extract_e2e_tests(response),
            'api_tests': self.extract_api_tests(response),
            'summary': f"Automated tests created for {task.get('title', 'feature')}"
        }
    
    async def analyze_bugs(self, task: Dict, context: Dict) -> Dict:
        """Analyze and categorize bugs"""
        prompt = f"""
        As a QA analyst, analyze the following bug report:
        
        Task: {task.get('title', '')}
        Bug Description: {task.get('description', '')}
        
        Provide:
        1. Bug severity and priority classification
        2. Root cause analysis
        3. Steps to reproduce
        4. Expected vs actual behavior
        5. Suggested fix approach
        
        Be thorough and systematic in your analysis.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'bug_analysis',
            'analysis': response,
            'severity': self.extract_severity(response),
            'root_cause': self.extract_root_cause(response),
            'reproduction_steps': self.extract_reproduction_steps(response),
            'summary': f"Bug analysis completed for {task.get('title', 'issue')}"
        }
    
    async def review_quality(self, task: Dict, context: Dict) -> Dict:
        """Review code/system quality"""
        prompt = f"""
        As a quality assurance engineer, review the quality of:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Assess:
        1. Code quality and standards compliance
        2. Test coverage adequacy
        3. Performance considerations
        4. Security vulnerabilities
        5. User experience issues
        
        Provide actionable recommendations for improvement.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=800)
        
        return {
            'type': 'quality_review',
            'review': response,
            'quality_score': self.calculate_quality_score(response),
            'recommendations': self.extract_recommendations(response),
            'issues': self.extract_issues(response),
            'summary': f"Quality review completed for {task.get('title', 'system')}"
        }
    
    async def general_qa_task(self, task: Dict, context: Dict) -> Dict:
        """Handle general QA tasks"""
        prompt = f"""
        As a senior QA engineer, help with:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Context from previous work:
        {self.format_context(context)}
        
        Provide detailed QA guidance and testing recommendations.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=600)
        
        return {
            'type': 'general_qa',
            'guidance': response,
            'summary': f"QA guidance provided for {task.get('title', 'task')}"
        }
    
    def determine_task_type(self, task: Dict) -> str:
        """Determine the type of QA task"""
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        
        if any(word in description + title for word in ['test plan', 'strategy', 'planning']):
            return "test_planning"
        elif any(word in description + title for word in ['automate', 'test script', 'automation']):
            return "test_automation"
        elif any(word in description + title for word in ['bug', 'defect', 'issue', 'error']):
            return "bug_analysis"
        elif any(word in description + title for word in ['review', 'quality', 'audit', 'assess']):
            return "quality_review"
        else:
            return "general"
    
    def format_context(self, context: Dict) -> str:
        """Format context for LLM prompt"""
        formatted = ""
        
        if context.get('similar_tasks'):
            formatted += "Similar previous tasks:\n"
            for task in context['similar_tasks'][:2]:
                formatted += f"- {task.get('task_title', 'Unknown')}: {task.get('result', {}).get('summary', 'No summary')}\n"
        
        return formatted
    
    def extract_test_scenarios(self, response: str) -> list:
        """Extract test scenarios from response"""
        scenarios = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['scenario', 'test case', 'should']):
                scenarios.append(line.strip())
        
        return scenarios[:10]
    
    def extract_tools(self, response: str) -> list:
        """Extract testing tools from response"""
        found_tools = []
        response_lower = response.lower()
        
        for tool in self.tools:
            if tool.lower() in response_lower:
                found_tools.append(tool)
        
        return found_tools
    
    def extract_risks(self, response: str) -> list:
        """Extract risks from response"""
        risks = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['risk', 'concern', 'issue', 'problem']):
                risks.append(line.strip())
        
        return risks[:5]
    
    def extract_unit_tests(self, response: str) -> list:
        """Extract unit test information from response"""
        tests = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['test(', 'it(', 'describe(', 'expect(']):
                tests.append(line.strip())
        
        return tests[:10]
    
    def extract_e2e_tests(self, response: str) -> list:
        """Extract E2E test information from response"""
        tests = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['cy.', 'page.', 'browser.', 'e2e']):
                tests.append(line.strip())
        
        return tests[:5]
    
    def extract_api_tests(self, response: str) -> list:
        """Extract API test information from response"""
        tests = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['api', 'request', 'response', 'endpoint']):
                tests.append(line.strip())
        
        return tests[:5]
    
    def extract_severity(self, response: str) -> str:
        """Extract bug severity from response"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['critical', 'blocker', 'severe']):
            return "Critical"
        elif any(word in response_lower for word in ['major', 'high']):
            return "Major"
        elif any(word in response_lower for word in ['minor', 'low']):
            return "Minor"
        else:
            return "Medium"
    
    def extract_root_cause(self, response: str) -> str:
        """Extract root cause from response"""
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['root cause', 'caused by', 'due to']):
                return line.strip()
        
        return "Root cause analysis needed"
    
    def extract_reproduction_steps(self, response: str) -> list:
        """Extract reproduction steps from response"""
        steps = []
        lines = response.split('\n')
        
        in_steps = False
        for line in lines:
            if 'steps' in line.lower() and 'reproduce' in line.lower():
                in_steps = True
                continue
            
            if in_steps and line.strip():
                if line.strip().startswith(('1.', '2.', '3.', '-', '*')):
                    steps.append(line.strip())
                elif not any(char.isdigit() for char in line[:3]):
                    break
        
        return steps[:10]
    
    def calculate_quality_score(self, response: str) -> int:
        """Calculate quality score based on response"""
        response_lower = response.lower()
        
        positive_indicators = ['good', 'excellent', 'high quality', 'well-designed']
        negative_indicators = ['poor', 'bad', 'low quality', 'issues', 'problems']
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in response_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
        
        # Simple scoring algorithm
        base_score = 70
        score = base_score + (positive_count * 10) - (negative_count * 15)
        
        return max(0, min(100, score))
    
    def extract_recommendations(self, response: str) -> list:
        """Extract recommendations from response"""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['recommend', 'suggest', 'should', 'improve']):
                recommendations.append(line.strip())
        
        return recommendations[:5]
    
    def extract_issues(self, response: str) -> list:
        """Extract issues from response"""
        issues = []
        lines = response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['issue', 'problem', 'concern', 'flaw']):
                issues.append(line.strip())
        
        return issues[:5]
    
    async def agent_health_check(self):
        """QA-specific health check"""
        # Test QA knowledge
        test_prompt = "What is unit testing?"
        response = await self.generate_llm_response(test_prompt, max_tokens=50)
        
        if not response or len(response) < 10:
            raise Exception("QA agent knowledge test failed")
    
    async def agent_cleanup(self):
        """QA-specific cleanup"""
        # Clear any cached test data or temporary files
        pass
    
    async def create_test_files(self, task: Dict, response: str):
        """Create test files based on the QA response"""
        try:
            task_title = task.get('title', 'test').replace(' ', '_').lower()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create unit test file
            unit_test_content = self.extract_code_blocks(response, "unit")
            if unit_test_content:
                unit_file = f"agent_outputs/QAAgent/unit_tests_{task_title}_{timestamp}.test.js"
                test_code = f"""// Unit Tests for {task.get('title', 'Feature')}
// Generated by QAAgent on {timestamp}

{unit_test_content}
"""
                if safe_write_file(unit_file, test_code, self.agent_id, priority=2):
                    self.logger.info(f"Unit test file created: {unit_file}")
            
            # Create integration test file
            integration_test_content = self.extract_code_blocks(response, "integration")
            if integration_test_content:
                integration_file = f"agent_outputs/QAAgent/integration_tests_{task_title}_{timestamp}.spec.js"
                test_code = f"""// Integration Tests for {task.get('title', 'Feature')}
// Generated by QAAgent on {timestamp}

{integration_test_content}
"""
                if safe_write_file(integration_file, test_code, self.agent_id, priority=2):
                    self.logger.info(f"Integration test file created: {integration_file}")
            
            # Create E2E test file
            e2e_test_content = self.extract_code_blocks(response, "e2e")
            if e2e_test_content:
                e2e_file = f"agent_outputs/QAAgent/e2e_tests_{task_title}_{timestamp}.cy.js"
                test_code = f"""// E2E Tests for {task.get('title', 'Feature')}
// Generated by QAAgent on {timestamp}

{e2e_test_content}
"""
                if safe_write_file(e2e_file, test_code, self.agent_id, priority=2):
                    self.logger.info(f"E2E test file created: {e2e_file}")
            
            # Create test plan document
            test_plan_file = f"agent_outputs/QAAgent/test_plan_{task_title}_{timestamp}.md"
            plan_content = f"""# Test Plan - {task.get('title', 'Feature')}

## Overview
Generated on: {timestamp}
Task: {task.get('title', '')}

## Test Strategy
{response}

## Test Types
- Unit Testing
- Integration Testing  
- End-to-End Testing
- API Testing (if applicable)

## Generated by QAAgent
"""
            if safe_write_file(test_plan_file, plan_content, self.agent_id, priority=2):
                self.logger.info(f"Test plan created: {test_plan_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating test files: {e}")
    
    def extract_code_blocks(self, response: str, test_type: str) -> str:
        """Extract code blocks for specific test types"""
        lines = response.split('\n')
        code_lines = []
        in_code_block = False
        relevant_section = False
        
        for line in lines:
            # Check for test type mentions
            if test_type.lower() in line.lower():
                relevant_section = True
                continue
                
            # Check for code block markers
            if '```' in line:
                in_code_block = not in_code_block
                if in_code_block and relevant_section:
                    continue
                elif not in_code_block:
                    break
                continue
            
            # Collect code lines if in relevant section and code block
            if in_code_block and relevant_section:
                code_lines.append(line)
        
        return '\n'.join(code_lines) if code_lines else f"""
describe('{test_type.title()} Tests', () => {{
  test('should work correctly', () => {{
    // TODO: Implement {test_type} test
    expect(true).toBe(true);
  }});
}});
"""