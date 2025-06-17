# SoloRealms Tutorial Guide
*A Complete Guide to AI-Powered D&D Adventures*

## Table of Contents
1. [Getting Started](#getting-started)
2. [Combat System](#combat-system)
3. [Character Management](#character-management)
4. [Authentication & Features](#authentication--features)
5. [Advanced Features](#advanced-features)

---

## Getting Started

### Welcome to SoloRealms
![Homepage](screenshot-01-homepage.png)

SoloRealms is an AI-powered solo D&D experience that brings epic adventures to life. The homepage showcases the core features:

- **AI Dungeon Master**: Experience dynamic storytelling with an AI DM that adapts to your choices
- **Epic Combat**: Engage in tactical turn-based combat with full D&D 5e rules
- **Rich Stories**: 30-minute adventures that fit into your schedule, with deeper campaigns available
- **Character Creation**: Build unique characters with D&D stats and abilities
- **Permadeath Stakes**: High-stakes gameplay where choices matter
- **Solo Play**: Perfect for solo gaming sessions

### Authentication Flow
![Authentication Modal](screenshot-02-after-start-adventure-click.png)

When you click "Start Your Adventure", SoloRealms uses Clerk authentication to secure your gaming experience. The system supports:

- **Google Sign-In**: Quick authentication with your Google account
- **Email Authentication**: Traditional email/password login
- **Secure Sessions**: Your characters and progress are safely stored
- **Development Mode**: Clear indication when in development environment

---

## Combat System

### Combat Overview
![Combat Test Interface](screenshot-03-combat-test-page.png)

SoloRealms features a comprehensive turn-based combat system built on D&D 5e rules:

- **State Machine**: XState-powered combat flow ensures consistent turn management
- **Initiative System**: Automatic initiative rolling determines turn order
- **Player/Enemy Panels**: Clear separation of allies and enemies
- **Combat Controls**: Easy-to-use buttons for starting combat, selecting actions, and managing turns

### Combat in Action
![Active Combat](screenshot-04-combat-started.png)

Once combat begins, you'll see:

- **Turn Indicators**: Current player's turn is highlighted (green for players, red for enemies)
- **Health Bars**: Animated health bars with real-time damage updates
- **Initiative Values**: Each combatant's initiative score displayed
- **Round Tracking**: Current round and turn index clearly shown
- **Combat State**: Visual feedback on whose turn it is

### Action Selection
![Action Selection Modal](screenshot-05-action-selection.png)

The action selection system provides comprehensive D&D combat options:

- **Action Categories**: 
  - **ACTION** (12 available): Primary combat actions like attacks and spells
  - **BONUS ACTION** (3 available): Quick secondary actions
  - **MOVEMENT** (2 available): Positioning and movement options
  - **REACTION** (1 available): Defensive responses
  - **FREE** (0 available): Minor actions that don't consume action economy

- **Detailed Information**: Each action shows damage, range, and description
- **Visual Feedback**: Clear icons and color coding for different action types

### Action Confirmation
![Action Confirmation](screenshot-07-after-action-click.png)

Before executing actions, the system provides:

- **Action Preview**: Confirmation of the selected action (e.g., "Use Melee Attack?")
- **Clear Buttons**: Confirm or Cancel options
- **Action Details**: Reminder of what the action does

### Target Selection
![Target Selection](screenshot-09-target-selection-actual.png)

For targeted actions, the interface shows:

- **Available Targets**: All valid targets highlighted with red borders for enemies
- **Health Information**: Current HP and percentage for each target
- **Range Validation**: Only targets within range are selectable
- **Clear Instructions**: "Choose a target (2 available)" with range information
- **Target Details**: AC (Armor Class) and enemy type clearly displayed

### Combat Results
![Combat Results](screenshot-11-combat-with-log.png)

After actions resolve, you can see:

- **Damage Applied**: Health bars update with smooth animations (Orc Brute: 11/15 HP, 73%)
- **Turn Progression**: Combat automatically advances to the next participant
- **Visual Feedback**: Damaged enemies show yellow/orange health bars
- **State Updates**: Combat state clearly indicates whose turn is next

### Initiative Order & Combat Log
![Initiative and Combat Log](screenshot-12-combat-log-visible.png)

The complete combat interface includes:

- **Initiative Order Panel**: 
  - Shows turn order with initiative values in parentheses
  - Current turn highlighted in green (Thorin the Fighter)
  - Clear numbering: 1. Aria (14), 2. Thorin (8), 3. Orc Brute (6), 4. Goblin Warrior (3)

- **Combat Log**: 
  - Real-time action logging with timestamps
  - Detailed action descriptions: "Aria the Rogue used Melee Attack on Orc Brute"
  - Damage indicators with weapon icons
  - Scrollable history of all combat actions
  - Settings panel for customizing log display

---

## Character Management

### Character Creation Flow
![Character Creation](screenshot-13-character-creation.png)

SoloRealms provides a comprehensive character creation system:

- **Secure Authentication**: Character data is protected by Clerk authentication
- **D&D 5e Compatible**: Full support for official D&D races, classes, and stats
- **Stat Generation**: Multiple methods for generating ability scores
- **Background & Personality**: Rich character development options

---

## Authentication & Features

### Protected Content
![Dashboard Authentication](screenshot-14-dashboard.png)

Most SoloRealms features require authentication to ensure:

- **Character Persistence**: Your characters are saved securely
- **Adventure History**: Track your completed quests and campaigns
- **Progress Tracking**: Save game states and continue where you left off
- **Personalized Experience**: AI learns from your choices and preferences

### Authentication Options
![Google Sign-In Flow](screenshot-15-after-email-entry.png)

The authentication system supports:

- **Google Integration**: "Sign in with Google" for quick access
- **Email Authentication**: Traditional email/password combination
- **Account Management**: Full profile and preference controls
- **Privacy Protection**: Clerk's enterprise-grade security

---

## Advanced Features

### Technical Highlights

**Combat Engine**:
- XState-powered state machine for deterministic combat flow
- Immutable state management with Immer
- Deterministic RNG for reproducible results
- Web Worker integration for performance

**UI/UX Excellence**:
- Framer Motion animations for smooth interactions
- React Spring physics-based effects
- Virtualized combat logging for performance
- Responsive design for all screen sizes

**AI Integration**:
- GPT-4o powered dungeon master
- Dynamic story adaptation based on player choices
- Context-aware narrative generation
- Redis-cached game state for fast responses

**Data Management**:
- PostgreSQL database with Neon hosting
- Alembic migrations for schema management
- FastAPI backend with async support
- Comprehensive test coverage

### Getting Started Checklist

1. **Visit SoloRealms**: Navigate to the application homepage
2. **Sign Up/Sign In**: Use Google or email authentication
3. **Create Character**: Build your D&D character with stats and background
4. **Start Adventure**: Choose your adventure type and begin your quest
5. **Master Combat**: Learn the turn-based combat system
6. **Explore Features**: Discover character management, adventure history, and settings

### Tips for New Players

- **Start Simple**: Begin with the combat test page to learn the mechanics
- **Read Tooltips**: Hover over actions and abilities for detailed information
- **Use the Log**: The combat log tracks all actions for review
- **Save Progress**: Your adventure state is automatically saved
- **Experiment**: Try different character builds and combat strategies

---

## Support & Resources

For additional help:
- **In-App Help**: Use the help sections within the application
- **Community**: Join other players for tips and strategies
- **Bug Reports**: Report issues through the support system
- **Feature Requests**: Suggest improvements and new features

---

*SoloRealms - Experience epic D&D adventures powered by AI* 