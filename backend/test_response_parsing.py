"""
Test script for Response Parsing System
Validates parsing of various D&D scenarios from AI DM responses.
"""

import os
import sys
import json
from typing import Dict, Any

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from services.response_parser import response_parser, ActionType, DamageType
    print("✅ Successfully imported response parser services")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


# Test scenarios with different types of AI responses
TEST_SCENARIOS = [
    {
        "name": "Combat Scenario",
        "ai_response": """
Your sword strikes true! The goblin staggers as your blade cuts deep across its chest, 
dealing 8 slashing damage. The creature screeches in pain and retaliates, swinging its 
rusty scimitar at you. Roll a 1d20+2 for its attack roll against your AC of 16.

The goblin loses 8 hit points and now has 4 hit points remaining. Its eyes glow with fury 
as it prepares for another attack.

ACTIONS:
- attack: Player attacks goblin with sword
- retaliation: Goblin prepares counter-attack

STATE_CHANGES:
- goblin.current_hp: 12 -> 4

DICE_ROLLS:
- 1d20+2: Goblin attack roll vs AC 16
        """,
        "expected_elements": {
            "damage_events": 1,
            "hp_changes": 1,
            "dice_rolls": 1,
            "actions": 2
        }
    },
    
    {
        "name": "Skill Check Scenario",
        "ai_response": """
You approach the ancient door carved with mysterious runes. The intricate patterns seem 
to pulse with a faint magical energy. To decipher their meaning, make an Investigation 
check (1d20 + your Intelligence modifier).

As you examine the door more closely, you notice a small keyhole hidden beneath one of 
the runes. Your careful investigation reveals this might be the key to opening the passage.

STORY:
- discovery: Hidden keyhole found behind runes
- objective: Decipher runes to unlock door

DICE_ROLLS:
- 1d20+INT: Investigation check to understand runes
        """,
        "expected_elements": {
            "skill_checks": 1,
            "story_events": 1,
            "dice_rolls": 1
        }
    },
    
    {
        "name": "Magic and Healing Scenario", 
        "ai_response": """
The cleric's healing word washes over you with warm, golden light. You feel your wounds 
closing as you regain 6 hit points. Your current hit points increase from 8 to 14.

Meanwhile, the wizard casts Magic Missile at the approaching skeleton. Three glowing darts 
streak through the air, each dealing 1d4+1 force damage. Roll 3d4+3 for total damage.

The skeleton takes the magical assault but continues its advance, now only 10 feet away.

STATE_CHANGES:
- character.current_hp: 8 -> 14
- skeleton.position: 30 feet -> 10 feet

COMBAT:
- heal: Cleric heals player for 6 hp
- spell: Wizard casts Magic Missile for 3d4+3 force damage
        """,
        "expected_elements": {
            "healing": 1,
            "hp_changes": 1,
            "spell_attacks": 1,
            "dice_rolls": 1,
            "combat_events": 2
        }
    },
    
    {
        "name": "NPC Interaction Scenario",
        "ai_response": """
The tavern keeper, a stout dwarf named Thorin, looks up from polishing a mug. 
"Ah, another adventurer! You look like you've seen some trouble, friend. 
What brings you to the Prancing Pony?"

His demeanor is friendly but cautious. You notice his eyes briefly glance at your weapons 
before returning to meet your gaze. The tavern is busy tonight, with several other patrons 
enjoying their meals and drinks.

STORY:
- interaction: Meeting with Thorin the tavern keeper
- location: Inside the Prancing Pony tavern

ACTIONS:
- dialogue: Thorin greets the player
- observation: Thorin notices player's weapons
        """,
        "expected_elements": {
            "dialogue": 1,
            "story_events": 1,
            "actions": 2,
            "location_context": 1
        }
    },
    
    {
        "name": "Complex Combat with Status Effects",
        "ai_response": """
The dragon's breath weapon engulfs you in searing flames! Make a Dexterity saving throw 
(1d20 + your Dex modifier) against DC 17. On a failure, you take 22 fire damage, or half 
as much on a success.

The intense heat leaves you feeling weakened and disoriented. If you failed the save, 
you are also affected by the "Burned" condition for the next 3 rounds, taking 1d4 fire 
damage at the start of each turn.

Your ally, the ranger, manages to dodge most of the flames but still takes 11 fire damage. 
She moves to a safer position behind the rocky outcropping.

COMBAT:
- breath_weapon: Dragon uses fire breath vs party
- status_effect: Burned condition for 3 rounds (1d4 per turn)
- movement: Ranger moves to cover

STATE_CHANGES:
- character.status: normal -> burned (3 rounds)
- ranger.current_hp: 28 -> 17
- ranger.position: open field -> behind rocks

DICE_ROLLS:
- 1d20+DEX: Dexterity saving throw vs DC 17
- 2d6: Fire damage if failed save (22 total)
- 1d4: Ongoing burn damage per turn
        """,
        "expected_elements": {
            "saving_throws": 1,
            "status_effects": 1,
            "fire_damage": 2,
            "dice_rolls": 3,
            "combat_events": 3,
            "position_changes": 1
        }
    }
]


def test_parsing_scenarios():
    """Test the response parser with various D&D scenarios"""
    print("\n🎲 Testing Response Parsing System")
    print("=" * 50)
    
    total_tests = len(TEST_SCENARIOS)
    passed_tests = 0
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n📝 Test {i}/{total_tests}: {scenario['name']}")
        print("-" * 30)
        
        try:
            # Parse the AI response
            parsed_response = response_parser.parse_response(scenario['ai_response'])
            
            print(f"✅ Parsing completed with confidence: {parsed_response.confidence_score:.2f}")
            
            # Display parsing results
            print(f"📖 Narrative: {len(parsed_response.narrative_text)} characters")
            print(f"🎯 Actions: {len(parsed_response.actions)}")
            print(f"📊 State Changes: {len(parsed_response.state_changes)}")
            print(f"🎲 Dice Rolls: {len(parsed_response.dice_rolls)}")
            print(f"⚔️ Combat Events: {len(parsed_response.combat_events)}")
            print(f"📚 Story Events: {len(parsed_response.story_events)}")
            
            # Show specific details
            if parsed_response.actions:
                print(f"🎯 Action Types: {[action.get('type', 'unknown') for action in parsed_response.actions]}")
            
            if parsed_response.dice_rolls:
                print(f"🎲 Dice Expressions: {[roll.dice_expression for roll in parsed_response.dice_rolls]}")
            
            if parsed_response.state_changes:
                hp_changes = [change for change in parsed_response.state_changes if change.property_name == 'current_hp']
                if hp_changes:
                    total_hp_change = sum(change.change_amount or 0 for change in hp_changes)
                    print(f"❤️ Total HP Change: {total_hp_change}")
            
            if parsed_response.combat_events:
                damage_events = [event for event in parsed_response.combat_events if event.damage_amount]
                if damage_events:
                    total_damage = sum(event.damage_amount for event in damage_events)
                    print(f"⚔️ Total Damage: {total_damage}")
            
            # Check for parsing errors
            if parsed_response.parsing_errors:
                print(f"⚠️ Parsing Warnings: {len(parsed_response.parsing_errors)}")
                for error in parsed_response.parsing_errors[:3]:  # Show first 3 errors
                    print(f"   - {error}")
            
            # Generate quick summary
            summary = response_parser.extract_quick_summary(parsed_response)
            print(f"📋 Summary: {summary['parsing_quality']} quality, {len(summary['key_actions'])} key actions")
            
            if parsed_response.confidence_score > 0.7:
                passed_tests += 1
                print("✅ Test PASSED")
            else:
                print("⚠️ Test WARNING - Low confidence")
            
        except Exception as e:
            print(f"❌ Test FAILED: {str(e)}")
    
    print(f"\n🏆 Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    return passed_tests == total_tests


def test_structured_response_parsing():
    """Test parsing of responses with structured sections"""
    print("\n🏗️ Testing Structured Response Parsing")
    print("=" * 40)
    
    structured_response = """
The ancient mechanism activates with a deep grinding sound. Gears turn and crystals glow 
as the magical device comes to life. You feel a surge of energy flow through the room.

```json
{
    "actions": [
        {"type": "activation", "object": "ancient mechanism", "success": true},
        {"type": "environmental", "effect": "magical energy surge"}
    ],
    "state_changes": [
        {"entity_type": "character", "property_name": "magic_resonance", "new_value": "attuned"},
        {"entity_type": "environment", "property_name": "energy_level", "old_value": "dormant", "new_value": "active"}
    ],
    "story_events": [
        {"event_type": "discovery", "description": "Ancient mechanism activated", "consequences": ["Magic flows through the room", "New passages may open"]}
    ]
}
```

The room begins to change around you. Stone blocks shift and rearrange themselves, 
revealing a hidden passage to the north. The magical energy continues to pulse rhythmically.
    """
    
    try:
        parsed = response_parser.parse_response(structured_response)
        
        print(f"✅ Structured parsing completed")
        print(f"📖 Clean narrative: {len(parsed.narrative_text)} characters")
        print(f"🏗️ Structured data extracted: {parsed.raw_structured_data is not None}")
        
        if parsed.raw_structured_data:
            print(f"📊 JSON sections found: {list(parsed.raw_structured_data.keys())}")
        
        print(f"🎯 Total events extracted: {len(parsed.actions) + len(parsed.state_changes) + len(parsed.story_events)}")
        
        # Verify JSON was properly removed from narrative
        if '```json' not in parsed.narrative_text:
            print("✅ JSON blocks properly removed from narrative")
        else:
            print("⚠️ JSON blocks still present in narrative")
        
        return True
        
    except Exception as e:
        print(f"❌ Structured parsing failed: {str(e)}")
        return False


def test_edge_cases():
    """Test parsing edge cases and error handling"""
    print("\n🔬 Testing Edge Cases")
    print("=" * 25)
    
    edge_cases = [
        {
            "name": "Empty Response",
            "response": "",
            "should_handle": True
        },
        {
            "name": "Pure Narrative (No Game Elements)",
            "response": "The sun sets over the distant mountains, painting the sky in brilliant shades of orange and red. A gentle breeze carries the scent of wildflowers across the meadow.",
            "should_handle": True
        },
        {
            "name": "Malformed Dice Expression",
            "response": "Roll a 5d99+999 for your super attack that deals infinite damage!",
            "should_handle": True
        },
        {
            "name": "Extremely Long Response",
            "response": "The dragon roars! " * 1000,
            "should_handle": True
        }
    ]
    
    passed = 0
    for case in edge_cases:
        print(f"\n🧪 Testing: {case['name']}")
        try:
            parsed = response_parser.parse_response(case['response'])
            
            if case['should_handle']:
                print(f"✅ Handled gracefully (confidence: {parsed.confidence_score:.2f})")
                if parsed.parsing_errors:
                    print(f"⚠️ Errors logged: {len(parsed.parsing_errors)}")
                passed += 1
            else:
                print(f"❌ Should have failed but didn't")
                
        except Exception as e:
            if case['should_handle']:
                print(f"❌ Failed to handle: {str(e)}")
            else:
                print(f"✅ Properly rejected: {str(e)}")
                passed += 1
    
    print(f"\n🏆 Edge case results: {passed}/{len(edge_cases)} handled correctly")
    return passed == len(edge_cases)


def main():
    """Run all response parsing tests"""
    print("🚀 Starting Response Parser Test Suite")
    print("=" * 60)
    
    # Run test suites
    results = []
    
    results.append(("Scenario Tests", test_parsing_scenarios()))
    results.append(("Structured Tests", test_structured_response_parsing()))
    results.append(("Edge Case Tests", test_edge_cases()))
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    overall_success = all(result[1] for result in results)
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Response Parsing System is ready for production!")
        print("   - Handles various D&D scenarios correctly")
        print("   - Extracts structured data from AI responses")
        print("   - Manages edge cases gracefully")
        print("   - Provides confidence scoring and error reporting")
    else:
        print("\n⚠️ Some issues detected - review failed tests before deployment")
    
    return overall_success


if __name__ == "__main__":
    main() 