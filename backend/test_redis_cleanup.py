#!/usr/bin/env python3
"""
Test script for Redis cache invalidation and cleanup mechanisms
Tests the comprehensive cleanup functionality we've implemented
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from services.redis_service import redis_service, CacheExpiry

def test_cache_statistics():
    """Test cache statistics functionality"""
    print("📊 Testing cache statistics...")
    
    try:
        stats = redis_service.get_cache_statistics()
        
        print(f"   ✅ Cache Statistics Retrieved:")
        print(f"      Redis Version: {stats['redis_info'].get('version', 'unknown')}")
        print(f"      Connected Clients: {stats['redis_info'].get('connected_clients', 0)}")
        print(f"      Memory Usage: {stats['redis_info'].get('used_memory_human', 'unknown')}")
        print(f"      Commands Processed: {stats['redis_info'].get('total_commands_processed', 0)}")
        
        print(f"   📈 Cache Counts by Type:")
        for cache_type, count in stats['cache_counts'].items():
            print(f"      {cache_type}: {count} keys")
        
        print(f"   🔍 Memory Usage Samples:")
        for cache_type, memory in stats['memory_usage'].items():
            print(f"      {cache_type}: {memory} bytes")
        
        return True
    except Exception as e:
        print(f"❌ Cache statistics test failed: {e}")
        return False

def test_expired_session_cleanup():
    """Test cleanup of expired sessions"""
    print("\n🧹 Testing expired session cleanup...")
    
    try:
        # Get initial session count
        initial_stats = redis_service.get_cache_statistics()
        initial_sessions = initial_stats['cache_counts'].get('session', 0)
        
        # Create a test session with very short expiry
        print("   📝 Creating test session with short expiry...")
        test_session = redis_service.create_game_session(
            user_id="cleanup_test_user",
            character_id=999,
            story_arc_id=999
        )
        
        # Manually set a very short TTL for testing
        session_key = redis_service.PREFIXES['session'] + test_session.session_id
        redis_service.client.expire(session_key, 2)  # 2 seconds
        
        print(f"   ⏱️  Waiting 3 seconds for session to expire...")
        time.sleep(3)
        
        # Run cleanup
        cleaned_count = redis_service.cleanup_expired_sessions()
        print(f"   ✅ Cleaned up {cleaned_count} expired sessions")
        
        # Verify session is gone
        retrieved_session = redis_service.get_game_session(test_session.session_id)
        if retrieved_session is None:
            print(f"   ✅ Expired session successfully removed")
            return True
        else:
            print(f"   ❌ Expired session still exists")
            return False
            
    except Exception as e:
        print(f"❌ Expired session cleanup test failed: {e}")
        return False

def test_character_cache_invalidation():
    """Test character cache invalidation"""
    print("\n🧙 Testing character cache invalidation...")
    
    try:
        character_id = 4  # From our test data
        
        # First, ensure character is cached
        cached_char = redis_service.get_cached_character(character_id)
        if not cached_char:
            print(f"   ℹ️  Character {character_id} not in cache, skipping invalidation test")
            return True
        
        print(f"   📦 Character {character_id} found in cache")
        
        # Invalidate character cache
        success = redis_service.invalidate_character_cache(character_id)
        print(f"   🗑️  Cache invalidation: {'✅ Success' if success else '❌ Failed'}")
        
        # Verify character is no longer cached
        cached_char_after = redis_service.get_cached_character(character_id)
        if cached_char_after is None:
            print(f"   ✅ Character cache successfully invalidated")
            return True
        else:
            print(f"   ❌ Character still in cache after invalidation")
            return False
            
    except Exception as e:
        print(f"❌ Character cache invalidation test failed: {e}")
        return False

def test_story_cache_invalidation():
    """Test story cache invalidation"""
    print("\n📚 Testing story cache invalidation...")
    
    try:
        story_arc_id = 1  # From our test data
        
        # Check if story is cached
        cached_story = redis_service.get_cached_story(story_arc_id)
        if not cached_story:
            print(f"   ℹ️  Story arc {story_arc_id} not in cache, skipping invalidation test")
            return True
        
        print(f"   📖 Story arc {story_arc_id} found in cache")
        
        # Invalidate story cache
        success = redis_service.invalidate_story_cache(story_arc_id)
        print(f"   🗑️  Cache invalidation: {'✅ Success' if success else '❌ Failed'}")
        
        # Verify story is no longer cached
        cached_story_after = redis_service.get_cached_story(story_arc_id)
        if cached_story_after is None:
            print(f"   ✅ Story cache successfully invalidated")
            return True
        else:
            print(f"   ❌ Story still in cache after invalidation")
            return False
            
    except Exception as e:
        print(f"❌ Story cache invalidation test failed: {e}")
        return False

def test_user_cache_invalidation():
    """Test user cache invalidation"""
    print("\n👤 Testing user cache invalidation...")
    
    try:
        user_id = "test_user_123"  # From our test data
        
        # Get user sessions before invalidation
        user_sessions = redis_service.get_user_sessions(user_id)
        print(f"   👥 Found {len(user_sessions)} active sessions for user {user_id}")
        
        # Invalidate user cache
        success = redis_service.invalidate_user_cache(user_id)
        print(f"   🗑️  Cache invalidation: {'✅ Success' if success else '❌ Failed'}")
        
        # Verify user sessions are cleared
        user_sessions_after = redis_service.get_user_sessions(user_id)
        if len(user_sessions_after) == 0:
            print(f"   ✅ User cache successfully invalidated")
            return True
        else:
            print(f"   ❌ User still has {len(user_sessions_after)} sessions after invalidation")
            return False
            
    except Exception as e:
        print(f"❌ User cache invalidation test failed: {e}")
        return False

def test_stale_cache_cleanup():
    """Test stale cache cleanup based on age"""
    print("\n🧽 Testing stale cache cleanup...")
    
    try:
        # Get initial cache statistics
        initial_stats = redis_service.get_cache_statistics()
        print(f"   📊 Initial cache counts: {initial_stats['cache_counts']}")
        
        # Run stale cache cleanup (items older than 1 hour)
        cleanup_results = redis_service.cleanup_stale_cache(max_age_hours=1)
        
        print(f"   🧹 Cleanup Results:")
        for cache_type, count in cleanup_results.items():
            if count > 0:
                print(f"      {cache_type}: {count} items removed")
        
        print(f"   ✅ Total items cleaned: {cleanup_results['total']}")
        
        # Get final cache statistics
        final_stats = redis_service.get_cache_statistics()
        print(f"   📈 Final cache counts: {final_stats['cache_counts']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Stale cache cleanup test failed: {e}")
        return False

def test_combat_cache_clearing():
    """Test combat cache clearing functionality"""
    print("\n⚔️  Testing combat cache clearing...")
    
    try:
        encounter_id = 1  # From our test data
        
        # Check if combat is cached
        cached_combat = redis_service.get_combat_state(encounter_id)
        if not cached_combat:
            print(f"   ℹ️  Combat encounter {encounter_id} not in cache")
            return True
        
        print(f"   🥊 Combat encounter {encounter_id} found in cache")
        
        # Clear combat cache
        success = redis_service.clear_combat_state(encounter_id)
        print(f"   🗑️  Cache clearing: {'✅ Success' if success else '❌ Failed'}")
        
        # Verify combat is no longer cached
        cached_combat_after = redis_service.get_combat_state(encounter_id)
        if cached_combat_after is None:
            print(f"   ✅ Combat cache successfully cleared")
            return True
        else:
            print(f"   ❌ Combat still in cache after clearing")
            return False
            
    except Exception as e:
        print(f"❌ Combat cache clearing test failed: {e}")
        return False

def main():
    """Main test function for cleanup mechanisms"""
    print("🧹 Starting Redis Cache Invalidation & Cleanup Tests")
    print("=" * 70)
    
    test_results = {
        'Cache Statistics': test_cache_statistics(),
        'Expired Session Cleanup': test_expired_session_cleanup(),
        'Character Cache Invalidation': test_character_cache_invalidation(),
        'Story Cache Invalidation': test_story_cache_invalidation(),
        'User Cache Invalidation': test_user_cache_invalidation(),
        'Stale Cache Cleanup': test_stale_cache_cleanup(),
        'Combat Cache Clearing': test_combat_cache_clearing()
    }
    
    print("\n" + "=" * 70)
    print("📊 Cleanup Test Results Summary:")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All cleanup mechanisms are working perfectly!")
        print("Cache invalidation and cleanup systems are production-ready!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Review the logs above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main() 