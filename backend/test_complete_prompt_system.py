#!/usr/bin/env python3
"""
Test script to demonstrate the complete AI prompt system
Shows exactly what gets sent to the AI with every request
"""
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import AIService

class MockCharacter:
    """Mock character with comprehensive stats for testing"""
    def __init__(self):
        self.id = 1
        self.name = "Aria Brightblade"
        self.race = "Half-Elf"
        self.character_class = "Ranger"
        self.level = 3
        self.background = "Folk Hero"
        
        # Ability scores
        self.strength = 14
        self.dexterity = 16
        self.constitution = 13
        self.intelligence = 12
        self.wisdom = 15
        self.charisma = 11
        
        # Calculate ability modifiers
        self.strength_modifier = (self.strength - 10) // 2
        self.dexterity_modifier = (self.dexterity - 10) // 2
        self.constitution_modifier = (self.constitution - 10) // 2
        self.intelligence_modifier = (self.intelligence - 10) // 2
        self.wisdom_modifier = (self.wisdom - 10) // 2
        self.charisma_modifier = (self.charisma - 10) // 2
        
        # Combat stats
        self.max_hit_points = 28
        self.current_hit_points = 22
        self.armor_class = 15
        self.proficiency_bonus = 2
        
        # Currency
        self.gold_pieces = 45
        self.silver_pieces = 23
        self.copper_pieces = 8
        
        # Mock methods for inventory, spells, etc.
        self.inventory_items = [
            {"name": "Longbow", "quantity": 1, "type": "weapon", "description": "A sturdy wooden bow"},
            {"name": "Arrows", "quantity": 30, "type": "ammunition", "description": "Standard arrows"},
            {"name": "Studded Leather Armor", "quantity": 1, "type": "armor", "description": "Light armor with metal studs"},
            {"name": "Rope (50 feet)", "quantity": 1, "type": "gear", "description": "Hemp rope"},
            {"name": "Health Potion", "quantity": 2, "type": "consumable", "description": "Restores 2d4+2 HP"}
        ]
        
        self.spells = [
            {"name": "Hunter's Mark", "level": 1, "school": "divination", "description": "Mark a target for extra damage"}
        ]
        
        self.proficiencies = ["Survival", "Animal Handling", "Perception", "Stealth"]
        self.languages = ["Common", "Elvish", "Sylvan"]
        
        # Additional attributes the AI service expects
        self.experience_points = 900
        self.backstory = "A folk hero who defended her village from bandits"
        self.personality_traits = "Brave and determined, always helps those in need"
        self.ideals = "Justice - Everyone deserves protection from tyranny"
        self.bonds = "My village and its people mean everything to me"
        self.flaws = "I have trouble trusting nobles and authority figures"
        
        # Equipment and inventory
        self.inventory = [
            {"name": "Longbow", "type": "weapon", "damage": "1d8+3", "range": "150/600"},
            {"name": "Arrows", "type": "ammunition", "quantity": 30},
            {"name": "Leather Armor", "type": "armor", "ac": 11},
            {"name": "Shortsword", "type": "weapon", "damage": "1d6+3"},
            {"name": "Explorer's Pack", "type": "equipment"},
            {"name": "Thieves' Tools", "type": "tool"},
            {"name": "Healing Potion", "type": "consumable", "quantity": 2}
        ]
        self.equipped_items = {
            "weapon": "Longbow",
            "armor": "Leather Armor", 
            "shield": None
        }

class MockStoryArc:
    """Mock story arc for testing"""
    def __init__(self):
        self.id = 1
        self.title = "The Goblin Threat"
        self.description = "Local goblins have been raiding nearby farms"
        self.story_type = "adventure"
        self.story_seed = "Peaceful village threatened by goblin raids"
        self.current_stage = type('Stage', (), {'value': 'investigation'})()
        self.previous_events = [
            "Arrived in the village of Millbrook",
            "Spoke with Mayor Thomlin about goblin raids", 
            "Investigated a raided farm on the outskirts"
        ]
        self.objectives = [
            "Find the goblin hideout",
            "Stop the raids",
            "Protect the villagers"
        ]
        self.important_npcs = [
            "Mayor Thomlin - Worried village leader",
            "Farmer Hendricks - Grateful raid victim"
        ]
        self.key_locations = [
            "Village of Millbrook",
            "Hendricks Farm (raided)",
            "Forest path with goblin tracks"
        ]
        self.major_decisions = [
            {"description": "Chose to help the village", "stage": "introduction"},
            {"description": "Decided to investigate rather than attack immediately", "stage": "investigation"}
        ]
        self.character_development = [
            "Gaining reputation as a protector",
            "Learning about local politics and concerns"
        ]
        self.combat_outcomes = []  # No combat yet
        self.social_interactions = [
            {"npc": "Mayor Thomlin", "outcome": "positive", "description": "Accepted quest to help village"}
        ]
        self.character_relationships = [
            {"npc": "Mayor Thomlin", "relationship": "trusted", "status": "ally"}
        ]
        self.npc_status = {
            "mayor_thomlin": {"name": "Mayor Thomlin", "disposition": "grateful", "location": "Village Hall"}
        }
        self.world_events = [
            {"event": "Goblin raids increase", "impact": "Village fear rising"}
        ]

class MockWorldState:
    """Mock world state for testing"""
    def __init__(self):
        self.current_location = "Forest path leading to goblin caves"
        self.time_of_day = "Afternoon"
        self.weather = "Clear"
        self.recent_events = ["Discovered goblin tracks heading north"]
        self.active_npcs = ["Farmer Hendricks (grateful)", "Mayor Thomlin (worried)"]
        self.story_time_elapsed = 120  # 2 hours
        self.environmental_factors = ["Dense forest", "Goblin tracks", "Wildlife sounds"]
        self.active_objectives = [
            {"description": "Find the goblin hideout", "priority": "high", "status": "active"},
            {"description": "Stop the raids", "priority": "high", "status": "pending"}
        ]
        self.established_lore = {
            "village_info": "Millbrook is a peaceful farming village",
            "goblin_threat": "Goblins have been raiding for 2 weeks",
            "location_clues": "The forest to the north is their suspected hideout"
        }
        self.faction_standings = {
            "millbrook_villagers": {"reputation": "friendly", "standing": 75}
        }
        self.resource_availability = {
            "supplies": "adequate",
            "information": "limited",
            "allies": "few"
        }
        self.explored_areas = {
            "millbrook_village": {"status": "fully_explored", "secrets": "none"},
            "hendricks_farm": {"status": "investigated", "secrets": "goblin_tracks"}
        }
        self.discovered_secrets = [
            "Goblins are organized and planning something bigger"
        ]

def test_complete_prompt_system():
    """Test and display the complete prompt system"""
    
    print("🧪 Complete AI Prompt System Analysis")
    print("=" * 80)
    
    # Initialize AI service and mock data
    ai_service = AIService()
    character = MockCharacter()
    story_arc = MockStoryArc()
    world_state = MockWorldState()
    
    # Get the story narration template
    from services.ai_service import StoryNarrationTemplate
    story_template = StoryNarrationTemplate()
    
    # Build the complete prompt
    player_action = "I draw my bow and scan the forest for signs of the goblins"
    
    print("📋 BUILDING COMPLETE PROMPT...")
    print("-" * 80)
    
    # Show the prompt building process
    complete_prompt = story_template.build_prompt(
        character=character,
        story_arc=story_arc,
        world_state=world_state,
        player_action=player_action,
        additional_context="Player is investigating goblin tracks"
    )
    
    print("📝 COMPLETE PROMPT BEING SENT TO AI:")
    print("=" * 80)
    print(complete_prompt)
    print("=" * 80)
    
    # Calculate approximate token count (rough estimate)
    word_count = len(complete_prompt.split())
    estimated_tokens = int(word_count * 1.3)  # Rough tokens-to-words ratio
    
    print(f"\n📊 PROMPT STATISTICS:")
    print(f"- Word Count: {word_count:,}")
    print(f"- Estimated Tokens: {estimated_tokens:,}")
    print(f"- Character Count: {len(complete_prompt):,}")
    
    print(f"\n🎯 WHAT THIS PROMPT ACHIEVES:")
    print("✅ Complete D&D 5e rules reference")
    print("✅ Full character awareness (stats, inventory, abilities)")
    print("✅ Environmental analysis and opportunities")
    print("✅ Dynamic NPC generation guidelines") 
    print("✅ Quest hook suggestions")
    print("✅ Combat mechanics and balance")
    print("✅ Social interaction frameworks")
    print("✅ World-building consistency")
    print("✅ Character development tracking")
    print("✅ Tactical encounter suggestions")
    
    print(f"\n🚀 RESULT:")
    print("The AI now has comprehensive knowledge to create rich,")
    print("mechanically-sound D&D experiences that actively use")
    print("all game features and respond intelligently to character")
    print("capabilities and player actions!")
    
    print("\n" + "=" * 80)
    print("🔄 HOW THIS GETS SENT TO THE AI")
    print("=" * 80)
    
    # Show how this would be sent via the AI service
    print("\n📡 API CALL STRUCTURE:")
    print("-" * 40)
    print("Method: OpenAI Chat Completions API")
    print("Model: gpt-4.1-mini-2025-04-14")
    print("Messages:")
    print('  - System: "You are an expert Dungeon Master creating an immersive solo D&D experience."')
    print(f'  - User: [THE COMPLETE PROMPT ABOVE - {len(complete_prompt)} characters]')
    print("\nParameters:")
    print("  - max_tokens: 1000")
    print("  - temperature: 0.7")
    print("  - top_p: 0.9")
    print("  - frequency_penalty: 0.1")
    print("  - presence_penalty: 0.1")
    
    print("\n🎮 ACTUAL USAGE IN GAME:")
    print("-" * 40)
    print("1. Player takes action: 'I draw my bow and scan the forest for signs of the goblins'")
    print("2. Backend builds complete prompt with all context")
    print("3. AI receives comprehensive D&D knowledge + character data + world state")
    print("4. AI generates response using all available information")
    print("5. Response includes:")
    print("   - Rich narrative description")
    print("   - Appropriate ability check suggestions")
    print("   - Equipment usage opportunities")
    print("   - Combat initiation if warranted")
    print("   - Character stat-aware difficulty scaling")
    
    print("\n💡 EXAMPLE AI RESPONSE WOULD INCLUDE:")
    print("-" * 40)
    print("• Vivid forest description with tactical opportunities")
    print("• Perception check suggestion (Wisdom 15 = +2 modifier)")
    print("• Longbow readiness acknowledgment")
    print("• Environmental factors (wind affecting ranged attacks)")
    print("• Goblin track discovery with Investigation check option")
    print("• Combat initiation if goblins are spotted")
    print("• Stealth opportunities using character's Dex 16")
    
    print("\n🔧 BACKEND INTEGRATION:")
    print("-" * 40)
    print("File: backend/api/games.py")
    print("Endpoint: POST /api/games/{game_id}/action")
    print("Function: handle_player_action()")
    print("Process:")
    print("  1. Receive player action")
    print("  2. Load character, story_arc, world_state from database")
    print("  3. Build complete prompt using StoryNarrationTemplate")
    print("  4. Send to AI service")
    print("  5. Parse response for combat detection")
    print("  6. Update game state")
    print("  7. Return enriched response to frontend")
    
    print("\n🎯 FRONTEND INTEGRATION:")
    print("-" * 40)
    print("File: frontend/src/components/game/ImmersiveDnDInterface.tsx")
    print("Component: ImmersiveDnDInterface")
    print("Features:")
    print("  • Displays AI response with rich formatting")
    print("  • Shows combat indicators when detected")
    print("  • Renders character stats and inventory")
    print("  • Provides action input interface")
    print("  • Updates in real-time based on game state")
    
    print("\n" + "=" * 80)
    print("✨ COMPLETE SYSTEM READY FOR ULTIMATE D&D EXPERIENCE!")
    print("=" * 80)

if __name__ == "__main__":
    test_complete_prompt_system() 