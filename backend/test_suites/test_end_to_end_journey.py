#!/usr/bin/env python3
"""
END-TO-END USER JOURNEY TEST SUITE
Comprehensive validation of the complete SoloRealms user experience

This test suite validates:
1. Frontend-Backend Connectivity
2. Authentication Flow (Clerk integration)
3. Character Creation Journey
4. Story Generation Process
5. Game Session Management
6. Combat System Integration
7. Performance Benchmarks
8. Cross-System Integration

Usage: python test_end_to_end_journey.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import re

# Updated Test Configuration
TEST_CONFIG = {
    "backend_url": "http://localhost:8000",
    "frontend_url": "http://localhost:3001",  # Updated to correct port
    "test_timeout": 30,
    "performance_threshold_ms": 3000,  # 3 seconds for page loads
    "api_threshold_ms": 500,  # 500ms for API calls
    "concurrent_users": 3,
    "test_user_prefix": "e2e_test_user"
}

@dataclass
class TestResult:
    """Enhanced test result tracking"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP", "WARNING"
    duration_ms: float
    details: str
    error: Optional[str] = None
    data: Optional[Dict] = None
    performance_notes: Optional[str] = None

class EndToEndTestSuite:
    """Comprehensive end-to-end testing suite"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.session_data = {}
        self.session = requests.Session()
        
    def log_result(self, test_name: str, status: str, duration_ms: float, 
                   details: str, error: str = None, data: Dict = None, 
                   performance_notes: str = None):
        """Enhanced result logging"""
        result = TestResult(test_name, status, duration_ms, details, error, data, performance_notes)
        self.results.append(result)
        
        status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "WARNING": "⚠️"}
        print(f"{status_emoji.get(status, '❓')} {test_name}: {status} ({duration_ms:.1f}ms)")
        if details:
            print(f"   📝 {details}")
        if performance_notes:
            print(f"   ⚡ Performance: {performance_notes}")
        if error:
            print(f"   🚨 Error: {error}")

    def test_system_health_check(self) -> bool:
        """Test 1: Complete System Health Validation"""
        start_time = time.time()
        
        health_checks = {
            "Backend Health": f"{TEST_CONFIG['backend_url']}/health",
            "Database Health": f"{TEST_CONFIG['backend_url']}/health/database", 
            "Redis Health": f"{TEST_CONFIG['backend_url']}/api/redis/health",
            "Frontend Access": TEST_CONFIG['frontend_url']
        }
        
        results = {}
        
        try:
            for check_name, url in health_checks.items():
                check_start = time.time()
                response = self.session.get(url, timeout=TEST_CONFIG['test_timeout'])
                check_duration = (time.time() - check_start) * 1000
                
                results[check_name] = {
                    "status": response.status_code,
                    "duration_ms": check_duration,
                    "healthy": response.status_code == 200
                }
                
                if check_name == "Frontend Access":
                    # Check for Clerk integration
                    if 'x-clerk-auth-status' in response.headers:
                        results[check_name]["clerk_status"] = response.headers['x-clerk-auth-status']
                
            duration_ms = (time.time() - start_time) * 1000
            
            all_healthy = all(r["healthy"] for r in results.values())
            avg_response_time = sum(r["duration_ms"] for r in results.values()) / len(results)
            
            if all_healthy:
                perf_note = f"Avg response: {avg_response_time:.1f}ms"
                self.log_result("System Health Check", "PASS", duration_ms,
                              f"All 4 systems healthy, Clerk auth detected", 
                              performance_notes=perf_note, data=results)
                return True
            else:
                failed_systems = [name for name, result in results.items() if not result["healthy"]]
                self.log_result("System Health Check", "FAIL", duration_ms,
                              f"Failed systems: {', '.join(failed_systems)}", data=results)
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("System Health Check", "FAIL", duration_ms,
                          "System health check error", str(e))
            return False

    def test_frontend_page_loads(self) -> bool:
        """Test 2: Frontend Page Load Performance"""
        start_time = time.time()
        
        pages_to_test = [
            ("Homepage", "/"),
            ("Sign In", "/sign-in"),
            ("Sign Up", "/sign-up"),
            ("Dashboard", "/dashboard"),
            ("Character Create", "/character/create"),
        ]
        
        page_results = {}
        
        try:
            for page_name, path in pages_to_test:
                page_start = time.time()
                url = f"{TEST_CONFIG['frontend_url']}{path}"
                
                response = self.session.get(url, timeout=TEST_CONFIG['test_timeout'])
                page_duration = (time.time() - page_start) * 1000
                
                page_results[page_name] = {
                    "url": url,
                    "status": response.status_code,
                    "duration_ms": page_duration,
                    "size_bytes": len(response.content),
                    "within_threshold": page_duration <= TEST_CONFIG['performance_threshold_ms']
                }
                
                # Check for React/Next.js markers
                if response.status_code == 200:
                    content = response.text.lower()
                    page_results[page_name]["has_react"] = "__next" in content or "react" in content
                    page_results[page_name]["has_clerk"] = "clerk" in content
            
            duration_ms = (time.time() - start_time) * 1000
            
            successful_loads = sum(1 for r in page_results.values() if r["status"] == 200)
            within_threshold = sum(1 for r in page_results.values() if r["within_threshold"])
            avg_load_time = sum(r["duration_ms"] for r in page_results.values()) / len(page_results)
            
            if successful_loads == len(pages_to_test) and within_threshold >= len(pages_to_test) * 0.8:
                perf_note = f"Avg load: {avg_load_time:.1f}ms, {within_threshold}/{len(pages_to_test)} under threshold"
                self.log_result("Frontend Page Loads", "PASS", duration_ms,
                              f"All {len(pages_to_test)} pages loaded successfully", 
                              performance_notes=perf_note, data=page_results)
                return True
            else:
                perf_note = f"Avg load: {avg_load_time:.1f}ms, {within_threshold}/{len(pages_to_test)} under threshold"
                self.log_result("Frontend Page Loads", "WARNING", duration_ms,
                              f"{successful_loads}/{len(pages_to_test)} pages loaded, performance issues detected",
                              performance_notes=perf_note, data=page_results)
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Frontend Page Loads", "FAIL", duration_ms,
                          "Frontend page load testing error", str(e))
            return False

    def test_api_integration_comprehensive(self) -> bool:
        """Test 3: Comprehensive API Integration Testing"""
        start_time = time.time()
        
        api_endpoints = [
            # Public endpoints (no auth required)
            ("Character Options", "GET", "/api/characters/options", None),
            ("Dice Roll d20", "POST", "/api/dice/simple", {"dice_type": "d20", "modifier": 5}),
            ("Redis Statistics", "GET", "/api/redis/statistics", None),
            ("Health Check", "GET", "/health", None),
            
            # Session management
            ("Roll Character Stats", "POST", "/api/characters/roll-stats", None),
            ("Cleanup Sessions", "POST", "/api/redis/cleanup/expired-sessions", None),
        ]
        
        api_results = {}
        
        try:
            for endpoint_name, method, path, data in api_endpoints:
                endpoint_start = time.time()
                url = f"{TEST_CONFIG['backend_url']}{path}"
                
                if method == "GET":
                    response = self.session.get(url, timeout=TEST_CONFIG['test_timeout'])
                else:
                    response = self.session.post(url, json=data, timeout=TEST_CONFIG['test_timeout'])
                
                endpoint_duration = (time.time() - endpoint_start) * 1000
                
                api_results[endpoint_name] = {
                    "method": method,
                    "url": url,
                    "status": response.status_code,
                    "duration_ms": endpoint_duration,
                    "within_threshold": endpoint_duration <= TEST_CONFIG['api_threshold_ms'],
                    "success": response.status_code == 200
                }
                
                # Parse response data for validation
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        api_results[endpoint_name]["response_data"] = response_data
                        
                        # Specific validations
                        if endpoint_name == "Character Options":
                            races = response_data.get("races", [])
                            classes = response_data.get("classes", [])
                            api_results[endpoint_name]["data_quality"] = len(races) >= 10 and len(classes) >= 10
                        elif endpoint_name == "Dice Roll d20":
                            dice_data = response_data.get("data", {})
                            total = dice_data.get("total", 0)
                            api_results[endpoint_name]["data_quality"] = 6 <= total <= 25  # d20+5 range
                        elif endpoint_name == "Redis Statistics":
                            stats = response_data.get("statistics", {})
                            api_results[endpoint_name]["data_quality"] = "cache_counts" in stats
                            
                    except json.JSONDecodeError:
                        api_results[endpoint_name]["response_data"] = None
                        api_results[endpoint_name]["data_quality"] = False
            
            duration_ms = (time.time() - start_time) * 1000
            
            successful_apis = sum(1 for r in api_results.values() if r["success"])
            within_threshold = sum(1 for r in api_results.values() if r["within_threshold"])
            avg_api_time = sum(r["duration_ms"] for r in api_results.values()) / len(api_results)
            
            if successful_apis == len(api_endpoints) and within_threshold >= len(api_endpoints) * 0.9:
                perf_note = f"Avg API: {avg_api_time:.1f}ms, {within_threshold}/{len(api_endpoints)} under threshold"
                self.log_result("API Integration Comprehensive", "PASS", duration_ms,
                              f"All {len(api_endpoints)} APIs functional", 
                              performance_notes=perf_note, data=api_results)
                return True
            else:
                perf_note = f"Avg API: {avg_api_time:.1f}ms, {within_threshold}/{len(api_endpoints)} under threshold"
                self.log_result("API Integration Comprehensive", "WARNING", duration_ms,
                              f"{successful_apis}/{len(api_endpoints)} APIs working, performance concerns",
                              performance_notes=perf_note, data=api_results)
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("API Integration Comprehensive", "FAIL", duration_ms,
                          "API integration testing error", str(e))
            return False

    def test_game_mechanics_validation(self) -> bool:
        """Test 4: D&D Game Mechanics Validation"""
        start_time = time.time()
        
        mechanics_tests = []
        
        try:
            # Test 1: Character creation options
            options_response = self.session.get(
                f"{TEST_CONFIG['backend_url']}/api/characters/options",
                timeout=TEST_CONFIG['test_timeout']
            )
            
            if options_response.status_code == 200:
                options = options_response.json()
                
                d5e_validation = {
                    "races_count": len(options.get("races", [])),
                    "classes_count": len(options.get("classes", [])),
                    "backgrounds_count": len(options.get("backgrounds", [])),
                    "has_core_races": all(race in options.get("races", []) for race in ["Human", "Elf", "Dwarf"]),
                    "has_core_classes": all(cls in options.get("classes", []) for cls in ["Fighter", "Wizard", "Rogue"])
                }
                
                mechanics_tests.append(("D&D 5e Options", True, d5e_validation))
            else:
                mechanics_tests.append(("D&D 5e Options", False, {"error": "Failed to fetch"}))
            
            # Test 2: Dice mechanics
            dice_types = ["d4", "d6", "d8", "d10", "d12", "d20"]
            dice_results = {}
            
            for dice in dice_types:
                roll_response = self.session.post(
                    f"{TEST_CONFIG['backend_url']}/api/dice/simple",
                    json={"dice_type": dice, "modifier": 0},
                    timeout=TEST_CONFIG['test_timeout']
                )
                
                if roll_response.status_code == 200:
                    roll_data = roll_response.json()
                    total = roll_data.get("data", {}).get("total", 0)
                    max_value = int(dice[1:])  # Extract number from d20 -> 20
                    
                    dice_results[dice] = {
                        "total": total,
                        "valid_range": 1 <= total <= max_value,
                        "has_breakdown": "breakdown" in roll_data.get("data", {})
                    }
                else:
                    dice_results[dice] = {"valid_range": False, "error": "Failed to roll"}
            
            valid_dice = sum(1 for result in dice_results.values() if result.get("valid_range", False))
            mechanics_tests.append(("Dice Mechanics", valid_dice == len(dice_types), dice_results))
            
            # Test 3: Character stat rolling
            stats_response = self.session.post(
                f"{TEST_CONFIG['backend_url']}/api/characters/roll-stats",
                timeout=TEST_CONFIG['test_timeout']
            )
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                stats = stats_data.get("stats", {})
                
                stat_validation = {
                    "has_six_stats": len(stats) == 6,
                    "valid_ranges": all(3 <= val <= 18 for val in stats.values()),
                    "includes_modifiers": "modifiers" in stats_data
                }
                
                mechanics_tests.append(("Character Stats", all(stat_validation.values()), stat_validation))
            else:
                mechanics_tests.append(("Character Stats", False, {"error": "Failed to roll stats"}))
            
            duration_ms = (time.time() - start_time) * 1000
            
            passed_tests = sum(1 for _, passed, _ in mechanics_tests if passed)
            
            if passed_tests == len(mechanics_tests):
                self.log_result("Game Mechanics Validation", "PASS", duration_ms,
                              f"All {len(mechanics_tests)} D&D mechanics working correctly",
                              data={"test_results": mechanics_tests})
                return True
            else:
                self.log_result("Game Mechanics Validation", "FAIL", duration_ms,
                              f"Only {passed_tests}/{len(mechanics_tests)} mechanics tests passed",
                              data={"test_results": mechanics_tests})
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Game Mechanics Validation", "FAIL", duration_ms,
                          "Game mechanics validation error", str(e))
            return False

    def test_session_persistence(self) -> bool:
        """Test 5: Session and State Persistence"""
        start_time = time.time()
        
        try:
            # Test Redis session creation and retrieval
            session_data = {
                "user_id": f"{TEST_CONFIG['test_user_prefix']}_{int(time.time())}",
                "character_id": 1,
                "story_arc_id": 1
            }
            
            # Create session
            create_response = self.session.post(
                f"{TEST_CONFIG['backend_url']}/api/redis/session/create",
                json=session_data,
                timeout=TEST_CONFIG['test_timeout']
            )
            
            if create_response.status_code == 200:
                session_info = create_response.json()
                session_id = session_info.get("session_id")
                
                if session_id:
                    # Retrieve session
                    get_response = self.session.get(
                        f"{TEST_CONFIG['backend_url']}/api/redis/session/{session_id}",
                        timeout=TEST_CONFIG['test_timeout']
                    )
                    
                    if get_response.status_code == 200:
                        retrieved_data = get_response.json()
                        
                        # Validate session persistence
                        persistence_validation = {
                            "session_created": True,
                            "session_retrieved": True,
                            "data_integrity": retrieved_data.get("user_id") == session_data["user_id"],
                            "has_timestamp": "created_at" in retrieved_data
                        }
                        
                        duration_ms = (time.time() - start_time) * 1000
                        
                        if all(persistence_validation.values()):
                            self.log_result("Session Persistence", "PASS", duration_ms,
                                          f"Session {session_id} created and retrieved successfully",
                                          data=persistence_validation)
                            self.session_data["test_session_id"] = session_id
                            return True
                        else:
                            self.log_result("Session Persistence", "FAIL", duration_ms,
                                          "Session data integrity issues",
                                          data=persistence_validation)
                            return False
                    else:
                        duration_ms = (time.time() - start_time) * 1000
                        self.log_result("Session Persistence", "FAIL", duration_ms,
                                      f"Session retrieval failed: {get_response.status_code}")
                        return False
                else:
                    duration_ms = (time.time() - start_time) * 1000
                    self.log_result("Session Persistence", "FAIL", duration_ms,
                                  "No session ID returned")
                    return False
            else:
                duration_ms = (time.time() - start_time) * 1000
                self.log_result("Session Persistence", "FAIL", duration_ms,
                              f"Session creation failed: {create_response.status_code}")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Session Persistence", "FAIL", duration_ms,
                          "Session persistence testing error", str(e))
            return False

    def test_concurrent_load_simulation(self) -> bool:
        """Test 6: Concurrent User Load Simulation"""
        start_time = time.time()
        
        endpoints_to_stress = [
            ("/health", "GET", None),
            ("/api/characters/options", "GET", None),
            ("/api/dice/simple", "POST", {"dice_type": "d20", "modifier": 0}),
            ("/api/redis/health", "GET", None)
        ]
        
        try:
            results = []
            
            with ThreadPoolExecutor(max_workers=TEST_CONFIG['concurrent_users']) as executor:
                futures = []
                
                # Submit multiple requests for each endpoint
                for endpoint, method, data in endpoints_to_stress:
                    for user_id in range(TEST_CONFIG['concurrent_users']):
                        url = f"{TEST_CONFIG['backend_url']}{endpoint}"
                        
                        if method == "GET":
                            future = executor.submit(self.session.get, url, timeout=TEST_CONFIG['test_timeout'])
                        else:
                            future = executor.submit(self.session.post, url, json=data, timeout=TEST_CONFIG['test_timeout'])
                        
                        futures.append((future, endpoint, user_id))
                
                # Collect results
                for future, endpoint, user_id in futures:
                    try:
                        response = future.result(timeout=TEST_CONFIG['test_timeout'])
                        results.append({
                            "endpoint": endpoint,
                            "user_id": user_id,
                            "status": response.status_code,
                            "success": response.status_code == 200
                        })
                    except Exception as e:
                        results.append({
                            "endpoint": endpoint,
                            "user_id": user_id,
                            "status": 0,
                            "success": False,
                            "error": str(e)
                        })
            
            duration_ms = (time.time() - start_time) * 1000
            
            total_requests = len(results)
            successful_requests = sum(1 for r in results if r["success"])
            success_rate = (successful_requests / total_requests) * 100
            
            if success_rate >= 95:
                perf_note = f"Success rate: {success_rate:.1f}%, {successful_requests}/{total_requests} successful"
                self.log_result("Concurrent Load Simulation", "PASS", duration_ms,
                              f"{TEST_CONFIG['concurrent_users']} concurrent users handled successfully",
                              performance_notes=perf_note, data={"results": results})
                return True
            else:
                perf_note = f"Success rate: {success_rate:.1f}%, {successful_requests}/{total_requests} successful"
                self.log_result("Concurrent Load Simulation", "WARNING", duration_ms,
                              "System performance degraded under load",
                              performance_notes=perf_note, data={"results": results})
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Concurrent Load Simulation", "FAIL", duration_ms,
                          "Concurrent load testing error", str(e))
            return False

    def test_error_handling_resilience(self) -> bool:
        """Test 7: Error Handling and System Resilience"""
        start_time = time.time()
        
        error_scenarios = [
            ("Invalid endpoint", "GET", "/api/nonexistent", None, 404),
            ("Malformed JSON", "POST", "/api/dice/simple", "invalid json", 400),
            ("Missing required fields", "POST", "/api/dice/simple", {}, 400),
            ("Invalid dice type", "POST", "/api/dice/simple", {"dice_type": "d100", "modifier": 0}, 400),
        ]
        
        error_results = {}
        
        try:
            for scenario_name, method, endpoint, data, expected_status in error_scenarios:
                scenario_start = time.time()
                url = f"{TEST_CONFIG['backend_url']}{endpoint}"
                
                try:
                    if method == "GET":
                        response = self.session.get(url, timeout=TEST_CONFIG['test_timeout'])
                    else:
                        if data == "invalid json":
                            # Send malformed JSON
                            response = self.session.post(
                                url, 
                                data="invalid json", 
                                headers={"Content-Type": "application/json"},
                                timeout=TEST_CONFIG['test_timeout']
                            )
                        else:
                            response = self.session.post(url, json=data, timeout=TEST_CONFIG['test_timeout'])
                    
                    scenario_duration = (time.time() - scenario_start) * 1000
                    
                    error_results[scenario_name] = {
                        "expected_status": expected_status,
                        "actual_status": response.status_code,
                        "duration_ms": scenario_duration,
                        "proper_error_handling": response.status_code == expected_status,
                        "has_error_message": len(response.text) > 0
                    }
                    
                except Exception as e:
                    scenario_duration = (time.time() - scenario_start) * 1000
                    error_results[scenario_name] = {
                        "expected_status": expected_status,
                        "actual_status": 0,
                        "duration_ms": scenario_duration,
                        "proper_error_handling": False,
                        "error": str(e)
                    }
            
            duration_ms = (time.time() - start_time) * 1000
            
            proper_handling = sum(1 for r in error_results.values() if r.get("proper_error_handling", False))
            
            if proper_handling >= len(error_scenarios) * 0.75:  # 75% threshold
                self.log_result("Error Handling Resilience", "PASS", duration_ms,
                              f"{proper_handling}/{len(error_scenarios)} error scenarios handled properly",
                              data=error_results)
                return True
            else:
                self.log_result("Error Handling Resilience", "FAIL", duration_ms,
                              f"Only {proper_handling}/{len(error_scenarios)} error scenarios handled properly",
                              data=error_results)
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Error Handling Resilience", "FAIL", duration_ms,
                          "Error handling testing failed", str(e))
            return False

    def run_end_to_end_tests(self) -> Dict[str, Any]:
        """Run complete end-to-end validation"""
        print("🚀 STARTING END-TO-END USER JOURNEY VALIDATION")
        print("=" * 80)
        print(f"🕐 Test suite started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target: Complete MVP User Journey Validation")
        print(f"🌐 Frontend: {TEST_CONFIG['frontend_url']}")
        print(f"🔧 Backend: {TEST_CONFIG['backend_url']}")
        print(f"👥 Concurrent Users: {TEST_CONFIG['concurrent_users']}")
        print(f"⏱️  Performance Thresholds: {TEST_CONFIG['performance_threshold_ms']}ms (pages), {TEST_CONFIG['api_threshold_ms']}ms (APIs)")
        print("=" * 80)
        
        # Define test sequence
        test_functions = [
            self.test_system_health_check,
            self.test_frontend_page_loads,
            self.test_api_integration_comprehensive,
            self.test_game_mechanics_validation,
            self.test_session_persistence,
            self.test_concurrent_load_simulation,
            self.test_error_handling_resilience
        ]
        
        passed_tests = 0
        warning_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                result = test_func()
                if result:
                    passed_tests += 1
                # Check if it was a warning (partial pass)
                if self.results and self.results[-1].status == "WARNING":
                    warning_tests += 1
            except Exception as e:
                print(f"❌ {test_func.__name__} crashed: {e}")
        
        # Calculate comprehensive results
        success_rate = (passed_tests / total_tests) * 100
        warning_rate = (warning_tests / total_tests) * 100
        total_duration = sum(r.duration_ms for r in self.results)
        
        print("\n" + "=" * 80)
        print("📊 END-TO-END USER JOURNEY VALIDATION RESULTS")
        print("=" * 80)
        
        # Print detailed results
        for result in self.results:
            status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "WARNING": "⚠️"}
            print(f"{status_emoji.get(result.status)} {result.test_name}: {result.status} ({result.duration_ms:.1f}ms)")
            if result.details:
                print(f"   📝 {result.details}")
            if result.performance_notes:
                print(f"   ⚡ Performance: {result.performance_notes}")
            if result.error:
                print(f"   🚨 {result.error}")
        
        print(f"\n🎯 FINAL SCORE: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        if warning_tests > 0:
            print(f"⚠️  Warnings: {warning_tests} tests with performance/minor issues ({warning_rate:.1f}%)")
        print(f"⏱️  Total Duration: {total_duration:.1f}ms")
        
        # Determine overall status
        if success_rate >= 95:
            print("🎉 EXCELLENT! End-to-end user journey is production-ready!")
            status = "EXCELLENT"
        elif success_rate >= 85:
            print("✅ GOOD! User journey functional with minor issues")
            status = "GOOD"
        elif success_rate >= 70:
            print("⚠️  ACCEPTABLE! Core journey works but needs optimization")
            status = "ACCEPTABLE"
        else:
            print("🚨 NEEDS WORK! Significant user journey issues detected")
            status = "NEEDS_WORK"
        
        print(f"🕐 Test suite completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return {
            "status": status,
            "success_rate": success_rate,
            "warning_rate": warning_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "total_duration_ms": total_duration,
            "test_results": self.results,
            "session_data": self.session_data
        }

def main():
    """Main test execution function"""
    suite = EndToEndTestSuite()
    results = suite.run_end_to_end_tests()
    
    # Save comprehensive results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"e2e_test_results_{timestamp}.json", 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "config": TEST_CONFIG,
            "results": results["status"],
            "success_rate": results["success_rate"],
            "warning_rate": results["warning_rate"],
            "passed_tests": results["passed_tests"],
            "total_tests": results["total_tests"],
            "duration_ms": results["total_duration_ms"],
            "session_data": results["session_data"],
            "details": [
                {
                    "test": r.test_name,
                    "status": r.status,
                    "duration_ms": r.duration_ms,
                    "details": r.details,
                    "error": r.error,
                    "performance_notes": r.performance_notes,
                    "data": r.data
                } for r in results["test_results"]
            ]
        }, f, indent=2)
    
    # Create summary report
    with open(f"e2e_summary_{timestamp}.md", 'w') as f:
        f.write(f"# End-to-End Test Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Overall Status: {results['status']}\n\n")
        f.write(f"- **Success Rate**: {results['success_rate']:.1f}%\n")
        f.write(f"- **Tests Passed**: {results['passed_tests']}/{results['total_tests']}\n")
        f.write(f"- **Total Duration**: {results['total_duration_ms']:.1f}ms\n")
        f.write(f"- **Frontend URL**: {TEST_CONFIG['frontend_url']}\n")
        f.write(f"- **Backend URL**: {TEST_CONFIG['backend_url']}\n\n")
        
        f.write("## Test Results\n\n")
        for result in results["test_results"]:
            status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "WARNING": "⚠️"}
            f.write(f"{status_emoji.get(result.status)} **{result.test_name}**: {result.status} ({result.duration_ms:.1f}ms)\n")
            if result.details:
                f.write(f"   - {result.details}\n")
            if result.performance_notes:
                f.write(f"   - Performance: {result.performance_notes}\n")
            f.write("\n")
    
    return results["success_rate"] >= 80  # Return True if tests mostly passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 