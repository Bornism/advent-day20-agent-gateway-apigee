#!/usr/bin/env python3
"""Advent of Agents - Day 20 Demo Runner

Tests the Apigee MCP Proxy and demonstrates:
1. tools/list discovery
2. tools/call execution
3. Spike Arrest policy enforcement (burst test)
"""

import json
import time
import requests

# Point to your Apigee ingress host or the live pre-prod endpoint
MCP_URL = "https://136.69.97.200.nip.io/v1/mcp"

def test_tools_list():
  print("=" * 60)
  print("1. Discovery: Requesting tools/list via Apigee MCP Proxy")
  print("=" * 60)
  payload = {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/list",
      "params": {},
  }
  resp = requests.post(MCP_URL, json=payload, timeout=10)
  print(f"Status Code: {resp.status_code}")
  print(json.dumps(resp.json(), indent=2))
  assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


def test_tools_call():
  print("\n" + "=" * 60)
  print("2. Tool Invocation: Calling lookup_customer_account tool")
  print("   (Waiting 6.5s to respect the 10pm Spike Arrest window)")
  print("=" * 60)
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
  print("\n" + "=" * 60)
  print("3. Governance: Rapid Burst Test against Apigee SA-SpikeArrest")
  print("   Sending 5 rapid requests to trigger 429 SpikeArrestViolation")
  print("=" * 60)
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
  test_tools_list()
  test_tools_call()
  test_spike_arrest()
  print("\n>>> All Day 20 demo test assertions passed successfully! <<<")
