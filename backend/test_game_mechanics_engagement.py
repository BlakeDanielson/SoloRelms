#!/usr/bin/env python3
"""
Test enhanced AI prompts for game mechanics engagement
"""
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService

def test_game_mechanics_engagement():
    """Test that AI actively suggests using game mechanics"""
    
    print("🎮 Testing Game Mechanics Engagement")
    print("=" * 60)
    
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.client:
        print("❌ AI service not available - missing API key")
        return
    
    # Test scenarios that should trigger different game mechanics
    test_scenarios = [
        {
            "character_state": "High Strength (18), Low Intelligence (8), full HP, basic equipment",
            "situation": "Standing before a locked heavy door in a dungeon",
            "expected_suggestions": ["Strength check", "force the door", "use Athletics skill"]
        },
        {
            "character_state": "High Charisma (16), Bard class, injured (5/20 HP)",
            "situation": "Encountering a group of hostile bandits",
            "expected_suggestions": ["Persuasion", "rest/healing", "bardic abilities", "social resolution"]
        },
        {
            "character_state": "Rogue class, High Dexterity (17), has thieves' tools",
            "situation": "Finding a treasure chest with a complex lock",
            "expected_suggestions": ["lockpicking", "thieves' tools", "Dexterity check", "Sleight of Hand"]
        },
        {
            "character_state": "Wizard class, level 3, has spell components, basic robes",
            "situation": "Exploring an ancient magical library",
            "expected_suggestions": ["Investigation", "Arcana checks", "spell usage", "equipment upgrades"]
        },
        {
            "character_state": "Fighter class, level 2, basic sword and shield, full HP",
            "situation": "Traveling through a monster-infested forest",
            "expected_suggestions": ["combat encounter", "tactical positioning", "equipment usage"]
        }
    ]
    
    print(f"🎯 Testing {len(test_scenarios)} scenarios for game mechanics suggestions")
    print("-" * 60)
    
    success_count = 0
    total_suggestions_found = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        character_state = scenario["character_state"]
        situation = scenario["situation"] 
        expected = scenario["expected_suggestions"]
        
        print(f"\n🎭 Test {i}/{len(test_scenarios)}")
        print(f"📊 Character: {character_state}")
        print(f"🏛️ Situation: {situation}")
        print(f"🎯 Expected: {', '.join(expected)}")
        print("-" * 40)
        
        try:
            # Create a test prompt that includes the character state and situation
            test_prompt = f"""
You are an expert Dungeon Master for a solo D&D 5e game.

CHARACTER STATE: {character_state}
CURRENT SITUATION: {situation}

ACTIVE GAME MECHANICS ENGAGEMENT:
- **Inventory & Equipment**: Regularly suggest opportunities to use items, find new equipment, or upgrade gear
- **Ability Checks**: Create scenarios requiring Strength, Dexterity, Intelligence, Wisdom, Charisma, or Constitution checks
- **Skill Usage**: Present opportunities for stealth, persuasion, investigation, perception, athletics, etc.
- **Combat Encounters**: When appropriate, create tactical combat scenarios that test different abilities
- **Experience & Leveling**: Acknowledge significant achievements and suggest when the character might gain XP
- **Resource Management**: Consider spell slots, hit points, and consumable items in scenario design
- **Character Growth**: Create challenges that allow the character to showcase their class features and abilities

Based on the character's state and current situation, provide a narrative response that:
1. Describes what the character sees and experiences
2. Actively suggests specific ability checks, skill usage, or equipment applications
3. Creates opportunities that match the character's strengths or address their weaknesses
4. Presents clear mechanical choices (stat checks, item usage, etc.)

**INCORPORATE GAME MECHANICS:**
- Suggest ability checks when appropriate
- Reference equipment and how it affects the situation  
- Consider class abilities and how they could be useful
- Mention opportunities for skill usage
- If injured, consider rest or healing opportunities
- Create scenarios that play to strengths or challenge weaknesses
- Suggest when items might be useful

Provide your response as a DM narrating this scenario.
"""
            
            # Generate AI response
            ai_result = ai_service.generate_response(
                prompt=test_prompt,
                max_tokens=400,
                temperature=0.7
            )
            
            if ai_result.get('success') and ai_result.get('content'):
                ai_content = ai_result['content'].lower()
                
                print(f"🤖 AI Response:")
                print(f"📄 {ai_result['content'][:300]}...")
                
                # Check if expected suggestions are present
                suggestions_found = []
                for suggestion in expected:
                    if any(keyword in ai_content for keyword in suggestion.lower().split()):
                        suggestions_found.append(suggestion)
                        total_suggestions_found += 1
                
                print(f"✅ Suggestions Found: {', '.join(suggestions_found) if suggestions_found else 'None'}")
                print(f"❌ Missing: {', '.join([s for s in expected if s not in suggestions_found])}")
                
                # Check for general game mechanics engagement
                mechanics_keywords = [
                    'check', 'roll', 'ability', 'skill', 'strength', 'dexterity', 
                    'charisma', 'wisdom', 'intelligence', 'constitution',
                    'equipment', 'inventory', 'spell', 'class', 'level',
                    'hp', 'health', 'rest', 'heal'
                ]
                
                mechanics_found = [keyword for keyword in mechanics_keywords if keyword in ai_content]
                print(f"🎲 Game Mechanics Keywords: {', '.join(mechanics_found[:5])}{'...' if len(mechanics_found) > 5 else ''}")
                
                if len(suggestions_found) >= len(expected) * 0.5:  # At least half the expected suggestions
                    success_count += 1
                    print("🎉 SUCCESS: Good mechanics engagement!")
                else:
                    print("⚠️ PARTIAL: Could use more mechanics engagement")
                
            else:
                print(f"❌ AI generation failed: {ai_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Game Mechanics Engagement Testing Complete!")
    print(f"📊 Scenarios with Good Engagement: {success_count}/{len(test_scenarios)}")
    print(f"✅ Success Rate: {(success_count/len(test_scenarios))*100:.1f}%")
    print(f"🎯 Total Mechanics Suggestions Found: {total_suggestions_found}")
    
    if success_count == len(test_scenarios):
        print("🎉 EXCELLENT! AI is actively engaging with all game mechanics!")
    elif success_count >= len(test_scenarios) * 0.8:
        print("👍 GREAT! AI is well-engaged with most game mechanics!")
    elif success_count >= len(test_scenarios) * 0.6:
        print("👌 GOOD! AI is moderately engaged with game mechanics!")
    else:
        print("⚠️ NEEDS IMPROVEMENT! AI needs more active mechanics engagement!")
    
    return success_count, len(test_scenarios)

if __name__ == "__main__":
    print("🌟 Starting Game Mechanics Engagement Testing")
    print("Testing if AI actively suggests using D&D features")
    print()
    
    success_count, total_tests = test_game_mechanics_engagement()
    
    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 60)
    
    if success_count >= total_tests * 0.8:
        print("✅ EXCELLENT: AI is actively encouraging use of game features!")
        print("Players should see regular suggestions for:")
        print("• Ability checks and skill usage")
        print("• Equipment and inventory utilization") 
        print("• Class feature applications")
        print("• Combat and tactical scenarios")
        print("• Rest and healing opportunities")
    else:
        print("⚠️ The AI needs more encouragement to use game mechanics.")
        print("Consider enhancing prompts further.") 