# Avatar System Specification — Human-Level Talking Head Avatars

**Status**: DRAFT — Awaiting Approval  
**Replaces**: Current DALL-E portrait + MuseTalk scaffold (substandard, to be removed)  
**Target**: Avatars indistinguishable from a real human on a video call  
**Benchmark**: HeyGen Interactive Avatar / D-ID Live Portrait quality  

---

## 1. Objective

Build a self-hosted, real-time talking head avatar system where **users cannot tell the difference between the avatar and a real human on a video call**. Each of the 6 epistemic actors must appear as a distinct, photorealistic person with:

- Natural lip sync matching spoken audio
- Head micro-movements (not a frozen photo)
- Eye blinking at natural intervals
- Facial expressions driven by conversational context (META tags)
- Smooth temporal consistency (no flickering, warping artefacts)
- < 200ms end-to-end latency (audio → visible lip movement)

---

## 2. Hardware & Infrastructure

### Dell Precision 7760 (Self-Hosted GPU Workstation)

| Component | Spec (estimated) |
|-----------|------------------|
| GPU | NVIDIA RTX A5000 — 16GB GDDR6, 8192 CUDA cores |
| CPU | Intel Core i9-11950H (8C/16T) or Xeon W-11955M |
| RAM | 64GB DDR4 (estimated) |
| CUDA | 12.x + cuDNN 8.x |
| OS | Ubuntu 22.04 LTS or Windows 11 Pro |
| Network | Cloudflare Tunnel → Railway (WSS) |

### VRAM Budget (During Real-Time Inference)

| Component | VRAM | Notes |
|-----------|------|-------|
| LivePortrait (warping network) | ~2.5 GB | Appearance features cached per actor |
| Audio-to-motion network | ~1.5 GB | SadTalker audio2exp + audio2pose |
| Wav2Lip (lip refinement) | ~1.5 GB | Optional — improves lip accuracy |
| GFPGAN (face enhancement) | ~1.0 GB | Optional — removes minor artefacts |
| Frame buffers + working memory | ~1.5 GB | Input/output frames, mel spectrograms |
| **Total (real-time)** | **~8.0 GB** | **50% of 16 GB — safe headroom** |
| Flux.1 Dev (portrait gen only) | ~12 GB | Loaded only during one-time generation, then unloaded |
| Hallo2 (offline idle loops) | ~12 GB | Loaded only during offline generation |

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Railway (Cloud)                                    │
│                                                                      │
│  ElevenLabs TTS ──MP3 chunks──▶ Voice WebSocket Router               │
│                                    │                                 │
│                                    │ binary MP3 + META JSON          │
│                                    ▼                                 │
│                              ┌───────────┐                           │
│                              │  Browser   │                          │
│                              │ (Frontend) │                          │
│                              └─────┬─────┘                           │
│                                    │                                 │
│                     Audio chunks + META tags                         │
│                     via WSS (Cloudflare Tunnel)                      │
│                                    │                                 │
└────────────────────────────────────┼─────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 Dell Workstation (GPU Inference)                      │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │ Audio Feature │    │ Audio-to-    │    │ LivePortrait         │   │
│  │ Extraction    │───▶│ Motion Model │───▶│ Warping + Rendering  │   │
│  │ (mel spec)    │    │ (expression  │    │ (source portrait +   │   │
│  │  ~5ms         │    │  + head pose │    │  motion coefficients │   │
│  └──────────────┘    │  + eye blink)│    │  → output frame)     │   │
│                       │  ~15ms       │    │  ~20ms               │   │
│                       └──────────────┘    └──────────┬───────────┘   │
│                                                       │              │
│                                              ┌────────▼─────────┐   │
│                                              │ Face Enhancement  │   │
│                                              │ (GFPGAN/optional) │   │
│                                              │  ~10ms            │   │
│                                              └────────┬─────────┘   │
│                                                       │              │
│                                              JPEG frame (~50ms total)│
│                                              via WSS to browser      │
└─────────────────────────────────────────────────────────────────────┘
```

### Audio Flow — Browser-Centric (Preferred Architecture)

The browser already receives MP3 audio from ElevenLabs via the voice WebSocket. Rather than routing audio through Railway→Dell→Browser (double hop), the browser forwards audio chunks directly to the Dell avatar service:

```
Railway Voice WS ──MP3──▶ Browser ──MP3──▶ Dell Avatar WS
                              │                    │
                              │◀──JPEG frames──────┘
                              ▼
                         <canvas> render + Audio playback (synchronised)
```

This eliminates an entire network hop and keeps latency under 200ms.

---

## 4. Portrait Generation Pipeline

### Goal
Generate photorealistic headshots indistinguishable from real photographs. Must look like a LinkedIn profile photo, not AI art.

### Why Not DALL-E 3
DALL-E 3 produces images with a distinctive "AI art" aesthetic — slightly stylised skin, unnatural lighting, visible brush-stroke patterns. Not suitable for human-passing avatars.

### Model: Flux.1 Dev + Face Restoration

| Step | Tool | Purpose |
|------|------|---------|
| 1. Base portrait | **Flux.1 Dev** (or Flux.1 Pro via API) | Photo-realistic face generation from text prompt |
| 2. Identity lock | **IP-Adapter FaceID** | Ensure re-generations produce the same person |
| 3. Multi-angle | **Zero-1-to-3++** or Flux re-prompting | Generate 3-5 reference angles for animation robustness |
| 4. Enhancement | **GFPGAN v1.4** / **CodeFormer** | Sharpen facial details, fix minor artefacts |
| 5. Validation | **ArcFace** similarity score | Verify identity consistency: cosine similarity > 0.7 across angles |

### Portrait Prompt Strategy

Each actor gets a photographic-style prompt (not artistic):

```
Professional photograph of [appearance], shot on Canon EOS R5, 
85mm f/1.4 lens, natural window light, shallow depth of field, 
neutral background, 8K resolution. Editorial portrait style.
```

### Outputs Per Actor

| Asset | Resolution | Purpose |
|-------|-----------|---------|
| Front-facing portrait | 1024×1024 | Primary animation source |
| 15° left turn | 1024×1024 | Head motion range |
| 15° right turn | 1024×1024 | Head motion range |
| Neutral expression close-up | 512×512 | Lip sync reference |
| Smile expression | 512×512 | Expression blending reference |

### Identity Consistency

Each actor's face is locked via **IP-Adapter FaceID embedding** — a 512-dim vector extracted from the first generation using ArcFace. All subsequent generations (re-render, different angles, different expressions) use this embedding as conditioning to ensure the same person appears every time.

---

## 5. Real-Time Animation Pipeline

### Core Pipeline: LivePortrait + Audio-Driven Motion

**LivePortrait** (Kuaishou, 2024) is the backbone — it performs high-quality, real-time face re-animation by warping a source portrait using motion coefficients. It handles:
- Expression transfer (mouth, eyebrows, cheeks)
- Head pose (pitch, yaw, roll)
- Eye gaze direction
- Stitching (seamless blending with background)

**Why LivePortrait over alternatives:**

| Model | Quality | Speed (A5000) | Real-time viable? | Notes |
|-------|---------|---------------|-------------------|-------|
| **LivePortrait** | ★★★★☆ | ~50 fps | **Yes** ✅ | Warping-based, very fast |
| Hallo2 | ★★★★★ | ~2 fps | No ❌ | Diffusion-based, offline only |
| EMO | ★★★★★ | ~1 fps | No ❌ | Diffusion-based, offline only |
| EchoMimic | ★★★★☆ | ~8 fps | Marginal ⚠️ | Could work with TensorRT |
| SadTalker | ★★★☆☆ | ~25 fps | Yes ✅ | 3DMM artefacts visible |
| MuseTalk | ★★☆☆☆ | ~30 fps | Yes ✅ | Lip-only, looks like a moving photo |
| Wav2Lip | ★★★☆☆ | ~30 fps | Yes ✅ | Lip-only, good sync but low res |

### Pipeline Components

#### 5.1 Audio Feature Extraction (~5ms)

```python
# Convert MP3 chunk to mel spectrogram
audio_pcm = decode_mp3_to_pcm(mp3_chunk, sr=16000)
mel = librosa.feature.melspectrogram(y=audio_pcm, sr=16000, n_mels=80)
```

Extracted features:
- 80-bin mel spectrogram (for lip sync)
- RMS energy (for mouth open amplitude)
- Pitch F0 via CREPE/pYIN (for expression intensity)

#### 5.2 Audio-to-Motion Network (~15ms)

Converts audio features to face motion coefficients that drive LivePortrait.

**Source**: SadTalker's pre-trained `audio2exp` and `audio2pose` networks, adapted to output LivePortrait-compatible motion vectors.

| Output | Dimensions | Drives |
|--------|-----------|--------|
| Expression coefficients | 63-dim (3DMM) | Mouth shape, eyebrow position, cheek deformation |
| Head pose | 3-dim (pitch/yaw/roll) | Natural head movement correlated to speech rhythm |
| Eye blink | 1-dim | Periodic blink overlaid (~4 blinks per 15s, natural distribution) |

**Blink generation**: Scripted via a stochastic model — Poisson-distributed with mean interval 3.5s, blink duration 150-400ms. Not audio-driven (real blinks are involuntary, not speech-correlated).

**Breathing**: Subtle sinusoidal head bob on the pitch axis, 0.5° amplitude, ~15 breaths/min. Adds life without being noticeable.

#### 5.3 LivePortrait Warping (~20ms)

```python
# One-time per actor (cached)
source_features = live_portrait.extract_appearance(portrait_image)

# Per frame (~20ms on A5000)
motion_input = convert_3dmm_to_liveportrait_motion(expression_coeffs, head_pose, eye_blink)
output_frame = live_portrait.warp(source_features, motion_input, stitching=True)
```

Key settings:
- **Stitching mode ON**: Seamlessly blends animated face region with original portrait background
- **Appearance features cached**: Extracted once per actor on startup, reused for every frame
- **TensorRT optimisation**: Convert ONNX → TensorRT FP16 for ~2x speedup

#### 5.4 Face Enhancement (Optional, ~10ms)

Light GFPGAN pass to clean up minor warping artefacts. Only applied if quality score < threshold (avoid unnecessary compute when output is already clean).

```python
if face_quality_score(output_frame) < 0.85:
    output_frame = gfpgan.enhance(output_frame, weight=0.5)  # Light touch
```

#### 5.5 Frame Encoding + Transmission (~5ms)

```python
# JPEG encode at quality 85 (good balance: ~30KB per 512×512 frame)
_, jpeg_buffer = cv2.imencode('.jpg', output_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
websocket.send_bytes(jpeg_buffer.tobytes())
```

At 25 fps with ~30KB per frame = ~750 KB/s = ~6 Mbps. Well within Cloudflare Tunnel bandwidth.

### Frame Rate & Timing

| Metric | Target | Justification |
|--------|--------|---------------|
| Output FPS | 25 fps | Matches PAL video, smooth to human eye |
| Pipeline latency | < 55ms | 5 + 15 + 20 + 10 + 5 = 55ms GPU time |
| Network latency | < 100ms | Cloudflare Tunnel typical |
| **End-to-end** | **< 155ms** | **Within 200ms target** ✅ |
| Audio-to-lip sync accuracy | < 80ms offset | Imperceptible to humans (McGurk threshold ~150ms) |

---

## 6. Expression & Motion System

### META Tag → Expression Mapping

The existing `ExpressiveState` model already outputs META tags (tone, mood, urgency, energy). These drive facial expressions in real-time:

| META Tag | Expression Effect |
|----------|------------------|
| `mood: enthusiastic` | Raised eyebrows, wider eyes, slight smile |
| `mood: concerned` | Furrowed brow, slight head tilt |
| `mood: thoughtful` | Narrowed eyes, hand-on-chin pose (if upper body visible) |
| `tone: warm` | Soft smile, relaxed brow |
| `tone: assertive` | Direct gaze, firm jaw, minimal head motion |
| `urgency: high` | Faster head movements, wider eyes, leaning forward |
| `energy: low` | Slower movements, smaller expression amplitude |

### Expression Blending

Expressions transition smoothly using exponential moving average:

```python
# Smooth transition over ~500ms (prevents jarring expression jumps)
alpha = 0.15  # Per-frame blend weight at 25fps
current_expression = alpha * target_expression + (1 - alpha) * current_expression
```

### Idle State

When the actor is NOT speaking (listening to the user), the avatar must still appear alive:
- Micro head movements (Perlin noise, ±2° amplitude)
- Regular blinking (stochastic, ~4/15s)
- Breathing animation (subtle pitch oscillation)
- Occasional gaze shifts (10% chance per second, small random yaw change)
- Slight expression changes (attentive listening → nodding occasionally)

---

## 7. Integration with Existing Platform

### What We Keep (Reusable from Current Scaffold)

| Component | Status | Reuse? |
|-----------|--------|--------|
| `avatar_service/` FastAPI structure | Scaffolded | ✅ Refactor endpoints, keep WS protocol shape |
| `avatar-video.tsx` React component | Scaffolded | ✅ Canvas rendering + WS connection logic intact |
| `actor-avatar.tsx` static fallback | Built | ✅ Used when Dell is offline |
| `config.py` → `avatar_service_url` | Built | ✅ No changes needed |
| `main.py` → `/api/client-config` | Built | ✅ No changes needed |
| Conversation.tsx / Debrief.tsx wiring | Built | ✅ Already imports ActorAvatar |

### What We Replace

| Component | Current | Replacement |
|-----------|---------|-------------|
| Portrait generator | DALL-E 3 (AI art look) | Flux.1 Dev + GFPGAN (photorealistic) |
| Animation engine | MuseTalk (lip-only) | LivePortrait + audio2motion (full face) |
| Motion source | None | SadTalker audio2exp/audio2pose networks |
| Expression control | Placeholder META | Full expression blending from ExpressiveState |
| Idle animation | None | Perlin noise head motion + stochastic blink |

### New `avatar_config` Schema

```json
{
  "portrait_url": "/static/portraits/professor_axelrod_front.png",
  "identity_embedding": [0.12, -0.34, ...],  // 512-dim ArcFace vector
  "reference_images": {
    "front": "/static/portraits/professor_axelrod_front.png",
    "left_15": "/static/portraits/professor_axelrod_left15.png",
    "right_15": "/static/portraits/professor_axelrod_right15.png",
    "neutral_close": "/static/portraits/professor_axelrod_neutral_close.png",
    "smile": "/static/portraits/professor_axelrod_smile.png"
  },
  "appearance_features_cached": true,
  "generation_model": "flux-1-dev",
  "generation_prompt": "Professional photograph of distinguished older...",
  "face_quality_score": 0.92,
  "generated_at": "2026-04-06T10:30:00Z"
}
```

### WebSocket Protocol (Refined)

```
Browser → Dell:
  {"type": "init", "actor_name": "Professor Axelrod", "session_id": "abc123"}
  {"type": "meta", "mood": "enthusiastic", "tone": "warm", "energy": "high"}
  <binary: MP3 audio chunk from ElevenLabs TTS>
  {"type": "audio_end"}  // Actor finished speaking → transition to idle
  {"type": "close"}

Dell → Browser:
  {"type": "ready", "fps": 25, "resolution": [512, 512]}
  <binary: JPEG frame>   // 25 per second during speech
  <binary: JPEG frame>   // ~5 per second during idle (lower rate to save bandwidth)
  {"type": "expression_change", "expression": "listening"}
  {"type": "error", "detail": "..."}
```

**Idle frame rate**: Drop to 5 fps during non-speaking periods (idle animations are slow-moving, don't need 25fps). Saves ~80% bandwidth during listening.

---

## 8. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| End-to-end latency (audio → visible lip) | < 200ms | Timestamp diff at browser |
| Lip sync accuracy | < 80ms audio-visual offset | Manual A/B test vs ground truth |
| Frame rate (speaking) | 25 fps sustained | FPS counter in avatar service |
| Frame rate (idle) | 5 fps | Sufficient for subtle movements |
| Identity consistency | ArcFace cosine sim > 0.7 | Between live frames and source portrait |
| VRAM usage | < 10 GB steady state | nvidia-smi monitoring |
| GPU utilisation | < 60% (headroom for spikes) | nvidia-smi monitoring |
| Uncanny valley test | 8/10 human panellists unable to identify as AI | Blind test |
| Startup time (cold) | < 30s (model loading) | Timer in service logs |
| Startup time (warm, cached) | < 2s | Timer in service logs |

---

## 9. Implementation Phases

### Phase A: Portrait Generation (Replace DALL-E) — 1 session

1. Install Flux.1 Dev on Dell (or use Flux.1 Pro API for faster iteration)
2. Write photorealistic prompt templates per actor (editorial style, not artistic)
3. Generate front-facing 1024×1024 portrait per actor
4. Run GFPGAN enhancement pass
5. Extract ArcFace identity embeddings
6. Generate multi-angle references using IP-Adapter FaceID conditioning
7. Validate identity consistency (cosine sim > 0.7 across all angles for each actor)
8. Update `avatar_config` in database with new schema
9. Serve from `static/portraits/` (same path as current)

**Deliverable**: 6 actors × 5 reference images = 30 photorealistic portraits stored in DB.

### Phase B: Audio-to-Motion Network — 1 session

1. Clone and install SadTalker on Dell
2. Extract `audio2exp` and `audio2pose` pretrained networks
3. Write motion adapter: converts SadTalker 3DMM output → LivePortrait motion format
4. Add stochastic blink generator (Poisson process, natural timing)
5. Add breathing animation (sinusoidal pitch modulation)
6. Add idle motion generator (Perlin noise for micro-movements)
7. Benchmark on A5000: target < 15ms per audio chunk → motion coefficients

**Deliverable**: `motion_driver.py` module that takes MP3 audio + META tags → motion coefficients at 25fps.

### Phase C: LivePortrait Integration — 1 session

1. Clone and install LivePortrait on Dell
2. Convert models to TensorRT FP16 for A5000 optimisation
3. Write portrait pre-processor: extract and cache appearance features per actor
4. Integrate motion driver output → LivePortrait warp call
5. Add stitching for seamless background blending
6. Add optional GFPGAN post-processing pass (quality-gated)
7. Benchmark full pipeline: target < 55ms per frame on A5000
8. Verify 25fps sustained output with GPU headroom

**Deliverable**: `animation_engine.py` module that takes motion coefficients + cached portrait → JPEG frame.

### Phase D: Service Integration + WebSocket — 1 session

1. Refactor `avatar_service/app.py` to use new `motion_driver` + `animation_engine`
2. Implement refined WebSocket protocol (init/meta/audio/idle transitions)
3. Add idle frame rate reduction (25fps speaking → 5fps idle)
4. Add expression blending from META tags (smooth EMA transitions)
5. Add actor switching (cache multiple actor appearances in VRAM)
6. Add health monitoring (VRAM, FPS, latency metrics)
7. Add reconnection handling (browser reconnects after tunnel blip)
8. Load test: verify sustained 25fps with realistic audio input

**Deliverable**: Production-ready avatar service running on Dell.

### Phase E: Frontend + End-to-End Testing — 1 session

1. Update `avatar-video.tsx` to handle idle/speaking frame rate differences
2. Add audio-video synchronisation logic (buffer frames to align with playback)
3. Add connection status indicator in UI (connected/reconnecting/offline)
4. Add graceful degradation: animated avatar → static portrait → initials
5. Wire MP3 audio forwarding from voice WebSocket to avatar WebSocket
6. End-to-end test: full conversation with animated avatar
7. Latency measurement: verify < 200ms audio → lip movement
8. Visual quality review against HeyGen reference recordings

**Deliverable**: Complete pipeline working in production on Railway + Dell.

### Phase F: Quality Iteration — As needed

1. Tune expression mapping coefficients based on visual testing
2. Adjust blink timing, breathing amplitude, idle motion ranges
3. A/B test with real users (can they tell it's AI?)
4. Optimise JPEG quality vs bandwidth trade-off
5. Add TensorRT INT8 quantisation if GPU headroom is tight

---

## 10. Dependency Inventory

### Models to Install on Dell

| Model | Source | Disk Size | VRAM (inference) |
|-------|--------|-----------|-----------------|
| LivePortrait | github.com/KwaiVGI/LivePortrait | ~2 GB | ~2.5 GB |
| SadTalker (audio2exp/audio2pose only) | github.com/OpenTalker/SadTalker | ~1.5 GB | ~1.5 GB |
| GFPGAN v1.4 | github.com/TencentARC/GFPGAN | ~350 MB | ~1 GB |
| ArcFace (identity verification) | insightface package | ~250 MB | ~500 MB |
| Flux.1 Dev (portrait gen only) | HuggingFace | ~12 GB | ~12 GB (one-time) |
| IP-Adapter FaceID | HuggingFace | ~1.5 GB | Part of Flux pipeline |

### Python Dependencies

```
torch>=2.1.0 (with CUDA 12.x)
torchvision
torchaudio
onnxruntime-gpu
tensorrt (optional, for FP16 optimisation)
opencv-python-headless
numpy
librosa
soundfile
ffmpeg-python
fastapi
uvicorn[standard]
pydantic-settings
httpx
insightface (for ArcFace)
```

### Infrastructure

| Component | What | Why |
|-----------|------|-----|
| Cloudflare Tunnel | `cloudflared` on Dell | Exposes port 8765 to Railway securely |
| Railway env var | `AVATAR_SERVICE_URL` | Frontend discovers Dell endpoint |
| Static file serving | Already configured | Portraits served from Railway |

---

## 11. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LivePortrait produces visible warping artefacts | Medium | High | GFPGAN post-processing, quality-gated fallback to static portrait |
| 200ms latency exceeded due to tunnel overhead | Low | Medium | Measure actual tunnel latency; if >100ms, consider dedicated VPN or Tailscale |
| A5000 VRAM insufficient for all models | Low | High | VRAM budget is 8/16GB — 50% headroom. Can drop GFPGAN if tight |
| Identity drift across sessions (actor looks different) | Medium | Medium | ArcFace embedding lock + IP-Adapter conditioning |
| SadTalker audio2motion produces unnatural head bobs | Medium | Medium | Clamp motion amplitude, tune damping coefficients |
| Uncanny valley: looks realistic but feels "off" | Medium | High | Extensive tuning of blink/breath/idle, A/B testing with real users |
| Dell offline (power outage, network) | Low | Low | Graceful fallback to static photorealistic portrait (still good UX) |

---

## 12. What This Replaces

The following code written in the current scaffold will be **refactored or replaced**:

| File | Action |
|------|--------|
| `engine/portrait_generator.py` | **Replace** — swap DALL-E 3 for Flux.1 + GFPGAN pipeline |
| `avatar_service/app.py` | **Refactor** — keep FastAPI structure, replace MuseTalk with LivePortrait + motion driver |
| `ACTOR_APPEARANCE` prompts | **Rewrite** — photographic editorial prompts instead of artistic |
| `avatar_service/requirements.txt` | **Update** — add LivePortrait, SadTalker, GFPGAN deps |
| `avatar-video.tsx` | **Enhance** — add sync logic, idle rate handling, connection status |
| `actor-avatar.tsx` | **Keep** — still needed as static fallback |

The WebSocket protocol shape, config plumbing, and frontend component mounting are all reusable.

---

## 13. Success Criteria

The avatar system is **complete** when:

1. ☐ All 6 actors have photorealistic portraits that pass as real photographs
2. ☐ Real-time lip sync matches audio with < 80ms offset
3. ☐ Natural head movement, blinking, and breathing during speech
4. ☐ Expression changes driven by META tags (mood, tone, energy)
5. ☐ Idle animation when actor is listening (not a frozen image)
6. ☐ End-to-end latency < 200ms (audio input → visible lip movement)
7. ☐ Sustained 25fps during speech on RTX A5000
8. ☐ VRAM usage < 10GB steady state
9. ☐ Graceful fallback when Dell is offline
10. ☐ Blind test: majority of testers cannot identify as AI-generated
