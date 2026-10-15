# Day 20: Apigee vs. Agent Gateway (The Tale of Two Gateways)

**Advent of Agents — Season 3 (October 2026)**  
**Authors:** Christopher Duncan & Elliott Abraham  
**Tags:** `Agent Gateway`, `Apigee`, `MCP`, `Security`, `API Management`  
**Video Demo:** *[5-minute video demo dropping tomorrow morning]*

---

### The Question Every Enterprise Team Asks

When teams start building production AI agents on Google Cloud, we almost always get asked:

> *"We already run Apigee across our whole company. Why do we need Agent Gateway? Aren't they doing the same thing?"*

Here's the deal: **they handle two completely different traffic patterns.**

* **Apigee is for Ingress (Inbound / North-South):** It guards your internal databases, ERPs, and microservices against incoming callers. It checks API keys, enforces rate limits, transforms legacy payloads, and keeps bad traffic off your servers.
* **Agent Gateway is for Egress (Outbound):** AI agents don't just sit there waiting for web traffic. They actively call external tools, third-party APIs, and MCP servers on their own. Agent Gateway sits right next to the agent runtime (Vertex AI, Cloud Run, GKE) to enforce a deny-by-default firewall on outbound tool calls, verify the agent's cryptographic SPIFFE identity, and run Model Armor on prompts before an agent reaches out to the world.

If you only run Apigee, your agent's outbound calls are flying blind with zero egress guardrails. If you only run Agent Gateway, your internal databases have no protection against runaway agent loops or context bloat. 

Using them together gives you end-to-end defense: Agent Gateway controls what the agent is allowed to call, and Apigee controls how enterprise tools and backends are consumed.

---

### Already using Apigee? Start here

If your company already standardizes on Apigee, you don't need to rebuild your backends or write custom MCP servers from scratch. 

You can take the proxy bundle in this repo (`advent-day20-mcp-proxy.zip`) and use it as a **starter kit**:
1. Drop the proxy bundle straight into your existing Apigee environment.
2. It translates standard Model Context Protocol JSON-RPC requests (`tools/list` and `tools/call`) directly into your backend APIs.
3. It puts Apigee's built-in **Spike Arrest** policy to work as a circuit breaker. If an agent hallucinates, loops recursively, or starts rapid-firing requests, Apigee cuts it off with an `HTTP 429` before your SAP, Salesforce, or BigQuery systems feel any pain.

---

### Ingress vs. Egress at a Glance

| Architectural Layer | Apigee API Gateway | Google Cloud Agent Gateway |
| :--- | :--- | :--- |
| **Where it sits** | In front of internal enterprise backends | Right at the agent runtime boundary (VPC egress) |
| **Traffic direction** | Ingress (traffic coming into your APIs) | Egress (calls initiated by your agents) |
| **Caller identity** | App API keys, OAuth 2.0, developer apps | Ephemeral cryptographic SPIFFE workload identity |
| **Security scanning** | WAF, DDoS mitigation, schema validation | Model Armor (prompt injection and jailbreak screening) |
| **Rate protection** | Spike arrest and quotas (stops backend meltdown) | Deny-by-default allowlists (stops rogue tool calls) |
| **Context efficiency** | Trims heavy JSON/XML down to clean tool responses | Passes filtered, verified tool context back to the model |

---

### Architecture Flow

![Architecture Flow](assets/architecture_flow.png)

1. **Client-to-Agent Ingress:** Incoming user requests hit the front-door Agent Gateway.
2. **Autonomous Agent Runtime:** Gemini agents in Vertex AI or Cloud Run pick tools dynamically based on user prompts.
3. **Agent-to-Any Egress Boundary:** The egress Agent Gateway intercepts outbound MCP tool calls, validates the agent's SPIFFE identity, checks the Agent Registry allowlist, and runs Model Armor prompt screening.
4. **Enterprise Tool Ingress (Apigee):** Permitted calls cross the network into Apigee, which handles TLS, checks client API keys, enforces Spike Arrest to kill recursive loops, and mediates payloads to your backends (SAP, Salesforce, BigQuery).

---

### What's in This Repo

* `advent-day20-mcp-proxy.zip`: Pre-built Apigee proxy bundle ready to import and deploy.
* `advent_day20_apiproxy/`: Unpacked XML proxy definition and policy files:
  * `SA-SpikeArrest.xml`: Throttles burst calls (set to 10 requests per minute for this demo).
  * `Extract-MCP-Method.xml`: Pulls out the JSON-RPC method (`tools/list` vs. `tools/call`).
  * `AM-Return-Tools-List.xml`: Returns the MCP tool schema.
  * `AM-Execute-Customer-Lookup.xml`: Returns the customer account record.
  * `policies/optional_llm_policies/`: Modular policies you can drop in for LLM Token Quotas, Response Caching, Context Trimming, and API Key checks.
* `demo_runner.py`: Python test runner that checks tool discovery, invokes the tool, and triggers Spike Arrest with a burst test.
* `deploy_to_apigee.sh`: Quick bash script to deploy the bundle using Apigee Management APIs.
* `.env.example`: Starter config for your Apigee host and project ID.

---

### Hands-On Kata: Running the Demo

#### 1. Setup your environment
Copy `.env.example` over to `.env` (or set environment variables in your terminal):

```bash
export APIGEE_HOST="<your-apigee-host-or-ip>"
# or
export APIGEE_MCP_URL="https://<your-apigee-host-or-ip>/v1/mcp"
```

#### 2. Test MCP Tool Discovery (`tools/list`)
Ask Apigee what tools are available over standard Model Context Protocol:

```bash
curl -X POST "${APIGEE_MCP_URL:-https://${APIGEE_HOST}/v1/mcp}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

Apigee returns the MCP tool schema:
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

#### 3. Test Tool Execution (`tools/call`)
Now call the tool through Apigee:

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

Apigee sends back the customer record:
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

#### 4. Test Runaway Loop Protection (Spike Arrest)
Run the Python test runner to verify everything, including rapid burst calls:

```bash
python3 demo_runner.py
```

Since the proxy enforces a `10pm` Spike Arrest policy (1 request every 6 seconds), rapid burst calls immediately trigger `HTTP 429 Too Many Requests`:

```text
Request 1: HTTP 200
Request 2: HTTP 429 -> SpikeArrestViolation intercepted by Apigee!
Request 3: HTTP 429 -> SpikeArrestViolation intercepted by Apigee!
```

That's how you keep a looping or hallucinating agent from bringing down your backend databases.

---

### Deploying the Proxy to Your Own GCP Project

If you want to deploy this starter proxy to your own Apigee org:

```bash
export PROJECT_ID="<your-gcp-project-id>"
export ENV_NAME="<your-apigee-env>"  # e.g., dev, eval, or prod

chmod +x deploy_to_apigee.sh
./deploy_to_apigee.sh
```

---

### Optional Starter Policies for LLM Governance

Inside `advent_day20_apiproxy/policies/optional_llm_policies/`, we included 4 extra policies you can plug into your proxy as your setup grows:

* **`LLM-Token-Quota.xml`:** Tracks token counts using Apigee's native `LLMTokenQuota` policy to enforce Tokens Per Minute (TPM) limits on agents.
* **`RC-Tool-Response-Cache.xml`:** Caches tool lookups right at the Apigee edge so repeated queries don't add extra latency or backend load.
* **`EV-Trim-Context-Payload.xml`:** Pulls only the required fields out of bloated enterprise payloads before handing data back to the LLM.
* **`VAK-Verify-API-Key.xml`:** Enforces standard API key authentication for client apps calling the tool.

---

### Bottom Line

* Put **Agent Gateway** on outbound agent traffic to stop prompt injection, verify agent identity, and block unauthorized network egress.
* Put **Apigee** on inbound tool traffic to expose enterprise APIs as MCP tools, protect backends with spike arrest, and keep payloads small.
* Run them together and you get zero-trust security across the whole agent lifecycle.
