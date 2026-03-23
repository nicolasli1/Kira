#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"

success_response="$(curl -sS -X POST "${API_URL}/transfer" \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"vendor":"vendorA","txhash":"0xabc123confirmed"}')"

echo "${success_response}" | grep '"status":"success"' >/dev/null

invalid_response_code="$(curl -sS -o /tmp/invalid-transfer.json -w "%{http_code}" -X POST "${API_URL}/transfer" \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"vendor":"vendorA","txhash":"0xdeadbeef"}')"

test "${invalid_response_code}" = "404"
grep '"detail":"txhash not found"' /tmp/invalid-transfer.json >/dev/null
