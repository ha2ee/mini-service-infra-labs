#!/usr/bin/env bash

set -u

APP_URL="${1:-http://127.0.0.1:8000}"
NGINX_URL="${2:-http://127.0.0.1:8080}"
CURL_TIMEOUT=3
HEALTH_FAILED=0

get_status_code() {
    local url="$1"
    curl -s -o /dev/null -w "%{http_code}" --max-time "$CURL_TIMEOUT" "$url"
}

check_health() {
    local name="$1"
    local base_url="$2"

    local status
    status=$(get_status_code "$base_url/health")

    if [ "$status" = "200" ]; then
        echo "[OK] $name health returned 200"
        return 0
    fi

    echo "[FAIL] $name health returned $status (expected 200)"
    return 1
}

check_ready() {
    local name="$1"
    local base_url="$2"

    local status
    status=$(get_status_code "$base_url/ready")

    if [ "$status" = "200" ]; then
        echo "[OK] $name ready returned 200"
    elif [ "$status" = "503" ]; then
        echo "[WARN] $name ready returned 503 (LAB_ENV may not be set yet)"
    else
        echo "[WARN] $name ready returned unexpected status: $status"
    fi
}

echo "Checking app direct at $APP_URL"
if ! check_health "app" "$APP_URL"; then
    HEALTH_FAILED=1
fi
check_ready "app" "$APP_URL"

echo
echo "Checking nginx proxy at $NGINX_URL"
if ! check_health "nginx" "$NGINX_URL"; then
    HEALTH_FAILED=1
fi
check_ready "nginx" "$NGINX_URL"

echo
if [ "$HEALTH_FAILED" = "0" ]; then
    echo "Health check completed successfully"
    exit 0
fi

echo "Health check completed with failures"
exit 1
