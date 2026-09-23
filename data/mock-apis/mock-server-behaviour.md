# Mock Server Behaviour — Simulated WTCHK Systems

How the coding agent should implement the mock server behind `openapi.yaml`, using `fixtures.json` (v2.0). These rules make the demo repeatable and keep the "simulated, never guessed" message credible.

## 1. Principles

| Principle | Implementation |
|---|---|
| **Deterministic** | Same request → same response, always. No random values. IDs are generated from a counter seeded per demo run (`PR-2026-1042`, `PD-2026-1042`, `AT-2026-3301`, `CR-2026-0187`). |
| **Labelled** | Every JSON body has `meta.simulated: true`, `meta.source`, `meta.fixtureVersion`. Any human-readable text a mock generates (draft descriptions, verifier names) carries `[SIMULATED]` / `(SIMULATED)`. |
| **Fixture-only** | Responses are assembled from `fixtures.json`. If an entity is absent, return `404 NOT_FOUND` — never invent one. The platform must handle the 404 by asking the user, not by guessing. |
| **Read-mostly** | `POST` endpoints create in-memory records only (drafts, reviews, tasks, notifications, verifications). They persist for the demo session and reset on restart. |
| **Time-aware** | The demo clock defaults to `2026-09-28` and can be overridden per request with `X-Demo-Clock: YYYY-MM-DD`. All "as of" logic (days at price, promotion history windows, availability, SLA, cut-off proximity) uses the demo clock or an explicit `asOf`. |
| **Fault-injectable** | `X-Demo-Fault` triggers specific failures so the storyline can show pause-and-ask behaviour. |

## 2. Derived fields the mock computes

| Endpoint | Derived field | Rule |
|---|---|---|
| `/erp/prices` | `daysAtCurrentPrice` | `asOf − effectiveFrom` in calendar days |
| | `lastChangeDirection` | Compare `regularPrice` with the last `history[].price` |
| `/erp/costs` | `effectiveUnitCost` | `landedCost − Σ amountPerUnit` of off-invoice adjustments with `status = CONFIRMED` whose period fully covers `[periodFrom, periodTo]`; partial coverage is reported with `coverage: PARTIAL_PERIOD` and **not** deducted |
| `/insights/.../performance` | `promoWeeksLast12ByChannel` | From fixture (pre-counted for the scenario start dates). The coding agent may instead compute from `promotions[]` overlapping `[asOf − 84 days, asOf)` per channel; both must agree with the fixture values for the demo dates |
| `/insights/.../stock` | `weeksOfCoverAtBaseline` | `stockOnHand ÷ baselineWeeklyUnits(HK-ALL)` |
| `/funding/commitments` | `coverage`, `recognisedForApproval`, `recognitionReason` | Evaluate against query `periodFrom/periodTo/channel`: `period = FULL` if commitment period ⊇ request period; `channels = FULL` if all requested channels are in `channels[]` (or `NOT_APPLICABLE` for `OFF_INVOICE`/`FREE_GOODS`); `recognisedForApproval = status == CONFIRMED && period == FULL && channels in (FULL, NOT_APPLICABLE) && fundingType in (SCAN_BACK, LUMP_SUM)` |
| `/funding/.../evidence-verifications` | `outcome`, `checks[]`, `newStatus` | Look up `evidenceVerificationOutcomes` by `fundingRef` + `documentRef`; run the seven checks from the Funding Procedure §4.1 against `extracted`; `VERIFIED` only if all pass; on `VERIFIED`, mutate the in-memory commitment status to `CONFIRMED` and set `evidenceRef` |
| `/authority/resolve` | `reviewer`, `approver`, `informed`, `gateOwners` | See §3 |
| `/promohub/drafts` | `409` / `422` | `409` if a draft exists for `caseRef`; `422` if `decisionPackId` missing, or `priceZone` missing, or `promotionType = EVENT` without `eventCode` |
| `/promohub/drafts/{id}/validation` | `checks[]` | Always run: `ITEM_ACTIVE`, `BARCODE_ACTIVE`, `PRICE_ZONE_PRESENT`, `SCOPE_VALID`, `DATES_ALIGNED`, `NO_OVERLAP`, `MECHANIC_SUPPORTED`. Fault `promohub-validation-warning` forces `PRICE_ZONE_PRESENT = WARN` |
| `/approvals/tasks/{id}` | `status` | `OPEN` → `REMINDED` after 1 working day past `createdAt` → `ESCALATED`/`REASSIGNED` after 3 working days or when the assignee is unavailable on the demo clock date (re-resolve via delegations) |

## 3. Authority resolution algorithm

Input: `categoryLeadRoles[]`, `band`, `requesterId`, `preparerIds[]`, `expectedDecisionDate`, `parallelGates[]`, `flash`.

1. **Role by band**: A → each `categoryLeadRole` (one approver per category; if more than one category and band A, return `additionalApprovers`); B → reviewer `FINANCE_CONTROLLER`, approver `HEAD_OF_TRADING`; C → reviewer `FINANCE_CONTROLLER`, approver `COMMERCIAL_DIRECTOR`, informed `HEAD_OF_TRADING`; D → reviewers `FINANCE_CONTROLLER` + Group Finance (placeholder), approver `MANAGING_DIRECTOR`, informed `COMMERCIAL_DIRECTOR`.
2. **Flash shortcut** (`flash = true`, band A, no escalation): approver = category lead; informed = `HEAD_OF_TRADING` same day.
3. **Primary holder**: the person whose `roles[]` contains the role.
4. **Availability**: if the holder has an `unavailability` window containing `expectedDecisionDate`, or containing the whole SLA window, choose the delegation with matching `role`, `type = ABSENCE`, and `from ≤ expectedDecisionDate ≤ to`; set `viaDelegation`.
5. **Segregation of duties** (DoA §6.1): if the resolved approver or reviewer equals `requesterId` or is in `preparerIds`, use the `STANDING` delegation for that role (`bandScope` must include the band); if none, escalate to the next band's approver and state the reason. At band B+ ensure reviewer ≠ approver.
6. **Gate owners**: `COMPLIANCE` → `COMPLIANCE_MANAGER` (with availability/delegation logic); `SUPPLY_CHAIN` → `SUPPLY_PLANNER_HB` for Health/Beauty items, `SUPPLY_PLANNER_BPC` for Baby/Personal Care; `CUTOFF_EXCEPTION` → `HEAD_OF_TRADING`.
7. **Informed extras**: caller may pass advisory reasons (e.g. A-01 own-brand margin < 40% → `HEAD_OF_TRADING`); the mock echoes them into `informed[]`.
8. Always return `policyVersion: WTCHK-COM-POL-032 v3.2`.

## 4. Fault injection

| `X-Demo-Fault` | Affected call | Behaviour | Expected platform behaviour |
|---|---|---|---|
| `erp-cost-timeout` | `GET /erp/costs` | Wait 8 s, return `504 UPSTREAM_TIMEOUT`, `retryable: true` | Report "margin not computable — cost unavailable", do **not** estimate, offer retry / notify Finance; case status `WAITING_DATA` |
| `promohub-validation-warning` | `GET /promohub/drafts/{id}/validation` | `status: WARNING`, `PRICE_ZONE_PRESENT: WARN` | Show the warning in the handover note; Pricing Ops action listed |
| `funding-register-unavailable` | `GET /funding/commitments` | `503` | Funding treated as unknown, not zero: pause and ask whether to proceed with funding recognised as zero (explicitly) or wait |

Faults are applied to the single request carrying the header. The demo UI exposes a small "Demo controls" panel to set the clock and toggle faults for the next call.

## 5. Latency

Add 150–400 ms of fixed (not random) latency per endpoint so the agent trace is legible during the demo: Product Master 150 ms, ERP 400 ms, Insights 300 ms, PromoHub 250 ms, Funding 250 ms, Authority 150 ms, Compliance 150 ms, Approval Hub 200 ms.

## 6. Identifier conventions

| Entity | Pattern | First value in a demo run |
|---|---|---|
| Case | `PR-2026-NNNN` | `PR-2026-1042` |
| Decision pack | `DP-<case>-vN` | `DP-2026-1042-v1` |
| PromoHub draft | `PD-2026-NNNN` (same number as case) | `PD-2026-1042` |
| Approval task | `AT-2026-NNNN` | `AT-2026-3301` |
| Compliance review | `CR-2026-NNNN` | `CR-2026-0187` |
| Supply gate | `SG-2026-NNNN` | `SG-2026-0052` |
| Notification | `NT-2026-NNNN` | `NT-2026-7001` |

## 7. Suggested implementation shape (for the coding agent)

- Single Node/TypeScript or Python (FastAPI) service; load `fixtures.json` at start; in-memory store for created records; middleware that injects `meta`, applies latency, honours `X-Demo-Clock` and `X-Demo-Fault`.
- Expose `/__demo/reset` (POST) to reset in-memory records and counters between rehearsals; `/__demo/state` (GET) to inspect created records.
- Unit tests: replay the golden scenarios (`testing/golden-scenarios.md`) against the mock and assert the derived fields listed in §2.
