# Promotion Approval Mock Artifact Pack — v2 Index and Review Guide

Everything here is fictional and built for the Watsons HK ("WTCHK") demo. Review order is top to bottom; each artefact lists the questions worth answering before the coding agent starts.

## 1. Source documents — `mock-documents/`

These are what a BU would leave on SharePoint as-is. They are written as real operating documents: numbered sections, versions, owners, effective dates, worked examples, appendices — and the kind of inconsistencies real document sets carry.

| File | Type · Level | Size | Contains | Built-in issue the platform must surface |
|---|---|---|---|---|
| `01-Promotion-Request-and-Approval-SOP-v1.4.md` | SOP · L2 | ~12 pages | Purpose, scope, document hierarchy §1.3, roles, mechanics table, process §4–§8, SLAs, KPIs, RACI, appendices | Leftover "Band B ≤150k" note (F-01); Flash cut-off 5 WD (F-02); "hero" used but undefined (F-07) |
| `02-Delegation-of-Authority-Promotions-and-Pricing-v3.2.md` | Policy · L1 | ~7 pages | Bands A ≤50k / B ≤200k / C ≤1M / D >1M; escalations §5.1–5.10; delegation rules §6; SoD §7; systems may not approve §8 | Hero depth threshold changed 30→35% between versions; change history shows it |
| `03-Promotional-Pricing-Margin-and-Funding-Policy-v2.1.md` | Policy · L1 | ~9 pages | Floors by category × brand type; effective cost; margin, depth, investment formulas; funding recognition; frequency ≤6/12 wk; multi-buy worst case; plausibility; §12 no estimates | Only document defining "effective cost" (F-04); plausibility excludes multi-buy (F-10) |
| `04-Regulatory-and-Restricted-Category-Guidelines-v1.2.md` | Guideline · L1 | ~6 pages | Prohibited / restricted classes with codes; reference price 28-day / 90-day, 14-day increase rule; claims; §9 mapping table | Reference price basis (national vs zone) left as open question (F-08) |
| `05-Promotion-Setup-and-Go-Live-Checklist-v1.0.md` | Checklist · L3 | ~4 pages | Pre-approval feasibility §2 (11 checks incl. price zone, event code, duplicate draft); T-timeline §3; go-live §4 | Needs fields the request form never asks for (F-03, F-12) |
| `06-Supplier-Trade-Funding-Procedure-v1.3.md` | Procedure · L2 | ~5 pages | Funding types, status lifecycle, seven evidence checks, coverage outcomes (FULL / PARTIAL_PERIOD / PARTIAL_CHANNEL / CAP_PRORATED) | Free goods and co-op media are real funding but not recognised in economics |
| `07-Promotion-Cycle-Calendar-FY26-H2.md` | Calendar · L3 | ~3 pages | C20–C28 with leaflet/in-store/digital cut-offs; Flash 3 WD; HK holidays; event codes SD1111, BF26, HLTH26, XMAS26 | Contradicts SOP on Flash cut-off (F-02) |
| `08-Promotion-Request-Form-Template-and-Guidance.md` | Form · L3 | ~3 pages | Sections A–E, mandatory markers, guidance notes | Gaps vs Checklist §2 (F-12) |
| `09-Trading-Meeting-Minutes-2026-09-08.md` | Minutes · L4 | ~3 pages | Seven items: own-brand <40% FYI; skincare hero freeze in C23; hero definition; Rachel's leave and delegate; Fiona's October delegate; Sunveil funding gap; Omega-3 expedite | Tacit rules not in any controlled document (F-05, F-06) |
| `10-Workflow-System-Context-Intake.md` | Intake · new | ~4 pages | Nine systems: purpose, owner, fields, sensitivity, latency, simulation requirements, aliases (e.g. "PromoHub" = "the promo tool") | The one artefact a BU has to fill in; PromoHub alias ambiguity (F-09) |
| `11-Funding-Confirmation-Letter-FC-2026-041.md` | Evidence | 1 page | Supplier letterhead, authorised signatory, ref, item, HK$12/unit, cap 2,000, period, channels, min price | Uploaded mid-case in Scenario B; all seven checks pass |
| `12-Post-Promotion-Evaluation-C19-Health-Week.md` | Report · L4 | ~3 pages | Uplift benchmarks by category, modifiers (depth, events, leaflet, local, hero), lessons incl. Omega-3 over-forecasting | Feeds plausibility and advisory A-03 |

Review questions
- Does the document set feel like a real trading department's SharePoint? What is missing or over-engineered?
- Are the twelve built-in issues the right ones to show, or are there Watsons-typical inconsistencies we should add?
- Is the intake (`10`) small enough that a BU would actually fill it in?

## 2. Mock systems — `mock-apis/`

| File | Contents |
|---|---|
| `openapi.yaml` | 26 endpoints across 9 systems; 21 schemas; every response wrapped with `meta.simulated: true`, `meta.source`, `meta.asOf` |
| `fixtures.json` v2.0 | 14 items (own-brand and third-party across Health, Beauty, Baby, Personal Care incl. prohibited and restricted classes), price histories, costs and off-invoice, baselines by scope and channel, stock and inbound, 7 existing promotions (incl. Member Day stacking and App Flash), 7 funding commitments in every status, 24 people, 7 delegations with date ranges, 12 store scopes, cycles, event codes, benchmarks, compliance rules, demo faults |
| `mock-server-behaviour.md` | Determinism, `X-Demo-Clock`, `X-Demo-Fault`, authority resolution algorithm (band → escalations → SoD → delegation → availability), ID conventions, reset semantics |

Systems: Product Master · ERP Pricing & Cost · Sales & Stock Insights · PromoHub · Trade Funding Register · Authority Directory · Compliance Register · Store Network · Approval & Notification Hub.

Review questions
- Which of these systems exist at Watsons HK under another name, and which are spreadsheets today? (Drives the Q1–Q2 integration column.)
- Are field names and granularity believable to a Pricing Ops or Finance reader?
- Are the three faults the ones a real audience would ask about, or should we add e.g. a stale price file?

## 3. Generated blueprint — `generated-blueprint/`

What Workflow Studio is expected to produce from the documents above. These files are the target output the coding agent builds towards and the reference for the Studio demo segment.

| File | Contents |
|---|---|
| `knowledge-model.yaml` | 12 sources with hierarchy level; 10 roles; 48 rules (33 HARD, 6 JUDGEMENT, 4 ADVISORY, 5 DERIVED) each with statement, source citation, inputs, systems; 12 findings F-01…F-12 with proposed resolution and owner; 10 glossary terms |
| `workflow-blueprint.yaml` | Draft 0.1 (12 stages) and approved 1.0 (14 stages) with owners, rules, systems, pauses, outputs; the seven feedback items and how each was handled; case statuses; decision pack template |
| `agents-and-skills.yaml` | 8 Studio agents, 12 runtime agents (Case Orchestrator + 11 specialists), 34 skills with rule and system bindings; reusable vs workflow-specific split (21 / 13) |

Cross-check performed: every rule referenced by a stage or skill exists, and every rule is used at least once.

Review questions
- Is the 14-stage flow how Trading would describe their process, or is it too granular for the audience?
- Are the seven feedback items realistic things a Head of Trade Marketing would say?
- Is the rejected item (skip Finance for Band B <100k) the right example of the hierarchy guardrail?

## 4. Testing — `testing/`

| File | Contents |
|---|---|
| `golden-scenarios.md` | 13 scenarios A–M with every expected value (margins, depths, investments, bands, routing, cut-offs, plausibility, stock), plus the rules each exercises |
| `conversation-scripts.md` | Scripted dialogues for the live scenarios and the Studio feedback session, with presenter cues |

Scenario spread: clean Band A (A) · evidence upload (B) · below floor + stacking + frequency (C) · regulatory block (D) · reference price (E) · missed cut-off (F) · event, funding cap, stock gate, plausibility (G) · mix-and-match worst case (H) · SoD and re-banding (I) · Studio feedback (J) · knowledge Q&A (K) · time travel (L) · fault injection (M).

Review questions
- Which 7–8 scenarios make the 40-minute cut for Kevin's audience?
- Are the assistant's replies in the scripts the tone Watsons users would accept — too terse, too chatty?

## 5. Design — `ASW-Promotion-Approval-Demo-Design.md`

Architecture, the two experiences, storyline with timings, mapping to Kevin's two questions, real vs simulated, ownership, build notes for the coding agent, open questions for DataLab.

## 6. What changed from v1

| v1 | v2 |
|---|---|
| 6 documents, ~1–2 pages each | 12 documents with hierarchy, versions, appendices, deliberate inconsistencies |
| 4 systems, ~8 endpoints, 5 items | 9 systems, 26 endpoints, 14 items, 7 promotions, 7 funding records, 24 people, 7 delegations |
| 8 rules, 1 finding | 48 rules in four types, 12 findings |
| 11-stage blueprint, 4 agents | 12 → 14 stage blueprint with feedback log, 20 agents, 34 skills |
| 6 scenarios, headline numbers | 13 scenarios, every value computed and cross-checked against fixtures |
| Two-day build framing | Quality-first framing; build notes for a coding agent |
