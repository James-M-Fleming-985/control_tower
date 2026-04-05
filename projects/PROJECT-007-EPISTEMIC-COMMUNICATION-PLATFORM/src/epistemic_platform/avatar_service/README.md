# Avatar Service — Self-Hosted Lip-Sync Animation

Standalone FastAPI service for running MuseTalk lip-sync inference on the Dell Precision 7760 (RTX A5000, 16GB VRAM).

## Architecture

```
Railway App  ──WebSocket──>  Cloudflare Tunnel  ──>  Dell Workstation (this service)
                                                         ├── MuseTalk (lip-sync)
                                                         ├── LivePortrait (expressions)
                                                         └── GPU inference
```

## Endpoints

- `POST /api/animate` — Takes portrait image + audio chunk, returns animated MJPEG frames
- `WS /ws/avatar/{session_id}` — Real-time streaming: receives audio chunks, returns video frames
- `GET /health` — Health check with GPU memory info

## Setup on Dell

```bash
# 1. Clone MuseTalk
git clone https://github.com/TMElyralab/MuseTalk.git
cd MuseTalk && pip install -r requirements.txt

# 2. Install this service
cd ../avatar_service
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit MUSETALK_PATH, PORTRAIT_DIR, etc.

# 4. Run
uvicorn app:app --host 0.0.0.0 --port 8765

# 5. Expose via Cloudflare Tunnel
cloudflared tunnel --url http://localhost:8765
```

## Requirements

- Python 3.10+
- CUDA 12.x+ with cuDNN
- ~8GB VRAM for MuseTalk
- ~4GB VRAM for LivePortrait (optional)
- Portraits pre-generated via DALL-E 3
