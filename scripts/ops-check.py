#!/usr/bin/env python3

import json
import shutil
import sys
import urllib.error
import urllib.request

APP_URL = "http://127.0.0.1:8000"
PROMETHEUS_URL = "http://127.0.0.1:19090"
GRAFANA_URL = "http://127.0.0.1:13000"
ALERTMANAGER_URL = "http://127.0.0.1:19093"
TIMEOUT_SECONDS = 3

has_failures = False


def fetch(url: str):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
        status = response.getcode()
        body = response.read().decode("utf-8", errors="replace")
        return status, body


def ok(message: str):
    print(f"[OK] {message}")


def warn(message: str):
    print(f"[WARN] {message}")


def fail(message: str):
    global has_failures
    has_failures = True
    print(f"[FAIL] {message}")


def check_app():
    try:
        status, _ = fetch(f"{APP_URL}/health")
        if status == 200:
            ok("app /health returned 200")
        else:
            fail(f"app /health returned {status}")
    except urllib.error.URLError as exc:
        fail(f"app /health request failed: {exc}")

    try:
        status, body = fetch(f"{APP_URL}/ready")
        if status == 200:
            ok("app /ready returned 200")
        elif status == 503:
            warn(f"app /ready returned 503: {body}")
        else:
            warn(f"app /ready returned unexpected status {status}")
    except urllib.error.HTTPError as exc:
        if exc.code == 503:
            body = exc.read().decode("utf-8", errors="replace")
            warn(f"app /ready returned 503: {body}")
        else:
            fail(f"app /ready request failed with HTTP {exc.code}")
    except urllib.error.URLError as exc:
        fail(f"app /ready request failed: {exc}")


def check_service(name: str, url: str):
    try:
        status, _ = fetch(url)
        if status == 200:
            ok(f"{name} reachable")
        else:
            warn(f"{name} returned unexpected status {status}")
    except urllib.error.URLError as exc:
        fail(f"{name} request failed: {exc}")


def check_disk():
    usage = shutil.disk_usage("/")
    percent_used = (usage.used / usage.total) * 100

    if percent_used >= 80:
        warn(f"disk usage is high: {percent_used:.1f}%")
    else:
        ok(f"disk usage {percent_used:.1f}%")


def read_meminfo():
    values = {}
    with open("/proc/meminfo", "r", encoding="utf-8") as meminfo:
        for line in meminfo:
            parts = line.split()
            key = parts[0].rstrip(":")
            value = int(parts[1])
            values[key] = value
    return values


def check_memory():
    meminfo = read_meminfo()
    total = meminfo["MemTotal"]
    available = meminfo["MemAvailable"]
    percent_used = (1 - (available / total)) * 100

    if percent_used >= 80:
        warn(f"memory usage is high: {percent_used:.1f}%")
    else:
        ok(f"memory usage {percent_used:.1f}%")


def main():
    print("== App checks ==")
    check_app()

    print("\n== Monitoring checks ==")
    check_service("prometheus", PROMETHEUS_URL)
    check_service("grafana", GRAFANA_URL)
    check_service("alertmanager", ALERTMANAGER_URL)

    print("\n== Host checks ==")
    check_disk()
    check_memory()

    if has_failures:
        print("\nops-check completed with failures")
        sys.exit(1)

    print("\nops-check completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
