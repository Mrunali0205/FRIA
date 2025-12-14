#!/bin/bash

BASE_URL="http://127.0.0.1:8000"

echo "=============================="
echo "🧪 Validation Test Suite (Corrected)"
echo "=============================="

START=$(curl -s "$BASE_URL/agent/start")
SESSION_ID=$(echo "$START" | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
LAST_MSG=$(echo "$START" | python3 -c "import sys,json; print(json.load(sys.stdin)['last_message'])")

echo "🤖 Agent: $LAST_MSG"
echo ""

send () {
  PAYLOAD="$1"
  EXPECT_KEYWORD="$2"

  RESPONSE=$(curl -s -X POST "$BASE_URL/agent/continue" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  LAST_MSG=$(echo "$RESPONSE" | python3 -c 'import sys,json; print(json.load(sys.stdin)["last_message"])')

  echo "🧑 You: $(echo $PAYLOAD | jq -r '.user_message // "GPS"')"
  echo "🤖 Agent: $LAST_MSG"

  if [[ "$LAST_MSG" == *"$EXPECT_KEYWORD"* ]]; then
    echo "✅ PASS"
  else
    echo "❌ FAIL (expected intent containing: $EXPECT_KEYWORD)"
  fi
  echo ""
}

# ---------------- SAFETY ----------------
echo "---- SAFETY VALIDATION ----"
send '{"session_id":"'$SESSION_ID'","user_message":"maybe"}' "safe"

# ---------------- INCIDENT ----------------
echo "---- INCIDENT VALIDATION ----"
send '{"session_id":"'$SESSION_ID'","user_message":"yes"}' "happened"

# ---------------- LOCATION ----------------
echo "---- LOCATION VALIDATION ----"
send '{"session_id":"'$SESSION_ID'","user_message":"flat tire"}' "happened"

# ---------------- OPERABILITY ----------------
echo "---- OPERABILITY VALIDATION ----"
send '{"session_id":"'$SESSION_ID'","user_message":"tire blew out"}' "location"

# ---------------- RECOVERY FLOW ----------------
echo "---- RECOVERY FLOW ----"
send '{"session_id":"'$SESSION_ID'","user_message":"Yes, I am safe"}' "where"
send '{"session_id":"'$SESSION_ID'","lat":41.8781,"lon":-87.6298}' "drive"
send '{"session_id":"'$SESSION_ID'","user_message":"No"}' "reason"
send '{"session_id":"'$SESSION_ID'","user_message":"Need tow to shop"}' "Thanks"

echo "✅ Validation test completed"
