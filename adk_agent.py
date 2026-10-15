"""Advent of Agents - Day 20: Governed Agent Runtime (ADK + SPIFFE Identity)

Demonstrates how an enterprise agent built with Google Agent Development Kit (ADK)
interacts with Apigee MCP tools routed through Agent Gateway.
"""

import os
import requests

MODEL = "gemini-3.5-flash"
AGENT_GATEWAY_EGRESS = os.getenv(
    "AGENT_GATEWAY_ENDPOINT", "http://agent-egress-gateway.internal:8080"
)
APIGEE_MCP_URL = os.getenv(
    "APIGEE_MCP_URL", "https://136.69.97.200.nip.io/v1/mcp"
)


def lookup_customer_account(customer_id: str) -> str:
  """Governed tool: Queries customer records via Apigee through Agent Gateway egress boundary.
  
  Args:
      customer_id: The customer unique account identifier (e.g., CUST-9921).
  Returns:
      Governed customer JSON record verified by Apigee.
  """
  payload = {
      "jsonrpc": "2.0",
      "id": 101,
      "method": "tools/call",
      "params": {
          "name": "lookup_customer_account",
          "arguments": {"customer_id": customer_id},
      },
  }
  
  # When deployed in VPC, route through Agent Gateway proxy
  proxies = (
      {"http": AGENT_GATEWAY_EGRESS, "https": AGENT_GATEWAY_EGRESS}
      if os.getenv("USE_GATEWAY_PROXY")
      else None
  )
  
  headers = {
      "Content-Type": "application/json",
      "X-Agent-Identity": "spiffe://corp.internal/ns/agents/sa/support-agent-runner",
  }

  response = requests.post(
      APIGEE_MCP_URL,
      json=payload,
      proxies=proxies,
      headers=headers,
      timeout=10,
  )
  response.raise_for_status()
  return response.json()["result"]["content"][0]["text"]


# Define ADK Agent if google-adk is available in the environment
try:
  from google.adk.agents import Agent
  from google.adk.models import Gemini
  from google.genai import Client as GenaiClient

  class GovernedGemini(Gemini):
    api_version: str = "v1beta1"

    @property
    def api_client(self) -> GenaiClient:
      return GenaiClient(vertexai=True, location="global")

  root_agent = Agent(
      name="governed_support_agent",
      model=GovernedGemini(model=MODEL),
      description="Enterprise customer support agent protected by Agent Gateway & Apigee.",
      instruction=(
          "You are an enterprise support assistant. Look up customer records "
          "using lookup_customer_account."
      ),
      tools=[lookup_customer_account],
  )
except ImportError:
  root_agent = None


if __name__ == "__main__":
  print("Testing lookup_customer_account tool invocation:")
  res = lookup_customer_account("CUST-9921")
  print("Response:", res)
