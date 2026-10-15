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
This PR adds the complete Day 20 kata, architectural documentation, deployable Apigee MCP Proxy bundle, automated demo runner, and reference ADK agent.

It addresses the fundamental enterprise question: *"We already run all corporate traffic through Apigee. Why do we need Agent Gateway?"* by delineating North-South enterprise ingress from autonomous agent outbound egress, providing a true defense-in-depth architecture.

### Package Contents
* `README.md`: Full architectural breakdown, ingress vs. egress decision matrix, hands-on kata exercises, and guidance for existing Apigee customers on using the proxy as an optional starter kit.
* `advent-day20-mcp-proxy.zip`: Pre-packaged Apigee API Proxy bundle implementing JSON-RPC Model Context Protocol (MCP) endpoints (`tools/list` and `tools/call`), Spike Arrest (`10pm`), and variable extraction.
* `advent_day20_apiproxy/`: Raw XML policies and proxy endpoint configurations for custom inspection or modification.
* `deploy_to_apigee.sh`: One-click Bash deployment script utilizing Apigee Management APIs.
* `demo_runner.py`: Validated Python test script asserting `tools/list` (200 OK), `tools/call` (200 OK), and `SA-SpikeArrest` throttling (429 SpikeArrestViolation).
* `adk_agent.py`: Reference Google Agent Development Kit (ADK) agent configured with the governed tool and SPIFFE identity headers.

### Live Validation Status
- **Deployed Proxy:** `advent-day20-mcp-proxy` (Revision 3 on `pre-prod`)
- **Live Ingress:** `https://136.69.97.200.nip.io/v1/mcp` (verified live with all assertions passing)
- **Video Recording:** Co-hosted 5-minute video recording with @elliottabraham scheduled for 9:00 AM tomorrow. Video URL will be appended upon recording completion.

### Reviewers & Approvals
- Elliott Abraham (@elliottabraham)
- Sita Lakshmi Sangameswaran (@sitalakshmi)
- Alan Blount (@alanblount)
- Afrina M (@afrinam)
```
