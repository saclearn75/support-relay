# Support Relay — implementation plan

## Goal

Demonstrate two agents resolving a synthetic API-support ticket in Band, then
using Cognee memory to adapt the next response for the same customer.

## Phase 1 — Band checkpoint (now)

- [x] Define distinct Support Lead and Technical Specialist mandates.
- [x] Add a two-process Codex/Band runner with per-agent credentials.
- [x] Create both remote identities in Band and start the TypeScript runners.
- [x] Add both agents to one room and prove a lead → specialist → lead exchange.

**Done when:** Band shows both connected agents and their room messages.

## Phase 2 — first-ticket resolution

- [x] Add a fixed Ticket 1 and synthetic expired-key log.
- [x] Have the specialist identify the expired API key and hand off the remediation.
- [x] Have the lead request human approval for a $10 service credit.
- [ ] Save the approved customer response as Markdown.

**Done when:** a room transcript and Markdown response resolve Ticket 1.

## Phase 3 — Cognee memory

- [x] Add a minimal `remember`/`recall` service scoped by customer ID.
- [ ] Persist the diagnosis, approved credit, and “written instructions only” preference.
- [ ] Start Ticket 2 in a fresh room/session and require a recall before drafting.

**Done when:** the Ticket 2 response cites the customer preference and gives
written rate-limit troubleshooting steps.

## Phase 4 — demo hardening

- Script the 2–3 minute walkthrough and seed predictable data.
- Add a smoke test for Band credentials and a local Cognee write/recall test.
- Capture the Band room and generated response as demo evidence.

## Deferred

Frontend, real email/CRM/billing integrations, and external ticket ingestion.
They are not required to demonstrate the collaboration and durable-memory loop.

