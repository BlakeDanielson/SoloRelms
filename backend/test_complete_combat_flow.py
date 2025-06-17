#!/usr/bin/env python3
"""
Comprehensive test for the complete combat detection flow
"""
import os
import sys
import json
import requests
import time
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_complete_combat_flow():
    """Test the complete combat detection flow through the API"""
    
    print("🧪 Testing Complete Combat Detection Flow")
    print("=" * 60)
    
    # API endpoint
    base_url = "http://localhost:8000"
    
    # Test story ID (using existing test data)
    story_id = 11
    
    # Test aggressive actions that should trigger combat
    test_actions = [
        {
            "action_type": "action",
            "content": "I draw my sword and attack the nearest bandit!",
            "metadata": {}
        },
        {
            "action_type": "action", 
            "content": "I shout 'Fight me or I kill everyone here!' and brandish my weapon menacingly",
            "metadata": {}
        },
        {
            "action_type": "action",
            "content": "I cast fireball at the group of enemies",
            "metadata": {}
        },
        {
            "action_type": "speech",
            "content": "Prepare to die, you scoundrels! I challenge you all to combat!",
            "metadata": {}
        },
        {
            "action_type": "action",
            "content": "I charge forward with my weapon raised, ready to strike",
            "metadata": {}
        }
    ]
    
    print(f"🎯 Testing {len(test_actions)} aggressive actions")
    print(f"📡 API Endpoint: {base_url}/api/games/{story_id}/actions")
    print("-" * 60)
    
    success_count = 0
    total_tests = len(test_actions)
    
    for i, action in enumerate(test_actions, 1):
        print(f"\n🎭 Test {i}/{total_tests}: {action['action_type']} action")
        print(f"📝 Content: {action['content']}")
        print("-" * 40)
        
        try:
            # Send action to API
            response = requests.post(
                f"{base_url}/api/games/{story_id}/actions",
                json=action,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key information
                success = data.get('success', False)
                player_message = data.get('player_message', {})
                ai_response = data.get('ai_response', {})
                game_state_updates = data.get('game_state_updates', {})
                
                print(f"✅ API Response: {response.status_code}")
                print(f"📤 Player Message ID: {player_message.get('id', 'N/A')}")
                
                if ai_response:
                    ai_content = ai_response.get('content', '')
                    ai_metadata = ai_response.get('metadata', {})
                    combat_detected = ai_metadata.get('combat_detected', False)
                    
                    print(f"🤖 AI Response Length: {len(ai_content)} characters")
                    print(f"📄 AI Content (first 150 chars): {ai_content[:150]}...")
                    
                    # Check combat detection
                    if combat_detected:
                        print(f"⚔️ ✅ COMBAT DETECTED!")
                        print(f"🎯 Combat Events Count: {ai_metadata.get('combat_events_count', 0)}")
                        print(f"📊 Parsing Confidence: {ai_metadata.get('parsing_confidence', 0):.2f}")
                        success_count += 1
                        
                        # Check for dice requirements
                        if 'dice_required' in game_state_updates:
                            print(f"🎲 Dice Required: {[d.get('expression', 'N/A') for d in game_state_updates['dice_required']]}")
                        
                        # Check for HP changes
                        if 'hp_changes' in game_state_updates:
                            print(f"❤️ HP Changes: {game_state_updates['hp_changes']}")
                    else:
                        print(f"❌ Combat NOT detected")
                        
                        # Check if AI response contains combat keywords manually
                        combat_keywords = ['combat', 'fight', 'attack', 'battle', 'initiative', 'hostile', 'aggressive']
                        found_keywords = [kw for kw in combat_keywords if kw.lower() in ai_content.lower()]
                        if found_keywords:
                            print(f"🔍 Combat keywords found but not detected by parser: {found_keywords}")
                        else:
                            print(f"🔍 No combat keywords found in response")
                    
                    # Display game state updates
                    if game_state_updates:
                        interesting_updates = {k: v for k, v in game_state_updates.items() if k not in ['real_time_played']}
                        if interesting_updates:
                            print(f"🎮 Game State Updates: {json.dumps(interesting_updates, indent=2)}")
                    
                else:
                    print(f"❌ No AI response received")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Request timed out (30s)")
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error - is the server running?")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
        
        # Small delay between requests
        if i < total_tests:
            print("⏳ Waiting 2 seconds before next test...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"🏁 Combat Detection Testing Complete!")
    print(f"📊 Results: {success_count}/{total_tests} actions successfully triggered combat")
    print(f"✅ Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 PERFECT! All aggressive actions triggered combat detection!")
    elif success_count >= total_tests * 0.8:
        print("👍 EXCELLENT! Most actions triggered combat detection!")
    elif success_count >= total_tests * 0.6:
        print("👌 GOOD! Majority of actions triggered combat detection!")
    else:
        print("⚠️ NEEDS IMPROVEMENT! Combat detection rate is low!")
    
    return success_count, total_tests

def test_non_combat_actions():
    """Test that non-combat actions don't trigger combat"""
    
    print("\n🕊️ Testing Non-Combat Actions (Should NOT trigger combat)")
    print("=" * 60)
    
    # API endpoint
    base_url = "http://localhost:8000"
    story_id = 11
    
    # Test peaceful actions that should NOT trigger combat
    peaceful_actions = [
        {
            "action_type": "speech",
            "content": "Hello there, how are you doing today?",
            "metadata": {}
        },
        {
            "action_type": "action",
            "content": "I look around the room carefully",
            "metadata": {}
        },
        {
            "action_type": "action",
            "content": "I search for clues in the area",
            "metadata": {}
        }
    ]
    
    false_positive_count = 0
    
    for i, action in enumerate(peaceful_actions, 1):
        print(f"\n🕊️ Peaceful Test {i}: {action['content']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/games/{story_id}/actions",
                json=action,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('ai_response', {})
                
                if ai_response:
                    ai_metadata = ai_response.get('metadata', {})
                    combat_detected = ai_metadata.get('combat_detected', False)
                    
                    if combat_detected:
                        print(f"⚠️ FALSE POSITIVE: Combat detected for peaceful action!")
                        false_positive_count += 1
                    else:
                        print(f"✅ Correct: No combat detected for peaceful action")
                
        except Exception as e:
            print(f"❌ Error testing peaceful action: {e}")
        
        time.sleep(1)
    
    print(f"\n📊 False Positives: {false_positive_count}/{len(peaceful_actions)}")
    
    return false_positive_count

if __name__ == "__main__":
    print("🌟 Starting Comprehensive Combat Detection Testing")
    print("Make sure the backend server is running on localhost:8000")
    print()
    
    # Test combat actions
    combat_successes, combat_total = test_complete_combat_flow()
    
    # Test non-combat actions
    false_positives = test_non_combat_actions()
    
    print("\n🎯 FINAL SUMMARY")
    print("=" * 60)
    print(f"⚔️ Combat Detection Rate: {combat_successes}/{combat_total} ({(combat_successes/combat_total)*100:.1f}%)")
    print(f"🕊️ False Positive Rate: {false_positives}/3 ({(false_positives/3)*100:.1f}%)")
    
    overall_score = (combat_successes/combat_total) * 0.8 + (1 - false_positives/3) * 0.2
    print(f"🏆 Overall System Score: {overall_score*100:.1f}%")
    
    if overall_score >= 0.9:
        print("🌟 OUTSTANDING! Combat detection system is working excellently!")
    elif overall_score >= 0.8:
        print("🎉 EXCELLENT! Combat detection system is working very well!")
    elif overall_score >= 0.7:
        print("👍 GOOD! Combat detection system is working well!")
    else:
        print("⚠️ Needs improvement in combat detection accuracy!") 