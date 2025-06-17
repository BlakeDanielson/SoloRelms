# SoloRealms MVP Manual Testing Guide 🎮

## Overview
This guide provides comprehensive manual testing procedures for the SoloRealms D&D MVP, focusing on end-to-end user journeys and scenarios not covered by automated testing.

## Testing Environment Setup

### Prerequisites
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3003`
- Redis server running (tested via `/api/redis/health`)
- PostgreSQL database connected (tested via `/health/database`)

### Test Data Requirements
- Valid Clerk JWT token for authentication testing
- Test user accounts with various permission levels
- Sample character data for different races/classes
- Test story scenarios and combat encounters

## Manual Test Categories

### 1. Authentication Flow Testing 🔐

#### Test 1.1: User Registration and Login
**Objective**: Validate complete authentication process

**Steps**:
1. Navigate to frontend sign-up page (`/sign-up`)
2. Create new account with valid email/password
3. Verify email confirmation process
4. Login with new credentials
5. Verify JWT token generation and storage
6. Test token refresh mechanism

**Expected Results**:
- Account created successfully
- Email verification sent and processed
- JWT token properly issued and stored
- User redirected to dashboard after login

**Test Data**:
```
Email: test-manual@solorealms.com
Password: TestPassword123!
```

#### Test 1.2: Authentication Error Handling
**Objective**: Validate error scenarios

**Steps**:
1. Attempt login with invalid credentials
2. Test with malformed email address
3. Test with weak password
4. Test with expired JWT token
5. Test API calls without authentication

**Expected Results**:
- Clear error messages displayed
- Appropriate HTTP status codes returned
- User guided to correct actions

### 2. Character Creation Journey 🧙‍♂️

#### Test 2.1: Complete Character Creation
**Objective**: Test full character creation workflow

**Pre-conditions**: User authenticated

**Steps**:
1. Navigate to character creation (`/character/create`)
2. Select race from available options (14 races available)
3. Select class from available options (13 classes available)
4. Select background from available options (12 backgrounds available)
5. Assign ability scores (manual entry or roll stats)
6. Set character name and description
7. Submit character creation form
8. Verify character appears in character list

**Expected Results**:
- All D&D 5e options available and functional
- Ability score calculations correct
- Character successfully created in database
- Character accessible from dashboard

**Test Matrix**:
```
Race Options: Human, Elf, Dwarf, Halfling, Dragonborn, Gnome, 
              Half-Elf, Half-Orc, Tiefling, Aasimar, Genasi, 
              Goliath, Tabaxi, Firbolg

Class Options: Barbarian, Bard, Cleric, Druid, Fighter, Monk, 
               Paladin, Ranger, Rogue, Sorcerer, Warlock, 
               Wizard, Artificer

Background Options: Acolyte, Criminal, Folk Hero, Noble, Sage, 
                   Soldier, Charlatan, Entertainer, Guild Artisan, 
                   Hermit, Outlander, Sailor
```

#### Test 2.2: Character Stat Validation
**Objective**: Ensure character stats are calculated correctly

**Steps**:
1. Create character with specific ability scores
2. Verify ability modifiers calculated correctly
3. Check proficiency bonus based on level
4. Validate saving throw bonuses
5. Confirm skill bonuses
6. Test hit point calculation

**Test Cases**:
```
Strength 15 → Modifier +2
Dexterity 14 → Modifier +2  
Constitution 13 → Modifier +1
Intelligence 12 → Modifier +1
Wisdom 10 → Modifier +0
Charisma 8 → Modifier -1

Level 1 → Proficiency Bonus +2
```

### 3. Story Generation and Progression 📚

#### Test 3.1: Story Arc Creation
**Objective**: Test AI-driven story generation

**Pre-conditions**: Character created and selected

**Steps**:
1. Navigate to story creation
2. Select story type (short_form, medium_form, long_form)
3. Choose genre preference
4. Set complexity level
5. Submit story generation request
6. Wait for AI processing (may take 30-60 seconds)
7. Review generated story arc

**Expected Results**:
- Story generated within reasonable time
- Story quality appropriate for D&D setting
- Story matches selected parameters
- Story stored in database with correct associations

**Test Data**:
```
Story Types: short_form, medium_form, long_form
Genres: classic_fantasy, dark_fantasy, high_fantasy, urban_fantasy
Complexity: simple, moderate, complex
```

#### Test 3.2: Story Progression
**Objective**: Test story advancement mechanics

**Steps**:
1. Start with generated story
2. Read opening scene
3. Make character decisions
4. Observe story branching
5. Test save/load functionality
6. Verify story state persistence

### 4. Combat System Testing ⚔️

#### Test 4.1: Combat Encounter Creation
**Objective**: Validate combat mechanics

**Steps**:
1. Enter combat scenario from story
2. Verify combat HUD display
3. Check initiative order
4. Test attack rolls using dice system
5. Verify damage calculation
6. Test healing mechanics
7. Check status effect application

**Expected Results**:
- Combat interface responsive and clear
- Dice rolls fair and properly calculated
- Damage/healing applied correctly
- Turn order maintained properly

#### Test 4.2: Dice Rolling Validation
**Objective**: Test dice system accuracy

**Manual Verification** (supplement to automated tests):
```
d20 + 5 modifier → Result between 6-25
d12 + 0 modifier → Result between 1-12
d10 - 2 modifier → Result between -1-8
d8 + 3 modifier → Result between 4-11
d6 + 1 modifier → Result between 2-7
d4 + 0 modifier → Result between 1-4
```

**Steps**:
1. Roll each die type multiple times
2. Verify results within expected ranges
3. Check modifier application
4. Test advantage/disadvantage mechanics
5. Validate critical hit/failure detection

### 5. Session Management Testing 🎮

#### Test 5.1: Game Session Persistence
**Objective**: Ensure game state preservation

**Steps**:
1. Start game session
2. Make progress through story
3. Exit application/browser
4. Return and resume session
5. Verify all progress maintained
6. Check Redis session storage

**Expected Results**:
- Session state preserved across browser sessions
- Character progress maintained
- Story position remembered
- Combat state restored if applicable

#### Test 5.2: Multi-Session Handling
**Objective**: Test concurrent session management

**Steps**:
1. Open multiple browser tabs
2. Start different characters/stories
3. Switch between sessions
4. Verify session isolation
5. Test session timeout handling

### 6. Performance and User Experience Testing 🚀

#### Test 6.1: Load Time Validation
**Objective**: Ensure responsive user experience

**Performance Benchmarks**:
```
Page Load Times (Target < 3 seconds):
- Dashboard: ___ seconds
- Character Creation: ___ seconds  
- Story Generation: ___ seconds
- Combat Interface: ___ seconds

API Response Times (Target < 500ms):
- Character Options: ___ ms
- Dice Rolling: ___ ms
- Redis Health: ___ ms
- Database Health: ___ ms
```

#### Test 6.2: Cross-Browser Compatibility
**Objective**: Ensure consistent experience across browsers

**Test Matrix**:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

**Test Areas**:
- Authentication flow
- Character creation UI
- Dice rolling animations
- Story text rendering
- Combat interface layout

### 7. Edge Case and Error Handling Testing 🔍

#### Test 7.1: Network Interruption Handling
**Objective**: Test system resilience

**Steps**:
1. Start game session
2. Disconnect network during story generation
3. Reconnect and observe behavior
4. Test with partial data transmission
5. Verify error recovery mechanisms

#### Test 7.2: Invalid Input Handling
**Objective**: Ensure robust input validation

**Test Cases**:
```
Character Creation:
- Empty name field
- Special characters in name
- Extremely long names (>100 chars)
- Invalid ability scores (<3 or >20)
- Negative values

Story Generation:
- Missing required fields
- Invalid enum values
- Extremely long custom inputs
```

#### Test 7.3: Database Connection Loss
**Objective**: Test graceful degradation

**Steps**:
1. Simulate database connection loss
2. Attempt character operations
3. Verify appropriate error messages
4. Test Redis fallback functionality
5. Validate reconnection handling

### 8. API Integration Testing 🔗

#### Test 8.1: Backend API Validation
**Objective**: Comprehensive API testing

**Core Endpoints to Test**:
```
Health Checks:
GET /health
GET /health/database
GET /api/redis/health

Character Management:
GET /api/characters/options
POST /api/characters/roll-stats
POST /api/characters (requires auth)
GET /api/characters (requires auth)

Game Mechanics:
POST /api/dice/simple
GET /api/redis/statistics
POST /api/redis/cleanup/expired-sessions

Session Management:
POST /api/redis/session/create
GET /api/redis/session/{id}
```

#### Test 8.2: Authentication API Testing
**Objective**: Validate auth-protected endpoints

**Test with Valid JWT**:
- Character creation/retrieval
- Story arc management
- Combat encounters
- User profile operations

**Test with Invalid/Expired JWT**:
- Verify 401/403 responses
- Check error message clarity
- Validate redirect behavior

### 9. Data Integrity Testing 💾

#### Test 9.1: Database Consistency
**Objective**: Ensure data relationships maintained

**Steps**:
1. Create character with specific stats
2. Generate story for character
3. Start combat encounter
4. Verify all foreign key relationships
5. Check data consistency across operations

#### Test 9.2: Cache Synchronization
**Objective**: Validate Redis-Database sync

**Steps**:
1. Create data via API
2. Verify Redis cache population
3. Clear cache manually
4. Verify cache repopulation
5. Test cache invalidation mechanisms

## Test Execution Checklist

### Pre-Testing Setup
- [ ] Backend server running and healthy
- [ ] Frontend application accessible
- [ ] Redis server operational
- [ ] Database connection verified
- [ ] Test user accounts available
- [ ] Automated tests passing (10/10)

### During Testing
- [ ] Document all observations
- [ ] Screenshot UI issues
- [ ] Record performance metrics
- [ ] Note browser/environment details
- [ ] Track error messages and stack traces

### Post-Testing
- [ ] Categorize findings by severity
- [ ] Create detailed bug reports
- [ ] Update test cases based on findings
- [ ] Verify fixes with re-testing
- [ ] Update documentation

## Bug Reporting Template

```markdown
## Bug Report #XXX

**Environment**: 
- Browser: [Chrome/Firefox/Safari/Edge]
- OS: [macOS/Windows/Linux]
- Screen Resolution: [1920x1080]

**Test Case**: [Reference to specific test]

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Result**: 
[What should happen]

**Actual Result**: 
[What actually happened]

**Severity**: [Critical/High/Medium/Low]
- Critical: System unusable
- High: Major feature broken
- Medium: Minor feature issue
- Low: Cosmetic/enhancement

**Screenshots/Videos**: 
[Attach relevant media]

**Additional Notes**:
[Any other relevant information]
```

## Success Criteria

### MVP Ready Criteria ✅
- [ ] All authentication flows working
- [ ] Character creation fully functional
- [ ] Story generation producing quality content
- [ ] Combat system responsive and accurate
- [ ] Session management robust
- [ ] Performance meets benchmarks (<3s page loads, <500ms API)
- [ ] Cross-browser compatibility confirmed
- [ ] Error handling graceful and informative
- [ ] Data integrity maintained
- [ ] No critical or high severity bugs

### Production Ready Indicators 🚀
- Automated test suite: 10/10 passing ✅
- Manual test coverage: >95% scenarios passing
- Performance benchmarks: All targets met
- User acceptance testing: Positive feedback
- Security testing: No vulnerabilities found
- Load testing: System stable under expected load

---

**Testing Status**: ✅ Automated Testing Complete (10/10)
**Next Phase**: Manual Testing Execution
**Target**: Production-Ready MVP

*Last Updated: 2025-05-24* 