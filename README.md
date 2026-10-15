# Day 20: Apigee vs. Agent Gateway: The Tale of Two Gateways

> **Advent of Agents (Season 3)** · **Day 20**  
> **Authors:** Christopher Duncan & Elliott Abraham  
> **Tags:** `AGENT GATEWAY` `APIGEE` `MCP` `SECURITY` `DEFENSE IN DEPTH`  
> **Starter Kit:** Production-ready Apigee MCP Proxy & Test Runner  
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

1. **Keep Your Existing API Catalog**: You do not need to rewrite your backend services or replace existing Apigee proxies.
2. **Use This Proxy as a Starter Kit**: You can optionally deploy the included `advent-day20-mcp-proxy.zip` starter bundle to instantly expose legacy enterprise REST, SOAP, or database backends as standardized, discoverable Model Context Protocol (MCP) tools.
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
|  |  AI Agent Runtime  |             |        AGENT GATEWAY (Egress)        |  |
|  | (Gemini / Vertex)  |  MCP Call   |                                      |  |
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

## Repository Contents

* `README.md`: Architecture guide, decision matrix, and deployment instructions.
* `.env.example`: Environment variable template for configuring target Apigee endpoints and project IDs.
* `advent-day20-mcp-proxy.zip`: Pre-packaged Apigee API Proxy starter bundle implementing JSON-RPC MCP discovery and execution.
* `advent_day20_apiproxy/`: Source XML configuration and policies:
  * `SA-SpikeArrest.xml`: Halts runaway agent recursion with HTTP 429.
  * `Extract-MCP-Method.xml`: Extracts JSON-RPC method routing.
  * `AM-Return-Tools-List.xml`: Dynamic MCP schema discovery.
  * `AM-Execute-Customer-Lookup.xml`: Governed enterprise tool response.
  * `policies/optional_llm_policies/`: Advanced modular policies for LLM token quotas, response caching, context trimming, and API keys.
* `deploy_to_apigee.sh`: One-click Bash deployment script utilizing Apigee Management APIs.
* `demo_runner.py`: Python test runner validating discovery, execution, and Spike Arrest throttling.

---

## Quickstart: Hands-On Exercise

### Prerequisites
1. Copy `.env.example` to `.env` or set your target Apigee host:
   ```bash
   export APIGEE_HOST="<YOUR_APIGEE_HOSTNAME_OR_IP>"
   # or
   export APIGEE_MCP_URL="https://<YOUR_APIGEE_HOSTNAME_OR_IP>/v1/mcp"
   ```

### Step 1: Verify Discovery (`tools/list`)
Query the Apigee MCP endpoint to discover available tools:

```bash
curl -X POST "${APIGEE_MCP_URL:-https://${APIGEE_HOST}/v1/mcp}" \
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
curl -X POST "${APIGEE_MCP_URL:-https://${APIGEE_HOST}/v1/mcp}" \
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
        "text": "{\"customer_id\": \"CUST-9921\", \"status\": \"ACTIVE\", \"tier\": \"PLATINUM\", \"verified_by\": \"APIGEE_ENTERPRISE_GATEWAY\"}"
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

## Advanced LLM & Agent Governance Policies

This starter package includes ready-to-use advanced policies in `advent_day20_apiproxy/policies/optional_llm_policies/`:

1. **`LLM-Token-Quota.xml` (Token Rate Limiting):**
   * Enforces rate limits based on estimated LLM token volume or request count, preventing agents from consuming downstream LLM quotas.
2. **`RC-Tool-Response-Cache.xml` (Tool Response Caching):**
   * Caches idempotent MCP tool invocations (such as product lookups or account status checks) at the Apigee edge, saving latency and downstream inference cost.
3. **`EV-Trim-Context-Payload.xml` (Context Window Optimization):**
   * Uses `ExtractVariables` to strip bulky 50+ field enterprise ERP payloads down to only the essential fields needed by the LLM, reducing prompt bloat and hallucination risk.
4. **`VAK-Verify-API-Key.xml` (Client Agent Authentication):**
   * Verifies API keys issued to calling agent applications or developers before allowing tool execution.

---

## Deploying to Your Google Cloud Project

To deploy the starter bundle to your Apigee organization:

```bash
export PROJECT_ID="<your-gcp-project-id>"
export ENV_NAME="<your-apigee-environment>"  # e.g., dev, eval, or prod

chmod +x deploy_to_apigee.sh
./deploy_to_apigee.sh
```

---

## Summary

* **Use Agent Gateway** at the agent runtime boundary for zero-trust outbound tool control, SPIFFE identity attestation, and Model Armor safety scanning.
* **Use Apigee** at the enterprise API boundary for legacy protocol translation, context optimization, credential verification, and spike arrest.
* **Together**, they provide end-to-end security and governance for production agentic AI architectures.
