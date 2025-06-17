#!/usr/bin/env python3
"""
Test AI awareness of character stats vs player intentions
"""
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService

class MockCharacter:
    """Mock character for testing"""
    def __init__(self, **kwargs):
        # Set defaults
        self.name = kwargs.get('name', 'Test Character')
        self.race = kwargs.get('race', 'Human')
        self.character_class = kwargs.get('character_class', 'Fighter')
        self.level = kwargs.get('level', 1)
        self.background = kwargs.get('background', 'Soldier')
        
        # Ability scores
        self.strength = kwargs.get('strength', 10)
        self.dexterity = kwargs.get('dexterity', 10)
        self.constitution = kwargs.get('constitution', 10)
        self.intelligence = kwargs.get('intelligence', 10)
        self.wisdom = kwargs.get('wisdom', 10)
        self.charisma = kwargs.get('charisma', 10)
        
        # Calculate modifiers
        self.strength_modifier = (self.strength - 10) // 2
        self.dexterity_modifier = (self.dexterity - 10) // 2
        self.constitution_modifier = (self.constitution - 10) // 2
        self.intelligence_modifier = (self.intelligence - 10) // 2
        self.wisdom_modifier = (self.wisdom - 10) // 2
        self.charisma_modifier = (self.charisma - 10) // 2
        
        # Combat stats
        self.current_hit_points = kwargs.get('current_hit_points', 10)
        self.max_hit_points = kwargs.get('max_hit_points', 10)
        self.armor_class = kwargs.get('armor_class', 12)
        self.proficiency_bonus = kwargs.get('proficiency_bonus', 2)
        
        # Equipment
        self.equipped_items = kwargs.get('equipped_items', {})
        self.inventory = kwargs.get('inventory', [])

def test_stat_mismatch_scenarios():
    """Test scenarios where character stats don't match their intended actions"""
    
    print("🧪 Testing AI Stat Awareness")
    print("=" * 60)
    
    ai_service = AIService()
    
    if not ai_service.client:
        print("❌ AI service not available - missing API key")
        return
    
    # Test scenarios where stats don't match actions
    test_scenarios = [
        {
            "name": "Weak Character Breaking Door",
            "character": MockCharacter(
                name="Weakling",
                strength=5,  # Very weak
                dexterity=14,
                intelligence=16,
                current_hit_points=8,
                max_hit_points=8
            ),
            "action": "I charge at the heavy iron door and try to break it down with my shoulder!",
            "expected_response": [
                "difficult", "challenging", "unlikely", "weak", "low strength",
                "alternative", "different approach", "dc", "roll", "disadvantage"
            ]
        },
        {
            "name": "Clumsy Character Stealth",
            "character": MockCharacter(
                name="Clumsy",
                strength=16,
                dexterity=6,  # Very clumsy
                wisdom=8,
                armor_class=18  # Heavy armor
            ),
            "action": "I try to sneak silently past the guards using stealth.",
            "expected_response": [
                "difficult", "heavy armor", "disadvantage", "clumsy", "low dexterity",
                "alternative", "noise", "clanking"
            ]
        },
        {
            "name": "Socially Awkward Persuasion",
            "character": MockCharacter(
                name="Awkward",
                charisma=4,  # Very awkward
                intelligence=18,
                strength=16
            ),
            "action": "I try to charm the noble into giving me information using my charisma.",
            "expected_response": [
                "difficult", "awkward", "low charisma", "challenging",
                "alternative", "different approach", "intimidation", "intelligence"
            ]
        },
        {
            "name": "Injured Character Combat",
            "character": MockCharacter(
                name="Injured",
                strength=16,
                current_hit_points=2,  # Critically injured
                max_hit_points=20
            ),
            "action": "I charge into melee combat with my sword!",
            "expected_response": [
                "dangerous", "injured", "low health", "risky", "critical",
                "healing", "rest", "avoid combat"
            ]
        },
        {
            "name": "Smart Character Physical Challenge",
            "character": MockCharacter(
                name="Scholar",
                strength=6,  # Weak
                intelligence=18,  # Very smart
                dexterity=8
            ),
            "action": "I want to climb this steep cliff face to reach the castle.",
            "expected_response": [
                "difficult", "weak", "low strength", "challenging",
                "alternative", "clever", "intelligence", "different route"
            ]
        }
    ]
    
    print(f"🎯 Testing {len(test_scenarios)} stat mismatch scenarios")
    print("-" * 60)
    
    success_count = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        name = scenario["name"]
        character = scenario["character"]
        action = scenario["action"]
        expected_keywords = scenario["expected_response"]
        
        print(f"\n🎭 Test {i}/{len(test_scenarios)}: {name}")
        print(f"📊 Character: STR {character.strength}, DEX {character.dexterity}, INT {character.intelligence}, CHA {character.charisma}")
        print(f"❤️ HP: {character.current_hit_points}/{character.max_hit_points}, AC: {character.armor_class}")
        print(f"🎯 Action: {action}")
        print("-" * 40)
        
        try:
            # Create AI template and get character context
            template = ai_service.templates['story']
            character_context = template.format_character_context(character)
            
            # Create test prompt
            test_prompt = f"""{template.base_instructions}

{character_context}

### CURRENT SITUATION ###
The character is standing in front of a challenge that requires careful consideration of their abilities.

### PLAYER ACTION ###
The player has chosen to: {action}

### RESPONSE FORMAT ###
As an expert DM, respond to this action by:
1. Acknowledging the character's intention
2. Considering their ability scores and current condition
3. Explaining the likelihood of success or difficulty
4. Suggesting appropriate alternatives if the action seems ill-suited to their abilities
5. Setting appropriate DCs based on their specific stats

**IMPORTANT**: Pay close attention to the character's ability scores and condition. If they're attempting something that their stats suggest would be very difficult or dangerous, acknowledge this and provide guidance.

Provide a response that takes into account the character's specific capabilities and limitations.
"""
            
            # Generate AI response
            ai_result = ai_service.generate_response(
                prompt=test_prompt,
                max_tokens=400,
                temperature=0.7
            )
            
            if ai_result.get('success') and ai_result.get('content'):
                response = ai_result['content'].lower()
                
                print(f"🤖 AI Response:")
                print(f"📄 {ai_result['content'][:400]}...")
                
                # Check if AI recognized the stat mismatch
                keywords_found = []
                for keyword in expected_keywords:
                    if keyword.lower() in response:
                        keywords_found.append(keyword)
                
                awareness_score = len(keywords_found) / len(expected_keywords)
                
                print(f"✅ Stat Awareness Keywords Found: {', '.join(keywords_found)}")
                print(f"❌ Missing Keywords: {', '.join([k for k in expected_keywords if k not in keywords_found])}")
                print(f"📊 Awareness Score: {awareness_score:.1%}")
                
                if awareness_score >= 0.3:  # At least 30% of expected keywords
                    success_count += 1
                    print("🎉 SUCCESS: AI recognized stat mismatch!")
                else:
                    print("⚠️ FAILURE: AI didn't recognize stat limitations")
                
            else:
                print(f"❌ AI generation failed: {ai_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Test failed with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Stat Awareness Testing Complete!")
    print(f"📊 Scenarios where AI recognized stat mismatches: {success_count}/{len(test_scenarios)}")
    print(f"✅ Success Rate: {(success_count/len(test_scenarios))*100:.1f}%")
    
    if success_count == len(test_scenarios):
        print("🎉 EXCELLENT! AI perfectly recognizes character limitations!")
    elif success_count >= len(test_scenarios) * 0.8:
        print("👍 GREAT! AI usually recognizes stat limitations!")
    elif success_count >= len(test_scenarios) * 0.6:
        print("👌 GOOD! AI often recognizes stat limitations!")
    else:
        print("⚠️ NEEDS IMPROVEMENT! AI should better recognize character limitations!")
    
    return success_count, len(test_scenarios)

if __name__ == "__main__":
    print("🎯 Testing AI Awareness of Character Stats vs Actions")
    print("Does the AI adjust difficulty and suggest alternatives based on character abilities?")
    print()
    
    success_count, total_tests = test_stat_mismatch_scenarios()
    
    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 60)
    
    if success_count >= total_tests * 0.8:
        print("✅ EXCELLENT: AI is highly aware of character limitations!")
        print("The AI will:")
        print("• Recognize when actions don't match character abilities")
        print("• Adjust difficulty and DCs appropriately")
        print("• Suggest better alternatives based on character strengths")
        print("• Warn about dangerous actions for injured characters")
    else:
        print("⚠️ The AI needs better stat awareness training.")
        print("Consider enhancing character analysis prompts.") 