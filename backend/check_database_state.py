#!/usr/bin/env python3
import sys
sys.path.append('/Users/carendanielson/BlakeProjects/SoloRelms/backend')

from database import get_db
from models.user import User
from models.character import Character

def check_database():
    db = next(get_db())
    
    users = db.query(User).all()
    characters = db.query(Character).all()
    
    print('🔍 CURRENT DATABASE STATE:')
    print(f'Users: {len(users)}')
    for user in users:
        print(f'  - {user.id}: {user.email}')
    
    print(f'Characters: {len(characters)}')
    for char in characters:
        print(f'  - {char.id}: {char.name} (user: {char.user_id})')
    
    db.close()

if __name__ == "__main__":
    check_database() 