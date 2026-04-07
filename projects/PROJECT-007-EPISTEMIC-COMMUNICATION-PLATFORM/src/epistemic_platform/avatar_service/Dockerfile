FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3-pip python3.10-venv git wget ffmpeg \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/bin/python3.10 /usr/bin/python3

# Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# PyTorch with CUDA 12.1
RUN pip3 install --no-cache-dir torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu121

# LivePortrait
RUN git clone --depth 1 https://github.com/KwaiVGI/LivePortrait /opt/liveportrait \
    && cd /opt/liveportrait && pip3 install --no-cache-dir -e .

# SadTalker
RUN git clone --depth 1 https://github.com/OpenTalker/SadTalker /opt/sadtalker \
    && cd /opt/sadtalker && pip3 install --no-cache-dir -e .

# GFPGAN
RUN pip3 install --no-cache-dir gfpgan>=1.3.8

# Download model checkpoints (run separately or mount a volume)
# RUN cd /opt/liveportrait && python3 scripts/download_models.py
# RUN cd /opt/sadtalker && bash scripts/download_models.sh

# App code
COPY app.py .

# Directories for portraits and features
RUN mkdir -p /app/portraits /app/features /app/checkpoints

ENV PORTRAIT_DIR=/app/portraits
ENV FEATURES_DIR=/app/features
ENV SADTALKER_CHECKPOINT_DIR=/opt/sadtalker/checkpoints
ENV LIVEPORTRAIT_CHECKPOINT_DIR=/opt/liveportrait/checkpoints
ENV GFPGAN_MODEL_PATH=/app/checkpoints/gfpgan/GFPGANv1.4.pth
ENV DEVICE=cuda:0
ENV ENABLE_GFPGAN=true

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
