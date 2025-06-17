"""
AI Service for GPT-4.1-mini Integration
Provides structured prompt templates and AI response handling for the SoloRealms D&D game.
"""

import os
import json
from typing import Dict, List, Optional, Any, Union
from openai import OpenAI
from sqlalchemy.orm import Session
from models.character import Character
from models.story import StoryArc, WorldState, StoryStage
from models.combat import CombatEncounter, CombatParticipant


class AIPromptTemplate:
    """Base class for AI prompt templates"""
    
    def __init__(self, template_name: str):
        self.template_name = template_name
        self.base_instructions = """You are an expert Dungeon Master for a solo D&D 5e game. 
You create immersive, engaging narratives while following D&D rules and maintaining consistency with the established story and world state.

Key guidelines:
- Stay in character as an experienced, creative DM
- Maintain consistency with established story elements, character details, and world state
- Create vivid, descriptive scenes that engage the player
- Present clear choices and consequences
- Respect D&D 5e mechanics and logic
- Keep responses focused and avoid unnecessary repetition
- Adapt tone and content to the current story stage

ACTIVE GAME MECHANICS ENGAGEMENT:
- **Inventory & Equipment**: Regularly suggest opportunities to use items, find new equipment, or upgrade gear
- **Ability Checks**: Create scenarios requiring Strength, Dexterity, Intelligence, Wisdom, Charisma, or Constitution checks
- **Skill Usage**: Present opportunities for stealth, persuasion, investigation, perception, athletics, etc.
- **Combat Encounters**: When appropriate, create tactical combat scenarios that test different abilities
- **Experience & Leveling**: Acknowledge significant achievements and suggest when the character might gain XP
- **Resource Management**: Consider spell slots, hit points, and consumable items in scenario design
- **Character Growth**: Create challenges that allow the character to showcase their class features and abilities
- **Environmental Interaction**: Describe how the character's stats and equipment affect their interaction with the world

PROACTIVE SUGGESTIONS:
- When the character has useful items, suggest scenarios where they'd be valuable
- When HP is low, create opportunities for rest or healing
- When abilities are high, create challenges that showcase those strengths
- When equipment is basic, hint at potential upgrades or improvements
- Create varied encounters that require different approaches (combat, social, exploration, puzzle-solving)

### D&D 5E RULES REFERENCE ###

**DIFFICULTY CLASS (DC) GUIDELINES:**
- Very Easy: DC 5 (Almost certain success)
- Easy: DC 10 (High chance of success)
- Medium: DC 15 (Moderate challenge)
- Hard: DC 20 (Difficult but achievable)
- Very Hard: DC 25 (Requires exceptional ability or luck)
- Nearly Impossible: DC 30 (Legendary achievement)

**ABILITY CHECK MODIFIERS:**
- Proficiency: Add proficiency bonus if skilled
- Advantage: Roll twice, take higher (favorable conditions)
- Disadvantage: Roll twice, take lower (unfavorable conditions)
- Help: +2 bonus if another can assist
- Tools: Proficiency with relevant tools adds bonus

**SAVING THROW DCs BY SPELL LEVEL:**
- Cantrip: DC 8 + proficiency + spellcasting modifier
- 1st-3rd level: DC 13-15
- 4th-6th level: DC 16-18
- 7th-9th level: DC 19-21

**CONDITION EFFECTS:**
- Blinded: Can't see, attacks have disadvantage, attacks against have advantage
- Charmed: Can't attack charmer, charmer has advantage on social interactions
- Deafened: Can't hear, automatically fails hearing-based Perception checks
- Frightened: Disadvantage on ability checks and attacks while source is in sight
- Grappled: Speed becomes 0, ends if grappler is incapacitated
- Incapacitated: Can't take actions or reactions
- Invisible: Can't be seen, attacks have advantage, attacks against have disadvantage
- Paralyzed: Incapacitated, can't move or speak, fails Str and Dex saves
- Petrified: Transformed to stone, incapacitated, weight increases 10x
- Poisoned: Disadvantage on attack rolls and ability checks
- Prone: Disadvantage on attack rolls, attacks against have advantage if within 5 feet
- Restrained: Speed 0, disadvantage on Dex saves, attacks against have advantage
- Stunned: Incapacitated, can't move, fails Str and Dex saves
- Unconscious: Incapacitated, prone, drops held items, fails Str and Dex saves

**COMBAT MECHANICS:**
- Armor Class: 10 + Dex modifier + armor bonus + shield bonus + other bonuses
- Initiative: d20 + Dex modifier
- Attack Roll: d20 + ability modifier + proficiency (if proficient)
- Damage Roll: Weapon die + ability modifier + other bonuses
- Critical Hit: Natural 20, roll damage dice twice
- Critical Fumble: Natural 1, automatic miss
- Cover: +2 AC (half cover), +5 AC (three-quarters cover), can't be targeted (total cover)
- Flanking: Advantage on melee attacks when ally is opposite enemy
- Opportunity Attacks: When creature leaves reach without Disengaging
- Two-Weapon Fighting: Bonus action attack with light weapon, no ability modifier to damage

**SKILL CHECK GUIDELINES:**
- Athletics (Str): Climbing, jumping, swimming, pushing
- Acrobatics (Dex): Balance, diving, flips, tumbling
- Sleight of Hand (Dex): Pickpocketing, concealing objects, magic tricks
- Stealth (Dex): Hiding, moving silently, avoiding detection
- Arcana (Int): Knowledge of magic, identifying spells/magical effects
- History (Int): Knowledge of past events, legends, ancient civilizations
- Investigation (Int): Looking for clues, deducing information, research
- Nature (Int): Knowledge of natural world, plants, animals, weather
- Religion (Int): Knowledge of deities, religious practices, holy symbols
- Animal Handling (Wis): Calming animals, training, riding
- Insight (Wis): Reading people's intentions, detecting lies
- Medicine (Wis): Stabilizing dying, diagnosing illness, first aid
- Perception (Wis): Noticing things, searching, listening
- Survival (Wis): Tracking, navigating, finding food/shelter
- Deception (Cha): Lying convincingly, misleading others
- Intimidation (Cha): Threatening, coercing through fear
- Performance (Cha): Entertaining, acting, musical performance
- Persuasion (Cha): Convincing others, diplomacy, negotiation

**MAGIC ITEM RARITY AND POWER:**
- Common: Mundane benefits, flavor items (50-100 gp)
- Uncommon: Minor magical benefits (101-500 gp)
- Rare: Moderate magical benefits (501-5,000 gp)
- Very Rare: Major magical benefits (5,001-50,000 gp)
- Legendary: Powerful artifacts (50,001+ gp)

**REST MECHANICS:**
- Short Rest: 1 hour, regain hit dice, some class features
- Long Rest: 8 hours, regain all HP and hit dice, spell slots, most class features
- Exhaustion: 6 levels, each adds disadvantage/penalties, removed by long rest

### DYNAMIC ENVIRONMENT SYSTEM ###

**BIOME CHARACTERISTICS:**
- Forest: Dense canopy, limited visibility, natural cover, climbing opportunities, wildlife
- Mountains: Steep terrain, altitude effects, rockslides, caves, extreme weather
- Desert: Extreme heat/cold, sandstorms, mirages, scarce water, hidden oases
- Swamp: Difficult terrain, disease, poison, hidden dangers, poor visibility
- Arctic: Extreme cold, ice hazards, avalanches, limited resources, survival challenges
- Urban: Crowds, buildings, sewers, rooftops, guards, politics, commerce
- Underground: Darkness, tight spaces, structural hazards, echoes, limited escape routes

**WEATHER EFFECTS:**
- Rain: Disadvantage on Perception (sight), extinguishes flames, slippery surfaces
- Snow: Difficult terrain, reduced visibility, tracks easily seen
- Fog: Heavily obscured beyond 5 feet, advantage on Stealth
- Wind: Ranged attacks affected, flying difficult, fire spreads
- Extreme Heat: Constitution saves or exhaustion, double water consumption
- Extreme Cold: Constitution saves or exhaustion, frostbite risk

**INTERACTIVE ENVIRONMENTAL OBJECTS:**
- Doors: Locked (Thieves' Tools/force), barred (Strength check), magically sealed
- Walls: Climbable (Athletics), breakable (Strength), searchable (Investigation)
- Furniture: Moveable (Strength), hideable behind (Stealth), throwable (improvised weapon)
- Natural Features: Rivers (Athletics to cross), cliffs (Athletics to climb), caves (explore)

**TIME OF DAY EFFECTS:**
- Dawn/Dusk: Dim light, advantage on Stealth, romantic atmosphere
- Day: Bright light, normal activities, crowds in settlements
- Night: Darkness, disadvantage on Perception (sight), nocturnal creatures active
- Midnight: Deep darkness, supernatural activity peaks, guard changes

### ADVANCED COMBAT INTELLIGENCE ###

**ENEMY TACTICAL PATTERNS:**
- Beasts: Instinctive, pack tactics, flee when wounded
- Humanoids: Tactical, use cover, retreat strategically, call for help
- Undead: Fearless, relentless, exploit weaknesses, resist certain damage
- Fiends: Cunning, cruel, psychological warfare, exploit fears
- Dragons: Aerial advantage, breath weapons, lair actions, legendary actions

**ENVIRONMENTAL COMBAT OPPORTUNITIES:**
- High Ground: Advantage on ranged attacks, tactical positioning
- Narrow Passages: Limit enemy numbers, create chokepoints
- Hazards: Push enemies into fire/pits/traps, environmental damage
- Cover: Protect from ranged attacks, break line of sight
- Difficult Terrain: Slow enemy movement, create tactical advantages

**ENCOUNTER SCALING FACTORS:**
- Character Level: Adjust enemy CR and numbers
- Current HP: Reduce difficulty if injured, increase if healthy
- Resources: Consider spell slots, abilities used, equipment condition
- Story Importance: Major battles should be challenging, random encounters moderate

### CHARACTER DEVELOPMENT FRAMEWORK ###

**PERSONAL QUEST HOOKS BY BACKGROUND:**
- Acolyte: Religious mysteries, temple politics, divine quests
- Criminal: Past crimes, underworld connections, redemption arcs
- Folk Hero: Community needs, defending the innocent, growing reputation
- Noble: Family obligations, political intrigue, maintaining honor
- Sage: Ancient knowledge, research opportunities, scholarly pursuits
- Soldier: Military missions, veteran bonds, war consequences

**CHARACTER GROWTH MILESTONES:**
- First Combat Victory: Confidence boost, reputation begins
- First Major Decision: Character defines their moral compass
- Class Feature Mastery: Opportunities to use new abilities
- Story Revelation: Personal backstory elements emerge
- Relationship Development: Bonds with NPCs or causes

**MEANINGFUL CHOICE CONSEQUENCES:**
- Short-term: Immediate results visible in current scene
- Medium-term: Effects appear in next few encounters
- Long-term: Major story or world changes
- Personal: Character growth or relationship changes

### LIVING WORLD SYSTEM ###

**NPC MOTIVATION MATRICES:**
- Goals: What they want to achieve
- Fears: What they want to avoid
- Loyalties: Who/what they serve
- Secrets: Hidden information they possess
- Resources: What they can offer or need

**FACTION RELATIONSHIPS:**
- Allied: +2 to social interactions, aid readily given
- Friendly: +1 to social interactions, help with reasonable requests
- Neutral: Standard interactions, fair treatment
- Unfriendly: -1 to social interactions, reluctant cooperation
- Hostile: -2 to social interactions, active opposition

**WORLD EVENT CONSEQUENCES:**
- Economic: Prices change, trade routes affected, job opportunities
- Political: Leadership changes, law enforcement variations, diplomatic relations
- Military: Troop movements, conflicts, security levels
- Social: Public opinion shifts, cultural events, social movements

### ENHANCED SOCIAL INTERACTION ###

**NPC PERSONALITY ARCHETYPES:**
- The Mentor: Wise, patient, teaching through questions
- The Rival: Competitive, challenging, pushing character to improve
- The Innocent: Naive, trusting, needs protection
- The Trickster: Playful, unpredictable, hiding wisdom in jest
- The Guardian: Protective, duty-bound, suspicious of strangers
- The Merchant: Practical, profit-focused, information broker

**SOCIAL ENCOUNTER FRAMEWORKS:**
- Negotiation: Multiple offers, compromise solutions, win-win outcomes
- Intimidation: Show of force, reputation leverage, consequences of refusal
- Persuasion: Logical arguments, emotional appeals, shared interests
- Deception: Partial truths, misdirection, maintaining cover stories
- Performance: Entertainment value, crowd reactions, memorable moments

**CULTURAL CONTEXT BY RACE:**
- Elves: Long-lived perspective, artistic appreciation, natural harmony
- Dwarves: Clan honor, craftsmanship pride, grudge remembrance
- Halflings: Community focus, comfort appreciation, storytelling tradition
- Humans: Ambition driven, adaptable, diverse cultures
- Tieflings: Prejudice faced, self-reliance, prove worthiness

### QUEST GENERATION ENGINE ###

**QUEST TEMPLATE STRUCTURES:**
- Fetch Quest: Retrieve object → Travel to location → Overcome obstacle → Return with item
- Escort Quest: Meet NPC → Travel together → Protect from dangers → Deliver safely
- Investigation: Discover problem → Gather clues → Follow leads → Confront perpetrator
- Exploration: Discover location → Navigate dangers → Map area → Report findings
- Rescue Mission: Learn of captive → Locate prison → Infiltrate/assault → Extract target

**PLOT TWIST GENERATORS:**
- Ally Betrayal: Trusted NPC reveals hidden agenda
- Hidden Identity: Character/NPC is not who they seem
- False Objective: Real goal different from stated mission
- Time Pressure: Deadline forces immediate action
- Moral Dilemma: Success requires questionable actions

**SIDE QUEST INTEGRATION:**
- Character Background: Relate to personal history
- World Events: Connect to larger story developments
- NPC Requests: Build relationship through favors
- Environmental Discovery: Find while exploring
- Consequence Chains: Result from previous actions

### MAGICAL WORLD DETAILS ###

**MAGIC ITEM GENERATION GUIDELINES:**
- Minor Items: Simple enchantments, utility focused, common materials
- Major Items: Powerful enchantments, combat focused, rare materials
- Artifacts: Unique history, multiple abilities, legendary materials
- Cursed Items: Hidden drawbacks, difficult to remove, moral lessons

**SPELL RESEARCH SYSTEM:**
- Component Gathering: Rare materials for new spells
- Knowledge Seeking: Research in libraries or with mentors
- Experimentation: Risk/reward for magical innovation
- Divine Inspiration: Religious characters receive visions

**MAGICAL PHENOMENA:**
- Wild Magic Surges: Unpredictable effects in high-magic areas
- Ley Lines: Enhanced spellcasting along magical connections
- Planar Rifts: Temporary access to other planes
- Magical Storms: Areas of chaotic magical energy
- Divine Manifestations: Direct intervention by deities

**PLANAR TRAVEL MECHANICS:**
- Material Plane: Standard reality, balanced elements
- Feywild: Emotion-driven, time distortion, fey creatures
- Shadowfell: Despair-focused, undead prevalent, muted colors
- Elemental Planes: Extreme environments, elemental creatures
- Outer Planes: Aligned with moral/ethical concepts, divine realms
"""
    
    def format_character_context(self, character: Character) -> str:
        """Format comprehensive character information for AI context"""
        
        # Calculate AC description
        ac_desc = "Well-armored" if character.armor_class >= 15 else "Lightly armored"
        if character.armor_class >= 18:
            ac_desc = "Heavily armored"
        elif character.armor_class <= 12:
            ac_desc = "Poorly armored"
        
        # Calculate HP status
        hp_percentage = (character.current_hit_points / character.max_hit_points) * 100 if character.max_hit_points > 0 else 0
        if hp_percentage <= 25:
            hp_status = "CRITICAL - Needs immediate healing"
        elif hp_percentage <= 50:
            hp_status = "INJURED - Should consider rest/healing"
        elif hp_percentage <= 75:
            hp_status = "WOUNDED - Could use healing"
        else:
            hp_status = "HEALTHY - Ready for action"
        
        character_info = f"""
### COMPLETE CHARACTER PROFILE ###
**Basic Information:**
- Name: {character.name}
- Race: {character.race}
- Class: {character.character_class}
- Level: {character.level}
- Background: {character.background or 'Not specified'}

**Ability Scores & Modifiers:**
- Strength: {character.strength} ({character.strength_modifier:+d}) {"[STRONG]" if character.strength >= 15 else "[WEAK]" if character.strength <= 8 else ""}
- Dexterity: {character.dexterity} ({character.dexterity_modifier:+d}) {"[AGILE]" if character.dexterity >= 15 else "[CLUMSY]" if character.dexterity <= 8 else ""}
- Constitution: {character.constitution} ({character.constitution_modifier:+d}) {"[TOUGH]" if character.constitution >= 15 else "[FRAIL]" if character.constitution <= 8 else ""}
- Intelligence: {character.intelligence} ({character.intelligence_modifier:+d}) {"[SMART]" if character.intelligence >= 15 else "[DIM]" if character.intelligence <= 8 else ""}
- Wisdom: {character.wisdom} ({character.wisdom_modifier:+d}) {"[WISE]" if character.wisdom >= 15 else "[UNAWARE]" if character.wisdom <= 8 else ""}
- Charisma: {character.charisma} ({character.charisma_modifier:+d}) {"[CHARISMATIC]" if character.charisma >= 15 else "[AWKWARD]" if character.charisma <= 8 else ""}

**Combat Statistics:**
- Hit Points: {character.current_hit_points}/{character.max_hit_points} ({hp_percentage:.0f}%) - {hp_status}
- Armor Class: {character.armor_class} ({ac_desc})
- Proficiency Bonus: +{character.proficiency_bonus}

**Equipment & Inventory:**"""
        
        # Enhanced equipment information
        if hasattr(character, 'equipped_items') and character.equipped_items:
            character_info += f"\n- Currently Equipped: {json.dumps(character.equipped_items, indent=2)}"
        else:
            character_info += "\n- Currently Equipped: Basic starting equipment"
            
        if hasattr(character, 'inventory') and character.inventory:
            character_info += f"\n- Inventory Items: {json.dumps(character.inventory, indent=2)}"
        else:
            character_info += "\n- Inventory: Basic supplies"
            
        if hasattr(character, 'gold') and character.gold:
            character_info += f"\n- Gold: {character.gold} pieces"
        
        # Skills and proficiencies
        character_info += f"""

**Skills & Proficiencies:**"""
        
        if hasattr(character, 'skills') and character.skills:
            character_info += f"\n- Skill Proficiencies: {', '.join(character.skills)}"
        else:
            character_info += "\n- Skill Proficiencies: Class and background defaults"
            
        if hasattr(character, 'proficiencies') and character.proficiencies:
            character_info += f"\n- Other Proficiencies: {', '.join(character.proficiencies)}"
            
        # Spellcasting information (if applicable)
        if hasattr(character, 'spell_slots') and character.spell_slots:
            character_info += f"""

**Spellcasting:**
- Spell Slots: {json.dumps(character.spell_slots, indent=2)}"""
            
        if hasattr(character, 'known_spells') and character.known_spells:
            character_info += f"\n- Known Spells: {', '.join(character.known_spells)}"
            
        if hasattr(character, 'prepared_spells') and character.prepared_spells:
            character_info += f"\n- Prepared Spells: {', '.join(character.prepared_spells)}"
        
        # Class features and abilities
        if hasattr(character, 'class_features') and character.class_features:
            character_info += f"""

**Class Features:**
{json.dumps(character.class_features, indent=2)}"""
        else:
            character_info += f"""

**Class Features:**
- Standard {character.character_class} abilities for level {character.level}"""
        
        # Current conditions and effects
        if hasattr(character, 'conditions') and character.conditions:
            character_info += f"""

**Current Conditions/Effects:**
{', '.join(character.conditions)}"""
        else:
            character_info += f"""

**Current Conditions/Effects:**
- None (character is in normal state)"""
            
        # Add tactical recommendations based on stats
        character_info += f"""

**AI TACTICAL ANALYSIS:**
- Primary Strengths: {self._identify_strong_abilities(character)}
- Potential Weaknesses: {self._identify_weak_abilities(character)}
- Combat Role: {self._suggest_combat_role(character)}
- Recommended Approach: {self._suggest_tactical_approach(character)}

**IMPORTANT FOR DM:**
- When setting DCs, consider this character's specific ability scores
- Strength {character.strength} means {"easy" if character.strength >= 15 else "challenging" if character.strength <= 10 else "moderate"} physical tasks
- Dexterity {character.dexterity} means {"easy" if character.dexterity >= 15 else "challenging" if character.dexterity <= 10 else "moderate"} agility tasks
- Adjust encounter difficulty based on current HP ({character.current_hit_points}/{character.max_hit_points})
- Consider character's equipment when describing environmental interactions
"""
        
        return character_info

    def format_story_context(self, story_arc: StoryArc, world_state: WorldState = None) -> str:
        """Format story and world state for AI context"""
        story_context = f"""
### STORY CONTEXT ###
Title: {story_arc.title or 'Untitled Adventure'}
Current Stage: {story_arc.current_stage.value}
Story Type: {story_arc.story_type}
Story Seed: {story_arc.story_seed or 'Dynamic adventure'}

Major Decisions Made:
{self._format_decisions(story_arc.major_decisions)}

Combat History:
{self._format_combat_history(story_arc.combat_outcomes)}

NPC Status:
{self._format_npc_status(story_arc.npc_status)}
"""
        
        if world_state:
            story_context += f"""
### WORLD STATE ###
Current Location: {world_state.current_location}
Story Time Elapsed: {world_state.story_time_elapsed} minutes

Active Objectives:
{self._format_objectives(world_state.active_objectives)}

Established Lore:
{self._format_lore(world_state.established_lore)}

Explored Areas:
{self._format_explored_areas(world_state.explored_areas)}
"""
        
        return story_context
    
    def _format_decisions(self, decisions: List[Dict]) -> str:
        """Format major decisions for context"""
        if not decisions:
            return "- None yet"
        
        formatted = []
        for decision in decisions[-3:]:  # Last 3 decisions for context
            formatted.append(f"- {decision.get('description', 'Unknown decision')} (Stage: {decision.get('stage', 'unknown')})")
        return "\n".join(formatted)
    
    def _format_combat_history(self, combats: List[Dict]) -> str:
        """Format combat outcomes for context"""
        if not combats:
            return "- No combat encounters yet"
        
        formatted = []
        for combat in combats[-2:]:  # Last 2 combats for context
            result = combat.get('result', 'unknown')
            encounter_type = combat.get('encounter_type', 'unknown encounter')
            formatted.append(f"- {encounter_type}: {result}")
        return "\n".join(formatted)
    
    def _format_npc_status(self, npc_status: Dict) -> str:
        """Format NPC status information"""
        if not npc_status:
            return "- No NPCs encountered yet"
        
        formatted = []
        for npc_id, status in npc_status.items():
            disposition = status.get('disposition', 'neutral')
            health = status.get('health', 'unknown')
            formatted.append(f"- {npc_id}: {disposition} ({health})")
        return "\n".join(formatted)
    
    def _format_objectives(self, objectives: List[Dict]) -> str:
        """Format active objectives"""
        if not objectives:
            return "- No active objectives"
        
        formatted = []
        for obj in objectives:
            priority = obj.get('priority', 'normal')
            title = obj.get('title', 'Unknown objective')
            formatted.append(f"- [{priority.upper()}] {title}")
        return "\n".join(formatted)
    
    def _format_lore(self, lore: Dict) -> str:
        """Format established world lore"""
        if not lore:
            return "- World details being established dynamically"
        
        formatted = []
        for key, value in lore.items():
            formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        return "\n".join(formatted)
    
    def _format_explored_areas(self, areas: dict) -> str:
        """Format explored areas information"""
        if not areas:
            return "No areas explored yet"
        
        formatted = []
        # Get the last 3 areas for context
        area_items = list(areas.items())[-3:]
        for area_name, area_data in area_items:
            status = area_data.get('status', 'unknown')
            secrets = area_data.get('secrets', 'none')
            formatted.append(f"- {area_name}: {status} (secrets: {secrets})")
        
        return "\n".join(formatted)

    def _identify_strong_abilities(self, character: Character) -> str:
        """Identify character's strongest ability scores"""
        abilities = {
            'Strength': character.strength,
            'Dexterity': character.dexterity,
            'Constitution': character.constitution,
            'Intelligence': character.intelligence,
            'Wisdom': character.wisdom,
            'Charisma': character.charisma
        }
        
        # Find abilities with scores 14+ (good) or 16+ (excellent)
        strong_abilities = []
        for ability, score in abilities.items():
            if score >= 16:
                strong_abilities.append(f"{ability} {score} (Excellent)")
            elif score >= 14:
                strong_abilities.append(f"{ability} {score} (Good)")
        
        return ", ".join(strong_abilities) if strong_abilities else "No particularly strong abilities"
    
    def _identify_weak_abilities(self, character: Character) -> str:
        """Identify character's weakest ability scores"""
        abilities = {
            'Strength': character.strength,
            'Dexterity': character.dexterity,
            'Constitution': character.constitution,
            'Intelligence': character.intelligence,
            'Wisdom': character.wisdom,
            'Charisma': character.charisma
        }
        
        # Find abilities with scores 10 or lower (weak)
        weak_abilities = []
        for ability, score in abilities.items():
            if score <= 8:
                weak_abilities.append(f"{ability} {score} (Very Weak)")
            elif score <= 10:
                weak_abilities.append(f"{ability} {score} (Weak)")
        
        return ", ".join(weak_abilities) if weak_abilities else "No particularly weak abilities"

    def _suggest_combat_role(self, character: Character) -> str:
        """Suggest the character's best combat role based on stats and class"""
        class_name = character.character_class.lower()
        
        # Class-based suggestions
        if class_name in ['fighter', 'paladin', 'barbarian']:
            if character.strength >= 15 and character.armor_class >= 15:
                return "Tank/Frontline Fighter - High damage and defense"
            elif character.strength >= 13:
                return "Damage Dealer - Focus on offense"
            else:
                return "Support Fighter - Consider tactical positioning"
                
        elif class_name in ['rogue', 'ranger']:
            if character.dexterity >= 15:
                return "Skirmisher/Scout - Hit and run tactics, stealth"
            else:
                return "Support - Focus on skills and utility"
                
        elif class_name in ['wizard', 'sorcerer', 'warlock']:
            if character.intelligence >= 15 or character.charisma >= 15:
                return "Spellcaster - Ranged damage and utility"
            else:
                return "Support Caster - Focus on utility spells"
                
        elif class_name in ['cleric', 'druid']:
            if character.wisdom >= 15:
                return "Support/Healer - Keep party healthy and provide utility"
            else:
                return "Versatile Support - Mix of combat and utility"
                
        elif class_name == 'bard':
            if character.charisma >= 15:
                return "Social/Support - Inspiration, spells, and social encounters"
            else:
                return "Jack-of-all-trades - Versatile support"
        
        # Fallback based on highest stat
        highest_stat = max([
            (character.strength, 'Physical Combat'),
            (character.dexterity, 'Agile Combat/Ranged'),
            (character.constitution, 'Tank/Endurance'),
            (character.intelligence, 'Tactical/Magical'),
            (character.wisdom, 'Support/Perception'),
            (character.charisma, 'Social/Inspiration')
        ])
        
        return f"{highest_stat[1]} (based on highest stat)"

    def _suggest_tactical_approach(self, character: Character) -> str:
        """Suggest tactical approaches based on character's stats and condition"""
        hp_percentage = (character.current_hit_points / character.max_hit_points) * 100 if character.max_hit_points > 0 else 0
        
        suggestions = []
        
        # HP-based suggestions
        if hp_percentage <= 25:
            suggestions.append("AVOID COMBAT - Seek healing immediately")
        elif hp_percentage <= 50:
            suggestions.append("Cautious approach - Stay at range, avoid melee")
        elif hp_percentage >= 75:
            suggestions.append("Aggressive approach possible")
        
        # Stat-based suggestions
        if character.strength >= 15:
            suggestions.append("Physical solutions (break doors, climb, swim)")
        if character.dexterity >= 15:
            suggestions.append("Agile solutions (stealth, acrobatics, ranged combat)")
        if character.intelligence >= 15:
            suggestions.append("Clever solutions (investigation, arcana, puzzles)")
        if character.wisdom >= 15:
            suggestions.append("Perceptive solutions (insight, survival, perception)")
        if character.charisma >= 15:
            suggestions.append("Social solutions (persuasion, deception, intimidation)")
        
        # AC-based suggestions
        if character.armor_class >= 15:
            suggestions.append("Can tank damage in frontline combat")
        else:
            suggestions.append("Avoid melee, use ranged attacks or magic")
        
        # Weakness-based warnings
        if character.strength <= 8:
            suggestions.append("AVOID: Physical challenges (climbing, breaking, athletics)")
        if character.dexterity <= 8:
            suggestions.append("AVOID: Agility challenges (stealth, acrobatics)")
        if character.constitution <= 8:
            suggestions.append("AVOID: Endurance challenges (long fights, poison)")
        if character.intelligence <= 8:
            suggestions.append("AVOID: Complex puzzles or arcane challenges")
        if character.wisdom <= 8:
            suggestions.append("AVOID: Perception-based challenges")
        if character.charisma <= 8:
            suggestions.append("AVOID: Social interactions")
        
        return "; ".join(suggestions) if suggestions else "Standard D&D approach"


class StoryNarrationTemplate(AIPromptTemplate):
    """Template for story narration and scene setting"""
    
    def __init__(self):
        super().__init__("story_narration")
    
    def build_prompt(self, character: Character, story_arc: StoryArc, world_state: WorldState = None, 
                    player_action: str = None, additional_context: str = None) -> str:
        """Build a story narration prompt"""
        
        # Detect if this is an aggressive action that should trigger combat
        combat_trigger_detected = False
        if player_action:
            combat_keywords = [
                'attack', 'fight', 'strike', 'hit', 'stab', 'slash', 'shoot', 'cast',
                'kill', 'murder', 'threaten', 'intimidate', 'draw weapon', 'draw sword',
                'fight me', 'i kill', 'violence', 'combat', 'battle', 'assault',
                'charge', 'swing', 'lunge', 'brandish', 'prepare to die', 'challenge',
                'weapon raised', 'ready to strike', 'aggressive', 'hostile'
            ]
            action_lower = player_action.lower()
            
            # More aggressive detection - if ANY combat keyword is present
            combat_trigger_detected = any(keyword in action_lower for keyword in combat_keywords)
            
            # Also detect patterns like "I [verb] [weapon/target]"
            combat_patterns = [
                r'i\s+(attack|strike|hit|stab|slash|shoot|fight)',
                r'draw\s+(sword|weapon|blade|dagger|axe)',
                r'brandish\s+(weapon|sword|blade)',
                r'charge\s+(forward|at|toward)',
                r'ready\s+to\s+(fight|attack|strike)',
                r'prepare\s+to\s+(die|fight)',
                r'weapon\s+raised'
            ]
            
            import re
            for pattern in combat_patterns:
                if re.search(pattern, action_lower):
                    combat_trigger_detected = True
                    break
        
        prompt = f"""{self.base_instructions}

{self.format_character_context(character)}

{self.format_story_context(story_arc, world_state)}

### CURRENT SITUATION ###
You are narrating the story for the {story_arc.current_stage.value} stage.

### GAME MECHANICS ANALYSIS ###
Based on the character's current state, consider these opportunities:

Character Condition Analysis:
- HP Status: {character.current_hit_points}/{character.max_hit_points} {"(LOW - consider rest/healing opportunities)" if character.current_hit_points < character.max_hit_points * 0.5 else "(GOOD - can handle challenges)"}
- Combat Readiness: AC {character.armor_class} {"(Well-armored)" if character.armor_class >= 15 else "(Lightly armored - be cautious)"}

Ability Score Opportunities:
- Primary Strengths: {self._identify_strong_abilities(character)}
- Potential Challenges: {self._identify_weak_abilities(character)}

Equipment Considerations:
- Current Equipment: {json.dumps(character.equipped_items) if character.equipped_items else 'Basic gear - opportunities for upgrades'}
- Suggested Usage: Create scenarios where current equipment would be useful or new equipment could be found

Class Feature Utilization:
- Class: {character.character_class} Level {character.level}
- Consider creating scenarios that highlight {character.character_class} abilities and features
- Present challenges appropriate for a level {character.level} character
"""
        
        if player_action:
            prompt += f"""
### PLAYER ACTION ###
The player has chosen to: {player_action}

"""
            
            if combat_trigger_detected:
                prompt += """⚔️ **COMBAT INITIATION REQUIRED** ⚔️
This player action is clearly aggressive and combative. You MUST initiate combat immediately.

MANDATORY COMBAT RESPONSE:
1. Recognize this as a hostile action that provokes combat
2. Describe NPCs/enemies immediately responding with hostility
3. Create an appropriate combat encounter based on the location and context
4. Set up initiative order and begin combat proceedings
5. Include clear combat indicators in your response

CRITICAL: You MUST use these EXACT phrases in your response:
- "Combat begins!" or "Initiative time!" or "Roll for initiative!"
- "The fight starts" or "Battle commences"
- Use words like "hostile", "aggressive", "attacks", "combat"

DO NOT redirect to peaceful resolution. DO NOT have NPCs ignore the aggression.
The player wants combat - give them combat immediately with clear combat language.

"""
            
            prompt += """Narrate the immediate consequences and outcomes of this action. Describe what happens, how NPCs react, what the character observes, and what new challenges emerge.
"""
        else:
            prompt += f"""
### SCENE SETTING ###
Set the scene for this stage of the adventure. Describe the environment, atmosphere, and present the character with meaningful choices or encounters appropriate for the {story_arc.current_stage.value} stage.
"""
        
        if additional_context:
            prompt += f"""
### ADDITIONAL CONTEXT ###
{additional_context}
"""
        
        if combat_trigger_detected:
            prompt += """
### RESPONSE FORMAT ###
Provide a vivid, combat-focused narrative response (2-4 paragraphs) that:
1. Immediately establishes that combat has begun
2. Describes enemy reactions and positions
3. Sets the scene for tactical combat
4. Presents clear combat options for the player
5. Includes phrases like "combat begins", "initiative", "roll for combat", or "the fight starts"

**IMPORTANT**: Your response MUST trigger combat detection by including combat-related keywords and situations.

End with a clear combat scenario and tactical choices for the player.
"""
        else:
            prompt += """
### RESPONSE FORMAT ###
Provide a vivid, immersive narrative response (2-4 paragraphs) that:
1. Describes the scene and atmosphere
2. Shows the consequences of actions (if applicable)
3. Presents clear choices or next steps for the player
4. Maintains consistency with established story elements
5. If the situation becomes hostile, don't hesitate to initiate combat

**INCORPORATE GAME MECHANICS:**
- Suggest ability checks when appropriate (e.g., "This looks like it might require a Strength check")
- Reference the character's equipment and how it affects the situation
- Consider the character's class abilities and how they could be useful
- Mention opportunities for skill usage (stealth, persuasion, investigation, etc.)
- If the character is injured, consider rest or healing opportunities
- Create scenarios that play to the character's strengths or challenge their weaknesses
- Suggest when items from inventory might be useful
- For significant achievements, mention potential XP gains

End with a clear question or choice for the player that incorporates potential stat usage.
"""
        
        # Enhanced combat trigger instructions for aggressive actions
        if combat_trigger_detected:
            prompt += f"""

**IMPORTANT: COMBAT INITIATION DETECTED**
The player has taken an aggressive combat action: "{player_action}"

YOU MUST respond as follows:
1. Describe the immediate combat situation
2. Include the phrase "Combat begins!" or "Initiative time!" or "Roll for initiative!"
3. Set the scene for turn-based combat
4. Indicate what dice rolls are needed (initiative, attack rolls, etc.)

Structure your response to include:
- Immediate reaction to the aggressive action
- Clear indication that combat has started
- Initiative or turn order instructions
- Any immediate effects or damage

Example format:
"[Combat description]... Combat begins! Roll for initiative to determine turn order. [Additional combat details]"
"""
        
        prompt += f"""

### ENVIRONMENTAL ASSESSMENT ###
Current Location Analysis:
- Biome: {self._analyze_biome(story_arc, world_state)}
- Weather Conditions: {self._get_weather_effects()}
- Time of Day: {self._get_time_effects()}
- Interactive Elements: {self._identify_environmental_opportunities()}
- Hidden Secrets: {self._suggest_discovery_opportunities()}

### NPC ENCOUNTER FRAMEWORK ###
For any NPCs in this scene, consider:
- **Personality Archetype**: {self._select_npc_archetype()}
- **Motivation**: What do they want right now?
- **Relationship Potential**: How might they connect to the character's goals/background?
- **Information**: What useful knowledge might they possess?
- **Challenge Level**: Social, combat, or puzzle challenge they might present

### QUEST OPPORTUNITY ANALYSIS ###
Based on current situation and character background:
- **Immediate Hooks**: Problems visible in current scene
- **Background Connections**: How current location relates to character's past
- **Skill Showcases**: Opportunities to use character's best abilities
- **Growth Challenges**: Areas where character could develop
- **Resource Needs**: Equipment, allies, or knowledge character might seek

### WORLD STATE INTEGRATION ###
Consider these world dynamics:
- **Faction Activity**: What groups are active in this area?
- **Economic Situation**: Trade, prosperity, or hardship affecting locals
- **Political Climate**: Authority figures, laws, tensions
- **Recent Events**: How past adventures have affected this region
- **Future Consequences**: How current events might evolve

### ENCOUNTER BALANCE ASSESSMENT ###
For any challenges presented:
- **Character Readiness**: Current HP ({character.current_hit_points}/{character.max_hit_points}), resources, equipment
- **Optimal Challenge**: Neither too easy nor overwhelmingly difficult
- **Multiple Solutions**: Combat, stealth, social, or creative approaches
- **Consequence Clarity**: Player should understand stakes and potential outcomes

### STORY CONTINUITY CHECKS ###
Ensure consistency with:
- **Previous Scenes**: Reference established details and consequences
- **Character Development**: Show growth from past experiences
- **World Logic**: Realistic cause-and-effect relationships
- **Genre Tone**: Maintain appropriate D&D fantasy atmosphere

"""
        
        return prompt

    def _analyze_biome(self, story_arc: StoryArc, world_state: WorldState = None) -> str:
        """Analyze the current biome based on story context"""
        # You can expand this based on your story/world data structure
        default_biomes = ["Temperate Forest", "Mountain Pass", "Coastal Town", "Underground Cavern", "Desert Oasis", "Frozen Wasteland", "Swampland", "Urban Settlement"]
        return "Temperate Forest (Dense canopy, natural cover, wildlife activity)"
    
    def _get_weather_effects(self) -> str:
        """Generate weather conditions and their mechanical effects"""
        import random
        weather_options = [
            "Clear skies (Normal visibility, no penalties)",
            "Light rain (Disadvantage on Perception checks relying on sight)",
            "Heavy rain (Heavily obscured beyond 100 feet)",
            "Fog (Lightly obscured, Disadvantage on Wisdom (Perception) checks)",
            "Strong wind (Disadvantage on ranged weapon attacks)",
            "Snow (Difficult terrain, tracks easily visible)"
        ]
        return random.choice(weather_options)
    
    def _get_time_effects(self) -> str:
        """Generate time of day effects"""
        import random
        time_options = [
            "Dawn (Dim light, creatures stirring)",
            "Morning (Bright light, normal activity)",
            "Midday (Bright light, peak activity)",
            "Afternoon (Bright light, winding down)",
            "Dusk (Dim light, nocturnal creatures emerging)",
            "Night (Darkness, advantage for stealth)"
        ]
        return random.choice(time_options)
    
    def _identify_environmental_opportunities(self) -> str:
        """Identify interactive elements in the environment"""
        opportunities = [
            "Climbable trees for vantage points",
            "Dense undergrowth for hiding",
            "Stream for water and tracking",
            "Rocky outcroppings for cover",
            "Animal trails to follow"
        ]
        return ", ".join(opportunities[:3])  # Return 3 random opportunities
    
    def _suggest_discovery_opportunities(self) -> str:
        """Suggest hidden secrets or discoveries"""
        secrets = [
            "Hidden cache of supplies",
            "Ancient ruins partially buried",
            "Secret passage behind vegetation",
            "Abandoned campsite with clues",
            "Rare herbs or materials"
        ]
        import random
        return random.choice(secrets)
    
    def _select_npc_archetype(self) -> str:
        """Select an appropriate NPC archetype"""
        archetypes = [
            "Helpful Guide (knows local area)",
            "Mysterious Stranger (hidden agenda)",
            "Merchant Trader (has useful goods)",
            "Fellow Adventurer (potential ally)",
            "Local Authority (law enforcement)",
            "Wise Elder (knowledge and advice)",
            "Desperate Refugee (needs help)"
        ]
        import random
        return random.choice(archetypes)
    
    def _get_quest_hooks_by_background(self, background: str) -> str:
        """Generate quest hooks based on character background"""
        background_hooks = {
            "acolyte": "Religious mysteries, temple politics, divine quests, protecting faith",
            "criminal": "Past crimes resurface, underworld connections, redemption opportunities",
            "folk hero": "Community needs protection, innocent people in danger, growing reputation",
            "noble": "Family obligations, political intrigue, maintaining honor, court dynamics",
            "sage": "Ancient knowledge needed, research opportunities, scholarly pursuits",
            "soldier": "Military missions, veteran bonds, consequences of war, tactical challenges",
            "hermit": "Spiritual journeys, natural harmony, isolated wisdom, environmental threats",
            "entertainer": "Performance opportunities, cultural events, artistic challenges, fame management"
        }
        return background_hooks.get(background.lower(), "Personal growth, skill challenges, social encounters")
    
    def _assess_tactical_situation(self, character: Character) -> str:
        """Assess character's tactical strengths for encounter design"""
        tactical_notes = []
        
        # Combat assessment
        if character.armor_class >= 16:
            tactical_notes.append("Well-armored frontline fighter")
        elif character.dexterity >= 14:
            tactical_notes.append("Mobile skirmisher or ranged combatant")
        else:
            tactical_notes.append("Support role or tactical thinker")
        
        # Social assessment
        if character.charisma >= 14:
            tactical_notes.append("Strong social interaction capabilities")
        
        # Mental assessment
        if character.intelligence >= 14:
            tactical_notes.append("Problem-solving and investigation specialist")
        elif character.wisdom >= 14:
            tactical_notes.append("Perceptive and intuitive decision maker")
        
        # Physical assessment
        if character.strength >= 14:
            tactical_notes.append("Physical challenges and athletics specialist")
        
        return "; ".join(tactical_notes)
    
    def _generate_encounter_suggestions(self, character: Character) -> str:
        """Generate specific encounter types based on character capabilities"""
        suggestions = []
        
        # Based on strong abilities
        if character.strength >= 14:
            suggestions.append("Physical obstacles requiring strength (breaking barriers, lifting objects)")
        if character.dexterity >= 14:
            suggestions.append("Agility challenges (climbing, acrobatics, stealth scenarios)")
        if character.intelligence >= 14:
            suggestions.append("Puzzles, riddles, or research opportunities")
        if character.wisdom >= 14:
            suggestions.append("Tracking, survival challenges, or insight-based social encounters")
        if character.charisma >= 14:
            suggestions.append("Negotiation, performance, or leadership opportunities")
        if character.constitution >= 14:
            suggestions.append("Endurance challenges or poison/disease resistance scenarios")
        
        # Based on low HP
        if character.current_hit_points < character.max_hit_points * 0.5:
            suggestions.append("Opportunities for rest, healing, or non-combat solutions")
        
        # Based on class (if available)
        if hasattr(character, 'character_class'):
            class_suggestions = {
                'fighter': "Combat encounters showcasing martial prowess",
                'wizard': "Magical mysteries requiring arcane knowledge",
                'rogue': "Stealth missions, traps, or social infiltration",
                'cleric': "Divine guidance scenarios, healing opportunities, undead encounters",
                'ranger': "Wilderness navigation, tracking, natural environment challenges",
                'bard': "Social encounters, performance opportunities, information gathering"
            }
            class_suggestion = class_suggestions.get(character.character_class.lower())
            if class_suggestion:
                suggestions.append(class_suggestion)
        
        return "; ".join(suggestions) if suggestions else "Balanced encounters testing multiple abilities"


class CombatNarrationTemplate(AIPromptTemplate):
    """Template for combat narration and descriptions"""
    
    def __init__(self):
        super().__init__("combat_narration")


class NPCInteractionTemplate(AIPromptTemplate):
    """Template for NPC dialogue and interactions"""
    
    def __init__(self):
        super().__init__("npc_interaction")


class DecisionOutcomeTemplate(AIPromptTemplate):
    """Template for major decision outcomes and consequences"""
    
    def __init__(self):
        super().__init__("decision_outcome")


class AIService:
    """Main AI service for GPT-4o integration"""
    
    def __init__(self, api_key: str = None):
        try:
            self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        except Exception:
            self.client = None  # Will handle gracefully in generate_response
        self.model = "gpt-4.1-mini-2025-04-14"
        self.templates = {
            'story': StoryNarrationTemplate(),
            'combat': CombatNarrationTemplate(),
            'npc': NPCInteractionTemplate(),
            'decision': DecisionOutcomeTemplate()
        }
    
    def generate_response(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate AI response using the configured model"""
        if not self.client:
            print(f"❌ OpenAI client not initialized - API key missing")
            return {
                'success': False,
                'error': 'OpenAI client not initialized - API key missing',
                'content': None
            }
        
        try:
            print(f"🤖 Making OpenAI API call with model: {self.model}")
            print(f"📝 Prompt length: {len(prompt)} characters")
            print(f"⚙️ Settings: max_tokens={max_tokens}, temperature={temperature}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Dungeon Master creating an immersive solo D&D experience."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            content = response.choices[0].message.content
            print(f"✅ OpenAI API response received successfully")
            print(f"📄 Response length: {len(content) if content else 0} characters")
            print(f"🔢 Token usage: {response.usage.total_tokens} total tokens")
            
            if not content or len(content.strip()) == 0:
                print(f"⚠️ OpenAI returned empty content!")
                return {
                    'success': False,
                    'error': 'OpenAI returned empty content',
                    'content': None
                }
            
            return {
                'success': True,
                'content': content,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                'model': response.model
            }
        
        except Exception as e:
            print(f"❌ OpenAI API error: {str(e)}")
            print(f"🔍 Error type: {type(e).__name__}")
            return {
                'success': False,
                'error': str(e),
                'content': None
            }

    def narrate_story(self, db, character_id: int, story_arc_id: int, 
                     player_action: str = None, additional_context: str = None) -> Dict[str, Any]:
        """Generate story narration based on character, story, and player action"""
        try:
            from models.character import Character
            from models.story import StoryArc, WorldState
            
            # Get character
            character = db.query(Character).filter(Character.id == character_id).first()
            if not character:
                return {
                    'success': False,
                    'error': 'Character not found',
                    'content': None
                }
            
            # Get story arc
            story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
            if not story_arc:
                return {
                    'success': False,
                    'error': 'Story arc not found',
                    'content': None
                }
            
            # Get world state (optional)
            world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
            
            # Build prompt using story template
            story_template = self.templates['story']
            prompt = story_template.build_prompt(
                character=character,
                story_arc=story_arc,
                world_state=world_state,
                player_action=player_action,
                additional_context=additional_context
            )
            
            # Generate AI response
            return self.generate_response(prompt, max_tokens=500, temperature=0.8)
            
        except Exception as e:
            print(f"❌ Error in narrate_story: {str(e)}")
            return {
                'success': False,
                'error': f'Error generating story narration: {str(e)}',
                'content': None
            }

    def narrate_combat(self, db, character_id: int, story_arc_id: int, 
                      combat_encounter_id: int, combat_action: Dict[str, Any], 
                      combat_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate combat narration for actions and results"""
        try:
            from models.character import Character
            from models.story import StoryArc
            
            # Get character
            character = db.query(Character).filter(Character.id == character_id).first()
            if not character:
                return {
                    'success': False,
                    'error': 'Character not found',
                    'content': None
                }
            
            # Get story arc for context
            story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
            if not story_arc:
                return {
                    'success': False,
                    'error': 'Story arc not found',
                    'content': None
                }
            
            # Build combat narration prompt
            prompt = f"""
You are narrating a D&D combat encounter for {character.name}, a level {character.level} {character.race} {character.character_class}.

COMBAT ACTION:
{combat_action.get('description', 'Unknown action')}

COMBAT RESULT:
- Success: {combat_result.get('success', False)}
- Damage Dealt: {combat_result.get('damage_dealt', 0)}
- Damage Taken: {combat_result.get('damage_taken', 0)}
- Status Effects: {combat_result.get('status_effects', [])}

CHARACTER STATE:
- Current HP: {character.current_hit_points}/{character.max_hit_points}
- AC: {character.armor_class}

Provide a vivid, exciting narration of this combat action and its results. Focus on:
1. The dramatic execution of the action
2. The visual and auditory effects
3. The impact on enemies and the battlefield
4. Any tactical changes or new opportunities

Keep the narration to 2-3 paragraphs and maintain high energy and excitement.
"""
            
            return self.generate_response(prompt, max_tokens=400, temperature=0.8)
            
        except Exception as e:
            print(f"❌ Error in narrate_combat: {str(e)}")
            return {
                'success': False,
                'error': f'Error generating combat narration: {str(e)}',
                'content': None
            }

    def handle_npc_interaction(self, db, character_id: int, story_arc_id: int, 
                              npc_name: str, interaction_type: str, player_input: str) -> Dict[str, Any]:
        """Generate NPC dialogue and reactions"""
        try:
            from models.character import Character
            from models.story import StoryArc
            
            # Get character
            character = db.query(Character).filter(Character.id == character_id).first()
            if not character:
                return {
                    'success': False,
                    'error': 'Character not found',
                    'content': None
                }
            
            # Get story arc for context
            story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
            if not story_arc:
                return {
                    'success': False,
                    'error': 'Story arc not found',
                    'content': None
                }
            
            # Build NPC interaction prompt
            npc_status = story_arc.npc_status or {}
            npc_info = npc_status.get(npc_name, {})
            
            prompt = f"""
You are roleplaying as {npc_name}, an NPC in a D&D adventure.

NPC STATUS:
- Disposition: {npc_info.get('disposition', 'neutral')}
- Health: {npc_info.get('health', 'healthy')}
- Current Status: {npc_info.get('status', 'present')}

PLAYER CHARACTER:
- Name: {character.name}
- Race/Class: {character.race} {character.character_class}
- Background: {character.background}

STORY CONTEXT:
- Current Stage: {story_arc.current_stage.value}
- Location: {story_arc.current_stage.value}

INTERACTION TYPE: {interaction_type}

PLAYER INPUT: "{player_input}"

Respond as {npc_name} would, considering:
1. Their current disposition toward the character
2. The type of interaction (dialogue, persuasion, etc.)
3. The current story context and location
4. Their personality and motivations

Provide the NPC's response in 1-2 paragraphs, including dialogue and any actions they take.
Format dialogue with quotes and describe actions in italics.
"""
            
            return self.generate_response(prompt, max_tokens=300, temperature=0.8)
            
        except Exception as e:
            print(f"❌ Error in handle_npc_interaction: {str(e)}")
            return {
                'success': False,
                'error': f'Error generating NPC interaction: {str(e)}',
                'content': None
            }

    def process_decision_outcome(self, db, character_id: int, story_arc_id: int, 
                               decision: Dict[str, Any]) -> Dict[str, Any]:
        """Generate narration for decision consequences"""
        try:
            from models.character import Character
            from models.story import StoryArc, WorldState
            
            # Get character
            character = db.query(Character).filter(Character.id == character_id).first()
            if not character:
                return {
                    'success': False,
                    'error': 'Character not found',
                    'content': None
                }
            
            # Get story arc
            story_arc = db.query(StoryArc).filter(StoryArc.id == story_arc_id).first()
            if not story_arc:
                return {
                    'success': False,
                    'error': 'Story arc not found',
                    'content': None
                }
            
            # Get world state for context
            world_state = db.query(WorldState).filter(WorldState.story_arc_id == story_arc_id).first()
            
            # Build decision outcome prompt
            prompt = f"""
You are narrating the consequences of a major decision in a D&D adventure.

CHARACTER: {character.name}, level {character.level} {character.race} {character.character_class}

DECISION MADE:
- Title: {decision.get('title', 'Unknown Decision')}
- Description: {decision.get('description', 'No description')}
- Choice: {decision.get('choice', 'Unknown choice')}

STORY CONTEXT:
- Current Stage: {story_arc.current_stage.value}
- Story Title: {story_arc.title}
{f"- Current Location: {world_state.current_location}" if world_state else ""}

Narrate the immediate and potential long-term consequences of this decision. Consider:
1. How the world and NPCs react
2. What opportunities open or close
3. Any immediate changes to the situation
4. Foreshadowing of future implications

Provide a compelling narrative in 2-3 paragraphs that shows the weight and impact of the character's choice.
"""
            
            return self.generate_response(prompt, max_tokens=400, temperature=0.7)
            
        except Exception as e:
            print(f"❌ Error in process_decision_outcome: {str(e)}")
            return {
                'success': False,
                'error': f'Error generating decision outcome: {str(e)}',
                'content': None
            }

    def generate_dynamic_content(self, prompt_type: str, custom_prompt: str, 
                               max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate custom AI content from prompts"""
        try:
            # Add context based on prompt type
            system_context = "You are an expert Dungeon Master creating immersive D&D content."
            
            if prompt_type == "location":
                system_context = "You are creating detailed location descriptions for D&D adventures."
            elif prompt_type == "item":
                system_context = "You are creating interesting items and treasures for D&D adventures."
            elif prompt_type == "quest":
                system_context = "You are designing engaging quests and objectives for D&D adventures."
            elif prompt_type == "npc":
                system_context = "You are creating memorable NPCs for D&D adventures."
            
            # Use a modified system message based on type
            modified_prompt = f"{system_context}\n\n{custom_prompt}"
            
            return self.generate_response(modified_prompt, max_tokens=max_tokens, temperature=temperature)
            
        except Exception as e:
            print(f"❌ Error in generate_dynamic_content: {str(e)}")
            return {
                'success': False,
                'error': f'Error generating dynamic content: {str(e)}',
                'content': None
            }

# Global AI service instance
ai_service = AIService() 