"""
Mock data generator for quests to populate the system with sample quests.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from models.quest import Quest, QuestObjective, QuestReward, CharacterQuest, QuestObjectiveProgress
from schemas.quest import QuestType, DifficultyLevel, ObjectiveType, RewardType, QuestStatus


class QuestMockDataGenerator:
    """Generate mock quest data for testing and development."""
    
    def __init__(self):
        self.sample_quests = self._initialize_sample_quests()
    
    def _initialize_sample_quests(self) -> List[Dict[str, Any]]:
        """Initialize sample quest data."""
        return [
            {
                "title": "The Goblin Menace",
                "description": "A band of goblins has been raiding merchant caravans along the trade route. The local merchant guild is offering a bounty for their elimination.",
                "quest_type": QuestType.side,
                "difficulty_level": DifficultyLevel.easy,
                "required_level": 1,
                "location": "Tradesman's Road",
                "giver_name": "Marcus Goldweaver",
                "is_active": True,
                "is_repeatable": False,
                "objectives": [
                    {
                        "description": "Eliminate 5 goblins threatening the trade route",
                        "objective_type": ObjectiveType.kill,
                        "target_type": "monster",
                        "target_id": "goblin",
                        "required_amount": 5,
                        "order_index": 0
                    }
                ],
                "rewards": [
                    {
                        "reward_type": RewardType.xp,
                        "amount": 150,
                        "rarity": "common"
                    },
                    {
                        "reward_type": RewardType.gold,
                        "amount": 25,
                        "rarity": "common"
                    },
                    {
                        "reward_type": RewardType.item,
                        "reward_id": "leather_armor",
                        "amount": 1,
                        "rarity": "uncommon"
                    }
                ]
            },
            {
                "title": "Herbs for the Healer",
                "description": "The village healer is running low on medicinal herbs. Gather moonbell flowers from the nearby forest to help her prepare healing potions.",
                "quest_type": QuestType.daily,
                "difficulty_level": DifficultyLevel.easy,
                "required_level": 1,
                "time_limit_hours": 24,
                "location": "Whispering Woods",
                "giver_name": "Elder Miriam",
                "is_active": True,
                "is_repeatable": True,
                "objectives": [
                    {
                        "description": "Collect 8 moonbell flowers from the forest",
                        "objective_type": ObjectiveType.collect,
                        "target_type": "herb",
                        "target_id": "moonbell_flower",
                        "required_amount": 8,
                        "order_index": 0
                    }
                ],
                "rewards": [
                    {
                        "reward_type": RewardType.xp,
                        "amount": 75,
                        "rarity": "common"
                    },
                    {
                        "reward_type": RewardType.gold,
                        "amount": 10,
                        "rarity": "common"
                    },
                    {
                        "reward_type": RewardType.item,
                        "reward_id": "healing_potion",
                        "amount": 2,
                        "rarity": "common"
                    }
                ]
            },
            {
                "title": "The Lost Artifact",
                "description": "An ancient artifact has been stolen from the temple and taken to the ruins of an old fortress. Retrieve it before it falls into the wrong hands.",
                "quest_type": QuestType.main,
                "difficulty_level": DifficultyLevel.medium,
                "required_level": 3,
                "prerequisite_quest_ids": [],
                "location": "Ruins of Shadowmere",
                "giver_name": "High Priest Aldren",
                "is_active": True,
                "is_repeatable": False,
                "objectives": [
                    {
                        "description": "Navigate to the Ruins of Shadowmere",
                        "objective_type": ObjectiveType.visit,
                        "target_type": "location",
                        "target_id": "shadowmere_ruins",
                        "required_amount": 1,
                        "order_index": 0
                    },
                    {
                        "description": "Defeat the fortress guardian",
                        "objective_type": ObjectiveType.kill,
                        "target_type": "monster",
                        "target_id": "stone_guardian",
                        "required_amount": 1,
                        "order_index": 1
                    },
                    {
                        "description": "Retrieve the Crystal of Eternal Light",
                        "objective_type": ObjectiveType.collect,
                        "target_type": "artifact",
                        "target_id": "crystal_eternal_light",
                        "required_amount": 1,
                        "order_index": 2
                    }
                ],
                "rewards": [
                    {
                        "reward_type": RewardType.xp,
                        "amount": 500,
                        "rarity": "common"
                    },
                    {
                        "reward_type": RewardType.gold,
                        "amount": 100,
                        "rarity": "common"
                    },
                    {
                        "reward_type": RewardType.item,
                        "reward_id": "blessed_pendant",
                        "amount": 1,
                        "rarity": "rare"
                    }
                ]
            },
            {
                "title": "Mysterious Disappearances",
                "description": "Several villagers have gone missing near the old cemetery. Investigate the area and discover what's causing these disappearances.",
                "quest_type": QuestType.side,
                "difficulty_level": DifficultyLevel.medium,
                "required_level": 4,
                "location": "Hollowbrook Cemetery",
                "giver_name": "Captain Thorne",
                "is_active": True,
                "is_repeatable": False,
                "objectives": [
                    {
                        "description": "Investigate the cemetery for clues",
                        "objective_type": ObjectiveType.explore,
                        "target_type": "location",
                        "target_id": "cemetery_grounds",
                        "required_amount": 3,
                        "order_index": 0
                    },
                    {
                        "description": "Question the cemetery keeper",
                        "objective_type": ObjectiveType.talk,
                        "target_type": "npc",
                        "target_id": "cemetery_keeper",
                        "required_amount": 1,
                        "order_index": 1
                    },
                    {
                        "description": "Eliminate the undead threat",
                        "objective_type": ObjectiveType.kill,
                        "target_type": "monster",
                        "target_id": "zombie",
                        "required_amount": 6,
                        "order_index": 2
                    }
                ],
                "rewards": [
                    {
                        "reward_type": RewardType.xp,
                        "amount": 350,
                        "rarity": "common"
                    },
                    {
                        "reward_type": RewardType.gold,
                        "amount": 75,
                        "rarity": "common"
                    },
                    {
                        "reward_type": RewardType.item,
                        "reward_id": "silver_sword",
                        "amount": 1,
                        "rarity": "uncommon"
                    }
                ]
            },
            {
                "title": "Dragon's Hoard",
                "description": "An ancient red dragon has awakened and threatens the entire kingdom. Gather your courage and face this legendary beast in its mountain lair.",
                "quest_type": QuestType.main,
                "difficulty_level": DifficultyLevel.legendary,
                "required_level": 15,
                "prerequisite_quest_ids": [],
                "location": "Dragon's Peak",
                "giver_name": "King Aldric",
                "is_active": True,
                "is_repeatable": False,
                "objectives": [
                    {
                        "description": "Reach the dragon's lair at the peak",
                        "objective_type": ObjectiveType.visit,
                        "target_type": "location",
                        "target_id": "dragons_lair",
                        "required_amount": 1,
                        "order_index": 0
                    },
                    {
                        "description": "Defeat Pyraxis the Red",
                        "objective_type": ObjectiveType.kill,
                        "target_type": "dragon",
                        "target_id": "pyraxis_red_dragon",
                        "required_amount": 1,
                        "order_index": 1
                    }
                ],
                "rewards": [
                    {
                        "reward_type": RewardType.xp,
                        "amount": 2000,
                        "rarity": "legendary"
                    },
                    {
                        "reward_type": RewardType.gold,
                        "amount": 1000,
                        "rarity": "legendary"
                    },
                    {
                        "reward_type": RewardType.item,
                        "reward_id": "dragonslayer_sword",
                        "amount": 1,
                        "rarity": "legendary"
                    },
                    {
                        "reward_type": RewardType.item,
                        "reward_id": "dragon_scale_armor",
                        "amount": 1,
                        "rarity": "legendary"
                    }
                ]
            },
            {
                "title": "Delivery to the Outpost",
                "description": "The frontier outpost needs fresh supplies. Deliver this package safely through bandit-infested territory.",
                "quest_type": QuestType.daily,
                "difficulty_level": DifficultyLevel.easy,
                "required_level": 2,
                "time_limit_hours": 12,
                "location": "Frontier Trail",
                "giver_name": "Merchant Gareth",
                "is_active": True,
                "is_repeatable": True,
                "objectives": [
                    {
                        "description": "Deliver supplies to Frontier Outpost",
                        "objective_type": ObjectiveType.deliver,
                        "target_type": "package",
                        "target_id": "supply_package",
                        "required_amount": 1,
                        "order_index": 0
                    }
                ],
                "rewards": [
                    {
                        "reward_type": RewardType.xp,
                        "amount": 100,
                        "rarity": "common"
                    },
                    {
                        "reward_type": RewardType.gold,
                        "amount": 20,
                        "rarity": "common"
                    }
                ]
            }
        ]
    
    def generate_mock_quests(self, db: Session) -> List[Quest]:
        """Generate and save mock quests to the database."""
        created_quests = []
        
        for quest_data in self.sample_quests:
            # Create the main quest
            quest_dict = quest_data.copy()
            objectives_data = quest_dict.pop('objectives', [])
            rewards_data = quest_dict.pop('rewards', [])
            
            # Create quest
            quest = Quest(**quest_dict)
            db.add(quest)
            db.flush()  # Get the quest ID
            
            # Create objectives
            for obj_data in objectives_data:
                obj_data['quest_id'] = quest.id
                objective = QuestObjective(**obj_data)
                db.add(objective)
            
            # Create rewards
            for reward_data in rewards_data:
                reward_data['quest_id'] = quest.id
                reward = QuestReward(**reward_data)
                db.add(reward)
            
            created_quests.append(quest)
        
        db.commit()
        return created_quests
    
    def assign_quests_to_character(self, character_id: int, quest_ids: List[int], db: Session) -> List[CharacterQuest]:
        """Assign quests to a character with mock progress."""
        character_quests = []
        
        for i, quest_id in enumerate(quest_ids[:5]):  # Limit to 5 quests
            # Randomly assign status
            if i == 0:
                status = QuestStatus.completed
                completed_at = datetime.utcnow() - timedelta(days=random.randint(1, 7))
            elif i == 1:
                status = QuestStatus.active
                completed_at = None
            elif i == 2:
                status = QuestStatus.active
                completed_at = None
            else:
                status = QuestStatus.active if random.random() < 0.7 else QuestStatus.abandoned
                completed_at = None
            
            # Create character quest
            accepted_at = datetime.utcnow() - timedelta(days=random.randint(1, 14))
            expires_at = accepted_at + timedelta(hours=24) if random.random() < 0.3 else None
            
            character_quest = CharacterQuest(
                character_id=character_id,
                quest_id=quest_id,
                status=status,
                accepted_at=accepted_at,
                completed_at=completed_at,
                expires_at=expires_at
            )
            db.add(character_quest)
            db.flush()
            
            # Create objective progress for active quests
            if status == QuestStatus.active:
                quest = db.query(Quest).filter(Quest.id == quest_id).first()
                if quest:
                    for objective in quest.objectives:
                        # Random progress (0 to required_amount)
                        current_amount = random.randint(0, objective.required_amount - 1)
                        progress = QuestObjectiveProgress(
                            character_quest_id=character_quest.id,
                            objective_id=objective.id,
                            current_amount=current_amount,
                            completed_at=None if current_amount < objective.required_amount else datetime.utcnow()
                        )
                        db.add(progress)
            
            character_quests.append(character_quest)
        
        db.commit()
        return character_quests
    
    def create_sample_data(self, character_id: int, db: Session) -> Dict[str, Any]:
        """Create a full set of sample quest data for a character."""
        # Generate mock quests
        quests = self.generate_mock_quests(db)
        quest_ids = [q.id for q in quests]
        
        # Assign some quests to the character
        character_quests = self.assign_quests_to_character(character_id, quest_ids, db)
        
        return {
            "quests_created": len(quests),
            "character_quests_assigned": len(character_quests),
            "quest_ids": quest_ids,
            "character_quest_ids": [cq.id for cq in character_quests]
        } 