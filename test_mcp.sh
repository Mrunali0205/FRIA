#!/bin/bash
MCP_URL="http://127.0.0.1:8765/mcp/"

echo "🔵 Opening MCP Session…"

INIT_RESPONSE=$(curl -s -X POST "$MCP_URL" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'
)

echo "💬 Init Response: $INIT_RESPONSE"

# Extract session_id
SESSION_ID=$(echo "$INIT_RESPONSE" | sed -n 's/.*"session_id":"\([^"]*\)".*/\1/p')

echo "🔵 Session: $SESSION_ID"

if [ -z "$SESSION_ID" ]; then
  echo "❌ Failed to obtain session_id"
  exit 1
fi

echo "-----------------------------------"
echo "📌 get_fields"

curl -s -X POST "${MCP_URL}${SESSION_ID}/tools/get_fields" \
  -H "Content-Type: application/json" \
  -d '{"args":{}}'
echo ""
echo "-----------------------------------"

echo "📌 set_field full_name"

curl -s -X POST "${MCP_URL}${SESSION_ID}/tools/set_field" \
  -H "Content-Type: application/json" \
  -d '{"args":{"field":"full_name","value":"Navika Maglani"}}'
echo ""
echo "-----------------------------------"

echo "📌 get_fields (after update)"

curl -s -X POST "${MCP_URL}${SESSION_ID}/tools/get_fields" \
  -H "Content-Type: application/json" \
  -d '{"args":{}}'
echo ""
echo "-----------------------------------"

echo "📌 required fields"

curl -s -X POST "${MCP_URL}${SESSION_ID}/tools/list_required_fields" \
  -H "Content-Type: application/json" \
  -d '{"args":{}}'
echo ""
echo "-----------------------------------"

echo "🔴 Closing session"

curl -s -X DELETE "${MCP_URL}${SESSION_ID}"
echo ""
echo "-----------------------------------"

echo "🎉 DONE"
