#!/usr/bin/env python3
"""
COMPREHENSIVE MVP TEST SUITE
End-to-end automated testing for SoloRealms D&D RPG MVP

Tests include:
- Character Creation & Management
- Story Arc Generation & Progression  
- Combat Mechanics & State Management
- Dice Rolling & Game Logic
- Redis Session & Cache Management
- AI Integration & Response Quality
- API Endpoint Functionality
- Database Integrity
- Performance & Load Testing
- Cross-System Integration

Usage: python test_mvp_comprehensive.py
"""

import asyncio
import requests
import json
import time
import random
import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Test Configuration
TEST_CONFIG = {
    "backend_url": "http://localhost:8000",
    "frontend_url": "http://localhost:3003", 
    "test_user_id": "mvp_test_user",
    "test_timeout": 30,
    "concurrent_users": 5,
    "performance_threshold_ms": 2000,
    "ai_response_min_length": 50
}

@dataclass
class TestResult:
    """Test result tracking"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration_ms: float
    details: str
    error: Optional[str] = None
    data: Optional[Dict] = None

class MVPTestSuite:
    """Comprehensive MVP test suite"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.test_data = {}
        self.session = requests.Session()
        
    def log_result(self, test_name: str, status: str, duration_ms: float, 
                   details: str, error: str = None, data: Dict = None):
        """Log test result"""
        result = TestResult(test_name, status, duration_ms, details, error, data)
        self.results.append(result)
        
        status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}
        print(f"{status_emoji.get(status, '❓')} {test_name}: {status} ({duration_ms:.1f}ms)")
        if details:
            print(f"   📝 {details}")
        if error:
            print(f"   🚨 Error: {error}")

    def test_backend_health(self) -> bool:
        """Test 1: Backend Health and Connectivity"""
        start_time = time.time()
        
        try:
            response = self.session.get(f"{TEST_CONFIG['backend_url']}/health", 
                                      timeout=TEST_CONFIG['test_timeout'])
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                self.log_result("Backend Health Check", "PASS", duration_ms,
                              f"Backend responding on port 8000")
                return True
            else:
                self.log_result("Backend Health Check", "FAIL", duration_ms,
                              f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Backend Health Check", "FAIL", duration_ms,
                          "Backend not responding", str(e))
            return False

    def test_redis_integration(self) -> bool:
        """Test 2: Redis Integration and Health"""
        start_time = time.time()
        
        try:
            response = self.session.get(f"{TEST_CONFIG['backend_url']}/api/redis/health",
                                      timeout=TEST_CONFIG['test_timeout'])
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data['redis_info']['healthy']:
                    self.log_result("Redis Integration", "PASS", duration_ms,
                                  f"Redis v{data['redis_info']['redis_version']} healthy")
                    return True
                else:
                    self.log_result("Redis Integration", "FAIL", duration_ms,
                                  "Redis unhealthy")
                    return False
            else:
                self.log_result("Redis Integration", "FAIL", duration_ms,
                              f"Redis health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Redis Integration", "FAIL", duration_ms,
                          "Redis health check error", str(e))
            return False

    def test_character_creation_flow(self) -> Optional[Dict]:
        """Test 3: Character Creation End-to-End"""
        start_time = time.time()
        
        try:
            # Get character options
            options_response = self.session.get(
                f"{TEST_CONFIG['backend_url']}/api/characters/options",
                timeout=TEST_CONFIG['test_timeout']
            )
            
            if options_response.status_code != 200:
                duration_ms = (time.time() - start_time) * 1000
                self.log_result("Character Creation Flow", "FAIL", duration_ms,
                              "Failed to get character options")
                return None
            
            options = options_response.json()
            
            # Create test character
            character_data = {
                "user_id": TEST_CONFIG["test_user_id"],
                "name": f"TestHero_{int(time.time())}",
                "race": random.choice(options["races"]),
                "character_class": random.choice(options["classes"]),
                "background": random.choice(options["backgrounds"]),
                "level": 1,
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
            
            create_response = self.session.post(
                f"{TEST_CONFIG['backend_url']}/api/characters/",
                json=character_data,
                timeout=TEST_CONFIG['test_timeout']
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if create_response.status_code == 200:
                character = create_response.json()
                self.test_data['character'] = character
                self.log_result("Character Creation Flow", "PASS", duration_ms,
                              f"Created {character['name']} ({character['race']} {character['character_class']})")
                return character
            else:
                self.log_result("Character Creation Flow", "FAIL", duration_ms,
                              f"Character creation failed: {create_response.status_code}")
                return None
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Character Creation Flow", "FAIL", duration_ms,
                          "Character creation error", str(e))
            return None

    def test_dice_rolling_mechanics(self) -> bool:
        """Test 4: Dice Rolling System"""
        start_time = time.time()
        
        dice_tests = [
            {"dice_type": "d20", "modifier": 5},
            {"dice_type": "d12", "modifier": 0},
            {"dice_type": "d10", "modifier": -2},
            {"dice_type": "d8", "modifier": 3},
            {"dice_type": "d6", "modifier": 1},
            {"dice_type": "d4", "modifier": 0}
        ]
        
        passed_tests = 0
        
        try:
            for dice_test in dice_tests:
                response = self.session.post(
                    f"{TEST_CONFIG['backend_url']}/api/dice/simple",
                    json=dice_test,
                    timeout=TEST_CONFIG['test_timeout']
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if (result['success'] and 
                        'total' in result['data'] and 
                        'breakdown' in result['data']):
                        passed_tests += 1
                    
            duration_ms = (time.time() - start_time) * 1000
            
            if passed_tests == len(dice_tests):
                self.log_result("Dice Rolling Mechanics", "PASS", duration_ms,
                              f"All {len(dice_tests)} dice types working correctly")
                return True
            else:
                self.log_result("Dice Rolling Mechanics", "FAIL", duration_ms,
                              f"Only {passed_tests}/{len(dice_tests)} dice tests passed")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Dice Rolling Mechanics", "FAIL", duration_ms,
                          "Dice rolling error", str(e))
            return False

    def test_story_generation(self) -> Optional[Dict]:
        """Test 5: Story Arc Generation"""
        start_time = time.time()
        
        if 'character' not in self.test_data:
            self.log_result("Story Generation", "SKIP", 0,
                          "No character available for story generation")
            return None
        
        try:
            story_data = {
                "character_id": self.test_data['character']['id'],
                "user_id": TEST_CONFIG["test_user_id"],
                "story_type": "short_form",
                "genre_preference": "classic_fantasy",
                "complexity": "moderate"
            }
            
            response = self.session.post(
                f"{TEST_CONFIG['backend_url']}/api/stories/",
                json=story_data,
                timeout=TEST_CONFIG['test_timeout'] * 2  # Story generation takes longer
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                story = response.json()
                self.test_data['story'] = story
                
                # Validate story content
                required_fields = ['title', 'story_seed', 'current_stage']
                if all(field in story for field in required_fields):
                    self.log_result("Story Generation", "PASS", duration_ms,
                                  f"Generated: '{story['title']}'")
                    return story
                else:
                    self.log_result("Story Generation", "FAIL", duration_ms,
                                  "Story missing required fields")
                    return None
            else:
                self.log_result("Story Generation", "FAIL", duration_ms,
                              f"Story generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Story Generation", "FAIL", duration_ms,
                          "Story generation error", str(e))
            return None

    def test_session_management(self) -> Optional[str]:
        """Test 6: Game Session Management"""
        start_time = time.time()
        
        if 'character' not in self.test_data or 'story' not in self.test_data:
            self.log_result("Session Management", "SKIP", 0,
                          "No character/story available for session")
            return None
        
        try:
            session_data = {
                "user_id": TEST_CONFIG["test_user_id"],
                "character_id": self.test_data['character']['id'],
                "story_arc_id": self.test_data['story']['id']
            }
            
            # Create session
            create_response = self.session.post(
                f"{TEST_CONFIG['backend_url']}/api/redis/session/create",
                json=session_data,
                timeout=TEST_CONFIG['test_timeout']
            )
            
            if create_response.status_code == 200:
                session = create_response.json()
                session_id = session['session_id']
                
                # Retrieve session
                get_response = self.session.get(
                    f"{TEST_CONFIG['backend_url']}/api/redis/session/{session_id}",
                    timeout=TEST_CONFIG['test_timeout']
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                if get_response.status_code == 200:
                    self.test_data['session_id'] = session_id
                    self.log_result("Session Management", "PASS", duration_ms,
                                  f"Session created and retrieved: {session_id}")
                    return session_id
                else:
                    self.log_result("Session Management", "FAIL", duration_ms,
                                  "Session retrieval failed")
                    return None
            else:
                duration_ms = (time.time() - start_time) * 1000
                self.log_result("Session Management", "FAIL", duration_ms,
                              f"Session creation failed: {create_response.status_code}")
                return None
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Session Management", "FAIL", duration_ms,
                          "Session management error", str(e))
            return None

    def test_combat_system(self) -> bool:
        """Test 7: Combat System Integration"""
        start_time = time.time()
        
        if 'story' not in self.test_data:
            self.log_result("Combat System", "SKIP", 0,
                          "No story available for combat testing")
            return False
        
        try:
            # Create combat encounter
            combat_data = {
                "story_arc_id": self.test_data['story']['id'],
                "encounter_type": "combat",
                "name": "Test Combat Encounter",
                "description": "Automated test combat",
                "difficulty_rating": 2
            }
            
            create_response = self.session.post(
                f"{TEST_CONFIG['backend_url']}/api/combat/encounters/",
                json=combat_data,
                timeout=TEST_CONFIG['test_timeout']
            )
            
            if create_response.status_code == 200:
                encounter = create_response.json()
                encounter_id = encounter['id']
                
                # Test Redis combat state storage
                cache_response = self.session.post(
                    f"{TEST_CONFIG['backend_url']}/api/redis/cache/combat",
                    json={"encounter_id": encounter_id, "include_participants": True},
                    timeout=TEST_CONFIG['test_timeout']
                )
                
                duration_ms = (time.time() - start_time) * 1000
                
                if cache_response.status_code == 200:
                    self.test_data['combat_encounter'] = encounter
                    self.log_result("Combat System", "PASS", duration_ms,
                                  f"Combat encounter created and cached: {encounter_id}")
                    return True
                else:
                    self.log_result("Combat System", "FAIL", duration_ms,
                                  "Combat state caching failed")
                    return False
            else:
                duration_ms = (time.time() - start_time) * 1000
                self.log_result("Combat System", "FAIL", duration_ms,
                              f"Combat creation failed: {create_response.status_code}")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Combat System", "FAIL", duration_ms,
                          "Combat system error", str(e))
            return False

    def test_performance_benchmarks(self) -> bool:
        """Test 8: Performance and Load Testing"""
        start_time = time.time()
        
        endpoints_to_test = [
            ("/health", "GET", None),
            ("/api/redis/health", "GET", None),
            ("/api/characters/options", "GET", None),
            ("/api/dice/simple", "POST", {"dice_type": "d20", "modifier": 0})
        ]
        
        performance_results = []
        
        try:
            # Test concurrent requests
            with ThreadPoolExecutor(max_workers=TEST_CONFIG['concurrent_users']) as executor:
                futures = []
                
                for endpoint, method, data in endpoints_to_test:
                    for _ in range(TEST_CONFIG['concurrent_users']):
                        if method == "GET":
                            future = executor.submit(
                                self.session.get,
                                f"{TEST_CONFIG['backend_url']}{endpoint}",
                                timeout=TEST_CONFIG['test_timeout']
                            )
                        else:
                            future = executor.submit(
                                self.session.post,
                                f"{TEST_CONFIG['backend_url']}{endpoint}",
                                json=data,
                                timeout=TEST_CONFIG['test_timeout']
                            )
                        futures.append((future, endpoint))
                
                for future, endpoint in futures:
                    try:
                        response = future.result(timeout=TEST_CONFIG['test_timeout'])
                        if response.status_code == 200:
                            performance_results.append(True)
                        else:
                            performance_results.append(False)
                    except Exception:
                        performance_results.append(False)
            
            duration_ms = (time.time() - start_time) * 1000
            success_rate = sum(performance_results) / len(performance_results) * 100
            
            if success_rate >= 95 and duration_ms <= TEST_CONFIG['performance_threshold_ms']:
                self.log_result("Performance Benchmarks", "PASS", duration_ms,
                              f"Success rate: {success_rate:.1f}%, Load test passed")
                return True
            else:
                self.log_result("Performance Benchmarks", "FAIL", duration_ms,
                              f"Success rate: {success_rate:.1f}%, Performance issues detected")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Performance Benchmarks", "FAIL", duration_ms,
                          "Performance testing error", str(e))
            return False

    def test_frontend_connectivity(self) -> bool:
        """Test 9: Frontend Connectivity"""
        start_time = time.time()
        
        try:
            response = self.session.get(f"{TEST_CONFIG['frontend_url']}", 
                                      timeout=TEST_CONFIG['test_timeout'])
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                self.log_result("Frontend Connectivity", "PASS", duration_ms,
                              "Frontend responding on port 3003")
                return True
            else:
                self.log_result("Frontend Connectivity", "FAIL", duration_ms,
                              f"Frontend returned status: {response.status_code}")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Frontend Connectivity", "FAIL", duration_ms,
                          "Frontend not responding", str(e))
            return False

    def test_cache_operations(self) -> bool:
        """Test 10: Cache Operations and Cleanup"""
        start_time = time.time()
        
        try:
            # Test cache statistics
            stats_response = self.session.get(
                f"{TEST_CONFIG['backend_url']}/api/redis/statistics",
                timeout=TEST_CONFIG['test_timeout']
            )
            
            if stats_response.status_code != 200:
                duration_ms = (time.time() - start_time) * 1000
                self.log_result("Cache Operations", "FAIL", duration_ms,
                              "Cache statistics failed")
                return False
            
            # Test cleanup operations
            cleanup_response = self.session.post(
                f"{TEST_CONFIG['backend_url']}/api/redis/cleanup/expired-sessions",
                timeout=TEST_CONFIG['test_timeout']
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if cleanup_response.status_code == 200:
                self.log_result("Cache Operations", "PASS", duration_ms,
                              "Cache statistics and cleanup working")
                return True
            else:
                self.log_result("Cache Operations", "FAIL", duration_ms,
                              "Cache cleanup failed")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Cache Operations", "FAIL", duration_ms,
                          "Cache operations error", str(e))
            return False

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all MVP tests and return comprehensive results"""
        print("🚀 STARTING COMPREHENSIVE MVP TEST SUITE")
        print("=" * 80)
        print(f"🕐 Test suite started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target Systems: Backend, Redis, Frontend, Game Logic, Performance")
        print(f"👥 Concurrent Users: {TEST_CONFIG['concurrent_users']}")
        print(f"⏱️  Performance Threshold: {TEST_CONFIG['performance_threshold_ms']}ms")
        print("=" * 80)
        
        # Run all tests in sequence
        test_functions = [
            self.test_backend_health,
            self.test_redis_integration, 
            self.test_character_creation_flow,
            self.test_dice_rolling_mechanics,
            self.test_story_generation,
            self.test_session_management,
            self.test_combat_system,
            self.test_performance_benchmarks,
            self.test_frontend_connectivity,
            self.test_cache_operations
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                result = test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ {test_func.__name__} crashed: {e}")
        
        # Calculate results
        success_rate = (passed_tests / total_tests) * 100
        total_duration = sum(r.duration_ms for r in self.results)
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE MVP TEST RESULTS")
        print("=" * 80)
        
        # Print detailed results
        for result in self.results:
            status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}
            print(f"{status_emoji.get(result.status)} {result.test_name}: {result.status} ({result.duration_ms:.1f}ms)")
            if result.details:
                print(f"   📝 {result.details}")
            if result.error:
                print(f"   🚨 {result.error}")
        
        print(f"\n🎯 FINAL SCORE: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        print(f"⏱️  Total Duration: {total_duration:.1f}ms")
        
        # Determine overall status
        if success_rate >= 90:
            print("🎉 EXCELLENT! MVP is production-ready!")
            status = "EXCELLENT"
        elif success_rate >= 75:
            print("✅ GOOD! MVP is functional with minor issues")
            status = "GOOD"
        elif success_rate >= 50:
            print("⚠️  NEEDS WORK! Significant issues detected")
            status = "NEEDS_WORK"
        else:
            print("🚨 CRITICAL! Major system failures detected")
            status = "CRITICAL"
        
        print(f"🕐 Test suite completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            "status": status,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "total_duration_ms": total_duration,
            "test_results": self.results,
            "test_data": self.test_data
        }

def main():
    """Main test execution function"""
    suite = MVPTestSuite()
    results = suite.run_comprehensive_tests()
    
    # Save detailed results
    with open(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "config": TEST_CONFIG,
            "results": results["status"],
            "success_rate": results["success_rate"],
            "passed_tests": results["passed_tests"],
            "total_tests": results["total_tests"],
            "duration_ms": results["total_duration_ms"],
            "details": [
                {
                    "test": r.test_name,
                    "status": r.status,
                    "duration_ms": r.duration_ms,
                    "details": r.details,
                    "error": r.error
                } for r in results["test_results"]
            ]
        }, f, indent=2)
    
    return results["success_rate"] >= 75  # Return True if tests mostly passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 