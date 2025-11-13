# Kitty Sanctuary - Game Design Document

## 🎮 Core Game Loop

```
Player discovers homeless cat
    ↓
Brings cat home (others follow)
    ↓
Builds sanctuary in garden
    ↓
Trains cats with unique skills
    ↓
Competes in mini-games
    ↓
Earns charity money
    ↓
Upgrades sanctuary & cats
    ↓
Becomes top rescuer globally
```

## 🐱 Cat System

### Cat Attributes
- **Name**: Randomly generated or player-named
- **Breed**: Visual appearance (Tabby, Siamese, Persian, etc.)
- **Rarity**: Common, Uncommon, Rare, Epic, Legendary
- **Skills**: 1-3 skills depending on rarity
- **Level**: 1-100 (increased through training)
- **Happiness**: Affected by sanctuary quality

### Cat Skills (Examples)
1. **Speed** - Racing mini-games
2. **Agility** - Parkour/obstacle courses
3. **Intelligence** - Puzzle games
4. **Strength** - Pushing/lifting challenges
5. **Charm** - Crowd-pleasing performances
6. **Stealth** - Hide-and-seek games

### Cat Rarity Distribution
- **Common** (70%): 1 skill, basic stats
- **Uncommon** (20%): 1-2 skills, better stats
- **Rare** (7%): 2 skills, good stats
- **Epic** (2.5%): 2-3 skills, great stats
- **Legendary** (0.5%): 3 skills, maximum stats

### Cat Discovery
- **Street Encounters**: Random cats appear near player's sanctuary (free)
- **Rescue Missions**: Special events to find rare cats (gameplay-based)
- **Mystery Eggs**: Purchasable with charity or Robux (monetization)
- **Friends**: Cats bring friends based on sanctuary happiness

## 🏡 Sanctuary System

### Building Types
1. **Cat Houses**: Sleeping quarters (affects happiness)
2. **Play Areas**: Training zones (affects skill growth)
3. **Food Stations**: Feeding areas (affects happiness)
4. **Gardens**: Decorative areas (affects prestige)
5. **Trophy Rooms**: Display achievements

### Material Tiers
1. **Wood** (Free) - Basic structures
2. **Stone** (Low charity) - Improved durability
3. **Brick** (Medium charity) - Better aesthetics
4. **Gold** (High charity) - Prestigious appearance
5. **Diamond** (Very high charity) - Ultimate luxury
6. **Emerald** (Premium/Top players) - Rarest material

### Sanctuary Progression
- **Plot Size**: Starts small, expands with charity investment
- **Capacity**: Max number of cats (base 5, expandable to 50+)
- **Prestige Score**: Calculated from materials, decorations, cat count
- **Visitor System**: Friends can visit, leave ratings

## 🎯 Mini-Games

### 1. Cat Race
- **Type**: Speed-based
- **Skill**: Speed
- **Format**: 4 players, circular track
- **Duration**: 60 seconds
- **Reward**: Based on placement (1st: 100%, 2nd: 75%, 3rd: 50%, 4th: 25%)

### 2. Agility Course
- **Type**: Parkour
- **Skill**: Agility
- **Format**: Solo time trial
- **Duration**: 90 seconds
- **Reward**: Based on completion time & obstacles cleared

### 3. Puzzle Challenge
- **Type**: Pattern matching
- **Skill**: Intelligence
- **Format**: 1v1 or solo
- **Duration**: 120 seconds
- **Reward**: Based on puzzles solved

### 4. Strength Contest
- **Type**: Button mashing
- **Skill**: Strength
- **Format**: Tournament bracket
- **Duration**: Variable
- **Reward**: Winner-takes-most

### 5. Charm Show
- **Type**: Rhythm/performance
- **Skill**: Charm
- **Format**: Audience voting
- **Duration**: 60 seconds
- **Reward**: Based on crowd approval

### Matchmaking
- **Skill-Based**: Match cats of similar levels
- **Casual**: Free-for-all, any level
- **Ranked**: Competitive mode with seasons
- **Private**: Friend-only matches

## 💰 Economy System

### Earning Charity (In-Game Currency)
1. **Mini-Game Wins**: Primary income source
   - 1st place: 100 charity (base)
   - 2nd place: 75 charity
   - 3rd place: 50 charity
   - 4th place: 25 charity
   - Multiplied by cat level & rarity

2. **Daily Login**: 50 charity/day
3. **Quests**: 100-500 charity each
4. **Achievements**: One-time bonuses
5. **Friend Visits**: Small passive income
6. **Premium**: 1.5x all charity earnings

### Spending Charity
1. **Cat Training**: 10-1000 charity (based on level)
2. **Buildings**: 100-10,000 charity (based on material)
3. **Furniture**: 50-5,000 charity
4. **Plot Expansion**: 1,000-50,000 charity
5. **Mystery Eggs (Common)**: 500 charity

### Robux Monetization
See main README for complete monetization strategy

## 📊 Progression Systems

### Player Level
- XP earned from all activities
- Unlocks new features (materials, mini-games, cat slots)
- Prestige system at level 100

### Cat Training
- **Training Time**: 5 mins to 24 hours (based on level)
- **Training Cost**: Charity-based
- **Skill Points**: Distribute to cat's skills
- **Evolution**: Visual changes at milestones (Level 25, 50, 75, 100)

### Sanctuary Prestige
- **Leaderboard Ranking**: Global & friend leaderboards
- **Unlocks**: Special items at prestige milestones
- **Title System**: "Novice Rescuer" → "Master Rescuer" → "Legendary Rescuer"

## 🎨 UI/UX Design

### Main HUD
- Charity balance (top right)
- Robux balance (top right)
- Current sanctuary prestige (top left)
- Active quests (left sidebar)
- Notifications (top center)

### Menus
1. **Cat Manager**: View/select cats for mini-games
2. **Sanctuary Builder**: Place/edit buildings
3. **Mini-Games**: Queue for matches
4. **Shop**: Purchase currency/items
5. **Leaderboards**: Rankings
6. **Settings**: Options, controls

### Mobile Optimization
- Large touch targets (minimum 60px)
- Simple controls (tap, drag, swipe)
- Auto-saving
- Reduced particles on low-end devices

## 🌟 Social Features

### Friend System
- Visit friends' sanctuaries
- Rate sanctuaries (1-5 stars)
- Send gifts (cats, items)
- Co-op mini-games (planned Phase 3)

### Clubs/Teams
- Create/join cat rescue clubs
- Club competitions
- Shared club sanctuary
- Club chat

### Trading
- Trade cats with friends
- Trade furniture/items
- Trade currency (with tax to prevent exploitation)

## 🎭 Events & Seasons

### Seasonal Events
1. **Halloween**: Spooky cats, haunted sanctuary items
2. **Christmas**: Holiday-themed cats, decorations
3. **Easter**: Egg hunt events, bunny cats
4. **Summer**: Beach-themed content

### Limited-Time Events
- **2x Charity Weekends**
- **Rare Cat Spawns**
- **Tournament Series**
- **Building Material Sales**

## 🎯 Success Metrics & KPIs

### Engagement
- Daily Active Users (DAU)
- Average session length: Target 30+ minutes
- Retention: D1 (40%), D7 (20%), D30 (10%)

### Monetization
- Conversion rate: Target 5% spending players
- ARPPU (Average Revenue Per Paying User): Target $5-10/month
- Most popular purchases

### Gameplay
- Mini-games played per session
- Average cat collection size
- Sanctuary upgrade frequency

## 🚧 Technical Considerations

### Performance
- Max 100 cats visible simultaneously
- LOD (Level of Detail) for distant sanctuaries
- Optimized building system (mesh combining)

### Anti-Cheat
- Server-authoritative economy
- Validation on all transactions
- Rate limiting on actions

### Data Persistence
- Auto-save every 60 seconds
- Cloud save via DataStore2 pattern
- Data recovery system

---

**Next**: See `DEVELOPMENT_PLAN.md` for implementation order and technical specs
