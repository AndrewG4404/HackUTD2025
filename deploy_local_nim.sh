#!/bin/bash
# Deploy Local NIM for VendorLens
# Bypasses NVIDIA Cloud API rate limits

set -e

echo "=================================="
echo "VendorLens - Local NIM Deployment"
echo "=================================="
echo ""

# Check if NGC_API_KEY is set
if [ -z "$NGC_API_KEY" ]; then
    echo "❌ Error: NGC_API_KEY environment variable not set"
    echo ""
    echo "Please set your NGC API key:"
    echo "  export NGC_API_KEY=<your-ngc-api-key>"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if nvidia-docker is available
if ! docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi > /dev/null 2>&1; then
    echo "⚠️  Warning: GPU access may not be available"
    echo "This script requires NVIDIA GPU with Docker GPU support"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create cache directory
export LOCAL_NIM_CACHE=~/.cache/nim
mkdir -p "$LOCAL_NIM_CACHE"
echo "✓ Cache directory created: $LOCAL_NIM_CACHE"

# Login to NVIDIA Container Registry
echo ""
echo "Logging in to NVIDIA Container Registry..."
echo "$NGC_API_KEY" | docker login nvcr.io -u '$oauthtoken' --password-stdin

if [ $? -eq 0 ]; then
    echo "✓ Successfully logged in to nvcr.io"
else
    echo "❌ Failed to login to nvcr.io"
    exit 1
fi

# Pull and run the NIM
echo ""
echo "Pulling and starting NVIDIA NIM..."
echo "This may take a while on first run (downloading model)..."
echo ""
echo "NIM will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the NIM"
echo ""

docker run -it --rm \
    --gpus all \
    --shm-size=16GB \
    -e NGC_API_KEY \
    -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
    -u $(id -u) \
    -p 8000:8000 \
    nvcr.io/nim/nvidia/nvidia-nemotron-nano-9b-v2:latest

