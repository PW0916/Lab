# Golden Scenarios — Expected Values

Demo clock: **Monday 28 September 2026** unless stated. All values computed from `mock-apis/fixtures.json` v2.0 using the formulas in the Margin Policy v2.1 and DoA v3.2. Margins shown to two decimals; the floor test uses unrounded values. Every scenario is fictional.

Legend: **Live** = run interactively in the demo; **Backup** = ready to run if time or questions allow; **Studio** = build-time scenario.

| # | Scenario | Mode | Rules exercised |
|---|---|---|---|
| A | Own-brand pilot price cut — clean Band A with advisory | Live | H-01, H-04–H-06, H-15, H-16, H-18, H-21, H-22, H-26, H-27, J-05, A-01, H-29, H-30 |
| B | Third-party hero SKU, 78 stores — funding evidence upload, Band B | Live | H-08–H-10, H-15 (at limit), H-16, H-21–H-23, H-25 |
| C | Below-floor item with stacking conflict and frequency breach — exception options | Live | H-14, H-15, H-16, H-17, H-23, J-01, H-08 (expired) |
| D | Prohibited class blocked; permitted alternatives with Compliance gate | Live | H-02, H-03, J-06, H-16 |
| E | Recent price increase — Special Price wording and Compliance gate; off-invoice cost | Live | H-26, H-12, H-16, H-22 |
| F | Missed leaflet cut-off — option framing; timing risk | Live | H-06, J-02, H-13, H-14 |
| G | 11.11 hero SKU — funding cap, stock shortfall gate, forecast plausibility with event modifier | Live | H-09, H-10, H-27, J-04, J-05, A-03, F-03 |
| H | Mix-and-match "Buy any 2 save HK$30" — eligibility, worst-case allocation, aggregation | Backup | H-01, H-20, H-21, H-09 (partial), H-13 |
| I | Category Lead requests own item — segregation of duties, forecast correction re-bands | Backup | H-24, J-05, H-22 |
| J | Studio: process owner feedback on the draft blueprint | Studio | Feedback items 1–7; F-02; consistency guardrail |
| K | Knowledge Q&A with citations | Live | RT-02; H-07; H-02; H-16 |
| L | Status query; demo clock advanced to 13 Oct — reminders, delegate rerouting, cut-off proximity | Live | H-25, H-32, H-06 |
| M | ERP cost timeout — no estimate, pause, retry | Live | H-28, fault injection |

---

## A — Watsons Vitamin C, pilot 20 stores (Band A)

**Request (Jason Lo, TM Exec Health):** `WTC-VITC-1000-20` 129 → **89**, `PILOT-20` (20 stores), STORE only, no leaflet, C21 (8–21 Oct), forecast 1,000, "was HK$129" claim intended, no funding.

| Check | Expected |
|---|---|
| Item | ACTIVE, own brand, HEALTH_SUPPLEMENT (proceed), HERO |
| Cut-off | In-store 1 Oct (+3 days); Band A decision expected by 30 Sep → feasible |
| Effective cost | 55.00 (no off-invoice) |
| Margin | (89 − 55) / 89 = **38.20%** vs own-brand floor 38% → pass |
| Advisory A-01 | 38.20% < 40% → FYI to Rachel Tsang |
| Depth | 40 / 129 = **31.01%** (≤ 35% hero threshold, ≤ 40%) |
| Duration | 14 days |
| Frequency | STORE 2 + 2 = 4 ≤ 6 |
| Reference price | 129 since 1 Mar 2026 → 221 days; no increase in 14 days → "was HK$129" permitted |
| Plausibility | Benchmark 160 × 2 × (3.0 − 0.2 local + 0.2 hero) = 960; range 256–1,248; forecast 1,000 → no flag |
| Stock | 14,200 ≥ 1,100 → OK |
| Investment | 40 × 1,000 = **HK$40,000** → **Band A** |
| Routing | Approver Vivian Chan (E10234); informed Rachel Tsang (A-01); no reviewer |
| Case | `PR-2026-1042`; decision pack `DP-2026-1042-v1`; task `AT-2026-3301` |
| After approval | PromoHub draft `PD-2026-1042` [SIMULATED], validation PASSED; handover note with Checklist §3 timeline (T-10 = 28 Sep → draft within 1 WD of approval; price file T-2 = 6 Oct; go-live 8 Oct) |

## B — Glow Radiance Serum, 78 stores (funding evidence, Band B)

**Request (Carmen Siu, TM Exec Beauty):** `GLW-SRM-30ML` 199 → **139**, `HKI-KLNE` (78 stores), STORE only, no leaflet, C22 (22 Oct–4 Nov), forecast 1,800, funding claimed: Glow Beauty scan-back HK$12/unit (FC-2026-041).

| Check | Expected |
|---|---|
| Funding lookup | FC-2026-041 SCAN_BACK 12.00, cap 2,000, 1 Oct–30 Nov, STORE, status **AGREED_PENDING_EVIDENCE** → recognised 0; pause: "upload letter now or proceed with zero?" |
| Without funding | Margin (139 − 82)/139 = **41.01%** (floor 32%); investment 60 × 1,800 = **108,000** → Band B |
| Letter uploaded | Extracted: Cheryl Kwan (authorised), GBL/TF/2026/0917, item, SCAN_BACK 12.00, cap 2,000, 1 Oct–30 Nov, STORE, min price 129 → **VERIFIED**; status → CONFIRMED (verifier: Finance Controller SIMULATED) |
| Coverage | Period FULL; channels FULL (STORE); cap 2,000 ≥ 1,800 → no proration; price 139 ≥ 129 |
| With funding | Margin (139 − 82 + 12)/139 = **49.64%**; investment (60 − 12) × 1,800 = **HK$86,400** → **Band B** |
| Depth | 60 / 199 = 30.15% (hero ≤ 35%) |
| Frequency | STORE 4 (PR-2026-0871, 30 Jul–26 Aug) + 2 = **6 = limit** → note "at limit; a further promotion before 21 Jan would breach" |
| A-02 | C22, not C23 → not triggered |
| Reference price | 199 since 1 Feb → permitted |
| Plausibility | 380 × 2 × (2.2 + 0.2 hero) = 1,824; forecast 1,800 → no flag |
| Stock | 5,400 + 2,000 (ETA 15 Oct ≤ 19 Oct) = 7,400 ≥ 1,980 → OK |
| Cut-off | In-store 15 Oct (+17 days) |
| Routing | Reviewer Priscilla Lam (2 WD) → Approver Rachel Tsang (expected decision 5 Oct, available); informed Samantha Yip |
| Case | `PR-2026-1043` |

## C — Sunveil SPF50, HK-ALL + ESHOP (exception options)

**Request (Carmen Siu):** `SUNV-SPF50-100` 145 → **109**, `HK-ALL` + ESHOP, leaflet yes, C22, forecast 3,000, funding claimed "lump sum FC-2026-033".

| Check | Expected |
|---|---|
| Funding | FC-2026-033 LUMP_SUM 30,000, 1 Jul–31 Aug → **EXPIRED** → 0 |
| Regular margin | (145 − 112)/145 = **22.76%** — already below the 32% skincare floor |
| Promo margin | (109 − 112)/109 = **−2.75%** |
| Floor price | 112 / 0.68 = **HK$164.71** — above regular price; no promotional price can meet the floor unfunded |
| Min funding at 109 | 0.32 × 109 − (109 − 112) = **HK$37.88/unit** (minutes 8 Sep item 3 said ≈ HK$38) |
| Stacking | PM-2026-1180 Skincare Member Day 2nd-item-50% on APP + ESHOP, C22 → **blocking conflict on ESHOP** |
| Frequency | STORE 6 + 2 = 8; ESHOP 6 + 2 = 8 → **> 6** |
| Depth | 24.83% |
| Investment | 36 × 3,000 = 108,000 (Band B by value) |
| Escalations | Below floor → **C**; unresolved stacking → **C**; frequency → ≥ B. Result **Band C** (Priscilla Lam review, Andrew Kwok approve) |
| Options offered | (1) Withdraw — recommended until supplier funding meeting (Samantha, 25 Sep action); (2) Drop ESHOP to clear the conflict — floor still fails; (3) Proceed as exception with stated reason/mitigation → Band C; (4) Ask supplier for ≥ HK$37.88/unit confirmed funding then resubmit |
| Case | `PR-2026-1044` status EXCEPTION_REVIEW or WITHDRAWN per choice |

## D — Infant formula blocked; alternatives

**Request (Bonnie Lai, TM Exec Baby):** `PURE-IF-S1-900` "10% off for members" C22.

| Check | Expected |
|---|---|
| Screen | **BLOCKED_REGULATORY** — INFANT_FORMULA_S1, Guideline §3: no price, value, gift, bundle, member price, points or coupon promotion. Case closed with citation |
| Alternatives (J-06) | `PURE-GUM-S3-900` (FORMULA_S3, permitted with Compliance review); `KIND-DPR-M64` (Baby Care) |
| If S3 chosen: 328 → 298, HK-ALL, C22, forecast 1,200 | FC-2026-047 SCAN_BACK 15 CONFIRMED, cap 5,000, 1 Oct–31 Dec, all channels → recognised 15.00; margin (298 − 262 + 15)/298 = **17.11%** vs 15% → pass; investment (30 − 15) × 1,200 = **18,000 → Band A** (Ivan Cheng); **Compliance gate mandatory** — assigned to Jonathan Lee (DLG-2026-019, October delegate), due 3 WD; leaflet placement conditions listed; plausibility 410 × 2 × 1.5 = 1,230 → 1,200 OK |
| KIND note | Regular margin 19.58% vs 18% floor; any price below **HK$185.37** breaches the floor without funding — platform states this before the requester chooses |

## E — FreshMint twin pack: recent price increase

**Request (Bonnie Lai):** `FRSH-TP-2X150` 59.9 → **45**, `HKI-CORE`, STORE only, no leaflet, C21, forecast 1,600, "save HK$14.9" claim intended.

| Check | Expected |
|---|---|
| Reference price | Price 59.9 effective 18 Sep → **20 days** at price by 8 Oct (< 28) → comparative claim **not permitted**; no increase within 14 days (20 > 14) — first test fails anyway |
| Fallback | "Special Price HK$45" wording; Compliance wording review task → Jonathan Lee (Oct delegate); parallel gate |
| Proactive note | "If you move to C22 (22 Oct) the price will have been held 34 days and 'was HK$59.9' becomes permissible" |
| Cost | Landed 30.00 − off-invoice FC-2026-049 4.00 (1–31 Oct, CONFIRMED, FULL coverage) = **26.00** effective |
| Margin | (45 − 26)/45 = **42.22%** vs 25% → pass |
| Depth | 14.9 / 59.9 = 24.87% |
| Investment | 14.9 × 1,600 = **HK$23,840** → **Band A** (Winnie Tam). Off-invoice is not in the investment formula |
| Plausibility | 520 × 2 × 1.9 = 1,976; range 832–2,569; 1,600 → no flag |
| Stock | 9,600 + 5,000 (ETA 3 Oct) = 14,600 → OK |
| Cut-off | In-store 1 Oct (+3 days) |
| Case | `PR-2026-1045`, status AWAITING_GATES after Winnie approves until Compliance closes |

## F — AquaDew mask: missed leaflet cut-off

**Request (Carmen Siu):** `AQUA-MSK-5P` 89 → **69**, HK-ALL + ESHOP + APP, **leaflet yes**, C21, forecast 4,000, funding "free goods 500 units".

| Check | Expected |
|---|---|
| Cut-off | C21 leaflet cut-off was **17 Sep (−11 days)** → cannot be met |
| Options (J-02 framing) | (1) C21 without leaflet — in-store cut-off 1 Oct (+3), digital 28 Sep (**today**) → APP/ESHOP at risk; (2) **C22 with leaflet** — cut-off 1 Oct (+3) but Band B decision expected 5 Oct → **at risk; would need expedited review or a cut-off exception from Rachel Tsang**; (3) C23 with leaflet — cut-off 15 Oct (+17) → comfortable, but C23 carries SD1111 |
| Chosen | Option 2; platform offers to notify Rachel Tsang of a possible cut-off exception request (J-02) and to ask Priscilla for expedited review |
| Funding | FC-2026-058 FREE_GOODS 500 units → **not recognised** (reported) |
| Margin | (69 − 41)/69 = **40.58%** vs 32% → pass |
| Depth | 22.47% |
| Frequency | APP 3 (incl. Flash 3–4 Oct) + 2 = 5 ≤ 6; STORE/ESHOP 2 + 2 = 4 |
| Conflict | PM-2026-1207 App Flash 3–4 Oct is outside C22 → none |
| Plausibility | 1,900 × 2 × (2.2 + 0.2 leaflet) = 9,120; forecast 4,000 ≥ 80% of baseline period (3,040) and ≤ 130% of benchmark → no flag (note: conservative vs benchmark) |
| Stock | 9,800 + 4,000 (ETA 12 Oct ≤ 19 Oct) = 13,800 ≥ 4,400 → OK |
| Investment | 20 × 4,000 = **HK$80,000** → **Band B** (Priscilla → Rachel) |
| Case | `PR-2026-1046` with cut-off risk flag |

## G — OceanPure Omega-3, 11.11 (funding cap, stock gate, plausibility)

**Request (Jason Lo):** `OMG-FO-1000-100` 259 → **199**, HK-ALL + ESHOP + APP, leaflet yes, C23 (5–18 Nov), forecast 4,500, funding FC-2026-052 scan-back HK$25.

| Check | Expected |
|---|---|
| Funding | FC-2026-052 SCAN_BACK 25.00, cap 6,000, 1–30 Nov, all channels, CONFIRMED → period FULL, channels FULL, cap ≥ forecast → **25.00 recognised** |
| Margin | (199 − 150 + 25)/199 = **37.19%** vs 28% third-party V&S → pass |
| Depth | 23.17% |
| Investment | (60 − 25) × 4,500 = **HK$157,500** → **Band B** |
| Plausibility (no event code) | 520 × 2 × (2.8 + 0.2 hero) = 3,120; 130% = 4,056 → **4,500 flagged** |
| Platform prompt | "C23 carries SD1111. If this is an event promotion, the +40% modifier applies: benchmark 4,368, upper bound 5,678 → within range. Tag event code SD1111? (PromoHub also needs it — Checklist §2.6)" → Jason confirms |
| A-03 | PPE Part 3: "Omega-3 has over-forecast by 20–30% in 11.11 cycles" shown as caution |
| Stock | SOH 2,900; inbound 2,400 ETA 10 Nov > T-3 (2 Nov) → not counted; 2,900 < 4,950 → **Supply Chain gate** to Kelvin Ho with the expedite option (ETA 1 Nov, ~HK$3,000, confirm by 10 Oct → cover 5,300 ≥ 4,950) |
| Cut-off | Leaflet 15 Oct (+17) |
| Routing | Priscilla Lam review → Rachel Tsang approve (expected 5 Oct); gate owner Kelvin Ho; informed Vivian Chan |
| Case | `PR-2026-1047` status AWAITING_FINANCE_REVIEW + AWAITING_GATES |

## H — Mix-and-match "Skincare & Beauty: Buy any 2, save HK$30" (backup)

**Request (Carmen Siu):** MULTI_BUY_SAVE, items GLW, AQUA, DERM, LUMI, SUNV, BLSM; HK-ALL + ESHOP + APP; leaflet yes; C24 (19 Nov–2 Dec, BF26); forecast 2,500 qualifying sets.

| Check | Expected |
|---|---|
| Eligibility | `BLSM-LIP-4G` PHASE_OUT, delist 30 Nov < promo end 2 Dec → **excluded** (or Clearance separately) |
| Worst-case partner | Lowest-priced eligible item = AQUA (89) |
| GLW | alloc 30 × 199/288 = 20.73 → 178.27 → margin **54.00%** pass |
| AQUA (with itself) | alloc 15.00 → 74.00 → **44.59%** pass |
| DERM | alloc 17.16 → 101.84 → **48.94%** pass |
| LUMI | alloc 19.23 → 139.77 → **49.92%** pass |
| SUNV | alloc 18.59 → 126.41 → **11.40%** vs 32% → **fails** (regular margin already 22.76%) → remove, fund, or exception |
| Funding | FC-2026-041 (GLW) period ends 30 Nov < 2 Dec → **PARTIAL_PERIOD → 0**; FC-2026-055 (LUMI) COOP_MEDIA → not recognised |
| Plausibility | Not applied to MULTI_BUY_SAVE (Margin Policy §10) → reported as "not checked (policy scope)" (F-10) |
| Investment | 30 × 2,500 = **HK$75,000** aggregated → **Band B** |
| Routing | Priscilla Lam → Rachel Tsang; Samantha Yip informed (items span Skincare and Cosmetics) |
| Cut-off | Leaflet 29 Oct (+31) |

## I — Vivian Chan requests her own item (backup)

**Request (Vivian Chan, Category Lead V&S):** `WTC-MULTI-60` 159 → **119**, HK-ALL, all channels, C22, forecast **800**.

| Check | Expected |
|---|---|
| Margin | (119 − 62)/119 = **47.90%** vs 38% → pass (no A-01) |
| Depth | 25.16% |
| Initial investment | 40 × 800 = 32,000 → Band A → approver would be Vivian → **segregation of duties** → Tommy Chu via DLG-2026-011 |
| Plausibility | Baseline period 900 × 2 = 1,800; 80% = 1,440 → **800 flagged low** ("looks like a weekly or single-scope number"); benchmark 5,400 |
| Correction | Vivian: 4,500 → within 4,320–7,020 → investment 40 × 4,500 = **HK$180,000 → Band B** → Priscilla Lam review, Rachel Tsang approve; SoD no longer relevant; the re-banding is explained |
| Stock | 8,300 (inbound 20 Oct > 19 Oct not counted) ≥ 4,950 → OK |
| Cut-off | Digital 12 Oct (+14) |

## J — Studio feedback (build-time)

See `workflow-blueprint.yaml` → `feedbackApplied`. Expected Studio behaviour per item: 1 accept (re-sequence), 2 accept (new stage), 3 accept as advisory with pending confirmation, 4 accept with recorded deviation, **5 reject with citation of DoA §4 and generate a change request to the policy owner**, 6 accept (labels only), 7 accept (split stage). Change Impact Analyst lists affected stages, skills and test scenarios for each accepted item.

## K — Knowledge Q&A

| Question | Expected answer (abridged) |
|---|---|
| "Can I run a Flash on MediRelief Ibuprofen this weekend?" | No — `MEDR-IBU-200-24` is PHARMACY_ONLY_P1: no public price promotion in any mechanic (Guideline §3). Also, OTC general-sale medicines cannot run Flash promotions (Margin Policy §3). |
| "What's the Flash cut-off?" | 3 working days before the Flash start (Calendar v2.0 §2). Note: SOP v1.4 §5.2 still says 5; the process owner decided to apply the calendar and log an SOP revision (F-02). Example: Flash on Sat 3 Oct → approve by Tue 29 Sep (1 Oct is a holiday). |
| "Who approves a HK$120k promotion if Rachel is away?" | Band B → Finance review (Priscilla Lam) then Head of Trading. If the expected decision date falls 12–16 Oct, Michelle Fung via DLG-2026-018 (DoA §6.3). |
| "Why did my Sunveil request go to Band C?" | Cites H-16/H-17 (below floor), H-14 (stacking), H-15 (frequency) with the measured values from case PR-2026-1044. |

## L — Status and time travel

Presenter sets `X-Demo-Clock: 2026-10-13` and asks "Where are my cases?"

| Case | Expected |
|---|---|
| PR-2026-1042 (A) | APPROVED 29 Sep by Vivian Chan; PD-2026-1042 validated; price file due 6 Oct (done, simulated); LIVE from 8 Oct |
| PR-2026-1043 (B) | Finance review completed 1 Oct; approval task to Rachel Tsang created 1 Oct; **reminder sent 5 Oct**; Rachel unavailable 12–16 Oct → **reassigned to Michelle Fung (DLG-2026-018) on 12 Oct**; in-store cut-off 15 Oct → **2 days left** — flagged |
| PR-2026-1047 (G) | Awaiting Rachel → reassigned to Michelle Fung; Supply gate: Kelvin Ho confirmed expedite 9 Oct (simulated) → gate closed; leaflet cut-off 15 Oct → 2 days left |
| PR-2026-1045 (E) | Approved by Winnie Tam 29 Sep; Compliance gate closed 2 Oct (APPROVED_WITH_WORDING_CHANGES: "Special Price HK$45"); LIVE from 8 Oct |
| PR-2026-1046 (F) | Cut-off exception requested 29 Sep; Rachel approved exception 30 Sep (simulated); Band B approved 2 Oct; leaflet in production |

## M — ERP cost timeout

**Request (Carmen Siu):** `DERM-CLN-150` 119 → **95**, HK-ALL, STORE only, C22, forecast 2,500, with `X-Demo-Fault: erp-cost-timeout` on the first cost call.

| Step | Expected |
|---|---|
| Cost call | 504 after 8 s → "ERP cost unavailable. Margin and floor test **not computable**. I will not estimate the cost (Margin Policy §12). Options: retry now, or park the case and notify Finance." Status WAITING_DATA |
| Retry | Cost 52.00 → margin (95 − 52)/95 = **45.26%** vs 32% → pass; depth 20.17%; investment 24 × 2,500 = **HK$60,000 → Band B** |
| Conflict note | PM-2026-1180 Member Day (APP + ESHOP, C22) includes DERM — STORE-only request does **not** conflict; adding APP/ESHOP would |
| Plausibility | 640 × 2 × 2.2 = 2,816; 130% = 3,661 → 2,500 OK |
| Stock | 5,200 + 2,000 (ETA 14 Oct) = 7,200 → OK |
