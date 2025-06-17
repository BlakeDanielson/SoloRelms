#!/usr/bin/env python3
"""
Script to clear all Supabase tables except users table.
This will give you a clean slate for testing while preserving user accounts.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import get_db, engine
from models import *  # Import all models

def clear_tables():
    """Clear all tables except users table"""
    
    # List of tables to clear (in order to respect foreign key constraints)
    # We clear dependent tables first, then parent tables
    tables_to_clear = [
        # Clear tables with foreign keys first
        "quest_objective_progress",
        "character_quests", 
        "quest_rewards",
        "quest_objectives",
        "combat_participants",
        "combat_encounters",
        "world_states",
        "timeline_events",
        "discoveries",
        "journal_entries",
        "quests",
        "enemy_templates",
        "story_arcs",
        "characters",
        # Note: NOT clearing "users" table
    ]
    
    try:
        # Get database session
        db = next(get_db())
        
        print("🧹 Starting database cleanup...")
        print("📋 Tables to clear:", tables_to_clear)
        print("⚠️  Preserving: users table")
        print()
        
        # Disable foreign key checks temporarily (for PostgreSQL/Supabase)
        print("🔓 Disabling foreign key constraints...")
        db.execute(text("SET session_replication_role = replica;"))
        
        # Clear each table
        for table in tables_to_clear:
            try:
                print(f"🗑️  Clearing table: {table}")
                result = db.execute(text(f"DELETE FROM {table}"))
                rows_deleted = result.rowcount if hasattr(result, 'rowcount') else 0
                print(f"   ✅ Deleted {rows_deleted} rows from {table}")
            except Exception as e:
                print(f"   ⚠️  Warning: Could not clear {table}: {e}")
                # Continue with other tables even if one fails
                continue
        
        # Re-enable foreign key checks
        print("\n🔒 Re-enabling foreign key constraints...")
        db.execute(text("SET session_replication_role = DEFAULT;"))
        
        # Commit all changes
        db.commit()
        
        print("\n✅ Database cleanup completed successfully!")
        print("🎉 You now have a clean slate for testing!")
        print("👤 User accounts have been preserved.")
        
        # Verify users table still has data
        user_count_result = db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = user_count_result.scalar()
        print(f"📊 Users remaining: {user_count}")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

def confirm_action():
    """Ask user to confirm the destructive action"""
    print("⚠️  WARNING: This will permanently delete ALL data except user accounts!")
    print("   This includes:")
    print("   - All characters")
    print("   - All stories/adventures") 
    print("   - All quests")
    print("   - All journal entries")
    print("   - All combat encounters")
    print("   - All world states")
    print()
    
    response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
    return response.strip().upper() == 'YES'

if __name__ == "__main__":
    print("🧹 SoloRelms Database Cleanup Tool")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("models"):
        print("❌ Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Confirm with user
    if not confirm_action():
        print("❌ Operation cancelled by user")
        sys.exit(0)
    
    # Perform cleanup
    success = clear_tables()
    
    if success:
        print("\n🎯 Next steps:")
        print("   1. Create new characters via the frontend")
        print("   2. Start fresh adventures")
        print("   3. Test the full user journey")
        sys.exit(0)
    else:
        print("\n❌ Cleanup failed - check the errors above")
        sys.exit(1) 