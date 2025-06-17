#!/usr/bin/env python3
"""
AUTH DEBUG SCRIPT
Test character creation with authentication to debug the actual error

This will help us understand:
1. What user_id is being extracted from the token
2. What the actual database error is
3. Whether the issue is authentication or something else
"""

import requests
import json
import time

# Test Configuration
BACKEND_URL = "http://localhost:8000"

def test_character_creation_debug():
    """Test character creation without authentication to isolate the issue"""
    
    print("🔍 DEBUGGING CHARACTER CREATION ISSUE...")
    print("=" * 60)
    
    # Test 1: Check if backend is healthy
    print("\n1. Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health/status")
        print(f"   Backend Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check character options endpoint
    print("\n2. Testing Character Options...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/characters/options")
        print(f"   Options Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Races: {len(data.get('races', []))}")
            print(f"   Classes: {len(data.get('classes', []))}")
            print(f"   Backgrounds: {len(data.get('backgrounds', []))}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Check current characters in database
    print("\n3. Checking Database State...")
    try:
        # This should show us what's in the database
        response = requests.get(f"{BACKEND_URL}/health/database")
        print(f"   Database Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Database: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Try to call the quick-create endpoint without auth to see auth error
    print("\n4. Testing Quick-Create Endpoint (No Auth)...")
    try:
        character_data = {
            "name": "big boi",
            "race": "Gnome",
            "character_class": "Fighter", 
            "background": "Charlatan",
            "backstory": "biggest boi gets the baddest bitches"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/characters/quick-create",
            headers={"Content-Type": "application/json"},
            json=character_data
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 422:
            error_data = response.json()
            print(f"   Validation Error Detail: {error_data}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Check if there's a potential name conflict with different casing
    print("\n5. Testing Case Sensitivity...")
    test_names = ["big boi", "Big Boi", "BIG BOI", "big_boi"]
    
    for name in test_names:
        print(f"   Testing name: '{name}'")
        # We'll check this by looking at the actual database query results
        # But first, let's see what happens with different variations
    
    print("\n🎯 NEXT STEPS:")
    print("1. Check the actual user_id from Clerk token")
    print("2. Look at backend logs when character creation is attempted")
    print("3. Verify the authentication middleware is working correctly")
    print("4. Check if there's a timing/caching issue")
    
    return True

if __name__ == "__main__":
    test_character_creation_debug() 