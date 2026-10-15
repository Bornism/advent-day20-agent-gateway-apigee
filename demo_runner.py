#!/usr/bin/env python3
"""Advent of Agents - Day 20 Demo Runner

Tests the Apigee MCP Proxy and demonstrates:
1. tools/list discovery
2. tools/call execution
3. Spike Arrest policy enforcement (burst test)

Configuration:
  Set APIGEE_MCP_URL or APIGEE_HOST in your environment (or in a local .env file):
    export APIGEE_HOST="your-apigee-host.example.com"
  or:
    export APIGEE_MCP_URL="https://your-apigee-host.example.com/v1/mcp"
"""

import json
import os
import sys
import time
import requests

# Load optional local .env if present
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
  with open(_env_path) as _f:
    for _line in _f:
      if "=" in _line and not _line.strip().startswith("#"):
        _k, _v = _line.strip().split("=", 1)
        os.environ.setdefault(_k.strip(), _v.strip())

# Resolve Apigee endpoint from environment variable with starter fallback
APIGEE_HOST = os.getenv("APIGEE_HOST", "api.enterprise.example.com")
MCP_URL = os.getenv("APIGEE_MCP_URL", f"https://{APIGEE_HOST}/v1/mcp")


def check_connectivity():
  print("=" * 60)
  print(f"Target Apigee MCP Gateway: {MCP_URL}")
  print("=" * 60)
  if "example.com" in MCP_URL:
    print("\n[NOTE] Using default placeholder URL.")
    print("To target your live environment, export APIGEE_HOST or APIGEE_MCP_URL:")
    print("  export APIGEE_HOST='<YOUR_APIGEE_IP_OR_HOST>'\n")


def test_tools_list():
  print("\n1. Discovery: Requesting tools/list via Apigee MCP Proxy")
  print("-" * 60)
  payload = {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/list",
      "params": {},
  }
  try:
    resp = requests.post(MCP_URL, json=payload, timeout=10)
  except requests.exceptions.RequestException as e:
    print(f"Error reaching Apigee endpoint {MCP_URL}: {e}")
    print("Please set export APIGEE_HOST='<your-host>' and retry.")
    sys.exit(1)

  print(f"Status Code: {resp.status_code}")
  print(json.dumps(resp.json(), indent=2))
  assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


def test_tools_call():
  print("\n2. Tool Invocation: Calling lookup_customer_account tool")
  print("   (Waiting 6.5s to respect the 10pm Spike Arrest window)")
  print("-" * 60)
  time.sleep(6.5)
  payload = {
      "jsonrpc": "2.0",
      "id": 2,
      "method": "tools/call",
      "params": {
          "name": "lookup_customer_account",
          "arguments": {"customer_id": "CUST-9921"},
      },
  }
  resp = requests.post(MCP_URL, json=payload, timeout=10)
  print(f"Status Code: {resp.status_code}")
  print(json.dumps(resp.json(), indent=2))
  assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


def test_spike_arrest():
  print("\n3. Governance: Rapid Burst Test against Apigee SA-SpikeArrest")
  print("   Sending 5 rapid requests to trigger 429 SpikeArrestViolation")
  print("-" * 60)
  payload = {
      "jsonrpc": "2.0",
      "id": 3,
      "method": "tools/list",
      "params": {},
  }
  caught_429 = False
  for i in range(1, 6):
    resp = requests.post(MCP_URL, json=payload, timeout=5)
    print(f"Request {i}: HTTP {resp.status_code}")
    if resp.status_code == 429:
      print("   -> 429 SpikeArrestViolation intercepted by Apigee! (Runaway agent loop halted)")
      caught_429 = True
    time.sleep(0.05)
  assert caught_429, "Expected Spike Arrest to trigger HTTP 429 on rapid burst"


if __name__ == "__main__":
  check_connectivity()
  test_tools_list()
  test_tools_call()
  test_spike_arrest()
  print("\n>>> All Day 20 demo test assertions passed successfully! <<<")
