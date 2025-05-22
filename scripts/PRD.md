**Product Requirements Document (PRD)**

**Product Name**: *SoloRealms* (working title)
**Description**: A web-based, AI-powered solo Dungeons & Dragons-style game where GPT-4o acts as the Dungeon Master. Designed for all players, from beginners to hardcore fans, the game features short adventures and campaign-length narratives with turn-based combat, world exploration, and story-driven quests.

---

## 1. Goals

* Deliver an immersive solo D\&D-style game experience.
* Use GPT-4o to simulate a Dungeon Master with full 5e rules.
* Focus MVP on narrative consistency, combat mechanics, and a smooth onboarding experience.
* Support text-based interaction with some visual UI elements (items, maps, scenes).

---

## 2. Target Audience

* Total beginners to veteran D\&D players.
* People who want to play D\&D solo.
* Users looking for short, engaging fantasy RPG experiences.

---

## 3. Key MVP Features

### 3.1. Core Gameplay

* Solo play only.
* AI-driven DM (GPT-4o) using 5e rules.
* Choose short-form or campaign-length stories.
* Character creation: roll stats, pick race/class.
* Turn-based combat system using initiative and stat-based rolls.
* Players can attack, cast spells, or interact.
* No re-rolls or respawn (Permadeath mode for MVP).

### 3.2. Story & Progression

* Structured story arcs (\~30 min for short adventures).
* Backend-managed story state machine:

  * Stages: Intro, Inciting Incident, First Combat, Twist, Final Conflict, Resolution
  * Track major decisions, combat outcomes, and NPC status.
* Dynamic AI-driven world building as users explore.
* Inventory, XP, and leveling handled by backend.

### 3.3. Visuals & UI

* Text-driven interface (chat-like interaction).
* Images for scenes, items, maps.
* UI for character sheet, combat HUD, item/inventory panel.

### 3.4. Technical

* Frontend: Next.js (hosted on Vercel)
* Backend: FastAPI (hosted on Fly.io or Render)
* Auth: Clerk
* Database: Neon (PostgreSQL)

  * Characters
  * World state
  * Campaign/story arc state
  * Enemy templates
* Memory Layer: Redis

  * Active combat state
  * Recent turns
  * NPCs in play

### 3.5. AI Prompting

* GPT-4o as AI Dungeon Master.
* Backend rolls dice and resolves mechanics.
* AI receives structured prompt:

  * Story state chunk
  * Combat result details
  * Player actions
  * World state summary
* Chained prompts with summary compression for long sessions.
* AI tone and personality is user-set.

---

## 4. MVP Exclusions (Planned for Future Features)

* Multiplayer
* Save/load game states
* Campaign world persistence between sessions
* Playing other users' campaigns
* Social layers / community sharing
* Magic items
* Character resurrection/respawn
* Visible story logs and annotations

---

## 5. Monetization

* Freemium model
* Free access to test game and early story
* Premium features TBD (e.g., longer campaigns, character classes, skins)

---

## 6. Prioritization

### P0 (Must Have for MVP)

* AI DM logic with GPT-4o + backend roll resolution
* Character creation
* Turn-based combat with initiative
* 30-minute one-shot adventure arc with 1-2 battles and moral dilemma
* Text interaction UI with image rendering
* World building on demand
* Neon + Redis integration

### P1 (Post-MVP Additions)

* Game state saving and loading
* Full-length campaigns with persistent world
* Magic items and equipment upgrades
* Player-set story seeds or plot types

### P2 (Stretch Features / Long-Term)

* Community campaign sharing
* Multiplayer cooperative sessions
* Character export/import
* Dynamic rule mods (homebrew)

---

## 7. Open Questions

* How should long-term campaign memory be compressed?
* Should players be able to reroll or retry combat in future non-permadeath modes?
* What tools will be used for content moderation, if any?

---

## 8. Next Steps

* Prototype FastAPI backend: dice rolls, combat resolution, prompt formatter.
* Finalize structured prompt format.
* Design schema for Neon (characters, story arcs, world elements).
* Build frontend skeleton in Next.js with Clerk auth.
* Test AI outputs with real player input and backend-generated results.

---

## Appendix: Story State Machine Structure (Short Form)

1. **Intro**

   * Establish location, motivation
2. **Inciting Incident**

   * Conflict is introduced
3. **First Combat Encounter**

   * Small-scale battle
4. **Discovery / Twist**

   * Secret or surprise element
5. **Final Conflict**

   * Boss fight or moral choice
6. **Resolution**

   * Epilogue / reward / failure consequences
