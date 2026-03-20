#!/usr/bin/env bash

set -u

BASE_URL="${1:-http://127.0.0.1:8000}"
CURL_TIMEOUT=3

check_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="$3"

    local status
    status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$CURL_TIMEOUT" "$url")

    if [ "$status" = "$expected_status" ]; then
        echo "[OK] $name returned $status"
        return 0
    fi

    echo "[FAIL] $name returned $status (expected $expected_status)"
    return 1
}

echo "Checking app at $BASE_URL"

if ! check_endpoint "health" "$BASE_URL/health" "200"; then
    echo "Health check failed"
    exit 1
fi

ready_status=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$CURL_TIMEOUT" "$BASE_URL/ready")

if [ "$ready_status" = "200" ]; then
    echo "[OK] ready returned 200"
elif [ "$ready_status" = "503" ]; then
    echo "[WARN] ready returned 503 (LAB_ENV may not be set yet)"
else
    echo "[WARN] ready returned unexpected status: $ready_status"
fi

echo "Health check completed"
exit 0

