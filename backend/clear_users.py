#!/usr/bin/env python3
"""
Script to clear all users from Neon database for fresh start
This will delete all user records and any associated data
"""

import os
import sys
sys.path.append('/Users/carendanielson/BlakeProjects/SoloRelms/backend')

from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.character import Character
from models.story import StoryArc, WorldState
from models.combat import CombatEncounter, CombatParticipant

def clear_all_users():
    """Clear all users and associated data from database"""
    
    print("🧹 CLEARING ALL USERS FROM DATABASE...")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Check current counts
        user_count = db.query(User).count()
        character_count = db.query(Character).count()
        story_arc_count = db.query(StoryArc).count()
        world_state_count = db.query(WorldState).count()
        combat_encounter_count = db.query(CombatEncounter).count()
        combat_participant_count = db.query(CombatParticipant).count()
        
        print(f"📊 Current database state:")
        print(f"   Users: {user_count}")
        print(f"   Characters: {character_count}")
        print(f"   Story Arcs: {story_arc_count}")
        print(f"   World States: {world_state_count}")
        print(f"   Combat Encounters: {combat_encounter_count}")
        print(f"   Combat Participants: {combat_participant_count}")
        
        total_records = (user_count + character_count + story_arc_count + 
                        world_state_count + combat_encounter_count + combat_participant_count)
        
        if total_records == 0:
            print("✅ Database is already clean!")
            return True
        
        # 2. Delete in correct order (children first to avoid foreign key violations)
        
        # Delete combat participants first (references combat_encounters and characters)
        if combat_participant_count > 0:
            print(f"\n🗑️  Deleting {combat_participant_count} combat participants...")
            deleted = db.query(CombatParticipant).delete()
            print(f"   ✅ Deleted {deleted} combat participants")
        
        # Delete world states (references story_arcs)
        if world_state_count > 0:
            print(f"\n🗑️  Deleting {world_state_count} world states...")
            deleted = db.query(WorldState).delete()
            print(f"   ✅ Deleted {deleted} world states")
        
        # Delete combat encounters (references story_arcs and characters)
        if combat_encounter_count > 0:
            print(f"\n🗑️  Deleting {combat_encounter_count} combat encounters...")
            deleted = db.query(CombatEncounter).delete()
            print(f"   ✅ Deleted {deleted} combat encounters")
        
        # Delete story arcs (references characters and users)
        if story_arc_count > 0:
            print(f"\n🗑️  Deleting {story_arc_count} story arcs...")
            deleted = db.query(StoryArc).delete()
            print(f"   ✅ Deleted {deleted} story arcs")
        
        # Delete characters (references users)
        if character_count > 0:
            print(f"\n🗑️  Deleting {character_count} characters...")
            deleted = db.query(Character).delete()
            print(f"   ✅ Deleted {deleted} characters")
        
        # Delete users (no foreign key dependencies)
        if user_count > 0:
            print(f"\n🗑️  Deleting {user_count} users...")
            deleted = db.query(User).delete()
            print(f"   ✅ Deleted {deleted} users")
        
        # 4. Commit changes
        db.commit()
        print("\n💾 Changes committed to database")
        
        # 5. Verify cleanup
        final_user_count = db.query(User).count()
        final_character_count = db.query(Character).count()
        final_story_arc_count = db.query(StoryArc).count()
        final_world_state_count = db.query(WorldState).count()
        final_combat_encounter_count = db.query(CombatEncounter).count()
        final_combat_participant_count = db.query(CombatParticipant).count()
        
        print(f"\n📊 Final database state:")
        print(f"   Users: {final_user_count}")
        print(f"   Characters: {final_character_count}")
        print(f"   Story Arcs: {final_story_arc_count}")
        print(f"   World States: {final_world_state_count}")
        print(f"   Combat Encounters: {final_combat_encounter_count}")
        print(f"   Combat Participants: {final_combat_participant_count}")
        
        final_total = (final_user_count + final_character_count + final_story_arc_count + 
                      final_world_state_count + final_combat_encounter_count + final_combat_participant_count)
        
        if final_total == 0:
            print("\n🎉 Database successfully cleared!")
            return True
        else:
            print(f"\n❌ Some records may not have been deleted (remaining: {final_total})")
            return False
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete ALL users and associated data from the database!")
    print("This includes characters, story arcs, combat encounters, and world states.")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() == 'yes':
        success = clear_all_users()
        if success:
            print("\n📋 NEXT STEPS:")
            print("1. Clear users from Clerk dashboard")
            print("2. Test user registration from frontend")
            print("3. Verify user auto-creation works")
        else:
            print("\n❌ Database clearing failed!")
    else:
        print("Operation cancelled.") 