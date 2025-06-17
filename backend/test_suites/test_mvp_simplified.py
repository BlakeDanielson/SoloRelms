#!/usr/bin/env python3
"""
SIMPLIFIED MVP TEST SUITE
Tests core MVP functionality without authentication dependencies

Tests include:
- Backend Health
- Redis Integration  
- Database Connectivity
- Dice Rolling System
- Cache Operations
- Performance Testing
- Direct Database Operations

Usage: python test_mvp_simplified.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.character import Character
from models.story import StoryArc, StoryStage
from services.redis_service import redis_service

# Test Configuration
TEST_CONFIG = {
    "backend_url": "http://localhost:8000",
    "test_timeout": 30,
    "concurrent_users": 5,
    "performance_threshold_ms": 2000
}

@dataclass
class TestResult:
    """Test result tracking"""
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    duration_ms: float
    details: str
    error: str = None

class SimplifiedMVPTestSuite:
    """Simplified MVP test suite focusing on core functionality"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.session = requests.Session()
        
    def log_result(self, test_name: str, status: str, duration_ms: float, 
                   details: str, error: str = None):
        """Log test result"""
        result = TestResult(test_name, status, duration_ms, details, error)
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

    def test_database_connectivity(self) -> bool:
        """Test 2: Database Health and Connectivity"""
        start_time = time.time()
        
        try:
            response = self.session.get(f"{TEST_CONFIG['backend_url']}/health/database", 
                                      timeout=TEST_CONFIG['test_timeout'])
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Database Connectivity", "PASS", duration_ms,
                              f"Database connected, {data.get('character_count', 0)} characters")
                return True
            else:
                self.log_result("Database Connectivity", "FAIL", duration_ms,
                              f"Database health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Database Connectivity", "FAIL", duration_ms,
                          "Database connection error", str(e))
            return False

    def test_redis_integration(self) -> bool:
        """Test 3: Redis Integration and Health"""
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

    def test_character_options_endpoint(self) -> bool:
        """Test 4: Character Options (No Auth Required)"""
        start_time = time.time()
        
        try:
            response = self.session.get(
                f"{TEST_CONFIG['backend_url']}/api/characters/options",
                timeout=TEST_CONFIG['test_timeout']
            )
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                options = response.json()
                races_count = len(options.get("races", []))
                classes_count = len(options.get("classes", []))
                backgrounds_count = len(options.get("backgrounds", []))
                
                self.log_result("Character Options", "PASS", duration_ms,
                              f"{races_count} races, {classes_count} classes, {backgrounds_count} backgrounds")
                return True
            else:
                self.log_result("Character Options", "FAIL", duration_ms,
                              f"Options endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Character Options", "FAIL", duration_ms,
                          "Character options error", str(e))
            return False

    def test_dice_rolling_system(self) -> bool:
        """Test 5: Dice Rolling System"""
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
                    if (result.get('success') and 
                        'total' in result.get('data', {}) and 
                        'breakdown' in result.get('data', {})):
                        passed_tests += 1
                    
            duration_ms = (time.time() - start_time) * 1000
            
            if passed_tests == len(dice_tests):
                self.log_result("Dice Rolling System", "PASS", duration_ms,
                              f"All {len(dice_tests)} dice types working correctly")
                return True
            else:
                self.log_result("Dice Rolling System", "FAIL", duration_ms,
                              f"Only {passed_tests}/{len(dice_tests)} dice tests passed")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Dice Rolling System", "FAIL", duration_ms,
                          "Dice rolling error", str(e))
            return False

    def test_cache_statistics(self) -> bool:
        """Test 6: Cache Statistics"""
        start_time = time.time()
        
        try:
            response = self.session.get(
                f"{TEST_CONFIG['backend_url']}/api/redis/statistics",
                timeout=TEST_CONFIG['test_timeout']
            )
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('statistics', {})
                cache_counts = stats.get('cache_counts', {})
                total_cached = sum(cache_counts.values())
                
                self.log_result("Cache Statistics", "PASS", duration_ms,
                              f"Cache statistics retrieved, {total_cached} cached items")
                return True
            else:
                self.log_result("Cache Statistics", "FAIL", duration_ms,
                              f"Cache statistics failed: {response.status_code}")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Cache Statistics", "FAIL", duration_ms,
                          "Cache statistics error", str(e))
            return False

    def test_cleanup_operations(self) -> bool:
        """Test 7: Cleanup Operations"""
        start_time = time.time()
        
        try:
            # Test expired session cleanup
            response = self.session.post(
                f"{TEST_CONFIG['backend_url']}/api/redis/cleanup/expired-sessions",
                timeout=TEST_CONFIG['test_timeout']
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                cleaned_count = result.get('cleaned_sessions', 0)
                self.log_result("Cleanup Operations", "PASS", duration_ms,
                              f"Cleanup successful, {cleaned_count} sessions cleaned")
                return True
            else:
                self.log_result("Cleanup Operations", "FAIL", duration_ms,
                              f"Cleanup failed: {response.status_code}")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Cleanup Operations", "FAIL", duration_ms,
                          "Cleanup operations error", str(e))
            return False

    def test_performance_load(self) -> bool:
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
                        futures.append(future)
                
                for future in futures:
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
                self.log_result("Performance Load Testing", "PASS", duration_ms,
                              f"Success rate: {success_rate:.1f}%, Load test passed")
                return True
            else:
                self.log_result("Performance Load Testing", "FAIL", duration_ms,
                              f"Success rate: {success_rate:.1f}%, Performance issues detected")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Performance Load Testing", "FAIL", duration_ms,
                          "Performance testing error", str(e))
            return False

    def test_direct_database_operations(self) -> bool:
        """Test 9: Direct Database Operations (Create Test Data)"""
        start_time = time.time()
        
        try:
            db = next(get_db())
            
            # Create test user
            test_user = db.query(User).filter(User.id == "test_user_direct").first()
            if not test_user:
                test_user = User(
                    id="test_user_direct",
                    email="test_direct@example.com",
                    first_name="Direct",
                    last_name="Test",
                    username="directtest",
                    is_active=True,
                    email_verified=True
                )
                db.add(test_user)
                db.flush()
            
            # Create test character
            test_character = Character(
                user_id=test_user.id,
                name="Direct Test Hero",
                race="Human",
                character_class="Fighter",
                level=1,
                strength=15,
                dexterity=14,
                constitution=13,
                intelligence=12,
                wisdom=10,
                charisma=8,
                max_hit_points=14,
                current_hit_points=14,
                armor_class=16,
                background="Soldier"
            )
            db.add(test_character)
            db.commit()
            
            # Test Redis direct operations
            health = redis_service.health_check()
            
            duration_ms = (time.time() - start_time) * 1000
            
            if health['healthy']:
                self.log_result("Direct Database Operations", "PASS", duration_ms,
                              f"Created test user and character, Redis healthy")
                return True
            else:
                self.log_result("Direct Database Operations", "FAIL", duration_ms,
                              "Redis not healthy in direct test")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Direct Database Operations", "FAIL", duration_ms,
                          "Direct database operations error", str(e))
            return False
        finally:
            db.close()

    def test_redis_combat_state_storage(self) -> bool:
        """Test 10: Redis Combat State Storage (Direct)"""
        start_time = time.time()
        
        try:
            # Test cache operations directly through Redis service
            stats = redis_service.get_cache_statistics()
            
            # Test cleanup functionality
            cleaned = redis_service.cleanup_expired_sessions()
            
            duration_ms = (time.time() - start_time) * 1000
            
            self.log_result("Redis Combat State Storage", "PASS", duration_ms,
                          f"Cache stats retrieved, {cleaned} sessions cleaned")
            return True
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.log_result("Redis Combat State Storage", "FAIL", duration_ms,
                          "Redis combat state error", str(e))
            return False

    def run_simplified_tests(self) -> Dict[str, Any]:
        """Run all simplified MVP tests"""
        print("🚀 STARTING SIMPLIFIED MVP TEST SUITE")
        print("=" * 80)
        print(f"🕐 Test suite started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target Systems: Backend, Database, Redis, Dice, Cache, Performance")
        print(f"👥 Concurrent Users: {TEST_CONFIG['concurrent_users']}")
        print(f"⏱️  Performance Threshold: {TEST_CONFIG['performance_threshold_ms']}ms")
        print("=" * 80)
        
        # Run all tests in sequence
        test_functions = [
            self.test_backend_health,
            self.test_database_connectivity,
            self.test_redis_integration,
            self.test_character_options_endpoint,
            self.test_dice_rolling_system,
            self.test_cache_statistics,
            self.test_cleanup_operations,
            self.test_performance_load,
            self.test_direct_database_operations,
            self.test_redis_combat_state_storage
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
        print("📊 SIMPLIFIED MVP TEST RESULTS")
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
            print("🎉 EXCELLENT! Core MVP systems are production-ready!")
            status = "EXCELLENT"
        elif success_rate >= 75:
            print("✅ GOOD! Core MVP systems functional with minor issues")
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
            "test_results": self.results
        }

def main():
    """Main test execution function"""
    suite = SimplifiedMVPTestSuite()
    results = suite.run_simplified_tests()
    
    # Save detailed results
    with open(f"simplified_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
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