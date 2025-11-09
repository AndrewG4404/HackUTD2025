#!/bin/bash
# Check VendorLens configuration

echo "=================================="
echo "VendorLens Configuration Check"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Copy env.template to .env and configure it"
    echo ""
    exit 1
fi

# Source .env
export $(grep -v '^#' .env | xargs 2>/dev/null)

# Check MongoDB
echo "📦 MongoDB Configuration:"
echo "   URI: ${MONGODB_URI:-NOT SET}"
echo "   DB: ${MONGODB_DB_NAME:-NOT SET}"
echo ""

# Check Nemotron
echo "🤖 Nemotron Configuration:"
echo "   API URL: ${NEMOTRON_API_URL:-NOT SET}"
echo "   API Key: ${NEMOTRON_API_KEY:0:15}..." 
echo "   Model: ${NEMOTRON_MODEL:-NOT SET}"

# Determine deployment type
if [[ "$NEMOTRON_API_URL" == *"localhost"* ]] || [[ "$NEMOTRON_API_URL" == *"127.0.0.1"* ]]; then
    echo "   Type: 🏠 LOCAL NIM DEPLOYMENT"
    echo "   → No rate limits!"
else
    echo "   Type: ☁️  CLOUD API"
    echo "   → Subject to rate limits"
fi
echo ""

# Check backend config
echo "🚀 Backend Configuration:"
echo "   Host: ${BACKEND_HOST:-0.0.0.0}"
echo "   Port: ${BACKEND_PORT:-8000}"
echo ""

# Check upload config
echo "📁 Upload Configuration:"
echo "   Directory: ${UPLOAD_DIR:-uploads}"
echo "   Max Size: ${MAX_FILE_SIZE:-10485760} bytes"
echo ""

# Port conflict check
if [[ "$NEMOTRON_API_URL" == *":8000"* ]] && [ "${BACKEND_PORT:-8000}" == "8000" ]; then
    echo "⚠️  WARNING: Port conflict detected!"
    echo "   NIM is using port 8000"
    echo "   Backend is also trying to use port 8000"
    echo "   Set BACKEND_PORT=8001 in .env"
    echo ""
fi

# Test MongoDB connection
echo "🔍 Testing MongoDB connection..."
if command -v mongosh &> /dev/null; then
    if mongosh "$MONGODB_URI" --eval "db.version()" --quiet &> /dev/null; then
        echo "   ✓ MongoDB is accessible"
    else
        echo "   ✗ MongoDB is not accessible"
        echo "   Run: docker-compose up -d"
    fi
elif command -v mongo &> /dev/null; then
    if mongo "$MONGODB_URI" --eval "db.version()" --quiet &> /dev/null; then
        echo "   ✓ MongoDB is accessible"
    else
        echo "   ✗ MongoDB is not accessible"
        echo "   Run: docker-compose up -d"
    fi
else
    echo "   ⊘ MongoDB client not installed, skipping test"
fi
echo ""

# Test Nemotron endpoint
if [[ "$NEMOTRON_API_URL" == *"localhost"* ]] || [[ "$NEMOTRON_API_URL" == *"127.0.0.1"* ]]; then
    echo "🔍 Testing Local NIM endpoint..."
    BASE_URL=$(echo $NEMOTRON_API_URL | sed 's|/v1$||')
    if curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/v1/models" 2>/dev/null | grep -q "200"; then
        echo "   ✓ Local NIM is running"
    else
        echo "   ✗ Local NIM is not accessible"
        echo "   Run: ./deploy_local_nim.sh"
    fi
else
    echo "🔍 Cloud API configured (skipping connectivity test)"
fi

echo ""
echo "=================================="
echo "Configuration check complete!"
echo "=================================="

