from typing import Dict, Any, List, Optional
import random
from datetime import datetime

class AIDMService:
    """AI Dungeon Master service for managing story progression and narrative"""
    
    def __init__(self):
        self.story_responses = {
            "intro": [
                "As you arrive at your destination, you notice something unusual in the air...",
                "The journey has been long, but now you stand before your next challenge...",
                "A sense of adventure fills you as you take in your surroundings..."
            ],
            "exploration": [
                "You explore the area carefully, searching for clues and signs of what lies ahead.",
                "The environment reveals its secrets to those who look closely enough.",
                "Each step forward brings new discoveries and potential dangers."
            ],
            "combat": [
                "Battle erupts! Your enemies charge forward with weapons drawn!",
                "The clash of steel rings out as combat begins in earnest!",
                "Your training kicks in as you face this dangerous encounter!"
            ],
            "social": [
                "The NPCs regard you with a mixture of curiosity and caution.",
                "Your words carry weight in this delicate social situation.", 
                "Diplomacy and wisdom will be key to navigating this encounter."
            ],
            "success": [
                "Your efforts pay off as you overcome the challenge before you!",
                "Success! Your skills and determination have seen you through!",
                "Victory is yours, but greater challenges may lie ahead..."
            ],
            "failure": [
                "Things don't go quite as planned, but this setback teaches valuable lessons.",
                "Not every attempt succeeds, but each failure brings wisdom for the future.",
                "This challenge proves more difficult than expected, requiring a new approach."
            ]
        }
        
        self.scene_descriptions = {
            "forest": [
                "Ancient trees tower overhead, their canopy filtering the sunlight into dancing patterns.",
                "The forest floor is carpeted with fallen leaves that crunch softly underfoot.",
                "Mysterious sounds echo from deeper in the woods, hinting at unseen inhabitants."
            ],
            "dungeon": [
                "Stone corridors stretch ahead, lit by flickering torches along the walls.", 
                "The air is thick with the scent of age and mystery in these underground chambers.",
                "Each shadow could hide danger or treasure in these forgotten depths."
            ],
            "city": [
                "Bustling streets filled with merchants, travelers, and local residents create a lively atmosphere.",
                "The architecture speaks of a rich history and prosperous present.",
                "Opportunities for adventure seem to lurk around every corner in this urban environment."
            ]
        }

    async def generate_story_response(self, player_action: str, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a story response based on player action and current context"""
        
        action_type = self._classify_action(player_action)
        current_scene = current_context.get("current_scene", "exploration")
        character_level = current_context.get("character_level", 1)
        
        # Generate base response
        response_text = self._generate_response_text(action_type, current_scene)
        
        # Determine consequences
        consequences = self._determine_consequences(player_action, action_type, character_level)
        
        # Generate any new NPCs or items that might appear
        new_elements = self._generate_scene_elements(action_type, current_scene)
        
        return {
            "narrative_text": response_text,
            "action_type": action_type,
            "consequences": consequences,
            "new_elements": new_elements,
            "suggested_actions": self._generate_suggested_actions(action_type, current_scene),
            "dice_suggestions": self._suggest_dice_rolls(action_type),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def advance_story_stage(self, adventure_id: int, current_stage: str, player_choices: List[str]) -> Dict[str, Any]:
        """Advance the story to the next stage based on player choices"""
        
        # Story stage progression logic
        stage_order = ["intro", "inciting_incident", "first_combat", "investigation", "climax", "resolution"]
        
        try:
            current_index = stage_order.index(current_stage)
            next_stage = stage_order[current_index + 1] if current_index < len(stage_order) - 1 else "resolution"
        except ValueError:
            next_stage = "investigation"  # Default fallback
        
        # Generate transition narrative
        transition_text = self._generate_stage_transition(current_stage, next_stage, player_choices)
        
        # Update scene based on new stage
        new_scene_data = self._generate_scene_for_stage(next_stage)
        
        return {
            "new_stage": next_stage,
            "transition_narrative": transition_text,
            "scene_data": new_scene_data,
            "stage_completed": True,
            "next_objectives": self._generate_objectives_for_stage(next_stage)
        }

    async def generate_scene_description(self, scene_type: str, context: Dict[str, Any]) -> str:
        """Generate a detailed scene description"""
        
        base_descriptions = self.scene_descriptions.get(scene_type, self.scene_descriptions["forest"])
        base_description = random.choice(base_descriptions)
        
        # Add context-specific details
        time_of_day = context.get("time_of_day", "day")
        weather = context.get("weather", "clear")
        
        time_modifier = {
            "dawn": "The early morning light casts long shadows across the landscape.",
            "day": "Bright daylight illuminates the area clearly.",
            "dusk": "The fading light of evening adds an air of mystery.",
            "night": "Darkness cloaks the area, broken only by scattered light sources."
        }
        
        weather_modifier = {
            "clear": "The weather is pleasant and clear.",
            "rainy": "A light rain adds a refreshing coolness to the air.",
            "stormy": "Dark clouds overhead threaten heavier weather.",
            "foggy": "A thin mist reduces visibility and adds an ethereal quality."
        }
        
        enhanced_description = f"{base_description} {time_modifier.get(time_of_day, '')} {weather_modifier.get(weather, '')}"
        
        return enhanced_description.strip()

    def _classify_action(self, action: str) -> str:
        """Classify player action into categories"""
        action_lower = action.lower()
        
        combat_keywords = ["attack", "fight", "cast", "shoot", "strike", "defend", "block"]
        social_keywords = ["talk", "speak", "persuade", "intimidate", "negotiate", "ask"]
        exploration_keywords = ["search", "look", "examine", "explore", "investigate", "check"]
        
        if any(keyword in action_lower for keyword in combat_keywords):
            return "combat"
        elif any(keyword in action_lower for keyword in social_keywords):
            return "social"
        elif any(keyword in action_lower for keyword in exploration_keywords):
            return "exploration"
        else:
            return "general"

    def _generate_response_text(self, action_type: str, scene_type: str) -> str:
        """Generate appropriate response text"""
        
        # Combine action type responses with scene-appropriate flavor
        base_responses = self.story_responses.get(action_type, self.story_responses["exploration"])
        base_response = random.choice(base_responses)
        
        # Add scene-specific flavor
        scene_flavor = {
            "forest": "The forest around you seems to respond to your presence.",
            "dungeon": "The ancient stones bear witness to your actions.",
            "city": "The urban environment buzzes with activity around you."
        }
        
        flavor_text = scene_flavor.get(scene_type, "The environment responds to your actions.")
        
        return f"{base_response} {flavor_text}"

    def _determine_consequences(self, action: str, action_type: str, character_level: int) -> Dict[str, Any]:
        """Determine consequences of player action"""
        
        # Base success chance varies by action type and character level
        base_success = {
            "combat": 0.7 + (character_level * 0.02),
            "social": 0.6 + (character_level * 0.03),
            "exploration": 0.8 + (character_level * 0.01),
            "general": 0.75
        }
        
        success_chance = base_success.get(action_type, 0.75)
        success = random.random() < success_chance
        
        consequences = {
            "success": success,
            "xp_gained": random.randint(10, 25) if success else random.randint(5, 10),
            "damage_taken": 0,
            "items_found": [],
            "story_progress": success
        }
        
        # Add specific consequences based on action type
        if action_type == "combat" and success:
            consequences["items_found"] = self._generate_combat_rewards()
        elif action_type == "exploration" and success:
            consequences["xp_gained"] += 5  # Bonus for successful exploration
        elif action_type == "social" and success:
            consequences["reputation_change"] = random.randint(1, 3)
        
        # Add some danger for failed actions
        if not success:
            if action_type == "combat":
                consequences["damage_taken"] = random.randint(1, 5)
            elif action_type == "exploration":
                consequences["story_setback"] = True
        
        return consequences

    def _generate_scene_elements(self, action_type: str, scene_type: str) -> Dict[str, List[str]]:
        """Generate new NPCs, items, or locations that might appear"""
        
        elements = {
            "npcs": [],
            "items": [],
            "locations": []
        }
        
        # Small chance to introduce new elements
        if random.random() < 0.3:  # 30% chance
            if scene_type == "city":
                elements["npcs"] = [random.choice([
                    "A curious merchant", "A traveling bard", "A local guard", "A mysterious stranger"
                ])]
            elif scene_type == "dungeon" and action_type == "exploration":
                elements["items"] = [random.choice([
                    "An ancient key", "A dusty tome", "A glowing crystal", "A worn map"
                ])]
            elif scene_type == "forest":
                elements["locations"] = [random.choice([
                    "A hidden grove", "An old hunting trail", "A babbling brook", "A circle of standing stones"
                ])]
        
        return elements

    def _generate_suggested_actions(self, action_type: str, scene_type: str) -> List[str]:
        """Generate suggested follow-up actions"""
        
        base_suggestions = {
            "combat": ["Continue fighting", "Attempt to disengage", "Use a special ability"],
            "social": ["Press for more information", "Change your approach", "Offer assistance"],
            "exploration": ["Search more thoroughly", "Move to a new area", "Examine specific details"],
            "general": ["Look around", "Consider your options", "Proceed carefully"]
        }
        
        return base_suggestions.get(action_type, base_suggestions["general"])

    def _suggest_dice_rolls(self, action_type: str) -> List[str]:
        """Suggest appropriate dice rolls for the situation"""
        
        roll_suggestions = {
            "combat": ["1d20 + attack bonus", "1d8 + damage modifier"],
            "social": ["1d20 + charisma modifier", "1d20 + persuasion"],
            "exploration": ["1d20 + investigation", "1d20 + perception"],
            "general": ["1d20 + relevant modifier"]
        }
        
        return roll_suggestions.get(action_type, roll_suggestions["general"])

    def _generate_stage_transition(self, current_stage: str, next_stage: str, player_choices: List[str]) -> str:
        """Generate narrative text for stage transitions"""
        
        transitions = {
            ("intro", "inciting_incident"): "Your arrival sets events in motion that will shape this adventure...",
            ("inciting_incident", "first_combat"): "The situation escalates as conflict becomes unavoidable...",
            ("first_combat", "investigation"): "With the immediate threat handled, you can focus on uncovering the truth...",
            ("investigation", "climax"): "All your discoveries lead to this crucial moment...",
            ("climax", "resolution"): "The final challenge behind you, the consequences of your choices become clear..."
        }
        
        return transitions.get((current_stage, next_stage), "The story continues to unfold based on your actions...")

    def _generate_scene_for_stage(self, stage: str) -> Dict[str, Any]:
        """Generate scene data appropriate for a story stage"""
        
        stage_scenes = {
            "intro": {"type": "peaceful", "danger_level": 1},
            "inciting_incident": {"type": "mysterious", "danger_level": 2},
            "first_combat": {"type": "combat", "danger_level": 4},
            "investigation": {"type": "exploration", "danger_level": 2},
            "climax": {"type": "dramatic", "danger_level": 5},
            "resolution": {"type": "peaceful", "danger_level": 1}
        }
        
        return stage_scenes.get(stage, {"type": "exploration", "danger_level": 3})

    def _generate_objectives_for_stage(self, stage: str) -> List[str]:
        """Generate objectives appropriate for a story stage"""
        
        stage_objectives = {
            "intro": ["Learn about your surroundings", "Meet key NPCs", "Establish your goals"],
            "inciting_incident": ["Respond to the crisis", "Make crucial decisions", "Prepare for challenges ahead"],
            "first_combat": ["Defeat your opponents", "Protect yourself and allies", "Use your abilities effectively"],
            "investigation": ["Gather important clues", "Examine evidence carefully", "Interview witnesses"],
            "climax": ["Face the final challenge", "Use everything you've learned", "Determine the outcome"],
            "resolution": ["Complete remaining tasks", "Reflect on your journey", "Prepare for what's next"]
        }
        
        return stage_objectives.get(stage, ["Progress the story", "Make meaningful choices"])

    def _generate_combat_rewards(self) -> List[str]:
        """Generate rewards for successful combat"""
        rewards = []
        
        if random.random() < 0.6:  # 60% chance
            rewards.append(random.choice([
                "A small healing potion",
                "A few gold coins", 
                "An enemy's weapon",
                "A useful tool"
            ]))
        
        return rewards 