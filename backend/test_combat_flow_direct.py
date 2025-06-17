#!/usr/bin/env python3
"""
Direct test for combat detection without API authentication
"""
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService
from services.response_parser import response_parser

def test_complete_combat_flow_direct():
    """Test the complete combat detection flow directly through services"""
    
    print("🧪 Testing Direct Combat Detection Flow")
    print("=" * 60)
    
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.client:
        print("❌ AI service not available - missing API key")
        return
    
    # Test aggressive actions that should trigger combat
    test_scenarios = [
        {
            "player_action": "I draw my sword and attack the nearest bandit!",
            "action_type": "action"
        },
        {
            "player_action": "I shout 'Fight me or I kill everyone here!' and brandish my weapon menacingly",
            "action_type": "action"
        },
        {
            "player_action": "I cast fireball at the group of enemies",
            "action_type": "action"
        },
        {
            "player_action": "Prepare to die, you scoundrels! I challenge you all to combat!",
            "action_type": "speech"
        },
        {
            "player_action": "I charge forward with my weapon raised, ready to strike",
            "action_type": "action"
        }
    ]
    
    print(f"🎯 Testing {len(test_scenarios)} aggressive scenarios")
    print("-" * 60)
    
    success_count = 0
    total_tests = len(test_scenarios)
    
    for i, scenario in enumerate(test_scenarios, 1):
        player_action = scenario["player_action"]
        action_type = scenario["action_type"]
        
        print(f"\n🎭 Test {i}/{total_tests}: {action_type}")
        print(f"📝 Action: {player_action}")
        print("-" * 40)
        
        try:
            # Create a context-aware prompt for story narration
            test_context = f"""
CHARACTER: Spooky Boi (Level 3 Rogue)
LOCATION: Bandit Camp
SITUATION: You are surrounded by hostile bandits who have been threatening travelers.

PLAYER ACTION ({action_type}): {player_action}

Additional context: Player action type: {action_type}
"""
            
            # Generate AI response using the story template approach
            result = ai_service.generate_response(
                prompt=test_context,
                max_tokens=300,
                temperature=0.7
            )
            
            if result.get('success') and result.get('content'):
                ai_content = result['content']
                
                print(f"🤖 AI Response Length: {len(ai_content)} characters")
                print(f"📄 AI Content (first 200 chars): {ai_content[:200]}...")
                
                # Parse the AI response for combat detection
                parsed_response = response_parser.parse_response(ai_content)
                
                # Check for combat initiation
                combat_events = parsed_response.combat_events
                combat_detected = any(event.event_type == "combat_initiated" for event in combat_events)
                
                print(f"⚔️ Combat Events Found: {[event.event_type for event in combat_events]}")
                print(f"🎯 Combat Detected: {combat_detected}")
                print(f"📊 Parsing Confidence: {parsed_response.confidence_score:.2f}")
                
                # Manual keyword check as fallback
                combat_keywords = ['combat', 'fight', 'attack', 'battle', 'initiative', 'hostile', 'aggressive', 'roll for initiative', 'combat begins']
                found_keywords = [kw for kw in combat_keywords if kw.lower() in ai_content.lower()]
                print(f"🔍 Combat Keywords Found: {found_keywords}")
                
                # Check for dice rolls
                if parsed_response.dice_rolls:
                    dice_info = [f"{roll.dice_expression} for {roll.purpose}" for roll in parsed_response.dice_rolls]
                    print(f"🎲 Dice Rolls Required: {dice_info}")
                
                # Check for state changes
                if parsed_response.state_changes:
                    state_info = [f"{change.property_name}: {change.change_amount}" for change in parsed_response.state_changes]
                    print(f"📊 State Changes: {state_info}")
                
                if combat_detected:
                    print("✅ SUCCESS: Combat properly detected!")
                    success_count += 1
                else:
                    print("❌ FAILED: Combat not detected")
                    # Show what we got instead
                    if found_keywords:
                        print(f"   ℹ️ Note: Keywords found but parser didn't detect combat structure")
                    else:
                        print(f"   ℹ️ Note: No combat-related content generated")
                
            else:
                print(f"❌ AI generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Test failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"🏁 Direct Combat Detection Testing Complete!")
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

def test_peaceful_actions_direct():
    """Test that peaceful actions don't falsely trigger combat"""
    
    print("\n🕊️ Testing Peaceful Actions (Should NOT trigger combat)")
    print("=" * 60)
    
    ai_service = AIService()
    
    if not ai_service.client:
        print("❌ AI service not available")
        return 0
    
    peaceful_scenarios = [
        "Hello there, how are you doing today?",
        "I look around the room carefully",
        "I search for clues in the area",
        "I ask the merchant about his wares",
        "I sit down and rest for a moment"
    ]
    
    false_positive_count = 0
    
    for i, action in enumerate(peaceful_scenarios, 1):
        print(f"\n🕊️ Peaceful Test {i}: {action}")
        
        try:
            test_context = f"""
CHARACTER: Spooky Boi (Level 3 Rogue)  
LOCATION: Peaceful Village
SITUATION: You are in a friendly village market.

PLAYER ACTION: {action}
"""
            
            result = ai_service.generate_response(
                prompt=test_context,
                max_tokens=200,
                temperature=0.7
            )
            
            if result.get('success') and result.get('content'):
                ai_content = result['content']
                parsed_response = response_parser.parse_response(ai_content)
                combat_detected = any(event.event_type == "combat_initiated" for event in parsed_response.combat_events)
                
                if combat_detected:
                    print(f"⚠️ FALSE POSITIVE: Combat detected for peaceful action!")
                    print(f"📄 AI Response: {ai_content[:100]}...")
                    false_positive_count += 1
                else:
                    print(f"✅ Correct: No combat detected for peaceful action")
            
        except Exception as e:
            print(f"❌ Error testing peaceful action: {e}")
    
    print(f"\n📊 False Positives: {false_positive_count}/{len(peaceful_scenarios)}")
    return false_positive_count

if __name__ == "__main__":
    print("🌟 Starting Direct Combat Detection Testing")
    print("Testing AI service and response parser directly")
    print()
    
    # Test combat actions
    combat_successes, combat_total = test_complete_combat_flow_direct()
    
    # Test peaceful actions
    false_positives = test_peaceful_actions_direct()
    
    print("\n🎯 FINAL SUMMARY")
    print("=" * 60)
    print(f"⚔️ Combat Detection Rate: {combat_successes}/{combat_total} ({(combat_successes/combat_total)*100:.1f}%)")
    print(f"🕊️ False Positive Rate: {false_positives}/5 ({(false_positives/5)*100:.1f}%)")
    
    overall_score = (combat_successes/combat_total) * 0.8 + (1 - false_positives/5) * 0.2
    print(f"🏆 Overall System Score: {overall_score*100:.1f}%")
    
    if overall_score >= 0.9:
        print("🌟 OUTSTANDING! Combat detection system is working excellently!")
    elif overall_score >= 0.8:
        print("🎉 EXCELLENT! Combat detection system is working very well!")
    elif overall_score >= 0.7:
        print("👍 GOOD! Combat detection system is working well!")
    else:
        print("⚠️ Needs improvement in combat detection accuracy!")
    
    print("\n💡 WHAT WAS FIXED:")
    print("✅ Enhanced AI prompts to explicitly trigger combat for aggressive actions")
    print("✅ Improved response parser with better combat keyword detection") 
    print("✅ Updated games.py API to use response parser for combat detection")
    print("✅ Added combat detection indicators to frontend interface")
    print("✅ Comprehensive debugging and logging throughout the system") 