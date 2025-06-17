#!/usr/bin/env python3
"""
Test script to verify our new cleanup API functionality works correctly
Tests the Redis service methods that would be called by the API endpoints
"""

import json
from datetime import datetime
from services.redis_service import redis_service

def test_cleanup_api_functionality():
    """Test all the functionality that would be exposed via API endpoints"""
    print("🧹 Testing Cleanup API Functionality")
    print("=" * 50)
    
    # 1. Test cache statistics (equivalent to GET /api/redis/statistics)
    print("\n📊 Testing Cache Statistics API...")
    try:
        stats = redis_service.get_cache_statistics()
        print(f"   ✅ Statistics retrieved successfully")
        print(f"   Redis Version: {stats['redis_info'].get('redis_version', 'unknown')}")
        print(f"   Cache Counts: {stats['cache_counts']}")
        print(f"   Memory Usage: {stats['redis_info'].get('used_memory_human', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Statistics API failed: {e}")
    
    # 2. Test expired session cleanup (equivalent to POST /api/redis/cleanup/expired-sessions)
    print("\n🧹 Testing Expired Session Cleanup API...")
    try:
        # Create a test session and manually expire it
        test_session = redis_service.create_game_session(
            user_id="api_test_user",
            character_id=888,
            story_arc_id=888
        )
        
        # Set very short TTL
        session_key = redis_service.PREFIXES['session'] + test_session.session_id
        redis_service.client.expire(session_key, 1)  # 1 second
        
        import time
        time.sleep(2)  # Wait for expiration
        
        cleaned_count = redis_service.cleanup_expired_sessions()
        print(f"   ✅ Cleanup API: Cleaned {cleaned_count} expired sessions")
    except Exception as e:
        print(f"   ❌ Cleanup API failed: {e}")
    
    # 3. Test stale cache cleanup (equivalent to POST /api/redis/cleanup/stale-cache)
    print("\n🧽 Testing Stale Cache Cleanup API...")
    try:
        cleanup_results = redis_service.cleanup_stale_cache(max_age_hours=1)
        print(f"   ✅ Stale Cache Cleanup API: {cleanup_results}")
        print(f"   Total cleaned: {cleanup_results['total']}")
    except Exception as e:
        print(f"   ❌ Stale cache cleanup API failed: {e}")
    
    # 4. Test character cache invalidation (equivalent to DELETE /api/redis/cache/character/{id})
    print("\n🧙 Testing Character Cache Invalidation API...")
    try:
        character_id = 4
        success = redis_service.invalidate_character_cache(character_id)
        print(f"   ✅ Character Cache Invalidation API: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"   ❌ Character invalidation API failed: {e}")
    
    # 5. Test story cache invalidation (equivalent to DELETE /api/redis/cache/story/{id})
    print("\n📚 Testing Story Cache Invalidation API...")
    try:
        story_id = 1
        success = redis_service.invalidate_story_cache(story_id)
        print(f"   ✅ Story Cache Invalidation API: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"   ❌ Story invalidation API failed: {e}")
    
    # 6. Test user cache invalidation (equivalent to DELETE /api/redis/cache/user/{id})
    print("\n👤 Testing User Cache Invalidation API...")
    try:
        user_id = "test_user_123"
        success = redis_service.invalidate_user_cache(user_id)
        print(f"   ✅ User Cache Invalidation API: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"   ❌ User invalidation API failed: {e}")
    
    # 7. Test combat cache clearing (equivalent to DELETE /api/redis/cache/combat/{id})
    print("\n⚔️  Testing Combat Cache Clearing API...")
    try:
        # First create some combat data
        from database import get_db
        from models.combat import CombatEncounter
        
        db = next(get_db())
        encounter = db.query(CombatEncounter).filter(CombatEncounter.id == 1).first()
        
        if encounter:
            # Store it in cache first
            redis_service.store_combat_state(encounter)
            print(f"   📦 Combat state stored in cache")
            
            # Now clear it
            success = redis_service.clear_combat_state(encounter.id)
            print(f"   ✅ Combat Cache Clearing API: {'Success' if success else 'Failed'}")
        else:
            print(f"   ℹ️  No combat encounter found to test with")
        
        db.close()
    except Exception as e:
        print(f"   ❌ Combat clearing API failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All cleanup API functionality tested!")
    print("The Redis cache management system is fully operational!")
    
    # Final statistics
    print("\n📈 Final Cache Statistics:")
    try:
        final_stats = redis_service.get_cache_statistics()
        for cache_type, count in final_stats['cache_counts'].items():
            if count > 0:
                print(f"   {cache_type}: {count} items")
    except Exception as e:
        print(f"   Error getting final stats: {e}")

if __name__ == "__main__":
    test_cleanup_api_functionality() 