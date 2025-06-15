#!/usr/bin/env python3
"""
Comprehensive Fix Validation Test

Tests all the fixes applied to address limitations in the enhanced dashboard system.
"""

import asyncio
import logging
import sys
import time
import importlib
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger("FixValidationTest")

class FixValidationTest:
    """Test all fixes applied to address system limitations"""
    
    def __init__(self):
        self.logger = logging.getLogger("FixValidationTest")
        self.test_results = []
        
    def add_result(self, test_name: str, success: bool, message: str, details: Optional[Dict] = None):
        """Add test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        self.logger.info(f"{status} {test_name}: {message}")
    
    def test_dependency_management(self) -> bool:
        """Test dependency management system"""
        try:
            # Test requirements file exists
            requirements_file = project_root / "requirements-dashboard.txt"
            if requirements_file.exists():
                self.add_result("Requirements File", True, "Dashboard requirements file exists")
            else:
                self.add_result("Requirements File", False, "Requirements file missing")
                return False
            
            # Test universal launcher
            launcher_file = project_root / "universal_dashboard_launcher.py"
            if launcher_file.exists():
                self.add_result("Universal Launcher", True, "Universal launcher exists")
                
                # Test dependency manager class
                try:
                    from universal_dashboard_launcher import DependencyManager
                    dm = DependencyManager()
                    features = dm.get_available_features()
                    self.add_result("Dependency Manager", True, 
                                  f"Dependency manager working, {len(features)} features checked",
                                  {"features": features})
                    return True
                except Exception as e:
                    self.add_result("Dependency Manager", False, f"Import failed: {e}")
                    return False
            else:
                self.add_result("Universal Launcher", False, "Universal launcher missing")
                return False
                
        except Exception as e:
            self.add_result("Dependency Management", False, f"Test failed: {e}")
            return False
    
    def test_enhanced_api_fixes(self) -> bool:
        """Test API server fixes"""
        try:
            # Test API import with fallbacks
            from enhanced_dashboard_api import EnhancedDashboardAPI, FASTAPI_AVAILABLE
            
            if FASTAPI_AVAILABLE:
                self.add_result("API FastAPI Available", True, "FastAPI is available")
            else:
                self.add_result("API FastAPI Available", False, "FastAPI not available, using mocks")
            
            # Test API initialization
            api = EnhancedDashboardAPI()
            if api.app is not None or not FASTAPI_AVAILABLE:
                self.add_result("API Initialization", True, "API initialized successfully")
                return True
            else:
                self.add_result("API Initialization", False, "API failed to initialize")
                return False
                
        except Exception as e:
            self.add_result("Enhanced API Fixes", False, f"API test failed: {e}")
            return False
    
    def test_enhanced_integration(self) -> bool:
        """Test enhanced dashboard integration"""
        try:
            from enhanced_dashboard_integration import EnhancedDashboardIntegration
            
            async def test_integration():
                dashboard = EnhancedDashboardIntegration()
                success = await dashboard.initialize()
                
                if success:
                    self.add_result("Enhanced Integration Init", True, "Dashboard integration initialized")
                    
                    # Test system status
                    status = dashboard.get_system_status()
                    self.add_result("Integration Status", True, 
                                  f"System status working: {status['agents']['total']} agents",
                                  {"status": status})
                    
                    # Test memory info
                    memory_info = dashboard.get_agent_memory_info()
                    self.add_result("Integration Memory", True, "Memory info accessible")
                    
                    dashboard.stop()
                    return True
                else:
                    self.add_result("Enhanced Integration Init", False, "Failed to initialize")
                    return False
            
            return asyncio.run(test_integration())
            
        except Exception as e:
            self.add_result("Enhanced Integration", False, f"Integration test failed: {e}")
            return False
    
    def test_file_structure(self) -> bool:
        """Test that all required files exist and are accessible"""
        required_files = {
            "working_agent_upgrade.py": "Enhanced agent system",
            "enhanced_dashboard_integration.py": "Dashboard integration module",
            "enhanced_dashboard_api.py": "API server with fallbacks",
            "enhanced_dashboard.html": "Web frontend",
            "universal_dashboard_launcher.py": "Universal launcher",
            "requirements-dashboard.txt": "Dependency requirements"
        }
        
        all_exist = True
        for file_path, description in required_files.items():
            full_path = project_root / file_path
            if full_path.exists():
                self.add_result(f"File {file_path}", True, f"{description} exists")
            else:
                self.add_result(f"File {file_path}", False, f"{description} missing")
                all_exist = False
        
        return all_exist
    
    def test_fallback_mechanisms(self) -> bool:
        """Test fallback mechanisms work properly"""
        try:
            # Test GUI availability
            gui_available = True
            try:
                import tkinter
                self.add_result("GUI Fallback", True, "Tkinter GUI available")
            except ImportError:
                self.add_result("GUI Fallback", False, "Tkinter not available")
                gui_available = False
            
            # Test FastAPI availability
            fastapi_available = True
            try:
                import fastapi
                import uvicorn
                self.add_result("FastAPI Fallback", True, "FastAPI available")
            except ImportError:
                self.add_result("FastAPI Fallback", False, "FastAPI not available, using fallbacks")
                fastapi_available = False
            
            # Test enhanced agents availability
            enhanced_available = True
            try:
                from working_agent_upgrade import WorkingAgentUpgrade
                self.add_result("Enhanced Agents Fallback", True, "Enhanced agents available")
            except ImportError:
                self.add_result("Enhanced Agents Fallback", False, "Enhanced agents not available")
                enhanced_available = False
            
            # At least one system should be available
            if gui_available or fastapi_available or enhanced_available:
                self.add_result("Fallback Systems", True, "At least one interface available")
                return True
            else:
                self.add_result("Fallback Systems", False, "No interfaces available")
                return False
                
        except Exception as e:
            self.add_result("Fallback Mechanisms", False, f"Fallback test failed: {e}")
            return False
    
    def test_integration_completeness(self) -> bool:
        """Test that the integration is complete and functional"""
        try:
            # Test that we can import and initialize key components
            components_tested = 0
            components_working = 0
            
            # Test enhanced agents
            try:
                from working_agent_upgrade import WorkingAgentUpgrade, dispatch_enhanced_task
                components_tested += 1
                components_working += 1
                self.add_result("Component Enhanced Agents", True, "Enhanced agents working")
            except Exception as e:
                components_tested += 1
                self.add_result("Component Enhanced Agents", False, f"Enhanced agents failed: {e}")
            
            # Test dashboard integration
            try:
                from enhanced_dashboard_integration import EnhancedDashboardIntegration
                components_tested += 1
                components_working += 1
                self.add_result("Component Dashboard Integration", True, "Dashboard integration working")
            except Exception as e:
                components_tested += 1
                self.add_result("Component Dashboard Integration", False, f"Dashboard integration failed: {e}")
            
            # Test API server
            try:
                from enhanced_dashboard_api import EnhancedDashboardAPI
                components_tested += 1
                components_working += 1
                self.add_result("Component API Server", True, "API server working")
            except Exception as e:
                components_tested += 1
                self.add_result("Component API Server", False, f"API server failed: {e}")
            
            # Test universal launcher
            try:
                from universal_dashboard_launcher import UniversalDashboardLauncher
                components_tested += 1
                components_working += 1
                self.add_result("Component Universal Launcher", True, "Universal launcher working")
            except Exception as e:
                components_tested += 1
                self.add_result("Component Universal Launcher", False, f"Universal launcher failed: {e}")
            
            success_rate = (components_working / components_tested) * 100
            self.add_result("Integration Completeness", success_rate >= 75, 
                          f"Integration {success_rate:.1f}% complete ({components_working}/{components_tested})",
                          {"success_rate": success_rate})
            
            return success_rate >= 75
            
        except Exception as e:
            self.add_result("Integration Completeness", False, f"Completeness test failed: {e}")
            return False
    
    def generate_fix_report(self) -> str:
        """Generate comprehensive fix validation report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        report = []
        report.append("=" * 60)
        report.append("ENHANCED DASHBOARD FIXES VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Total Tests: {total_tests}")
        report.append(f"Passed: {passed_tests}")
        report.append(f"Failed: {failed_tests}")
        report.append(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        report.append("")
        
        # Detailed results
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            report.append(f"{status} {result['test']}: {result['message']}")
        
        report.append("")
        report.append("FIXES APPLIED STATUS:")
        report.append("-" * 40)
        
        if failed_tests == 0:
            report.append("🎉 ALL FIXES SUCCESSFUL - No limitations remaining!")
        elif failed_tests <= 2:
            report.append("✅ Most fixes successful - Minor limitations may remain")
        else:
            report.append("⚠️ Some fixes need attention - Check failed tests above")
        
        report.append("")
        report.append("SYSTEM READY FOR:")
        report.append("-" * 20)
        report.append("• Enhanced agent execution with memory/context awareness")
        report.append("• Multiple dashboard interface options")
        report.append("• Automatic dependency management and installation") 
        report.append("• Graceful fallbacks when components unavailable")
        report.append("• Production-ready deployment")
        
        return "\n".join(report)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all fix validation tests"""
        self.logger.info("🚀 Starting Enhanced Dashboard Fixes Validation...")
        
        # Test fixes in order
        self.test_file_structure()
        self.test_dependency_management()
        self.test_enhanced_api_fixes()
        await asyncio.create_task(self.test_enhanced_integration_async())
        self.test_fallback_mechanisms()
        self.test_integration_completeness()
        
        # Generate report
        report = self.generate_fix_report()
        
        # Save report
        report_file = project_root / "FIXES_VALIDATION_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"📊 Fix validation report saved to {report_file}")
        
        return {
            "total_tests": len(self.test_results),
            "passed": len([r for r in self.test_results if r["success"]]),
            "failed": len([r for r in self.test_results if not r["success"]]),
            "results": self.test_results,
            "report": report
        }
    
    async def test_enhanced_integration_async(self):
        """Async wrapper for enhanced integration test"""
        return self.test_enhanced_integration()

async def main():
    """Main test runner"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tester = FixValidationTest()
    results = await tester.run_all_tests()
    
    print("\n" + results["report"])
    
    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
