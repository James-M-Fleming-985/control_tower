# M5: UI & Polish — Implementation Plan

**Project:** PROJECT-007 Epistemic Communication Platform  
**Milestone:** M5 — Complete React Frontend  
**Date:** 2026-03-21  
**Status:** PLANNING → READY TO BUILD

---

## Stack Decision

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Framework** | React 18 + TypeScript | Plan specifies React + TS |
| **Build** | Vite 5 | Plan specifies Vite; fast HMR |
| **Styling** | Tailwind CSS 3 + shadcn/ui | Plan specifies Tailwind; shadcn gives polished primitives (no extra bundle) |
| **Routing** | React Router v6 | Standard SPA routing |
| **State** | Zustand | Lightweight, no boilerplate, WebSocket-friendly |
| **HTTP** | Axios + React Query (TanStack Query) | Auth interceptor + cache/refetch |
| **WebSocket** | Native WebSocket + custom hook | 3 WS endpoints with different protocols |
| **Charts** | Recharts | Plan mentions Recharts; React-native, composable |
| **Audio** | Web Audio API + MediaRecorder | Voice capture + visualization |
| **Icons** | Lucide React | Tree-shakeable, consistent with shadcn |

**Frontend location:** `src/epistemic_platform/frontend/`  
**Dev server:** `localhost:5173` (already in backend CORS allowed_origins)  
**Production:** Static build served by FastAPI or separate deployment  

---

## Backend API Surface (consumed by frontend)

### REST Endpoints (JWT Bearer auth)

| Group | Endpoints | Used By |
|-------|-----------|---------|
| **Auth** | `POST /api/auth/register`, `/login`, `/refresh` | Auth pages |
| **Users** | `GET/PATCH /api/users/me` | Settings, profile header |
| **Actors** | `GET /api/actors/`, `/api/actors/{id}`, `/api/actors/stance/{stance}` | Actor browser, actor detail |
| **Scenarios** | `GET /api/scenarios/`, `/api/scenarios/{id}` | Scenario browser |
| **Sessions** | `GET/POST /api/sessions/`, `GET /api/sessions/active`, `POST /api/sessions/{id}/end` | Session management |
| **Assessment** | `GET /api/assessment/questions`, `POST /api/assessment/evaluate` | Assessment flow |
| **Gamification** | `GET /api/gamification/profile`, `/proficiency`, `/growth`, `/milestones` | Dashboard, results screen, header |
| **Analytics** | `GET /api/analytics/session/{id}`, `/stance-insights`, `/actor-evolution` | Session timeline, analytics |

### WebSocket Endpoints (JWT via `?token=`)

| Endpoint | Protocol | Used By |
|----------|----------|---------|
| `ws/conversation/{session_id}` | JSON: message ↔ stream_delta, trilemma_update, stance_update, coaching | Chat page |
| `ws/voice/{session_id}` | Binary audio + JSON: state_change, barge_in | Voice mode |
| `ws/debrief/{session_id}` | JSON: message ↔ stream_delta (premium only) | Debrief page |

---

## Phase Plan (8 phases, ~35 files)

### Phase 1: Scaffold + Auth + API Client
> Foundation that everything else depends on

**Files to create:**

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── tailwind.config.ts
├── postcss.config.js
├── src/
│   ├── main.tsx                          # App entry
│   ├── App.tsx                           # Router + providers
│   ├── index.css                         # Tailwind imports + globals
│   ├── lib/
│   │   ├── api.ts                        # Axios instance + auth interceptor + refresh logic
│   │   ├── ws.ts                         # WebSocket manager (connect, reconnect, auth)
│   │   └── utils.ts                      # cn() helper, formatters
│   ├── stores/
│   │   └── auth-store.ts                 # Zustand: user, tokens, login/logout/refresh
│   ├── types/
│   │   └── api.ts                        # TypeScript interfaces mirroring all Pydantic schemas
│   ├── hooks/
│   │   ├── use-auth.ts                   # Auth convenience hook
│   │   └── use-api.ts                    # React Query hooks (useActors, useSessions, etc.)
│   ├── components/
│   │   └── ui/                           # shadcn primitives (button, card, input, dialog, etc.)
│   └── pages/
│       ├── login.tsx                     # Email + password login form
│       ├── register.tsx                  # Registration form
│       └── layout.tsx                    # Authenticated shell (sidebar + header + outlet)
```

**Key decisions:**
- JWT stored in memory (Zustand) + httpOnly refresh cookie pattern, or localStorage with interceptor refresh. Given backend uses query-string tokens for WS, we store access_token in Zustand (memory) and refresh_token in localStorage.
- Axios interceptor: on 401 → try refresh → retry original request → if fail → logout
- Protected route wrapper: redirects to `/login` if no token

**Build plan tasks covered:** Create React app (Vite + TypeScript + Tailwind CSS) — scaffold, routing, auth context

---

### Phase 2: Assessment Flow
> The entry point for new users — must come before conversation

**Files:**

```
src/
├── pages/
│   └── assessment.tsx                    # Multi-step questionnaire → POST /api/assessment/evaluate
├── components/
│   └── assessment/
│       ├── question-card.tsx             # Single question display with options
│       └── result-display.tsx            # Assessment result with recommended actors
```

**Flow:** Register → Assessment → Recommended first actor → Start conversation

**Build plan tasks covered:** Part of scaffold (assessment is the onboarding funnel)

---

### Phase 3: Actor & Scenario Selection → Session Start
> Browse actors, pick one, start a session — the gateway to conversation

**Files:**

```
src/
├── pages/
│   ├── actors.tsx                        # Grid of actor cards (GET /api/actors/)
│   ├── actor-detail.tsx                  # Full profile + radar chart + "Start Conversation" CTA
│   └── scenarios.tsx                     # Scenario browser with filters (difficulty, category)
├── components/
│   ├── actors/
│   │   ├── actor-card.tsx                # Card: avatar, name, stance, difficulty badge, archetype
│   │   ├── actor-grid.tsx                # Responsive grid layout
│   │   └── ontology-radar.tsx            # Radar chart showing actor's communication register
│   └── scenarios/
│       ├── scenario-card.tsx             # Card: title, difficulty pill, category tag, objectives
│       └── scenario-filters.tsx          # Difficulty + category filter bar
```

**Flow:** Actor browser → Actor detail (radar + description) → Select scenario (optional) → POST /api/sessions/ → redirect to `/conversation/{session_id}`

**Build plan tasks covered:**
- Implement actor browser (grid/card view) — resource C
- Implement actor profile detail (full ontology visualization) — resource C
- Implement scenario browser (filter by difficulty, category, recommended) — resource D

---

### Phase 4: Core Conversation — Text Chat + Coaching Overlay
> The primary interaction — text WebSocket with streaming + coaching side panel

**Files:**

```
src/
├── pages/
│   └── conversation.tsx                  # Main conversation page (chat + coaching panel)
├── hooks/
│   ├── use-conversation-ws.ts            # WebSocket hook: connect, send message, receive stream
│   └── use-coaching.ts                   # Coaching annotation state management
├── components/
│   └── conversation/
│       ├── chat-panel.tsx                # Left: message list + input
│       ├── message-bubble.tsx            # User/actor message with avatar + timestamp
│       ├── streaming-indicator.tsx       # Animated dots / streaming text cursor
│       ├── message-input.tsx             # Text input + send button + voice toggle
│       ├── coaching-panel.tsx            # Right sidebar: real-time coaching annotations
│       ├── coaching-annotation.tsx       # Single annotation card (type, content, linked turn)
│       ├── trilemma-badge.tsx            # Current trilemma state indicator (horn badge)
│       └── stance-indicator.tsx          # Detected stance badge
```

**WebSocket message handling:**
- `stream_start` → show typing indicator
- `stream_delta` → append to current message buffer
- `stream_end` → finalize message in chat
- `coaching` → push coaching annotation to side panel
- `trilemma_update` → update trilemma badge
- `stance_update` → update stance indicator
- `session_ended` → navigate to results screen

**Build plan tasks covered:**
- Implement chat interface (message bubbles, streaming, typing indicator) — resource A
- Implement coaching side panel (real-time annotations) — resource B

---

### Phase 5: Voice Mode
> Extends conversation with mic button, audio capture, playback, composure visualization

**Files:**

```
src/
├── hooks/
│   ├── use-voice-ws.ts                   # Voice WebSocket: binary audio send/receive
│   ├── use-audio-capture.ts              # MediaRecorder + Web Audio API (mic access)
│   └── use-audio-playback.ts             # AudioContext for streaming TTS playback
├── components/
│   └── voice/
│       ├── voice-controls.tsx            # Mic button (hold-to-talk or toggle), mode switch
│       ├── audio-visualizer.tsx          # Real-time audio waveform/level meter
│       ├── voice-state-indicator.tsx     # listening ↔ processing ↔ speaking state display
│       └── composure-meter.tsx           # Real-time composure score display (if available)
```

**Voice flow:**
1. User clicks mic → `navigator.mediaDevices.getUserMedia({audio: true})`
2. MediaRecorder captures WebM chunks → send as binary frames to `/ws/voice/{session_id}`
3. User releases mic or pauses → send `{"type": "end_utterance"}`
4. Server responds: `state_change: processing` → `stream_audio` (binary TTS) → `state_change: listening`
5. `barge_in` event: stop current TTS playback immediately
6. Audio visualizer: Web Audio API `AnalyserNode` for real-time level display

**Build plan tasks covered:**
- Implement voice controls (mic button, audio viz, mode toggle) — resource A

---

### Phase 6: Post-Session Flow — Results + Completion + Coach Debrief
> After session ends: results screen → optional coach debrief (premium)

**Files:**

```
src/
├── pages/
│   ├── session-results.tsx               # Post-session results screen
│   └── debrief.tsx                       # Coach debrief chat (premium)
├── hooks/
│   └── use-debrief-ws.ts                 # Debrief WebSocket hook
├── components/
│   ├── results/
│   │   ├── xp-gain-animation.tsx         # Animated XP counter + level-up effect
│   │   ├── badge-reveal.tsx              # New badge unlock animation
│   │   ├── session-metrics.tsx           # Gricean scores, horns visited/escaped
│   │   ├── composure-sparkline.tsx       # Composure trend for voice sessions
│   │   └── next-session-cta.tsx          # "Start next recommended session" button
│   ├── debrief/
│   │   ├── debrief-chat.tsx              # Coach chat interface (distinct style from actor)
│   │   ├── context-sidebar.tsx           # Session metrics mini-display
│   │   ├── annotation-cards.tsx          # Tappable coaching annotation reference cards
│   │   └── subscription-gate.tsx         # Free: blurred preview + upgrade CTA; Premium: proceed
│   └── completion/
│       └── completion-screen.tsx         # Objectives met summary + "Start Debrief" CTA
```

**Build plan tasks covered:**
- Implement post-session results screen (XP earned, badges unlocked, metrics) — resource E
- Implement session completion screen (objectives met, transition prompt) — resource F
- Implement coach debrief chat interface (conversational feedback UI) — resource F
- Implement feedback reference cards (clickable coaching annotations) — resource F
- Implement subscription gate UI (tier check, upgrade prompt, feature preview) — resource F

---

### Phase 7: Gamification + Dashboard
> XP display, skill radar, badges gallery, session history, growth charts, settings

**Files:**

```
src/
├── pages/
│   ├── dashboard.tsx                     # Main dashboard: session history + growth + badges
│   └── settings.tsx                      # User settings: profile, preferences, subscription
├── components/
│   ├── gamification/
│   │   ├── xp-bar.tsx                    # Persistent header XP progress bar
│   │   ├── level-badge.tsx               # Current level display
│   │   ├── skill-radar.tsx               # 4-axis radar chart (Recharts RadarChart)
│   │   ├── badges-gallery.tsx            # Grid: earned (bright) + locked (grey) + tooltips
│   │   └── xp-history.tsx                # XP earned per session sparkline
│   ├── dashboard/
│   │   ├── session-history.tsx           # List of past sessions with scores
│   │   ├── growth-charts.tsx             # Score trends over time (Recharts LineChart)
│   │   └── session-timeline.tsx          # Trilemma journey visualization (horizontal flow)
│   └── settings/
│       ├── profile-form.tsx              # Display name, skill level, preferences
│       └── subscription-panel.tsx        # Current tier, upgrade placeholder
```

**Header integration:** `xp-bar` + `level-badge` live in the layout header, always visible when authenticated.

**Build plan tasks covered:**
- Implement progress dashboard (session history, growth charts, badges) — resource D
- Implement skill radar chart (4-axis) — resource E
- Implement level + XP display (progress bar, level badge, XP history) — resource E
- Implement achievement badges gallery (earned + locked + progress) — resource E
- Implement session timeline (trilemma journey visualization) — resource E
- Implement user settings (profile, preferences, assessment retake) — resource D

---

### Phase 8: Polish + Integration
> Wire everything end-to-end, responsive design, loading states, error boundaries

**Files:**

```
src/
├── components/
│   ├── error-boundary.tsx                # Global error boundary
│   ├── loading-skeleton.tsx              # Skeleton loaders for cards, chat, dashboard
│   └── toast-provider.tsx                # Toast notifications (badge unlocked, level up, errors)
├── lib/
│   └── constants.ts                      # Route paths, WS URLs, config
```

**Tasks:**
- Mobile responsive layouts (Tailwind breakpoints)
- Loading skeletons for all data-fetching pages
- Error boundaries + 404 page
- Toast notifications (achievement unlocked, level up, connection lost)
- Reconnection logic for all 3 WebSocket endpoints
- Dark mode support (Tailwind `dark:` classes)
- Build for production: `vite build` → static assets
- Wire production static serving in FastAPI (or separate deployment)
- End-to-end user journey test: Register → Assess → Browse actors → Chat → Results → Debrief → Dashboard

---

## Implementation Sequence & Dependencies

```
Phase 1: Scaffold + Auth ──────────────────────────────┐
    │                                                   │
Phase 2: Assessment Flow                                │
    │                                                   │
Phase 3: Actor/Scenario Browser ────┐                   │
    │                               │                   │
Phase 4: Text Chat + Coaching ──────┤── All need auth ──┘
    │                               │
Phase 5: Voice Mode                 │
    │                               │
Phase 6: Post-Session + Debrief ────┘
    │
Phase 7: Gamification + Dashboard
    │
Phase 8: Polish + Integration
```

**Critical path:** Phase 1 → Phase 3 → Phase 4 → Phase 6 (this gives the core user journey)

---

## File Count Summary

| Phase | New Files | Description |
|-------|-----------|-------------|
| 1 | ~18 | Scaffold, config, auth, API client, types, layout |
| 2 | 3 | Assessment questionnaire + result display |
| 3 | 8 | Actor cards/grid/radar, scenario cards/filters, pages |
| 4 | 10 | Chat panel, messages, coaching panel, WS hooks |
| 5 | 7 | Voice capture, playback, visualizer, controls |
| 6 | 11 | Results screen, debrief chat, completion, subscription gate |
| 7 | 11 | XP bar, radar, badges, dashboard, timeline, settings |
| 8 | 4 | Error boundary, skeletons, toasts, constants |
| **Total** | **~72** | |

---

## User Journey (complete flow)

```
1. REGISTER     → /register → POST /api/auth/register → auto-login
2. ASSESS       → /assessment → GET /api/assessment/questions → answer → POST /api/assessment/evaluate
3. BROWSE       → /actors → GET /api/actors/ → click actor → /actors/:id
4. START        → /actors/:id → select scenario → POST /api/sessions/ → redirect /conversation/:id
5. CONVERSE     → /conversation/:id → WS /ws/conversation/:id (or /ws/voice/:id)
                  ├── Messages stream in (stream_delta)
                  ├── Coaching annotations appear in side panel
                  ├── Trilemma + stance badges update live
                  └── session_ended → redirect to results
6. RESULTS      → /sessions/:id/results → GET /api/analytics/session/:id + GET /api/gamification/profile
                  ├── XP gain animation
                  ├── Badge reveals
                  ├── Session metrics
                  └── CTA: "Discuss with Coach" or "Next Session"
7. DEBRIEF      → /sessions/:id/debrief (premium only)
                  ├── Subscription check → gate or proceed
                  ├── WS /ws/debrief/:id
                  ├── Coach streams opening analysis
                  ├── User asks reflective questions
                  └── Annotation reference cards
8. DASHBOARD    → /dashboard
                  ├── Session history list
                  ├── Growth charts (score trends)
                  ├── Skill radar (4-axis)
                  ├── XP bar + level
                  └── Achievement badges gallery
9. SETTINGS     → /settings → PATCH /api/users/me
```

---

## Route Map

| Path | Page Component | Auth | Description |
|------|---------------|------|-------------|
| `/login` | LoginPage | No | Email + password |
| `/register` | RegisterPage | No | Registration form |
| `/assessment` | AssessmentPage | Yes | Epistemological profiling questionnaire |
| `/actors` | ActorsPage | Yes | Actor browser grid |
| `/actors/:id` | ActorDetailPage | Yes | Actor profile + start session CTA |
| `/scenarios` | ScenariosPage | Yes | Scenario browser with filters |
| `/conversation/:id` | ConversationPage | Yes | Live chat + coaching (text or voice) |
| `/sessions/:id/results` | SessionResultsPage | Yes | Post-session metrics + XP + badges |
| `/sessions/:id/debrief` | DebriefPage | Yes | Interactive coach debrief (premium) |
| `/dashboard` | DashboardPage | Yes | Progress, history, growth, achievements |
| `/settings` | SettingsPage | Yes | Profile, preferences, subscription |

---

## Ready to build. Phase 1 first?
