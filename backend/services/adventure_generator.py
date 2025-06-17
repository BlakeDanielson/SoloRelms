from typing import Dict, Any, List
import json
import random
from datetime import datetime

class AdventureGeneratorService:
    """Service for generating D&D adventures with AI-powered content"""
    
    def __init__(self):
        self.story_templates = {
            "mystery": {
                "stages": ["intro", "inciting_incident", "first_combat", "investigation", "climax", "resolution"],
                "themes": ["intrigue", "secrets", "investigation", "revelation"],
                "difficulty_modifiers": {
                    "easy": 0.8,
                    "medium": 1.0,
                    "hard": 1.3,
                    "deadly": 1.6
                }
            },
            "combat": {
                "stages": ["intro", "inciting_incident", "first_combat", "escalation", "climax", "resolution"],
                "themes": ["warfare", "tactics", "strength", "victory"],
                "difficulty_modifiers": {
                    "easy": 0.7,
                    "medium": 1.0,
                    "hard": 1.4,
                    "deadly": 1.8
                }
            },
            "exploration": {
                "stages": ["intro", "inciting_incident", "discovery", "challenges", "climax", "resolution"],
                "themes": ["discovery", "nature", "adventure", "survival"],
                "difficulty_modifiers": {
                    "easy": 0.9,
                    "medium": 1.0,
                    "hard": 1.2,
                    "deadly": 1.5
                }
            },
            "political": {
                "stages": ["intro", "inciting_incident", "negotiation", "complications", "climax", "resolution"],
                "themes": ["diplomacy", "intrigue", "power", "alliances"],
                "difficulty_modifiers": {
                    "easy": 0.8,
                    "medium": 1.0,
                    "hard": 1.3,
                    "deadly": 1.6
                }
            },
            "rescue": {
                "stages": ["intro", "inciting_incident", "tracking", "infiltration", "climax", "resolution"],
                "themes": ["heroism", "urgency", "stealth", "rescue"],
                "difficulty_modifiers": {
                    "easy": 0.9,
                    "medium": 1.0,
                    "hard": 1.3,
                    "deadly": 1.7
                }
            }
        }
        
        self.location_types = [
            "dungeon", "forest", "city", "mountain", "desert", "swamp", 
            "coast", "underground", "ruins", "castle", "village", "wilderness"
        ]
        
        self.npcs_templates = {
            "ally": ["Helpful merchant", "Wise sage", "Brave guard", "Friendly local"],
            "neutral": ["Cautious villager", "Busy innkeeper", "Traveling merchant", "Curious scholar"],
            "enemy": ["Bandit leader", "Corrupt official", "Dark cultist", "Monster chieftain"]
        }

    async def generate_adventure_story(self, character_data: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete adventure story with stages and content"""
        
        story_type = preferences.get("story_type", "mystery")
        themes = preferences.get("themes", [])
        difficulty = preferences.get("difficulty", "medium")
        
        # Get story template
        template = self.story_templates.get(story_type, self.story_templates["mystery"])
        
        # Generate adventure content
        title = self._generate_title(character_data, story_type, themes)
        summary = self._generate_summary(character_data, story_type, themes, difficulty)
        world_state = self._generate_world_state(character_data, story_type)
        stages = self._generate_stage_data(character_data, template, difficulty)
        
        return {
            "title": title,
            "summary": summary,
            "world_state": world_state,
            "stages": stages,
            "story_type": story_type,
            "themes": themes + template["themes"],
            "difficulty": difficulty,
            "estimated_sessions": self._estimate_sessions(difficulty),
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_title(self, character_data: Dict[str, Any], story_type: str, themes: List[str]) -> str:
        """Generate an adventure title"""
        character_name = character_data.get("name", "Hero")
        
        title_templates = {
            "mystery": [
                f"The Mystery of {self._random_location()}",
                f"{character_name} and the Hidden Secret",
                f"Shadows over {self._random_location()}",
                f"The Vanishing of {self._random_npc()}"
            ],
            "combat": [
                f"The Battle for {self._random_location()}",
                f"{character_name}'s War",
                f"Siege of {self._random_location()}",
                f"The Last Stand at {self._random_location()}"
            ],
            "exploration": [
                f"Journey to {self._random_location()}",
                f"{character_name} and the Lost {self._random_item()}",
                f"Expedition to {self._random_location()}",
                f"The Forgotten {self._random_location()}"
            ],
            "political": [
                f"The Crown of {self._random_location()}",
                f"{character_name} and the Royal Court",
                f"Diplomacy in {self._random_location()}",
                f"The Alliance of {self._random_location()}"
            ],
            "rescue": [
                f"Rescue at {self._random_location()}",
                f"{character_name} and the Missing {self._random_npc()}",
                f"The Captives of {self._random_location()}",
                f"Liberation of {self._random_location()}"
            ]
        }
        
        templates = title_templates.get(story_type, title_templates["mystery"])
        return random.choice(templates)

    def _generate_summary(self, character_data: Dict[str, Any], story_type: str, themes: List[str], difficulty: str) -> str:
        """Generate adventure summary"""
        character_name = character_data.get("name", "the hero")
        character_class = character_data.get("character_class", "adventurer")
        level = character_data.get("level", 1)
        
        summary_templates = {
            "mystery": f"A puzzling mystery has emerged that requires {character_name}, a skilled {character_class}, to uncover the truth. With keen investigation and careful deduction, they must solve this enigma before it's too late.",
            "combat": f"War has come to the land, and {character_name}, a brave {character_class}, must face overwhelming odds. Through tactical combat and unwavering courage, they will determine the fate of many.",
            "exploration": f"An expedition into unknown territory beckons {character_name}, an experienced {character_class}. Ancient secrets and hidden treasures await those bold enough to venture forth.",
            "political": f"The delicate balance of power is at stake, and {character_name}, a diplomatic {character_class}, must navigate treacherous political waters to prevent chaos.",
            "rescue": f"Lives hang in the balance as {character_name}, a heroic {character_class}, races against time to save those who cannot save themselves."
        }
        
        base_summary = summary_templates.get(story_type, summary_templates["mystery"])
        
        # Add difficulty context
        difficulty_context = {
            "easy": "This adventure is suitable for those new to such challenges.",
            "medium": "This adventure presents moderate challenges that will test your abilities.",
            "hard": "This adventure contains significant dangers that will push you to your limits.",
            "deadly": "This adventure is extremely perilous and only the most skilled should attempt it."
        }
        
        return f"{base_summary} {difficulty_context.get(difficulty, '')}"

    def _generate_world_state(self, character_data: Dict[str, Any], story_type: str) -> Dict[str, Any]:
        """Generate initial world state"""
        return {
            "current_location": self._random_location(),
            "weather": random.choice(["clear", "overcast", "rainy", "foggy", "stormy"]),
            "time_of_day": random.choice(["dawn", "morning", "midday", "afternoon", "evening", "night"]),
            "local_reputation": "unknown",
            "available_resources": {
                "gold": random.randint(10, 100),
                "supplies": random.randint(1, 5),
                "allies": []
            },
            "threats": {
                "active": [],
                "rumored": [f"Strange happenings near {self._random_location()}"]
            },
            "discovered_locations": [],
            "completed_objectives": [],
            "story_flags": {}
        }

    def _generate_stage_data(self, character_data: Dict[str, Any], template: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
        """Generate data for each story stage"""
        stages = {}
        stage_list = template["stages"]
        
        for i, stage_name in enumerate(stage_list):
            stages[stage_name] = {
                "name": stage_name.replace("_", " ").title(),
                "description": self._generate_stage_description(stage_name, character_data),
                "objectives": self._generate_stage_objectives(stage_name),
                "challenges": self._generate_stage_challenges(stage_name, difficulty),
                "rewards": self._generate_stage_rewards(stage_name, difficulty),
                "npcs": self._generate_stage_npcs(stage_name),
                "order": i + 1,
                "estimated_duration": random.randint(30, 90)  # minutes
            }
        
        return stages

    def _generate_stage_description(self, stage_name: str, character_data: Dict[str, Any]) -> str:
        """Generate description for a specific stage"""
        descriptions = {
            "intro": "The adventure begins as our hero arrives at their destination, setting the scene for what's to come.",
            "inciting_incident": "A crucial event occurs that sets the main story in motion and defines the primary challenge.",
            "first_combat": "The first real test of combat skills presents itself, introducing the dangers ahead.",
            "investigation": "Careful examination and questioning reveal important clues about the mystery at hand.",
            "discovery": "A significant discovery changes the course of the adventure and opens new possibilities.",
            "tracking": "Following leads and pursuing targets through challenging terrain and circumstances.",
            "negotiation": "Diplomatic efforts and social encounters that could resolve conflicts peacefully.",
            "infiltration": "Stealth and cunning are required to penetrate enemy defenses undetected.",
            "challenges": "Various obstacles and puzzles test different aspects of the hero's abilities.",
            "escalation": "The stakes are raised as the situation becomes more dangerous and urgent.",
            "complications": "Unexpected developments complicate the mission and require adaptive strategies.",
            "climax": "The final confrontation where all skills and preparation are put to the ultimate test.",
            "resolution": "The adventure concludes with the outcome of the hero's efforts becoming clear."
        }
        
        return descriptions.get(stage_name, "An important stage in the adventure unfolds.")

    def _generate_stage_objectives(self, stage_name: str) -> List[str]:
        """Generate objectives for a stage"""
        objective_templates = {
            "intro": ["Meet the quest giver", "Learn about the situation", "Gather initial information"],
            "inciting_incident": ["Respond to the crisis", "Make crucial first decisions", "Begin the main quest"],
            "first_combat": ["Defeat the initial threat", "Prove combat readiness", "Protect allies"],
            "investigation": ["Search for clues", "Interview witnesses", "Examine evidence"],
            "discovery": ["Explore the new area", "Uncover hidden secrets", "Find important items"],
            "tracking": ["Follow the trail", "Navigate obstacles", "Catch up to the target"],
            "negotiation": ["Establish communication", "Find common ground", "Reach an agreement"],
            "infiltration": ["Avoid detection", "Gather intelligence", "Reach the target location"],
            "challenges": ["Overcome obstacles", "Solve puzzles", "Test abilities"],
            "escalation": ["Handle increased pressure", "Make critical decisions", "Manage resources"],
            "complications": ["Adapt to new circumstances", "Deal with setbacks", "Find alternative solutions"],
            "climax": ["Face the final challenge", "Use all acquired skills", "Determine the outcome"],
            "resolution": ["Complete remaining tasks", "Tie up loose ends", "Reflect on the journey"]
        }
        
        return objective_templates.get(stage_name, ["Progress the story"])

    def _generate_stage_challenges(self, stage_name: str, difficulty: str) -> List[Dict[str, Any]]:
        """Generate challenges for a stage"""
        base_challenges = {
            "intro": [{"type": "social", "description": "Gain trust of locals", "dc": 12}],
            "inciting_incident": [{"type": "decision", "description": "Choose your approach", "dc": 10}],
            "first_combat": [{"type": "combat", "description": "Fight bandits", "dc": 13}],
            "investigation": [{"type": "skill", "description": "Investigation check", "dc": 15}],
            "discovery": [{"type": "exploration", "description": "Navigate treacherous terrain", "dc": 14}],
            "climax": [{"type": "combat", "description": "Final boss battle", "dc": 18}]
        }
        
        # Adjust difficulty
        modifier = self.story_templates["mystery"]["difficulty_modifiers"].get(difficulty, 1.0)
        challenges = base_challenges.get(stage_name, [{"type": "general", "description": "Overcome obstacles", "dc": 12}])
        
        for challenge in challenges:
            challenge["dc"] = int(challenge["dc"] * modifier)
        
        return challenges

    def _generate_stage_rewards(self, stage_name: str, difficulty: str) -> Dict[str, Any]:
        """Generate rewards for completing a stage"""
        base_xp = {
            "intro": 50, "inciting_incident": 75, "first_combat": 100,
            "investigation": 125, "discovery": 150, "tracking": 125,
            "negotiation": 100, "infiltration": 175, "challenges": 150,
            "escalation": 200, "complications": 175, "climax": 300, "resolution": 100
        }
        
        modifier = 1.0
        if difficulty == "hard":
            modifier = 1.5
        elif difficulty == "deadly":
            modifier = 2.0
        elif difficulty == "easy":
            modifier = 0.7
        
        xp = int(base_xp.get(stage_name, 100) * modifier)
        
        return {
            "xp": xp,
            "gold": random.randint(10, 50) if stage_name in ["climax", "resolution"] else random.randint(5, 20),
            "items": self._generate_reward_items(stage_name) if stage_name in ["first_combat", "climax"] else [],
            "story_progress": True
        }

    def _generate_stage_npcs(self, stage_name: str) -> List[Dict[str, Any]]:
        """Generate NPCs for a stage"""
        npc_counts = {
            "intro": 2, "inciting_incident": 1, "first_combat": 1,
            "investigation": 3, "negotiation": 2, "climax": 1
        }
        
        count = npc_counts.get(stage_name, 1)
        npcs = []
        
        for _ in range(count):
            npc_type = random.choice(["ally", "neutral", "enemy"])
            name = self._random_npc()
            
            npcs.append({
                "name": name,
                "type": npc_type,
                "description": f"A {random.choice(self.npcs_templates[npc_type])}",
                "disposition": random.choice(["friendly", "neutral", "hostile"]) if npc_type != "enemy" else "hostile"
            })
        
        return npcs

    def _generate_reward_items(self, stage_name: str) -> List[Dict[str, Any]]:
        """Generate reward items"""
        items = []
        if stage_name == "first_combat":
            items.append({
                "name": random.choice(["Healing Potion", "Silver Dagger", "Leather Armor"]),
                "type": "equipment",
                "rarity": "common"
            })
        elif stage_name == "climax":
            items.append({
                "name": random.choice(["Magic Sword", "Ring of Protection", "Cloak of Elvenkind"]),
                "type": "equipment", 
                "rarity": "uncommon"
            })
        
        return items

    def _random_location(self) -> str:
        """Generate a random location name"""
        prefixes = ["Ancient", "Forgotten", "Hidden", "Lost", "Mystic", "Dark", "Golden", "Crystal"]
        locations = ["Temple", "Tower", "Forest", "Cave", "Ruins", "Castle", "Village", "Mountain"]
        return f"{random.choice(prefixes)} {random.choice(locations)}"

    def _random_npc(self) -> str:
        """Generate a random NPC name"""
        names = [
            "Aldric", "Thessa", "Gareth", "Lyanna", "Darian", "Miriel", 
            "Tobias", "Celeste", "Marcus", "Aria", "Viktor", "Seraphina"
        ]
        return random.choice(names)

    def _random_item(self) -> str:
        """Generate a random item name"""
        items = ["Artifact", "Tome", "Crown", "Scepter", "Orb", "Blade", "Shield", "Amulet"]
        return random.choice(items)

    def _estimate_sessions(self, difficulty: str) -> int:
        """Estimate number of sessions based on difficulty"""
        session_estimates = {
            "easy": random.randint(2, 4),
            "medium": random.randint(3, 6), 
            "hard": random.randint(4, 8),
            "deadly": random.randint(6, 12)
        }
        return session_estimates.get(difficulty, 4) 