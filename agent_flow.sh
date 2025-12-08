#!/bin/bash

BASE_URL="http://127.0.0.1:8000"

echo "=============================="
echo "🚗 CCC First Responder Agent"
echo "=============================="

# -----------------------------
# START SESSION
# -----------------------------

START_RESPONSE=$(curl -s "$BASE_URL/agent/start")

SESSION_ID=$(echo "$START_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
LAST_MSG=$(echo "$START_RESPONSE" | python -c "import sys,json; print(json.load(sys.stdin)['last_message'])")

echo ""
echo "✅ Session Started!"
echo "Session ID: $SESSION_ID"
echo "Agent: $LAST_MSG"
echo ""

# -----------------------------
# SEND TEXT INPUT
# -----------------------------

send_text () {
  MESSAGE="$1"

  RESPONSE=$(curl -s -X POST "$BASE_URL/agent/continue" \
    -H "Content-Type: application/json" \
    -d "{
      \"session_id\": \"$SESSION_ID\",
      \"user_message\": \"$MESSAGE\"
    }")

  echo ""
  echo "🧑 You: $MESSAGE"
  echo "🤖 Agent: $(echo "$RESPONSE" | python -c 'import sys,json; print(json.load(sys.stdin)["last_message"])')"
  echo ""
}

# -----------------------------
# SEND GPS
# -----------------------------

send_gps () {
  LAT="$1"
  LON="$2"

  RESPONSE=$(curl -s -X POST "$BASE_URL/agent/continue" \
    -H "Content-Type: application/json" \
    -d "{
      \"session_id\": \"$SESSION_ID\",
      \"lat\": $LAT,
      \"lon\": $LON
    }")

  echo ""
  echo "📍 GPS Sent: ($LAT, $LON)"
  echo "🤖 Agent: $(echo "$RESPONSE" | python -c 'import sys,json; print(json.load(sys.stdin)["last_message"])')"
  echo ""
}

# -----------------------------
# DEMO FLOW
# -----------------------------

send_text "Yes, I am safe"
send_gps 41.8781 -87.6298
send_text "No"
send_text "Flat tire on highway shoulder"
send_text "Tire blew out while driving"

echo "✅ Flow Completed!"
