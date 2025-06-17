"""
Quest generation service for creating dynamic quests based on character level and preferences.
"""

import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from ..models.quest import Quest, QuestObjective, QuestReward
from ..schemas.quest import QuestType, DifficultyLevel, ObjectiveType, RewardType


class QuestGenerator:
    """Service for generating dynamic quests."""
    
    def __init__(self):
        self.quest_templates = self._initialize_quest_templates()
        self.objective_templates = self._initialize_objective_templates()
        self.reward_templates = self._initialize_reward_templates()
    
    def _initialize_quest_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize quest templates by type."""
        return {
            "daily": [
                {
                    "title_template": "Gather {amount} {item_name}",
                    "description_template": "The local {npc_type} needs {amount} {item_name} for their {purpose}. Collect them from the {location}.",
                    "objective_type": ObjectiveType.collect,
                    "target_types": ["herb", "mineral", "animal_part"],
                    "locations": ["Whispering Woods", "Crystal Caves", "Mountain Pass", "Ancient Grove"],
                    "difficulty_range": ["easy", "medium"]
                },
                {
                    "title_template": "Eliminate {amount} {monster_name}",
                    "description_template": "{monster_name} have been threatening travelers near {location}. Eliminate {amount} of them to restore safety.",
                    "objective_type": ObjectiveType.kill,
                    "target_types": ["goblin", "wolf", "bandit", "skeleton"],
                    "locations": ["Old Road", "Dark Forest", "Abandoned Mine", "Cursed Ruins"],
                    "difficulty_range": ["easy", "medium"]
                },
                {
                    "title_template": "Deliver Message to {npc_name}",
                    "description_template": "Deliver an urgent message from {sender} to {npc_name} in {location}.",
                    "objective_type": ObjectiveType.deliver,
                    "target_types": ["message", "letter", "package"],
                    "locations": ["Village Square", "Temple", "Tavern", "Guard Tower"],
                    "difficulty_range": ["easy"]
                }
            ],
            "side": [
                {
                    "title_template": "The Lost {artifact_name}",
                    "description_template": "A valuable {artifact_name} has been lost in {location}. Find it and return it to its rightful owner.",
                    "objective_type": ObjectiveType.collect,
                    "target_types": ["artifact", "relic", "tome"],
                    "locations": ["Ancient Temple", "Forgotten Crypt", "Wizard's Tower", "Dragon's Lair"],
                    "difficulty_range": ["medium", "hard"]
                },
                {
                    "title_template": "Rescue {npc_name}",
                    "description_template": "{npc_name} has been captured by {enemy_type} and is being held in {location}. Rescue them!",
                    "objective_type": ObjectiveType.visit,
                    "target_types": ["prisoner", "captive"],
                    "locations": ["Bandit Camp", "Orc Stronghold", "Dark Dungeon", "Cultist Hideout"],
                    "difficulty_range": ["medium", "hard", "legendary"]
                }
            ],
            "main": [
                {
                    "title_template": "The {threat_name} Crisis",
                    "description_template": "A great {threat_name} threatens the realm. You must gather allies and face this legendary challenge.",
                    "objective_type": ObjectiveType.kill,
                    "target_types": ["dragon", "demon_lord", "lich", "ancient_evil"],
                    "locations": ["Shadowlands", "Demon Realm", "Dragon's Peak", "Necropolis"],
                    "difficulty_range": ["legendary"]
                }
            ]
        }
    
    def _initialize_objective_templates(self) -> Dict[ObjectiveType, Dict[str, Any]]:
        """Initialize objective templates by type."""
        return {
            ObjectiveType.kill: {
                "amounts": {"easy": (1, 5), "medium": (3, 10), "hard": (5, 15), "legendary": (1, 3)},
                "targets": {
                    "easy": ["goblin", "wolf", "rat", "spider"],
                    "medium": ["orc", "bandit", "skeleton", "zombie"],
                    "hard": ["troll", "wyvern", "demon", "vampire"],
                    "legendary": ["dragon", "lich", "demon_lord", "ancient_evil"]
                }
            },
            ObjectiveType.collect: {
                "amounts": {"easy": (3, 8), "medium": (5, 12), "hard": (8, 20), "legendary": (1, 5)},
                "targets": {
                    "easy": ["herb", "flower", "stone", "wood"],
                    "medium": ["gem", "metal_ore", "rare_herb", "monster_part"],
                    "hard": ["crystal", "enchanted_item", "artifact_fragment", "rare_component"],
                    "legendary": ["legendary_artifact", "divine_relic", "dragon_scale", "phoenix_feather"]
                }
            },
            ObjectiveType.visit: {
                "amounts": {"easy": (1, 1), "medium": (1, 2), "hard": (1, 3), "legendary": (1, 1)},
                "targets": {
                    "easy": ["village", "camp", "shrine"],
                    "medium": ["town", "fortress", "temple"],
                    "hard": ["dungeon", "castle", "stronghold"],
                    "legendary": ["ancient_city", "divine_realm", "dragon_lair"]
                }
            },
            ObjectiveType.talk: {
                "amounts": {"easy": (1, 1), "medium": (1, 2), "hard": (1, 3), "legendary": (1, 1)},
                "targets": {
                    "easy": ["villager", "merchant", "guard"],
                    "medium": ["noble", "priest", "captain"],
                    "hard": ["king", "archmage", "high_priest"],
                    "legendary": ["ancient_spirit", "deity", "dragon"]
                }
            },
            ObjectiveType.deliver: {
                "amounts": {"easy": (1, 1), "medium": (1, 2), "hard": (1, 3), "legendary": (1, 1)},
                "targets": {
                    "easy": ["message", "package", "letter"],
                    "medium": ["important_document", "magical_item", "supply_crate"],
                    "hard": ["royal_decree", "artifact", "battle_plans"],
                    "legendary": ["divine_mandate", "legendary_weapon", "world_changing_item"]
                }
            },
            ObjectiveType.explore: {
                "amounts": {"easy": (1, 2), "medium": (2, 4), "hard": (3, 6), "legendary": (1, 3)},
                "targets": {
                    "easy": ["forest_area", "cave", "ruin"],
                    "medium": ["dungeon_level", "temple_chamber", "fortress_wing"],
                    "hard": ["ancient_complex", "magical_realm", "planar_gate"],
                    "legendary": ["lost_continent", "divine_realm", "time_rift"]
                }
            },
            ObjectiveType.survive: {
                "amounts": {"easy": (5, 10), "medium": (10, 20), "hard": (15, 30), "legendary": (30, 60)},
                "targets": {
                    "easy": ["wilderness", "storm", "cold_night"],
                    "medium": ["monster_waves", "cursed_area", "magical_storm"],
                    "hard": ["planar_invasion", "undead_horde", "dragon_assault"],
                    "legendary": ["apocalypse", "divine_trial", "reality_collapse"]
                }
            }
        }
    
    def _initialize_reward_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize reward templates by difficulty."""
        return {
            "easy": {
                RewardType.xp: (50, 200),
                RewardType.gold: (10, 50),
                RewardType.item: ["healing_potion", "basic_weapon", "simple_armor"]
            },
            "medium": {
                RewardType.xp: (150, 500),
                RewardType.gold: (25, 150),
                RewardType.item: ["magic_weapon", "enchanted_armor", "rare_potion"]
            },
            "hard": {
                RewardType.xp: (400, 1000),
                RewardType.gold: (100, 500),
                RewardType.item: ["powerful_weapon", "legendary_armor", "epic_accessory"]
            },
            "legendary": {
                RewardType.xp: (800, 2500),
                RewardType.gold: (300, 1500),
                RewardType.item: ["artifact_weapon", "divine_armor", "legendary_relic"]
            }
        }
    
    def generate_daily_quests(self, character, count: int, db: Session) -> List[Quest]:
        """Generate daily quests for a character."""
        daily_quests = []
        templates = self.quest_templates["daily"]
        
        for _ in range(count):
            template = random.choice(templates)
            difficulty = self._determine_difficulty(character.level, template["difficulty_range"])
            
            quest = self._create_quest_from_template(template, difficulty, QuestType.daily, character.level)
            
            # Add to database
            db_quest = Quest(**quest)
            db.add(db_quest)
            db.flush()
            
            # Add objectives
            for obj_data in quest["objectives"]:
                obj_data["quest_id"] = db_quest.id
                objective = QuestObjective(**obj_data)
                db.add(objective)
            
            # Add rewards
            for reward_data in quest["rewards"]:
                reward_data["quest_id"] = db_quest.id
                reward = QuestReward(**reward_data)
                db.add(reward)
            
            daily_quests.append(db_quest)
        
        db.commit()
        return daily_quests
    
    def generate_quest(self, quest_type: QuestType, difficulty: DifficultyLevel, character_level: int) -> Dict[str, Any]:
        """Generate a single quest of specified type and difficulty."""
        templates = self.quest_templates.get(quest_type.value, self.quest_templates["side"])
        template = random.choice(templates)
        
        return self._create_quest_from_template(template, difficulty.value, quest_type, character_level)
    
    def _create_quest_from_template(self, template: Dict[str, Any], difficulty: str, quest_type: QuestType, character_level: int) -> Dict[str, Any]:
        """Create a quest from a template."""
        # Generate quest details
        location = random.choice(template["locations"])
        target_type = random.choice(template["target_types"])
        
        # Generate objective
        obj_template = self.objective_templates[template["objective_type"]]
        amount_range = obj_template["amounts"][difficulty]
        amount = random.randint(*amount_range)
        target = random.choice(obj_template["targets"][difficulty])
        
        # Generate title and description
        title = template["title_template"].format(
            amount=amount,
            item_name=target,
            monster_name=target,
            npc_name=self._generate_npc_name(),
            artifact_name=target,
            threat_name=target
        )
        
        description = template["description_template"].format(
            amount=amount,
            item_name=target,
            monster_name=target,
            location=location,
            npc_type=random.choice(["alchemist", "blacksmith", "healer", "merchant"]),
            purpose=random.choice(["research", "crafting", "healing", "trade"]),
            npc_name=self._generate_npc_name(),
            sender=self._generate_npc_name(),
            artifact_name=target,
            enemy_type=random.choice(["bandits", "orcs", "cultists", "monsters"]),
            threat_name=target
        )
        
        # Generate rewards
        rewards = self._generate_rewards(difficulty, character_level)
        
        # Create quest data
        quest_data = {
            "title": title,
            "description": description,
            "quest_type": quest_type,
            "difficulty_level": difficulty,
            "required_level": max(1, character_level - 2),
            "location": location,
            "giver_name": self._generate_npc_name(),
            "is_active": True,
            "is_repeatable": quest_type == QuestType.daily,
            "objectives": [{
                "description": f"{template['objective_type'].value.title()} {amount} {target}",
                "objective_type": template["objective_type"],
                "target_type": target_type,
                "target_id": target,
                "required_amount": amount,
                "order_index": 0
            }],
            "rewards": rewards
        }
        
        return quest_data
    
    def _determine_difficulty(self, character_level: int, allowed_difficulties: List[str]) -> str:
        """Determine appropriate difficulty based on character level."""
        if character_level <= 3:
            return "easy" if "easy" in allowed_difficulties else allowed_difficulties[0]
        elif character_level <= 7:
            return "medium" if "medium" in allowed_difficulties else random.choice(allowed_difficulties)
        elif character_level <= 12:
            return "hard" if "hard" in allowed_difficulties else random.choice(allowed_difficulties)
        else:
            return random.choice(allowed_difficulties)
    
    def _generate_rewards(self, difficulty: str, character_level: int) -> List[Dict[str, Any]]:
        """Generate rewards for a quest."""
        rewards = []
        reward_template = self.reward_templates[difficulty]
        
        # Always give XP
        xp_range = reward_template[RewardType.xp]
        xp_amount = random.randint(*xp_range)
        rewards.append({
            "reward_type": RewardType.xp,
            "amount": xp_amount,
            "rarity": "common"
        })
        
        # Often give gold
        if random.random() < 0.8:
            gold_range = reward_template[RewardType.gold]
            gold_amount = random.randint(*gold_range)
            rewards.append({
                "reward_type": RewardType.gold,
                "amount": gold_amount,
                "rarity": "common"
            })
        
        # Sometimes give items
        if random.random() < 0.6:
            item = random.choice(reward_template[RewardType.item])
            rarity = self._determine_item_rarity(difficulty)
            rewards.append({
                "reward_type": RewardType.item,
                "reward_id": item,
                "amount": 1,
                "rarity": rarity
            })
        
        return rewards
    
    def _determine_item_rarity(self, difficulty: str) -> str:
        """Determine item rarity based on difficulty."""
        rarity_weights = {
            "easy": {"common": 0.7, "uncommon": 0.3},
            "medium": {"common": 0.4, "uncommon": 0.5, "rare": 0.1},
            "hard": {"uncommon": 0.4, "rare": 0.5, "epic": 0.1},
            "legendary": {"rare": 0.3, "epic": 0.5, "legendary": 0.2}
        }
        
        weights = rarity_weights[difficulty]
        return random.choices(list(weights.keys()), list(weights.values()))[0]
    
    def _generate_npc_name(self) -> str:
        """Generate a random NPC name."""
        first_names = [
            "Aeron", "Bella", "Cedric", "Diana", "Elias", "Fiona", "Gareth", "Helena",
            "Ivan", "Jenna", "Kael", "Luna", "Marcus", "Nora", "Owen", "Petra"
        ]
        last_names = [
            "Brightblade", "Stormwind", "Ironforge", "Goldleaf", "Shadowmere", "Firebeard",
            "Moonwhisper", "Stargazer", "Thornfield", "Riverstone", "Dragonbane", "Swiftarrow"
        ]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}" 