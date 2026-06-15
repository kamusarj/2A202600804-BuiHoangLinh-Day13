from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
ALERT_RULES = Path("config/alert_rules.yaml")
QUERIES = Path("data/sample_queries.jsonl")
SCENARIO_BY_RULE = {
    "high_latency_p95": "rag_slow",
    "high_error_rate": "tool_fail",
    "cost_budget_spike": "cost_spike",
}


def load_alert_rules(path: Path = ALERT_RULES) -> list[dict[str, str]]:
    rules: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line == "alerts:":
            continue
        if line.startswith("- name:"):
            if current:
                rules.append(current)
            current = {"name": line.split(":", 1)[1].strip()}
            continue
        if current and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip()
    if current:
        rules.append(current)
    return rules


def evaluate_condition(condition: str, metrics: dict[str, Any]) -> tuple[bool, str]:
    match = re.match(r"^([a-zA-Z0-9_]+)\s*([><]=?)\s*([0-9.]+)\s+for\s+(.+)$", condition)
    if not match:
        return False, f"unsupported condition: {condition}"

    metric_name, operator, threshold_raw, window = match.groups()
    actual = float(metrics.get(metric_name, 0) or 0)
    threshold = float(threshold_raw)
    passed = {
        ">": actual > threshold,
        ">=": actual >= threshold,
        "<": actual < threshold,
        "<=": actual <= threshold,
    }[operator]
    return passed, f"{metric_name}={actual} {operator} {threshold} for {window}"


def set_incident(client: httpx.Client, base_url: str, scenario: str, enabled: bool) -> None:
    action = "enable" if enabled else "disable"
    response = client.post(f"{base_url}/incidents/{scenario}/{action}", timeout=10.0)
    response.raise_for_status()


def send_requests(client: httpx.Client, base_url: str, limit: int) -> None:
    payloads = [
        json.loads(line)
        for line in QUERIES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ][:limit]
    for payload in payloads:
        try:
            client.post(f"{base_url}/chat", json=payload, timeout=30.0)
        except httpx.HTTPError as exc:
            print(f"request_error session={payload.get('session_id')} error={exc}")


def fetch_metrics(client: httpx.Client, base_url: str) -> dict[str, Any]:
    response = client.get(f"{base_url}/metrics", timeout=10.0)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--requests", type=int, default=10)
    args = parser.parse_args()

    rules = load_alert_rules()
    with httpx.Client() as client:
        for scenario in SCENARIO_BY_RULE.values():
            set_incident(client, args.base_url, scenario, False)

        print("Alert rule test")
        print(f"base_url={args.base_url}")
        for rule in rules:
            name = rule["name"]
            scenario = rule.get("test_scenario") or SCENARIO_BY_RULE.get(name)
            if not scenario:
                print(f"SKIP {name}: no test_scenario")
                continue

            set_incident(client, args.base_url, scenario, True)
            try:
                send_requests(client, args.base_url, args.requests)
                time.sleep(0.2)
                metrics = fetch_metrics(client, args.base_url)
                passed, detail = evaluate_condition(rule["condition"], metrics)
                status = "PASS" if passed else "FAIL"
                print(f"{status} {name} scenario={scenario} {detail}")
            finally:
                set_incident(client, args.base_url, scenario, False)

        metrics = fetch_metrics(client, args.base_url)
        print("final_metrics=" + json.dumps(metrics, sort_keys=True))


if __name__ == "__main__":
    main()
