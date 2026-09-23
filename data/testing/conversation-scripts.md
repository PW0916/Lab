# Conversation Scripts

Scripted dialogues for the live demo. The assistant's replies show the intended tone: short, specific, every number traceable, options instead of dead ends, and a `SIMULATED` badge on any system data. Presenter lines are in **bold**; assistant lines are plain. Bracketed notes describe what the screen shows.

Personas are played by the presenter switching identity in the demo header (Jason Lo, Carmen Siu, Bonnie Lai, Vivian Chan, Mei Wong, approvers via the inbox panel).

---

## Studio — Scenario J (build-time, ~8 minutes)

**[Mei Wong opens Workflow Studio, points it at the SharePoint folder "Promotion Approval — Knowledge" with the 12 documents and the intake template.]**

Studio: I read 12 documents: 4 policies (level 1), 2 procedures (level 2), 3 checklists/calendars/forms (level 3), 2 informative notes (level 4) and the system intake. I extracted 10 roles, 48 rules (33 hard, 6 judgement, 4 advisory, 5 interpretations) and 12 findings. Three findings need your decision before I finalise the workflow.

[Knowledge model view: rules grouped by type; each rule shows its citation. Findings panel with F-01, F-02, F-05 highlighted.]

**Mei: Show me F-02.**

Studio: Flash cut-off. SOP v1.4 §5.2 says 5 working days. Calendar v2.0 §2 says 3 working days and notes the SOP is pending update; the 8 September minutes confirm 3. Under the hierarchy the SOP would govern, so I have applied 5 as the safe default. Do you want to apply 3 and record an SOP revision action?

**Mei: Apply 3. Log the revision for me.**

Studio: Done. H-07 now applies 3 working days; the deviation is recorded against SOP §5.2 with you as owner. Scenario K.2 and the Flash worked example were updated.

**Mei: Here's the draft workflow. [Opens blueprint 0.1 — 12 stages.] A few things. First, you're asking for forecast and funding before you've even checked the item is allowed. Screen the item first.**

Studio: Accepted. Intake is now two stages: item and intent (S01), then offer details after the regulatory screen (S04). Affected: 2 stages, 1 skill, scenarios D and A.

**Mei: Second, Pricing Ops do a feasibility check before approval — it's in their checklist. Add it.**

Studio: Accepted. New stage S10 "Setup feasibility" before routing, owned by Setup Readiness, running Checklist §2.1–2.11. That also resolves F-03: price zone and event code are now collected at intake.

**Mei: Rachel wants to see any own-brand promotion under 40% margin.**

Studio: I found that in the 8 September minutes (item 1) and encoded it as advisory A-01. I can wire it as an "informed" notification to the Head of Trading — not a band change. Because it is not in a controlled document, I will mark it pending Rachel's confirmation. Proceed?

**Mei: Yes. And rename Requester to Promotion Owner.**

Studio: Both applied. Labels changed in the assistant and decision pack; the rule identifiers are unchanged.

**Mei: Also — Band B under HK$100k, skip the Finance review. It slows everything down.**

Studio: I can't encode that. DoA v3.2 §4 requires Finance review for all Band B promotions, and the DoA is a level-1 policy that the SOP and this workflow cannot override. I have drafted a change request note to Andrew Kwok as policy owner with your reasoning. Do you want me to send it?

**Mei: Send it. Last one: split economics and stock — Finance owns one, Supply Chain the other.**

Studio: Accepted. S08 Promotion economics and S09 Supply readiness now have separate owners and outputs. Blueprint 1.0 has 14 stages, 12 runtime agents and 34 skills. Approve?

**Mei: Approve.**

[Blueprint 1.0 marked APPROVED_BY_PROCESS_OWNER with Mei's name and date; agents and skills panel; "13 test scenarios generated" badge.]

---

## Scenario A — Jason Lo, Vitamin C pilot (~4 minutes)

**Jason: I want to run Vitamin C effervescent at 89 in the 20 pilot stores for the next cycle.**

Found `WTC-VITC-1000-20` Watsons Vitamin C 1000mg Effervescent 20s — own brand, ACTIVE, hero SKU, regular HK$129 [SIMULATED · Product Master, ERP]. Next cycle is C21, 8–21 Oct. `PILOT-20` is 20 stores in HKI-CORE and KLN-EAST. Stores only, no leaflet — correct?

**Jason: Correct.**

Regulatory: HEALTH_SUPPLEMENT — permitted, no review needed unless the copy makes claims. I need three more things: forecast units for the two weeks, whether you want to show "was HK$129", and any supplier funding.

**Jason: 1,000 units, yes show the was-price, no funding — it's own brand.**

Checks complete. [Result card]
- Margin 38.20% — passes the 38% own-brand floor. Below 40%, so Rachel Tsang will be informed (Trading decision, 8 Sep).
- Depth 31.0%; 14 days; 4 promotion weeks in the last 12 — all within limits.
- "Was HK$129" is fine: price unchanged for 221 days.
- Forecast 1,000 is in line with the benchmark (960).
- Stock 14,200 covers it.
- Investment HK$40,000 → Band A → approver Vivian Chan.
- In-store cut-off is 1 Oct; Vivian's decision is due by 30 Sep.

Shall I send the decision pack to Vivian?

**Jason: Yes.**

Sent. Case PR-2026-1042. I'll tell you when Vivian decides.

**[Presenter opens the inbox as Vivian Chan: decision pack card with all numbers, sources, formulas and the DoA/Margin Policy versions. Clicks Approve.]**

Vivian approved PR-2026-1042 on 28 Sep. I have created PromoHub draft PD-2026-1042 [SIMULATED] and it passed validation. Handover to Daniel Ng's team: draft confirmed by 29 Sep, shelf-talkers ordered by 1 Oct, price file released 6 Oct, go-live 8 Oct. Rachel Tsang has been informed of the sub-40% margin.

---

## Scenario B — Carmen Siu, Glow Serum with funding letter (~5 minutes)

**Carmen: Glow Radiance Serum at 139 in Hong Kong Island Core and Kowloon East for C22. Glow Beauty is giving us 12 dollars a unit scan-back.**

`GLW-SRM-30ML`, regular HK$199, hero SKU. Scope `HKI-KLNE` = 78 stores; stores only? And forecast for the two weeks?

**Carmen: Stores only. 1,800 units.**

The Register has FC-2026-041: Glow Beauty scan-back HK$12, cap 2,000, 1 Oct–30 Nov, stores — but its status is **agreed, pending evidence**. Under the Margin Policy I can only recognise confirmed funding. Two options: upload the confirmation letter now, or I proceed with funding at zero (margin 41.01%, investment HK$108,000, Band B).

**Carmen: I have the letter. [Uploads 11-Funding-Confirmation-Letter-FC-2026-041.]**

Extracted: Glow Beauty Laboratories, signed by Cheryl Kwan (authorised contact), ref GBL/TF/2026/0917, item GLW-SRM-30ML, scan-back HK$12.00, cap 2,000, 1 Oct–30 Nov, stores only, minimum selling price HK$129. All seven checks pass → verified; the Register record is now CONFIRMED [SIMULATED verifier: Finance Controller]. Note: the letter excludes eShop and the app, so if you add digital later the funding will not count there.

Updated results:
- Margin 49.64% (floor 32%). Investment HK$86,400 → Band B.
- Frequency: this takes the serum to 6 promotion weeks in the rolling 12 — exactly at the limit. Another promotion before 21 January would need Band B justification.
- Stock 7,400 including inbound on 15 Oct — fine. Cut-off 15 Oct.
- Route: Finance review by Priscilla Lam, then Rachel Tsang. Decision expected by 5 Oct.

Send?

**Carmen: Send.**

Case PR-2026-1043 is with Priscilla.

---

## Scenario C — Carmen Siu, Sunveil below floor (~4 minutes)

**Carmen: Sunveil SPF50 at 109, all stores plus eShop, leaflet, C22, 3,000 units. We had a lump sum from Sunveil — FC-2026-033.**

FC-2026-033 expired on 31 August; it was used for the summer promotion. Funding recognised: zero.

I have to stop here rather than route this. [Result card, red]
- Sunveil's regular margin is 22.76% — already below the 32% skincare floor. At HK$109 the margin is −2.75%. The price that would meet the floor is HK$164.71, above the regular price, so no promotional price works without funding. The funding needed at HK$109 is HK$37.88 per unit.
- eShop conflict: Skincare Member Day (PM-2026-1180) already runs 2nd-item-50% on Sunveil in the app and eShop for C22.
- Frequency: 8 promotion weeks in the rolling 12 against a limit of 6.

Any of these makes it a Band C exception for Andrew Kwok with Finance review. Options:
1. Withdraw for now — the minutes show Samantha is meeting Sunveil about funding before C22.
2. Drop eShop to clear the conflict — the floor problem remains.
3. Proceed as an exception — I'll need the reason, expected benefit and mitigation for the pack.
4. Get confirmed funding of at least HK$37.88 per unit and resubmit.

**Carmen: Withdraw, and tell Samantha.**

Withdrawn as PR-2026-1044 with the analysis attached; Samantha Yip notified.

---

## Scenario D — Bonnie Lai, infant formula (~2 minutes)

**Bonnie: Can we do 10% off PureNest Stage 1 for members in C22?**

No. `PURE-IF-S1-900` is Stage 1 infant formula. Under the Regulatory Guidelines §3 it cannot be promoted in any mechanic — price, member price, points, gifts or bundles. I've recorded the request as blocked so there is an audit trail.

If you're looking for a Baby promotion for C22, two permitted options: PureNest Growing-Up Milk Stage 3 (`PURE-GUM-S3-900`) — allowed with a Compliance review of copy and leaflet placement, and it has confirmed scan-back funding of HK$15; or KinderSoft Nappies M (`KIND-DPR-M64`) — but its regular margin is 19.58% against an 18% floor, so anything below HK$185.37 would need funding.

**Bonnie: Stage 3 at 298, all stores, 1,200 units.**

Margin 17.11% (floor 15%) with the HK$15 funding; investment HK$18,000 → Band A → Ivan Cheng. A Compliance review is mandatory for Stage 3 — assigned to Jonathan Lee (covering for Fiona Lau in October), due in 3 working days. The promotion can be approved in parallel but not released until he closes it. Send?

---

## Scenario E — Bonnie Lai, toothpaste twin pack (~3 minutes)

**Bonnie: FreshMint twin pack, 59.9 down to 45, Island Core stores, C21, 1,600 units. Show the saving on the shelf talker.**

One issue with the saving message. The regular price went up from HK$54.9 to HK$59.9 on 18 September — by 8 October it will have been in place 20 days, and the Guidelines need 28. So "save HK$14.9" or "was HK$59.9" is not permitted for C21. Two ways forward:
- Run C21 as "Special Price HK$45" with no comparison — Compliance reviews the wording (Jonathan Lee, 3 working days), in parallel with approval.
- Move to C22: by 22 October the price will have held 34 days and the comparison is allowed.

**Bonnie: Keep C21, Special Price.**

Economics: FreshMint has a confirmed off-invoice of HK$4 for October, so the effective cost is HK$26. Margin 42.22% (floor 25%). Investment HK$23,840 → Band A → Winnie Tam. Cut-off 1 Oct. Sending the pack to Winnie and the wording to Jonathan.

---

## Scenario F — Carmen Siu, mask with leaflet (~3 minutes)

**Carmen: AquaDew masks 89 to 69, everywhere, in the leaflet, C21, 4,000 units. AquaDew are giving 500 free units.**

The C21 leaflet closed on 17 September, so that route is gone. Options:
1. C21 without leaflet — in-store cut-off 1 Oct is reachable; the digital cut-off is today, so app and eShop are at risk.
2. C22 with leaflet — cut-off 1 Oct. This is Band B (HK$80,000), and the normal review plus approval runs to 5 Oct, so it would need an expedited Finance review or a cut-off exception from Rachel Tsang.
3. C23 with leaflet — cut-off 15 Oct, comfortable; note C23 is the Singles' Day cycle.

**Carmen: Option 2. Ask Rachel for the exception.**

Done — exception request drafted for Rachel with Pricing Ops' impact note; Priscilla asked for expedited review. Free goods are recorded but not counted in the economics. Margin 40.58%, no conflicts (the app flash on 3–4 Oct is outside C22), stock fine. Case PR-2026-1046, flagged "cut-off at risk".

---

## Scenario G — Jason Lo, Omega-3 for 11.11 (~4 minutes)

**Jason: OceanPure Omega-3 at 199, all channels, leaflet, C23, 4,500 units. OceanPure funds 25 a unit — FC-2026-052.**

FC-2026-052 is confirmed: HK$25 scan-back, cap 6,000, 1–30 Nov, all channels — covers the whole promotion, no proration. Margin 37.19% (floor 28%). Investment HK$157,500 → Band B.

Two things to check with you:
- Forecast. Baseline is 520 a week; the benchmark for a hero third-party supplement is 3,120 for two weeks, so 4,500 is above the 130% line. But C23 carries Singles' Day — if this is an SD1111 event promotion the +40% modifier applies and 4,500 is within range. Shall I tag it SD1111? PromoHub needs the event code anyway.
- The last evaluation notes Omega-3 has over-forecast by 20–30% in 11.11 cycles.

**Jason: Tag it SD1111. Keep 4,500.**

Recorded with your confirmation. Stock: 2,900 on hand; the 2,400 inbound lands 10 Nov, after the promotion starts, so cover is short of the 4,950 needed. Supply Chain gate to Kelvin Ho — the minutes mention an expedite to 1 Nov for about HK$3,000 if confirmed by 10 Oct; I've put that in his task. Routing: Priscilla, then Rachel. Case PR-2026-1047.

---

## Scenario K — Knowledge questions (~2 minutes)

**Jason: Can I run a flash on MediRelief ibuprofen this weekend?**

No, on two grounds. MediRelief Ibuprofen is a pharmacy-only medicine — no public price promotion in any mechanic (Guidelines §3). And even general-sale OTC medicines are excluded from Flash promotions (Margin Policy §3).

**Jason: What's the flash cut-off now?**

Three working days before the Flash starts (Calendar v2.0 §2). The SOP still says five — Mei Wong has decided to follow the calendar and has logged an SOP update. For a Flash on Saturday 3 Oct, approval is needed by Tuesday 29 Sep because 1 Oct is a holiday.

---

## Scenario L — Time travel (~3 minutes)

**[Presenter sets the demo clock to 13 Oct 2026 and switches to Carmen.] Carmen: Where are my cases?**

As of 13 Oct:
- PR-2026-1043 Glow Serum — Finance review done 1 Oct. Rachel Tsang's approval task was reminded on 5 Oct and reassigned to Michelle Fung yesterday because Rachel is on leave 12–16 Oct (delegation DLG-2026-018). The in-store cut-off is 15 Oct — two days. I've flagged it urgent.
- PR-2026-1046 AquaDew — Rachel approved the cut-off exception on 30 Sep; Band B approved 2 Oct; leaflet in production.
- PR-2026-1044 Sunveil — withdrawn 28 Sep.

[Shows the same for Jason: PR-2026-1042 live since 8 Oct; PR-2026-1047 with Kelvin's expedite confirmed on 9 Oct and the approval reassigned to Michelle.]

---

## Scenario M — Fault injection (~2 minutes)

**[Presenter toggles "ERP cost timeout" in demo controls.] Carmen: DermaCalm cleanser 119 to 95, all stores, C22, 2,500 units.**

I couldn't get the cost from ERP — the request timed out. That means I can't compute the margin or test the floor, and I won't estimate it (Margin Policy §12). I can retry now, or park the case and tell Finance.

**Carmen: Retry.**

Cost received: HK$52. Margin 45.26% (floor 32%), investment HK$60,000 → Band B. One note: DermaCalm is in the Skincare Member Day promotion for app and eShop in C22 — your stores-only request doesn't conflict, but adding digital would.

---

## Presenter cues

- After A: "Nobody typed a form. Nobody recalculated margin. Vivian saw a decision pack, not a spreadsheet."
- After B: "The platform did not trust the funding until Finance's rule was satisfied — and then it re-did the numbers in front of you."
- After C: "It stopped and explained instead of pushing a bad request to Andrew."
- After J: "Mei changed the process in minutes; the one thing she could not do was override the DoA — and the platform told her who could."
- After M: "When data is missing, it says so. It never guesses."
