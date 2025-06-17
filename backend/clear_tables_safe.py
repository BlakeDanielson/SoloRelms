#!/usr/bin/env python3
"""
Script to clear all Supabase tables except users table.
This version works with Supabase's permission restrictions.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import get_db, engine
from models import *  # Import all models

def clear_tables():
    """Clear all tables except users table"""
    
    # List of tables to clear (in reverse dependency order)
    # We clear dependent tables first, then parent tables
    tables_to_clear = [
        # Clear tables with foreign keys first (leaf tables)
        "quest_objective_progress",
        "character_quests", 
        "quest_rewards",
        "quest_objectives",
        "combat_participants",
        "timeline_events",
        "discoveries", 
        "journal_entries",
        
        # Then clear parent tables
        "combat_encounters",
        "world_states",
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
        print("📋 Tables to clear:", len(tables_to_clear), "tables")
        print("⚠️  Preserving: users table")
        print()
        
        total_deleted = 0
        
        # Clear each table without disabling foreign keys
        # Instead we rely on correct ordering
        for table in tables_to_clear:
            try:
                print(f"🗑️  Clearing table: {table}")
                
                # Use TRUNCATE if possible (faster), fallback to DELETE
                try:
                    # Try TRUNCATE CASCADE first
                    db.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                    print(f"   ✅ Truncated {table}")
                except Exception as truncate_error:
                    # Fallback to DELETE
                    result = db.execute(text(f"DELETE FROM {table}"))
                    rows_deleted = result.rowcount if hasattr(result, 'rowcount') else 0
                    print(f"   ✅ Deleted {rows_deleted} rows from {table}")
                    total_deleted += rows_deleted
                    
            except Exception as e:
                print(f"   ⚠️  Warning: Could not clear {table}: {e}")
                # Continue with other tables even if one fails
                continue
        
        # Commit all changes
        db.commit()
        
        print(f"\n✅ Database cleanup completed successfully!")
        print(f"🎉 Total rows deleted: {total_deleted}")
        print("👤 User accounts have been preserved.")
        
        # Verify users table still has data
        try:
            user_count_result = db.execute(text("SELECT COUNT(*) FROM users"))
            user_count = user_count_result.scalar()
            print(f"📊 Users remaining: {user_count}")
        except Exception as e:
            print(f"⚠️  Could not count users: {e}")
        
        # Check if main tables are empty
        print("\n📋 Verifying cleanup:")
        for table in ["characters", "story_arcs", "quests"]:
            try:
                count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                print(f"   {table}: {count} rows remaining")
            except Exception as e:
                print(f"   {table}: Could not verify ({e})")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        try:
            db.rollback()
        except:
            pass
        return False
    finally:
        try:
            db.close()
        except:
            pass
    
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
    print("🧹 SoloRelms Database Cleanup Tool (Supabase Safe)")
    print("=" * 55)
    
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
        print("\n✨ You now have a clean testing environment!")
        sys.exit(0)
    else:
        print("\n❌ Cleanup failed - check the errors above")
        print("💡 You can also try running the SQL script directly in Supabase")
        sys.exit(1) 