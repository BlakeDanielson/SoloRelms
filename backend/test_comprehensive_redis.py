#!/usr/bin/env python3
"""
Comprehensive Redis Integration Test Suite
Tests all Redis functionality including APIs, sessions, combat state, and cleanup
"""

import requests
import json
import time
from datetime import datetime
from services.redis_service import redis_service

# API Base URL
BASE_URL = "http://localhost:8000/api"

def test_redis_health_api():
    """Test Redis health check via API"""
    print("🏥 Testing Redis Health API...")
    try:
        response = requests.get(f"{BASE_URL}/redis/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Health Check: {data['status']}")
            print(f"   Redis Info: {data['redis_info']}")
            return True
        else:
            print(f"   ❌ Health API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health API error: {e}")
        return False

def test_session_creation_api():
    """Test session creation via API"""
    print("\n👤 Testing Session Creation API...")
    try:
        session_data = {
            "user_id": "test_user_123",
            "character_id": 4,
            "story_arc_id": 1
        }
        
        response = requests.post(f"{BASE_URL}/redis/session/create", json=session_data)
        if response.status_code == 200:
            session = response.json()
            print(f"   ✅ Session Created: {session['session_id']}")
            print(f"   Character ID: {session['character_id']}")
            print(f"   Story Arc ID: {session['story_arc_id']}")
            return session['session_id']
        else:
            print(f"   ❌ Session creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Session creation error: {e}")
        return None

def test_session_retrieval_api(session_id):
    """Test session retrieval via API"""
    print(f"\n🔍 Testing Session Retrieval API...")
    try:
        response = requests.get(f"{BASE_URL}/redis/session/{session_id}")
        if response.status_code == 200:
            session = response.json()
            print(f"   ✅ Session Retrieved: {session['session_id']}")
            print(f"   Active: {session['active']}")
            print(f"   Last Activity: {session['last_activity']}")
            return True
        else:
            print(f"   ❌ Session retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Session retrieval error: {e}")
        return False

def test_combat_state_api():
    """Test combat state storage and retrieval via API"""
    print(f"\n⚔️  Testing Combat State API...")
    try:
        # Test combat state storage
        combat_data = {
            "encounter_id": 1,
            "include_participants": True
        }
        
        store_response = requests.post(f"{BASE_URL}/redis/cache/combat", json=combat_data)
        if store_response.status_code == 200:
            print(f"   ✅ Combat state stored via API")
        else:
            print(f"   ⚠️  Combat storage response: {store_response.status_code}")
        
        # Test combat state retrieval
        get_response = requests.get(f"{BASE_URL}/redis/cache/combat/1")
        if get_response.status_code == 200:
            combat_state = get_response.json()
            print(f"   ✅ Combat state retrieved via API")
            print(f"   Encounter ID: {combat_state.get('encounter_id', 'N/A')}")
            print(f"   State: {combat_state.get('state', 'N/A')}")
            return True
        else:
            print(f"   ❌ Combat retrieval failed: {get_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Combat state API error: {e}")
        return False

def test_cache_character_api():
    """Test character caching via API"""
    print(f"\n🧙 Testing Character Cache API...")
    try:
        cache_data = {
            "character_id": 4,
            "expiry_minutes": 60
        }
        
        response = requests.post(f"{BASE_URL}/redis/cache/character", json=cache_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Character cached via API: {result['message']}")
            return True
        else:
            print(f"   ❌ Character caching failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Character cache API error: {e}")
        return False

def test_cache_story_api():
    """Test story caching via API"""
    print(f"\n📚 Testing Story Cache API...")
    try:
        cache_data = {
            "story_arc_id": 1,
            "expiry_minutes": 30
        }
        
        response = requests.post(f"{BASE_URL}/redis/cache/story", json=cache_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Story cached via API: {result['message']}")
            return True
        else:
            print(f"   ❌ Story caching failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Story cache API error: {e}")
        return False

def test_cleanup_apis():
    """Test cleanup functionality via APIs"""
    print(f"\n🧹 Testing Cleanup APIs...")
    
    cleanup_results = {}
    
    # Test expired session cleanup
    try:
        response = requests.post(f"{BASE_URL}/redis/cleanup/expired-sessions")
        if response.status_code == 200:
            result = response.json()
            cleanup_results['expired_sessions'] = result['cleaned_sessions']
            print(f"   ✅ Expired sessions cleanup: {result['cleaned_sessions']} cleaned")
        else:
            print(f"   ❌ Expired sessions cleanup failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Expired sessions cleanup error: {e}")
    
    # Test stale cache cleanup
    try:
        response = requests.post(f"{BASE_URL}/redis/cleanup/stale-cache?max_age_hours=24")
        if response.status_code == 200:
            result = response.json()
            cleanup_results['stale_cache'] = result['cleanup_results']['total']
            print(f"   ✅ Stale cache cleanup: {result['cleanup_results']['total']} cleaned")
        else:
            print(f"   ❌ Stale cache cleanup failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stale cache cleanup error: {e}")
    
    return cleanup_results

def test_cache_statistics_api():
    """Test cache statistics via API"""
    print(f"\n📊 Testing Cache Statistics API...")
    try:
        response = requests.get(f"{BASE_URL}/redis/statistics")
        if response.status_code == 200:
            result = response.json()
            stats = result['statistics']
            print(f"   ✅ Cache statistics retrieved via API")
            print(f"   Redis Version: {stats['redis_info'].get('redis_version', 'unknown')}")
            print(f"   Memory Usage: {stats['redis_info'].get('used_memory_human', 'unknown')}")
            print(f"   Cache Counts:")
            for cache_type, count in stats['cache_counts'].items():
                if count > 0:
                    print(f"      {cache_type}: {count}")
            return True
        else:
            print(f"   ❌ Statistics API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Statistics API error: {e}")
        return False

def test_cache_invalidation_apis():
    """Test cache invalidation via APIs"""
    print(f"\n🗑️  Testing Cache Invalidation APIs...")
    
    results = {}
    
    # Test character cache invalidation
    try:
        response = requests.delete(f"{BASE_URL}/redis/cache/character/4")
        if response.status_code == 200:
            result = response.json()
            results['character'] = True
            print(f"   ✅ Character cache invalidation: {result['message']}")
        else:
            print(f"   ❌ Character invalidation failed: {response.status_code}")
            results['character'] = False
    except Exception as e:
        print(f"   ❌ Character invalidation error: {e}")
        results['character'] = False
    
    # Test story cache invalidation
    try:
        response = requests.delete(f"{BASE_URL}/redis/cache/story/1")
        if response.status_code == 200:
            result = response.json()
            results['story'] = True
            print(f"   ✅ Story cache invalidation: {result['message']}")
        else:
            print(f"   ❌ Story invalidation failed: {response.status_code}")
            results['story'] = False
    except Exception as e:
        print(f"   ❌ Story invalidation error: {e}")
        results['story'] = False
    
    # Test user cache invalidation
    try:
        response = requests.delete(f"{BASE_URL}/redis/cache/user/test_user_123")
        if response.status_code == 200:
            result = response.json()
            results['user'] = True
            print(f"   ✅ User cache invalidation: {result['message']}")
        else:
            print(f"   ❌ User invalidation failed: {response.status_code}")
            results['user'] = False
    except Exception as e:
        print(f"   ❌ User invalidation error: {e}")
        results['user'] = False
    
    return results

def test_redis_service_direct():
    """Test Redis service directly (not via API)"""
    print(f"\n🔧 Testing Redis Service Direct Methods...")
    
    try:
        # Test health check
        health = redis_service.health_check()
        print(f"   ✅ Direct health check: {health['healthy']}")
        
        # Test cache statistics
        stats = redis_service.get_cache_statistics()
        print(f"   ✅ Direct cache statistics: {len(stats['cache_counts'])} cache types")
        
        # Test user sessions
        sessions = redis_service.get_user_sessions("test_user_123")
        print(f"   ✅ Direct user sessions: {len(sessions)} active sessions")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Direct service test error: {e}")
        return False

def main():
    """Main comprehensive test function"""
    print("🚀 COMPREHENSIVE REDIS INTEGRATION TEST SUITE")
    print("=" * 70)
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Test 1: Redis Health
    test_results['redis_health'] = test_redis_health_api()
    
    # Test 2: Session Management  
    session_id = test_session_creation_api()
    test_results['session_creation'] = session_id is not None
    
    if session_id:
        test_results['session_retrieval'] = test_session_retrieval_api(session_id)
    else:
        test_results['session_retrieval'] = False
    
    # Test 3: Combat State Management
    test_results['combat_state'] = test_combat_state_api()
    
    # Test 4: Character and Story Caching
    test_results['character_cache'] = test_cache_character_api()
    test_results['story_cache'] = test_cache_story_api()
    
    # Test 5: Cache Statistics
    test_results['cache_statistics'] = test_cache_statistics_api()
    
    # Test 6: Cache Invalidation
    invalidation_results = test_cache_invalidation_apis()
    test_results['cache_invalidation'] = all(invalidation_results.values())
    
    # Test 7: Cleanup Operations
    cleanup_results = test_cleanup_apis()
    test_results['cleanup_operations'] = len(cleanup_results) > 0
    
    # Test 8: Direct Service Methods
    test_results['direct_service'] = test_redis_service_direct()
    
    # Results Summary
    print("\n" + "=" * 70)
    print("📋 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        formatted_name = test_name.replace('_', ' ').title()
        print(f"   {formatted_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n🎯 Overall Score: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Redis integration is fully operational!")
        print("🚀 Ready for production deployment!")
        
        print(f"\n📡 Available API Endpoints:")
        print(f"   Health: GET /api/redis/health")
        print(f"   Sessions: POST /api/redis/session/create")
        print(f"   Combat: POST/GET /api/redis/cache/combat")
        print(f"   Statistics: GET /api/redis/statistics")
        print(f"   Cleanup: POST /api/redis/cleanup/*")
        
    else:
        failed_count = total_tests - passed_tests
        print(f"\n⚠️  {failed_count} test(s) failed. See details above.")
        
        if failed_count <= 2:
            print("🔶 Minor issues detected - system is mostly functional")
        else:
            print("🔴 Major issues detected - review implementation")
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main() 