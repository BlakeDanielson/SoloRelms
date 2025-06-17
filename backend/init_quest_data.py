#!/usr/bin/env python3
"""
Initialize quest mock data for testing
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from services.quest_mock_data import QuestMockDataGenerator
from database import SessionLocal

def main():
    """Initialize quest mock data"""
    db = SessionLocal()
    try:
        mock_generator = QuestMockDataGenerator()
        
        print("🔄 Creating sample quests...")
        quests = mock_generator.generate_mock_quests(db)
        print(f"✅ Created {len(quests)} sample quests")
        
        print("🔄 Assigning quests to character 14...")
        quest_ids = [q.id for q in quests]
        character_quests = mock_generator.assign_quests_to_character(14, quest_ids[:3], db)
        print(f"✅ Assigned {len(character_quests)} quests to character 14")
        
        print("🎉 Mock quest data initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main() 