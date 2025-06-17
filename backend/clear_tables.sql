-- SoloRelms Database Cleanup Script
-- This script clears all tables except the users table
-- Run this in your Supabase SQL editor for a quick cleanup

-- Disable foreign key constraints temporarily
SET session_replication_role = replica;

-- Clear tables in order (dependent tables first)
DELETE FROM quest_objective_progress;
DELETE FROM character_quests;
DELETE FROM quest_rewards;
DELETE FROM quest_objectives;
DELETE FROM combat_participants;
DELETE FROM combat_encounters;
DELETE FROM world_states;
DELETE FROM timeline_events;
DELETE FROM discoveries;
DELETE FROM journal_entries;
DELETE FROM quests;
DELETE FROM enemy_templates;
DELETE FROM story_arcs;
DELETE FROM characters;

-- Re-enable foreign key constraints
SET session_replication_role = DEFAULT;

-- Verify users table is preserved
SELECT COUNT(*) as users_remaining FROM users;

-- Verify other tables are empty
SELECT 
  'characters' as table_name, COUNT(*) as remaining_rows FROM characters
UNION ALL
SELECT 
  'story_arcs' as table_name, COUNT(*) as remaining_rows FROM story_arcs
UNION ALL
SELECT 
  'quests' as table_name, COUNT(*) as remaining_rows FROM quests
UNION ALL
SELECT 
  'journal_entries' as table_name, COUNT(*) as remaining_rows FROM journal_entries; 