#!/usr/bin/env python3
"""
Enhanced Dashboard Integration Test

Comprehensive test to validate the integration between the enhanced agent system
and the dashboard components.
"""

import asyncio
import json
import logging
import sys
import time
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger("DashboardIntegrationTest")

class DashboardIntegrationTest:
    """Comprehensive integration test for enhanced dashboard"""
    
    def __init__(self):
        self.logger = logging.getLogger("DashboardIntegrationTest")
        self.test_results = []
        self.api_url = "http://127.0.0.1:8001"
        
    def add_test_result(self, test_name: str, success: bool, message: str, details: Optional[Dict] = None):
        """Add a test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        self.logger.info(f"{status} {test_name}: {message}")
    
    async def test_enhanced_agent_system(self) -> bool:
        """Test enhanced agent system initialization"""
        try:
            from working_agent_upgrade import WorkingAgentUpgrade, dispatch_enhanced_task
            
            # Initialize enhanced agents
            enhanced_agents = WorkingAgentUpgrade()
            success = await enhanced_agents.initialize()
            
            if success:
                self.add_test_result("Enhanced Agent Initialization", True, 
                                   "Enhanced agent system initialized successfully")
                
                # Test dispatch function
                try:
                    result = await dispatch_enhanced_task("architect", "Test connectivity")
                    self.add_test_result("Enhanced Agent Dispatch", True, 
                                       "Agent dispatch function working", {"result": result})
                    return True
                except Exception as e:
                    self.add_test_result("Enhanced Agent Dispatch", False, 
                                       f"Agent dispatch failed: {e}")
                    return False
            else:
                self.add_test_result("Enhanced Agent Initialization", False, 
                                   "Enhanced agent system failed to initialize")
                return False
                
        except ImportError as e:
            self.add_test_result("Enhanced Agent Import", False, 
                               f"Failed to import enhanced agents: {e}")
            return False
        except Exception as e:
            self.add_test_result("Enhanced Agent System", False, 
                               f"Unexpected error: {e}")
            return False
    
    async def test_dashboard_integration_module(self) -> bool:
        """Test dashboard integration module"""
        try:
            from enhanced_dashboard_integration import EnhancedDashboardIntegration
            
            dashboard = EnhancedDashboardIntegration()
            success = await dashboard.initialize()
            
            if success:
                self.add_test_result("Dashboard Integration Module", True, 
                                   "Dashboard integration module working")
                
                # Test task execution
                result = await dashboard.execute_task("architect", "Test dashboard integration")
                self.add_test_result("Dashboard Task Execution", True, 
                                   "Task execution through dashboard working", {"result": result})
                
                # Test status retrieval
                status = dashboard.get_system_status()
                self.add_test_result("Dashboard Status Retrieval", True, 
                                   "System status retrieval working", {"status": status})
                
                return True
            else:
                self.add_test_result("Dashboard Integration Module", False, 
                                   "Dashboard integration failed to initialize")
                return False
                
        except ImportError as e:
            self.add_test_result("Dashboard Integration Import", False, 
                               f"Failed to import dashboard integration: {e}")
            return False
        except Exception as e:
            self.add_test_result("Dashboard Integration Module", False, 
                               f"Unexpected error: {e}")
            return False
    
    def test_api_server_files(self) -> bool:
        """Test API server file existence and basic validation"""
        api_file = project_root / "enhanced_dashboard_api.py"
        
        if not api_file.exists():
            self.add_test_result("API Server File", False, "API server file not found")
            return False
        
        try:
            # Try to import the API module
            sys.path.insert(0, str(project_root))
            from enhanced_dashboard_api import EnhancedDashboardAPI
            
            self.add_test_result("API Server Import", True, "API server module imported successfully")
            
            # Test API initialization
            api = EnhancedDashboardAPI()
            if hasattr(api, 'app') and api.app is not None:
                self.add_test_result("API Server App", True, "FastAPI app created successfully")
                return True
            else:
                self.add_test_result("API Server App", False, "FastAPI app not available (FastAPI not installed)")
                return False
                
        except ImportError as e:
            self.add_test_result("API Server Import", False, f"Failed to import API: {e}")
            return False
        except Exception as e:
            self.add_test_result("API Server Creation", False, f"API creation failed: {e}")
            return False
    
    def test_frontend_files(self) -> bool:
        """Test frontend dashboard file existence"""
        frontend_file = project_root / "enhanced_dashboard.html"
        
        if not frontend_file.exists():
            self.add_test_result("Frontend Dashboard File", False, "Frontend dashboard file not found")
            return False
        
        try:
            # Read and validate HTML file
            with open(frontend_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required elements
            required_elements = [
                "Ultimate Copilot",
                "System Status",
                "Agent Status", 
                "Execute Task",
                "Task History",
                "API_BASE"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.add_test_result("Frontend Dashboard Content", False, 
                                   f"Missing elements: {missing_elements}")
                return False
            else:
                self.add_test_result("Frontend Dashboard Content", True, 
                                   "All required frontend elements present")
                return True
                
        except Exception as e:
            self.add_test_result("Frontend Dashboard File", False, f"Error reading frontend file: {e}")
            return False
    
    async def test_api_endpoints(self, api_running: bool = False) -> bool:
        """Test API endpoints if server is running"""
        if not api_running:
            self.add_test_result("API Endpoints", False, "API server not running - skipping endpoint tests")
            return False
        
        endpoints_to_test = [
            ("/", "root"),
            ("/health", "health check"),
            ("/status", "system status"),
            ("/agents", "agent list")
        ]
        
        all_passed = True
        
        for endpoint, description in endpoints_to_test:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.add_test_result(f"API Endpoint {endpoint}", True, 
                                       f"{description} endpoint working")
                else:
                    self.add_test_result(f"API Endpoint {endpoint}", False, 
                                       f"{description} endpoint returned {response.status_code}")
                    all_passed = False
            except requests.RequestException as e:
                self.add_test_result(f"API Endpoint {endpoint}", False, 
                                   f"{description} endpoint failed: {e}")
                all_passed = False
        
        return all_passed
    
    def check_api_server_running(self) -> bool:
        """Check if API server is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def test_required_files(self) -> bool:
        """Test that all required files exist"""
        required_files = [
            "working_agent_upgrade.py",
            "enhanced_dashboard_integration.py", 
            "enhanced_dashboard_api.py",
            "enhanced_dashboard.html",
            "prompt_profiles/agent_prompt_profiles.json"
        ]
        
        all_exist = True
        for file_path in required_files:
            full_path = project_root / file_path
            if full_path.exists():
                self.add_test_result(f"Required File {file_path}", True, "File exists")
            else:
                self.add_test_result(f"Required File {file_path}", False, "File missing")
                all_exist = False
        
        return all_exist
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("=" * 60)
        report.append("ENHANCED DASHBOARD INTEGRATION TEST REPORT")
        report.append("=" * 60)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        report.append("")
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["test"].split()[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        for category, results in categories.items():
            report.append(f"\n{category.upper()} TESTS:")
            report.append("-" * 40)
            for result in results:
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                report.append(f"{status} {result['test']}: {result['message']}")
        
        report.append("")
        report.append("INTEGRATION STATUS:")
        report.append("-" * 40)
        
        if failed_tests == 0:
            report.append("🎉 ALL TESTS PASSED - Dashboard integration is fully functional!")
        elif failed_tests <= 2:
            report.append("⚠️  Minor issues found - Dashboard mostly functional with some limitations")
        else:
            report.append("❌ Significant issues found - Dashboard integration needs attention")
        
        return "\n".join(report)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        self.logger.info("🚀 Starting Enhanced Dashboard Integration Tests...")
        
        # Test 1: Required files
        self.test_required_files()
        
        # Test 2: Enhanced agent system
        await self.test_enhanced_agent_system()
        
        # Test 3: Dashboard integration module
        await self.test_dashboard_integration_module()
        
        # Test 4: API server files
        self.test_api_server_files()
        
        # Test 5: Frontend files
        self.test_frontend_files()
        
        # Test 6: Check if API server is running
        api_running = self.check_api_server_running()
        if api_running:
            self.add_test_result("API Server Running", True, "API server is accessible")
            await self.test_api_endpoints(api_running=True)
        else:
            self.add_test_result("API Server Running", False, "API server not running")
        
        # Generate report
        report = self.generate_report()
          # Save report to file
        report_file = project_root / "DASHBOARD_INTEGRATION_TEST_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"📊 Test report saved to {report_file}")
        
        return {
            "total_tests": len(self.test_results),
            "passed": len([r for r in self.test_results if r["success"]]),
            "failed": len([r for r in self.test_results if not r["success"]]),
            "results": self.test_results,
            "report": report
        }

async def main():
    """Main test runner"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tester = DashboardIntegrationTest()
    results = await tester.run_all_tests()
    
    print("\n" + results["report"])
    
    # Return appropriate exit code
    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
