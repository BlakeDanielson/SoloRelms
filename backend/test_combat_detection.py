#!/usr/bin/env python3
"""
Quick test script to verify combat detection is working
"""
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService
from services.response_parser import response_parser

def test_combat_detection():
    """Test combat detection with aggressive actions"""
    
    print("🧪 Testing Combat Detection System")
    print("=" * 50)
    
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.client:
        print("❌ AI service not available - missing API key")
        return
    
    # Test aggressive actions that should trigger combat
    test_actions = [
        "I draw my sword and attack the bandit!",
        "I shout 'Fight me or I kill everyone here!'",
        "I cast a fireball at the enemy",
        "I charge forward with my weapon raised",
        "I threaten the guards with violence"
    ]
    
    for i, action in enumerate(test_actions, 1):
        print(f"\n🎯 Test {i}: {action}")
        print("-" * 40)
        
        # Create a simple test prompt that should trigger combat
        test_prompt = f"""You are an expert Dungeon Master for a solo D&D 5e game.

PLAYER ACTION: {action}

This is clearly an aggressive action that should trigger combat. You MUST initiate combat immediately.

Respond with a combat scenario that includes phrases like "combat begins", "initiative", or "the fight starts".

IMPORTANT: Your response MUST trigger combat detection."""
        
        try:
            # Generate AI response
            result = ai_service.generate_response(test_prompt, max_tokens=300, temperature=0.7)
            
            if result.get('success') and result.get('content'):
                ai_content = result['content']
                print(f"📄 AI Response: {ai_content[:150]}...")
                
                # Parse response for combat detection
                parsed = response_parser.parse_response(ai_content)
                combat_events = parsed.combat_events
                combat_detected = any(event.event_type == "combat_initiated" for event in combat_events)
                
                print(f"⚔️ Combat Events: {[event.event_type for event in combat_events]}")
                print(f"🎯 Combat Detected: {combat_detected}")
                print(f"📊 Confidence: {parsed.confidence_score:.2f}")
                
                # Manual keyword check
                combat_keywords = ['combat', 'fight', 'attack', 'battle', 'initiative', 'hostile', 'aggressive']
                found_keywords = [kw for kw in combat_keywords if kw.lower() in ai_content.lower()]
                print(f"🔍 Combat Keywords Found: {found_keywords}")
                
                if combat_detected:
                    print("✅ SUCCESS: Combat properly detected!")
                else:
                    print("❌ FAILED: Combat not detected")
                
            else:
                print(f"❌ AI generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Combat detection testing complete!")

if __name__ == "__main__":
    test_combat_detection() 