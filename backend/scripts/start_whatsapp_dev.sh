#!/bin/bash

# Start ngrok in background
echo "Starting ngrok..."
ngrok http 8000 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 3

# Get ngrok URL
NGROK_URL=$(curl -s localhost:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])")

echo "Ngrok URL: $NGROK_URL"
echo "Webhook URL: $NGROK_URL/api/v1/webhooks/whatsapp"
echo ""
echo "Configure this webhook URL in your WhatsApp Business API settings"
echo ""

# Export for the app
export WHATSAPP_WEBHOOK_URL="$NGROK_URL"

# Start the FastAPI app
# uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Cleanup
# kill $NGROK_PID