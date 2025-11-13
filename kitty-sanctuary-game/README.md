# Kitty Sanctuary Game - Roblox Development Project

## 🐱 Game Concept
A cat rescue sanctuary builder with competitive mini-games where players:
- Rescue homeless cats with unique skills
- Build & upgrade a garden sanctuary
- Train cats for competitive mini-games
- Earn charity money to expand
- Compete globally for best sanctuary & skilled cats

## 📁 Project Structure (Copy-Paste Order)

This project is organized to match Roblox Studio's hierarchy. Copy scripts **in the order listed** for proper dependencies.

### Order of Implementation:

```
1. ServerScriptService/     <- Core game logic (Server-side)
2. ReplicatedStorage/       <- Shared modules (Client & Server)
3. StarterPlayer/           <- Client-side scripts
4. StarterGui/              <- UI scripts
```

## 🎮 Roblox Studio Setup Guide

### Step 1: Create New Place in Roblox Studio
1. Open Roblox Studio
2. Create new "Baseplate" template
3. Save as "Kitty Sanctuary"

### Step 2: Copy ServerScriptService Scripts (In Order)
Navigate to **ServerScriptService** in Explorer, then:

1. **DataStoreService.lua** - Create first (handles player data)
2. **GameConfig.lua** - Create second (game settings)
3. **EconomyService.lua** - Create third (charity/money system)
4. **CatService.lua** - Create fourth (cat management)
5. **SanctuaryService.lua** - Create fifth (building system)
6. **MiniGameService.lua** - Create sixth (mini-game logic)
7. **GameManager.lua** - Create last (orchestrates everything)

### Step 3: Copy ReplicatedStorage Modules
Navigate to **ReplicatedStorage** in Explorer, then create folder "Modules":

1. **CatTypes.lua** - Cat definitions
2. **ItemTypes.lua** - Furniture/building definitions
3. **MiniGameTypes.lua** - Mini-game definitions
4. **Utilities.lua** - Helper functions

### Step 4: Copy Client Scripts
Navigate to **StarterPlayer > StarterPlayerScripts**, then:

1. **ClientGameManager.lua** - Main client controller
2. **UIController.lua** - UI management
3. **SanctuaryBuilder.lua** - Building interface

### Step 5: Copy UI Scripts
Navigate to **StarterGui**, create ScreenGui "GameUI", then:

1. **MainUI.lua** - Main HUD
2. **SanctuaryUI.lua** - Building UI
3. **CatManagerUI.lua** - Cat selection UI
4. **ShopUI.lua** - Monetization shop

## 🧪 Test-Driven Development (TDD)

### Testing Locally in Codespaces
```bash
cd /workspaces/control_tower/kitty-sanctuary-game
lua tests/run_tests.lua
```

### Testing in Roblox Studio
1. Copy test files to ServerScriptService/Tests
2. Require TestEZ (install from Roblox library)
3. Run tests before publishing updates

## 💎 Monetization Strategy

### Game Passes (One-time purchases)
- **VIP Sanctuary** ($300 Robux) - Extra building space, exclusive cats
- **Auto Collect** ($150 Robux) - Auto-collect charity earnings
- **Fast Training** ($200 Robux) - 2x training speed
- **Premium Builder** ($100 Robux) - Access to rare materials early

### Developer Products (Repeatable)
- **Charity Bundles** (100-10000 Robux) - In-game currency
- **Cat Slots** ($50 Robux each) - More cat capacity
- **Instant Training** ($25 Robux) - Complete training instantly
- **Mystery Cat Egg** ($75 Robux) - Random rare cat

### Premium Benefits
- 1.5x charity earnings
- Daily premium cat rewards
- Exclusive sanctuary themes

## 🚀 Development Roadmap

### MVP (Week 1-2)
- [ ] Basic sanctuary building (grass plots, simple structures)
- [ ] 5 cat types with 2 skills each
- [ ] 2 mini-games (race, agility)
- [ ] Basic economy system
- [ ] Simple UI

### Phase 2 (Week 3-4)
- [ ] 10+ cat types
- [ ] 5 mini-games
- [ ] Advanced building (multiple materials)
- [ ] Competitive matchmaking
- [ ] Leaderboards

### Phase 3 (Week 5-6)
- [ ] Trading system
- [ ] Social features (friend visits)
- [ ] Premium materials (diamond, emerald)
- [ ] Seasonal events
- [ ] Polish & optimization

### Phase 4 (Week 7-8)
- [ ] Advanced monetization
- [ ] Mobile optimization
- [ ] Marketing & soft launch
- [ ] Community feedback iteration

## 🛠 Technology Stack

- **Language**: Lua 5.1 (Roblox Luau)
- **Testing**: TestEZ pattern (adapted for local TDD)
- **Version Control**: Git
- **Sync Tool**: Manual copy-paste (or Rojo for advanced users)

## 👨‍👩‍👧‍👧 Team Roles

- **Creative Directors**: Your daughters (game design, testing, feedback)
- **Developer**: You (implementation, systems, deployment)
- **QA Testers**: Your daughters + their friends (best testers!)

## 📝 Next Steps

1. Review game design document (`docs/GAME_DESIGN.md`)
2. Start with DataStoreService (first script)
3. Copy scripts in order to Roblox Studio
4. Test each system before moving to next
5. Get daughters to playtest each milestone!

## 🎯 Success Metrics

- **Week 1**: Playable MVP (daughters can test)
- **Week 4**: Soft launch to friends
- **Week 8**: Public release
- **Month 3**: 1000+ players
- **Month 6**: Profitable (>$100/month)

---

**Remember**: Start small, get it playable quickly, iterate based on feedback from your daughters and their friends!
