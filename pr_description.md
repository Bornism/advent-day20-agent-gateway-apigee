# Pull Request: Day 20 - Apigee vs. Agent Gateway: The Tale of Two Gateways

**Branch Name:** `feature/day-20-apigee-agent-gateway` (or `duncanchris/day-20`)  
**Target Repository:** `agent-platform/advent-of-agents` (`depot.code.corp.goog`)  
**Target Base:** `main`  
**Reviewers:** `@sitalakshmi`, `@alanblount`, `@afrinam`, `@elliottabraham`  

---

### PR Title
`feat(day-20): Apigee vs. Agent Gateway — The Tale of Two Gateways`

---

### PR Description
```markdown
## Day 20: Apigee vs. Agent Gateway: The Tale of Two Gateways
**Advent of Agents Season 3 (October 2026)**
**Presenters:** Christopher Duncan (@duncanchris) & Elliott Abraham (@elliottabraham)

### Summary
This PR adds the Day 20 kata, architecture documentation, deployable Apigee MCP Proxy starter bundle, and automated demo test runner.

It addresses the fundamental enterprise question: *"We already run all corporate traffic through Apigee. Why do we need Agent Gateway?"* by delineating North-South enterprise ingress from autonomous agent outbound egress, providing complete defense-in-depth.

### Package Contents
* `README.md`: Architecture breakdown, decision matrix, hands-on kata, and guidance for existing Apigee customers on using the proxy as an optional starter kit.
* `.env.example`: Configuration template for target environments.
* `advent-day20-mcp-proxy.zip`: Pre-packaged Apigee API Proxy starter bundle implementing JSON-RPC Model Context Protocol (MCP) endpoints (`tools/list` and `tools/call`), Spike Arrest (`10pm`), and variable extraction.
* `advent_day20_apiproxy/`: Source XML configurations including core policies and modular advanced LLM policies:
  - `LLM-Token-Quota.xml`: Token-aware rate limiting for agent tool calls.
  - `RC-Tool-Response-Cache.xml`: Response caching for idempotent MCP tool invocations.
  - `EV-Trim-Context-Payload.xml`: Context window optimization and payload minimization.
  - `VAK-Verify-API-Key.xml`: API key verification for client agents.
* `deploy_to_apigee.sh`: Parameterized Bash deployment script utilizing Apigee Management APIs.
* `deploy_agent_gateway.sh`: Bash deployment script creating the Google Cloud Agent Gateway egress perimeter and registering Apigee in Agent Registry.
* `demo_runner.py`: Validated Python test script asserting `tools/list` (200 OK), `tools/call` (200 OK), and `SA-SpikeArrest` throttling (429 SpikeArrestViolation).

### Live Validation Status
- **Deployed Starter Proxy:** `advent-day20-mcp-proxy`
- **Verification:** Verified live against an Apigee pre-prod environment with all assertions passing (discovery, tool invocation, and Spike Arrest 429 interception).
- **Video Recording:** Co-hosted 5-minute video recording with @elliottabraham scheduled for 9:00 AM tomorrow. Video link will be appended upon recording completion.

### Reviewers
- Elliott Abraham (@elliottabraham)
- Sita Lakshmi Sangameswaran (@sitalakshmi)
- Alan Blount (@alanblount)
- Afrina M (@afrinam)
```
