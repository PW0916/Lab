# WTCHK Promotion Approval Citizen Demo

Fictional Watsons Hong Kong (WTCHK) demo: **Workflow Studio** (process owner) plus **Workflow Assistant** (citizen chat), on a mock layer of nine systems and 26 OpenAPI endpoints. All names, items, suppliers and thresholds are fictional. Every system card is labelled **SIMULATED**. Demo clock defaults to **Monday 28 September 2026**.

The contract is `data/mock-apis/openapi.yaml`, `data/mock-apis/fixtures.json` v2.0, `data/generated-blueprint/*.yaml` and `data/testing/golden-scenarios.md`. Economics, routing and cut-offs are deterministic code — never LLM guesses.

## How to run

```bash
python3 -m pip install -r requirements.txt
./scripts/run.sh
```

Open http://127.0.0.1:8000

- **Workflow Studio** — 12 SharePoint documents, 48 rules, 12 findings, draft 0.1 → approved 1.0, Mei Wong’s seven feedback items (including the rejected DoA override).
- **Workflow Assistant** — conversational intake (EN/ZH), case panel, approver inbox, identity switcher, clock and fault injection.

Dev mode (Vite + API reload):

```bash
python3 -m pip install -r requirements.txt
./scripts/dev.sh
```

UI at http://127.0.0.1:5173 · API at http://127.0.0.1:8000

## Tests

```bash
python3 -m pytest tests/test_golden_scenarios.py -q
```

Replays golden scenarios A–M against the engine and mock derived fields (margin, depth, investment, bands, routing, cut-offs, funding verification, SoD, knowledge answers, Studio guardrail).

## Demo path (≈40 minutes)

1. Studio as **Mei Wong** — open findings F-02, apply the seven review items, approve blueprint 1.0.
2. Assistant as **Jason Lo** — Vitamin C pilot at 89 (Scenario A). Switch to **Vivian Chan** and Approve.
3. **Carmen Siu** — Glow Serum + funding letter (B); Sunveil withdraw (C).
4. **Bonnie Lai** — Stage 1 block then Stage 3 (D); FreshMint Special Price (E).
5. Clock to **2026-10-13** — “Where are my cases?” (L). Toggle **ERP cost timeout** for DermaCalm (M).

Hint chips on the Assistant replay the conversation-script openers. **Seed storyline** pre-creates A–G so time-travel can be shown without a full replay.

## Layout

```
backend/app/     FastAPI mock systems + Studio + Assistant + engine
frontend/        Vite + React workbench
data/            Review-pack fixtures, OpenAPI, blueprint, 12 documents, golden scenarios
tests/           Golden scenario tests
```
