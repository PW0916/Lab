# Promotion Approval Citizen Demo — Design v2

Watsons Hong Kong (fictional BU "WTCHK") · Demo clock Monday 28 September 2026 · All people, items, suppliers and numbers are fictional.

## What the demo has to prove

Kevin's two questions are the acceptance test:

1. **What are we enabling over time?** A BU can put its existing promotion documents on SharePoint, review a workflow the platform derives from them, and let citizen users run real promotion requests through a chat assistant — with simulated systems in Q4, live systems next year, more BUs after that, and an ontology only when several BUs share the same concepts.
2. **How are we enabling it?** The Q1 MVP is neither a prompt pack nor a self-service agent builder. It is a governed harness: **Workflow Studio** (build and change the workflow from documents) plus **Workflow Assistant** (run cases conversationally), on a mock system layer that carries the shape of the real systems.

The v1 pack proved the concept with a thin SOP and four APIs. This v2 makes the material as close to a real Watsons trading environment as a fictional pack can be, so the audience recognises their own process: twelve source documents with a hierarchy and deliberate inconsistencies, nine systems with 26 endpoints and coherent fixtures, 48 extracted rules, a 14-stage approved blueprint, 12 runtime agents, 34 skills and 13 test scenarios.

## Architecture

```
SharePoint folder (12 docs, as-is)  ──►  Workflow Studio
                                          ├─ Document Analyst → section map, hierarchy level
                                          ├─ Rule Extractor  → 48 rules (HARD / JUDGEMENT / ADVISORY / DERIVED)
                                          ├─ Consistency Checker → 12 findings, hierarchy enforcement
                                          ├─ Data & System Mapper → API contract + fixtures from intake
                                          ├─ Blueprint Composer → stages, agents, skills
                                          ├─ Test Case Generator → golden scenarios
                                          └─ Change Impact Analyst → feedback / re-upload diff
                                                 │  approved blueprint v1.0
                                                 ▼
Citizen user (chat, EN/ZH)  ──►  Workflow Assistant
                                  ├─ Case Orchestrator (state, decision pack)
                                  ├─ 11 specialist runtime agents, 24 runtime skills
                                  ├─ Human tasks: approver inbox, gates, exception review
                                  └─ Demo controls: identity, clock, fault injection
                                                 │  REST (OpenAPI)
                                                 ▼
Mock system layer — 9 systems, 26 endpoints, deterministic fixtures, `meta.simulated=true`
Product Master · ERP Pricing & Cost · Sales & Stock Insights · PromoHub · Trade Funding Register ·
Authority Directory · Compliance Register · Store Network · Approval & Notification Hub
```

Design principles the platform enforces (all traceable to the documents):

- **Only humans decide.** No agent can set a decision field; the DoA §8 says so and the API only allows it via a human task.
- **Every number shows its inputs, formula and policy version.** Margin Policy §12.
- **Missing data pauses the case.** No estimates, no defaults (H-28).
- **Document hierarchy wins over feedback.** Studio refuses to encode a rule that contradicts a higher-level policy and drafts a change request to the policy owner instead.
- **Simulation is visible.** Every card with system data carries a SIMULATED badge.

## The two user experiences

### Workflow Studio (process owner, DataLab)

| View | What the audience sees |
|---|---|
| Knowledge workspace | The 12 files with level (1 policy → 4 informative), version, owner, effective date; the small intake for systems |
| Knowledge model | 10 roles, 48 rules by type with citations, 10 glossary terms, 12 findings with proposed resolutions |
| Blueprint | Draft 0.1 (12 stages) → approved 1.0 (14 stages); click any stage for its rules, systems, pauses and outputs |
| Agents and skills | 8 Studio agents, 12 runtime agents, 34 skills, marked reusable vs workflow-specific |
| Review and change | Plain-language feedback → accepted / accepted-as-advisory / accepted-with-record / rejected with citation; before/after diff and impact on stages, skills, tests |
| Test and publish | 13 golden scenarios with expected values; approve a numbered version |

### Workflow Assistant (citizen user, approvers)

- Chat in English or Chinese; the assistant looks up the item as soon as it is named and confirms back.
- Progressive intake: item and intent first, regulatory screen, then offer details — nobody fills a forecast for a prohibited item.
- Case panel: stage progress, item facts with sources, check results (green / amber / red), cut-off table, routing with named people and delegation references.
- Approver inbox: decision pack per DoA template, Approve / Approve with conditions / Return / Reject; Compliance and Supply gates alongside.
- Status questions at any time ("where are my cases?"), including after the demo clock is advanced.

## Source documents (mock, as they would sit on SharePoint)

| # | Document | Level | What it contributes | Deliberate realism |
|---|---|---|---|---|
| 01 | Promotion Request & Approval SOP v1.4 | 2 | Process, roles, SLAs, KPIs | Leftover Band B ≤150k text (F-01); Flash cut-off 5 WD vs calendar 3 (F-02) |
| 02 | Delegation of Authority — Promotions & Pricing v3.2 | 1 | Bands A–D, ten escalation conditions, delegation, SoD, "systems may not approve" | Hero depth threshold changed 30→35% in this version |
| 03 | Promotional Pricing, Margin & Funding Policy v2.1 | 1 | Floors by category and brand type, formulas, funding recognition, frequency, multi-buy worst case, plausibility | Effective cost defined only here (F-04); plausibility scope gap (F-10) |
| 04 | Regulatory & Restricted Category Guidelines v1.2 | 1 | Prohibited and restricted classes, reference price 28/90 and 14-day rule, claims | Reference price basis left as open question (F-08) |
| 05 | Promotion Setup & Go-Live Checklist v1.0 | 3 | Pricing Ops pre-approval feasibility §2 and T-timeline | Requires price zone and event code that the form doesn't collect (F-03) |
| 06 | Supplier Trade Funding Procedure v1.3 | 2 | Funding types, statuses, seven evidence checks, coverage outcomes | Free goods and co-op media not recognised in economics |
| 07 | Promotion Cycle Calendar FY26 H2 | 3 | Cycles C20–C28, cut-offs, holidays, events SD1111/BF26/HLTH26 | Source of the Flash 3 WD rule |
| 08 | Promotion Request Form — template and guidance | 3 | Sections A–E, mandatory fields | Missing fields vs Checklist (F-12) |
| 09 | Trading Meeting Minutes 8 Sep 2026 | 4 | Tacit rules: own-brand <40% FYI Rachel; skincare hero no promo in C23; hero = strategicFlag; Rachel's leave; Fiona's October delegate; Sunveil funding; OMG expedite | Where the "how we actually work" lives |
| 10 | Workflow System Context Intake | — | Nine systems, fields, simulation requirements, aliases | The only new artefact a BU fills in |
| 11 | Funding Confirmation Letter FC-2026-041 | evidence | Uploaded mid-case in Scenario B | Seven checks pass |
| 12 | Post-Promotion Evaluation C19 Health Week | 4 | Uplift benchmarks and modifiers; "Omega-3 over-forecasts in 11.11" | Feeds plausibility |

## Mock system layer

`mock-apis/openapi.yaml` (26 paths, 21 schemas) and `mock-apis/fixtures.json` (14 items, 7 promotions, 7 funding commitments, 24 people, 7 delegations, 12 store scopes, cycles, event codes, benchmarks, compliance rules). `mock-server-behaviour.md` specifies determinism, `X-Demo-Clock`, `X-Demo-Fault` (ERP cost timeout, PromoHub validation warning, Register unavailable), the authority resolution algorithm and ID conventions. Fixtures were generated by a script that also verifies every scenario's arithmetic, so the numbers in the storyline, golden scenarios and fixtures agree.

## Demo storyline (≈40 minutes)

| Min | Segment | Scenario | Message |
|---|---|---|---|
| 0–3 | Frame | — | The BU's real documents, unchanged; one small intake for systems; simulated systems clearly labelled |
| 3–11 | Studio: from documents to workflow | J | Knowledge model, findings F-01/F-02/F-05; Mei's seven feedback items incl. the rejected DoA override; blueprint 1.0 approved |
| 11–15 | First case, clean | A | Conversational intake, all checks, Band A, Vivian approves, simulated PromoHub draft and handover |
| 15–20 | Evidence in the loop | B | Funding pending → letter upload → verified → re-computed; frequency at limit; Band B routing |
| 20–24 | The platform says no, well | C | Below floor, stacking, frequency → exception options, withdraw and notify |
| 24–26 | Regulatory | D | Infant formula blocked; alternatives with Compliance gate and delegate |
| 26–29 | Timing and options | E or F | Reference price rule with fallback wording; or missed leaflet cut-off with option framing |
| 29–33 | Event promotion | G | Funding cap, plausibility with event modifier, stock gate with expedite |
| 33–35 | Ask the knowledge | K | Flash on ibuprofen; Flash cut-off with provenance |
| 35–38 | Two weeks later | L | Clock to 13 Oct: reminders, delegate rerouting, cut-off proximity |
| 38–40 | When data is missing | M | ERP timeout → pause, no estimate, retry |

Backup: H (mix-and-match worst case, aggregation) and I (segregation of duties, forecast correction re-bands).

## Mapping to Kevin's questions

### Q1 — BU maturity journey

| Phase | What a BU can build or operate | Demo evidence | Trigger to move on |
|---|---|---|---|
| Q4 PoC | One workflow from its own documents; citizen users run cases against simulated systems; process owner changes the workflow via feedback | Everything in this pack | Process owner approves blueprint; ≥ 3 requesters complete cases; findings list resolved |
| Q1–Q2 | Same workflow on 2–3 live read-only systems (Product Master, ERP, PromoHub read); approvals still in the Assistant | Intake §10 marks which endpoints are read-only and low-sensitivity | Read-only integration signed off by Group IT; decision pack accepted by Finance as audit evidence |
| Q2–Q3 | Second workflow in the same BU reuses 21 of 34 skills; write-back to PromoHub draft | `agents-and-skills.yaml` reuse list | Two workflows share ≥ 50% skills; Pricing Ops accepts drafts |
| H2 | Second BU onboarded; cross-BU governance of shared rules (DoA, regulatory) | Findings and hierarchy model | Same concept (e.g. "hero SKU", "net investment") defined differently by two BUs → ontology work starts |

### Q2 — Toolkit maturity journey

| Aspect | Q1 MVP | Later |
|---|---|---|
| What the BU touches | Studio (process owner) and Assistant (everyone); no prompt writing, no agent building | Skill library browsing, cross-workflow dashboards |
| What DataLab / ASW provides | SharePoint folder access, one intake per workflow, process owner time (~2 h/week), approver participation, sign-off on findings | Read-only API access, then write-back scopes; identity integration |
| What Nagarro provides | Harness, Studio and Assistant, mock system layer, extraction and consistency engine, coaching for process owners | Integration adapters, evaluation harness, ontology accelerator when triggered |
| How it evolves | Prompt-free from day one; agents are generated, versioned and testable | Skills become shared assets; ontology replaces per-BU glossaries |

## Real vs simulated

| Real in the demo | Simulated |
|---|---|
| Document reading, rule extraction, consistency findings, blueprint generation, feedback handling | All nine business systems (fixtures behind OpenAPI) |
| Deterministic economics, routing, cut-off maths | Approver identities (presenter switches persona) |
| Conversational intake in EN/ZH, evidence extraction from the uploaded letter | Finance verification of funding evidence, Pricing Ops actions, notifications |
| Decision pack generation and audit trail | Clock and faults (demo controls) |

## Ownership

| Item | BU (Trading / TM) | DataLab | Nagarro | Group IT |
|---|---|---|---|---|
| Documents and intake | Own, keep on SharePoint | Curate, check completeness | Read | — |
| Findings resolution | Process owner decides | Facilitates | Presents | — |
| Blueprint approval | Process owner | Reviews | Generates | — |
| Mock system layer | Validates field realism | Approves aliases | Builds | Confirms shape vs real systems |
| Case testing | Requesters and approvers | Observes, collects feedback | Coaches | — |
| Audit evidence | Finance accepts decision pack | — | Provides | Security review |

## Build notes for the coding agent

- Stack is free; the contract is the OpenAPI, the fixtures, the blueprint YAML and the golden scenarios. Build the mock server first and make `testing/golden-scenarios.md` pass as automated tests before any UI.
- Economics, routing and cut-off logic are deterministic code, not LLM calls; the LLM does intake, explanation, evidence extraction and Studio reasoning.
- The Studio's extraction output must be reproducible for the demo: cache the knowledge model and blueprint; re-run live only for the feedback session.
- Demo controls: identity switcher (24 people), clock, three faults, reset to seed.
- UI copy uses "Promotion Owner" (Mei's feedback); rule IDs and citations visible on hover, not in the chat text.

## Open questions to validate with DataLab before build

1. Is promotion approval the workflow they want first, or should the same pack be shaped for another candidate (e.g. new item listing, markdown approval)?
2. Which of the nine systems exist under these names or aliases at Watsons HK, and which are spreadsheets today? This changes the Q1–Q2 integration column.
3. Who is the real process owner who would play Mei's role in the PoC, and can they give ~2 hours a week?
4. Are Microsoft 365 / SharePoint read permissions for a Nagarro-hosted harness acceptable, or should the PoC run inside ASW's tenant?
5. Which language mix do requesters actually use in chat — English, Cantonese-influenced Chinese, or mixed?

## Pack contents

See `ASW-Promotion-Approval-Mock-Artifact-Pack.md` for the index and review questions per artefact.
