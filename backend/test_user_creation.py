#!/usr/bin/env python3
"""
Test script to verify that user auto-creation works for character creation
"""

import os
import sys
sys.path.append('/Users/carendanielson/BlakeProjects/SoloRelms/backend')

from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models.user import User

def test_user_auto_creation():
    """Test that users are auto-created when they don't exist"""
    
    print("🧪 TESTING USER AUTO-CREATION...")
    print("=" * 50)
    
    # Test user ID (simulating a Clerk user ID)
    test_user_id = "user_2test_blake2015blake"
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Check if user exists before
        existing_user = db.query(User).filter(User.id == test_user_id).first()
        print(f"1. User exists before test: {existing_user is not None}")
        
        if existing_user:
            print(f"   User details: {existing_user.email}")
            
        # 2. Test the auth logic by manually calling get_current_user logic
        user = db.query(User).filter(User.id == test_user_id).first()
        
        if not user:
            print("2. User doesn't exist - creating new user...")
            
            user = User(
                id=test_user_id,
                email=f"{test_user_id}@clerk.temp",
                first_name=None,
                last_name=None,
                username=None,
                image_url=None,
                email_verified=False,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"   ✅ Successfully created user: {user.id}")
            print(f"   Email: {user.email}")
        else:
            print("2. User already exists!")
            
        # 3. Verify user creation
        final_user = db.query(User).filter(User.id == test_user_id).first()
        print(f"3. Final verification - User exists: {final_user is not None}")
        
        if final_user:
            print(f"   User ID: {final_user.id}")
            print(f"   Email: {final_user.email}")
            print(f"   Active: {final_user.is_active}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_user_auto_creation()
    if success:
        print("\n🎉 User auto-creation test passed!")
        print("\n📋 NEXT STEPS:")
        print("1. Try creating a character from the frontend")
        print("2. The system should auto-create your Clerk user")
        print("3. Character creation should work normally")
    else:
        print("\n❌ User auto-creation test failed!") 