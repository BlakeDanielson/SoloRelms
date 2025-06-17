#!/usr/bin/env python3
"""
Check database contents
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import SessionLocal
from models.character import Character
from models.user import User

def main():
    """Check database contents"""
    db = SessionLocal()
    try:
        # Check existing characters
        characters = db.query(Character).all()
        print(f"Found {len(characters)} characters:")
        for char in characters:
            print(f"  ID: {char.id}, Name: {char.name}, Level: {char.level}")
        
        # Check existing users
        users = db.query(User).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  ID: {user.id}, Email: {user.email}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main() 