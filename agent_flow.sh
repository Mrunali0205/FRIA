#!/bin/bash

BASE_URL="http://127.0.0.1:8000"

echo "=============================="
echo "🚗 CCC First Responder Agent"
echo "=============================="

# -----------------------------
# START SESSION (SAFE)
# -----------------------------

START_RESPONSE=$(curl -s "$BASE_URL/agent/start")

read -r SESSION_ID LAST_MSG <<EOF
$(echo "$START_RESPONSE" | python3 - <<'PY'
import json, sys
data = json.loads(sys.stdin.read())
print(data["session_id"])
print(data["last_message"])
PY
)
EOF

echo ""
echo "✅ Session Started!"
echo "Session ID: $SESSION_ID"
echo "🤖 Agent: $LAST_MSG"
echo ""

# -----------------------------
# SAFE JSON PARSER
# -----------------------------

parse_last_message () {
python3 - <<'EOF'
import sys, json
raw = sys.stdin.read().strip()
if not raw:
    print("")
else:
    try:
        data = json.loads(raw)
        print(data.get("last_message", ""))
    except Exception:
        print("")
EOF
}

# -----------------------------
# HELPERS
# -----------------------------

send_text () {
  MESSAGE="$1"

  RESPONSE=$(curl -s -X POST "$BASE_URL/agent/continue" \
    -H "Content-Type: application/json" \
    -d "{
      \"session_id\": \"$SESSION_ID\",
      \"user_message\": \"$MESSAGE\"
    }")

  LAST_MSG=$(echo "$RESPONSE" | parse_last_message)

  echo "🧑 You: $MESSAGE"
  echo "🤖 Agent: $LAST_MSG"
  echo ""

  sleep 0.5
}

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

  LAST_MSG=$(echo "$RESPONSE" | parse_last_message)

  echo "📍 GPS Sent: ($LAT, $LON)"
  echo "🤖 Agent: $LAST_MSG"
  echo ""

  sleep 0.5
}

# -----------------------------
# AUTO-LANE DRIVER (ROBUST)
# -----------------------------

while true; do

  # 🔒 Guard: wait until agent actually sends a message
  if [[ -z "$LAST_MSG" ]]; then
    sleep 0.2
    continue
  fi

  QUESTION=$(echo "$LAST_MSG" | tr '[:upper:]' '[:lower:]')

  # -------- FINALIZE --------
  if [[ "$QUESTION" == *"everything i need"* || "$QUESTION" == *"arrange your tow"* ]]; then
    echo "✅ Flow Completed!"
    break
  fi

  # -------- SAFETY --------
  if [[ "$QUESTION" == *"safe"* ]]; then
    send_text "Yes, I am safe"
    continue
  fi

  # -------- INCIDENT --------
  if [[ "$QUESTION" == *"what happened"* || "$QUESTION" == *"describe"* ]]; then
    send_text "Flat tire on highway shoulder"
    continue
  fi

  # -------- LOCATION --------
  if [[ "$QUESTION" == *"where"* || "$QUESTION" == *"location"* || "$QUESTION" == *"gps"* ]]; then
    send_gps 41.8781 -87.6298
    continue
  fi

  # -------- OPERABILITY --------
  if [[ "$QUESTION" == *"drive"* || "$QUESTION" == *"drivable"* || "$QUESTION" == *"operable"* ]]; then
    send_text "No"
    continue
  fi

  # -------- TOW REASON --------
  if [[ "$QUESTION" == *"tow"* || "$QUESTION" == *"towed"* || "$QUESTION" == *"why do you need"* ]]; then
    send_text "Tire blew out, need tow to nearest shop"
    continue
  fi

  # -------- SAFETY NET --------
  echo "⚠️ Unrecognized agent prompt:"
  echo "$LAST_MSG"
  break

done
