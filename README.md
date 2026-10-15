# Day 20: Apigee vs. Agent Gateway: The Tale of Two Gateways

> **Advent of Agents (Season 3)** · **Day 20**  
> **Authors:** Christopher Duncan & Elliott Abraham  
> **Tags:** `AGENT GATEWAY` `APIGEE` `MCP` `SECURITY` `DEFENSE IN DEPTH`  
> **Demo Video:** *[5-Minute Demo Video Recording Scheduled - 9:00 AM]*

---

## Overview

When organizations introduce autonomous AI agents into production environments, platform and security teams face an immediate architectural question:

> *"We already run all corporate traffic through Apigee. Why do we need Agent Gateway?"*

Traditional API gateways are optimized for **North-South ingress traffic**: securing published endpoints against external callers, applying API key quotas, and routing requests to internal microservices. However, autonomous AI agents operate on an **outbound Egress paradigm**: agents reason non-deterministically and make dynamic runtime calls to external APIs, SaaS endpoints, and Model Context Protocol (MCP) servers.

Relying solely on Apigee leaves the agent's outbound execution loop unmonitored and vulnerable to indirect prompt injection or unauthorized egress. Relying solely on Agent Gateway leaves backend systems vulnerable to runaway agent loops, schema bloat, and protocol mismatches. 

Combining both delivers complete **Defense-in-Depth**.

---

## For Existing Apigee Customers

If your organization already standardizes on Google Cloud Apigee:

1. **Keep Your Existing API Catalog**: You do not need to rewrite your backend services or rip-and-replace existing Apigee proxies.
2. **Use This Proxy as a Starter Kit**: You can optionally deploy the included `advent-day20-mcp-proxy.zip` bundle to instantly expose legacy enterprise REST, SOAP, or database backends as standardized, discoverable Model Context Protocol (MCP) tools.
3. **Add Agent Gateway for Outbound Zero-Trust**: Place Agent Gateway in front of your autonomous agent execution environments (Vertex AI Reasoning Engines, Cloud Run, GKE) to enforce deny-by-default egress, SPIFFE workload attestation, and Model Armor safety filters before outbound agent requests reach Apigee.

---

## Architectural Comparison: Ingress vs. Egress

| Capability | Apigee API Gateway | Google Cloud Agent Gateway | Combined Synergy |
| :--- | :--- | :--- | :--- |
| **Primary Domain** | Ingress / Enterprise API Backbone | Egress / Autonomous Agent Boundary | Full perimeter governance |
| **Traffic Direction** | North-South (Clients to Backend APIs) | East-West & Outbound (Agents to Tools) | Comprehensive boundary control |
| **Caller Identity** | Consumer Apps, API Keys, OAuth 2.0 | Cryptographic SPIFFE Workload IDs | App authentication + Agent identity |
| **Security Scanning** | WAF, DDoS, Schema Validation | Model Armor (Prompt Injection / Jailbreak) | Protocol validation + LLM content safety |
| **Loop & Rate Protection** | Spike Arrest & Quotas (HTTP 429) | Deny-by-Default Egress & Tool Whitelists | Circuit breaking for runaway agent loops |
| **Context Window Control** | Strips heavy XML/JSON payloads to clean MCP | Passes filtered tool context to model | Optimal token consumption & cost control |

---

## Architecture Flow

```
+-------------------------------------------------------------------------------+
|                       AUTONOMOUS AGENT RUNTIME BOUNDARY                       |
|                                                                               |
|  +--------------------+             +--------------------------------------+  |
|  |  AI Agent / ADK    |             |        AGENT GATEWAY (Egress)        |  |
|  | (Gemini Enterprise)|  MCP Call   |                                      |  |
|  |                    +------------>|  [1] Validate SPIFFE Identity        |  |
|  | [SPIFFE ID]        |             |  [2] Check Agent Registry Allowlist  |  |
|  +--------------------+             |  [3] Service Ext: Model Armor Scan   |  |
|                                     |  [4] Enforce Deny-by-Default Policy  |  |
|                                     +-------------------+------------------+  |
+---------------------------------------------------------|---------------------+
                                                          | Permitted Egress
                                                          v (HTTPS / mTLS)
+-------------------------------------------------------------------------------+
|                         ENTERPRISE API INFRASTRUCTURE                         |
|                                                                               |
|  +-------------------------------------------------------------------------+  |
|  |                         APIGEE API GATEWAY                              |  |
|  |                                                                         |  |
|  |  [A] Ingress TLS & IP Whitelist Termination                             |  |
|  |  [B] Verify API Key & Consumer App Entitlements                         |  |
|  |  [C] Spike Arrest & Rate Quotas (Stop Infinite Loops)                   |  |
|  |  [D] Context Optimization: ExtractVariables / Strip Heavy Payload XML   |  |
|  +-------------------------------------+-----------------------------------+  |
+----------------------------------------|--------------------------------------+
                                         | Mediated Call
                                         v
               +---------------------------------------------------+
               |  Enterprise Backends: SAP / Salesforce / BigQuery |
               +---------------------------------------------------+
```

---

## Kata Package Contents

* `README.md`: Architectural documentation, decision tree, and setup guide.
* `advent-day20-mcp-proxy.zip`: Complete Apigee API Proxy bundle configured for MCP discovery and tools execution.
* `advent_day20_apiproxy/`: Source XML configuration and policies (`SA-SpikeArrest`, `Extract-MCP-Method`, `AM-Return-Tools-List`, `AM-Execute-Customer-Lookup`).
* `deploy_to_apigee.sh`: Automated deployment script to import and deploy the proxy bundle to any Apigee organization.
* `demo_runner.py`: End-to-end Python test script demonstrating discovery (`tools/list`), execution (`tools/call`), and Spike Arrest governance.
* `adk_agent.py`: Reference Google Agent Development Kit (ADK) agent configured with the governed MCP tool and SPIFFE identity headers.

---

## Hands-On Exercise

### Step 1: Verify Discovery (`tools/list`)
Query the Apigee MCP endpoint to discover registered tools:

```bash
curl -X POST https://136.69.97.200.nip.io/v1/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

Expected Response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "lookup_customer_account",
        "description": "Governed enterprise tool to fetch verified customer account data.",
        "inputSchema": {
          "type": "object",
          "properties": {"customer_id": {"type": "string"}},
          "required": ["customer_id"]
        }
      }
    ]
  }
}
```

### Step 2: Execute Tool (`tools/call`)
Invoke the governed enterprise tool through Apigee:

```bash
curl -X POST https://136.69.97.200.nip.io/v1/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "lookup_customer_account",
      "arguments": {"customer_id": "CUST-9921"}
    }
  }'
```

Expected Response:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"customer_id\": \"CUST-9921\", \"status\": \"ACTIVE\", \"tier\": \"PLATINUM\", \"verified_by\": \"APIGEE_PRE_PROD\"}"
      }
    ]
  }
}
```

### Step 3: Test Spike Arrest (Runaway Agent Loop Protection)
Run the automated test runner to trigger the `SA-SpikeArrest` policy:

```bash
python3 demo_runner.py
```

Notice that rapid successive requests receive `HTTP 429 Too Many Requests`:
```
policies.ratelimit.SpikeArrestViolation: Spike arrest violation. Allowed rate : MessageRate{messagesPerPeriod=10, periodInMicroseconds=60000000}
```

---

## Deploying to Your Own Apigee Environment

To deploy the bundle to your Google Cloud project:

```bash
export PROJECT_ID="<your-gcp-project-id>"
export ENV_NAME="<your-apigee-env-name>"

chmod +x deploy_to_apigee.sh
./deploy_to_apigee.sh
```

---

## Summary

* **Use Agent Gateway** at the agent runtime boundary for zero-trust outbound tool control, SPIFFE identity attestation, and Model Armor safety scanning.
* **Use Apigee** at the enterprise API boundary for legacy protocol translation, context optimization, credential verification, and spike arrest.
* **Together**, they provide end-to-end security and governance for production agentic AI architectures.
