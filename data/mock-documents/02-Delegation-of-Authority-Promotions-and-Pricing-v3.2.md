# Delegation of Authority — Promotions and Promotional Pricing

| | |
|---|---|
| **Document ID** | WTCHK-COM-POL-032 |
| **Version** | 3.2 |
| **Effective date** | 15 August 2026 |
| **Document owner** | Commercial Director, Watsons Hong Kong |
| **Approved by** | Managing Director |
| **Supersedes** | v3.1 (effective 1 February 2025) |
| **Classification** | Internal — **fictional demonstration content** |

---

## 1. Purpose

This policy sets out who may approve promotions and promotional pricing for Watsons Hong Kong, on what basis, and with what controls. It is the controlling document for approval limits. Where any SOP, checklist, form or note states a different limit, this policy governs.

## 2. Principles

1. **Every promotion has a named human approver.** Authority attaches to a role held by a person listed in the Authority Directory as at the decision date. It does not attach to systems, agents, teams or job titles outside the directory.
2. **Authority follows commercial exposure.** The approval band is determined by net promotion investment and raised by escalation conditions that signal higher commercial, legal or execution risk.
3. **Segregation of duties.** No person may approve a promotion they requested or materially prepared. No person may review and approve the same case at Band B or above.
4. **Delegation is explicit and recorded.** Authority may be exercised by a delegate only where a delegation is recorded in the Authority Directory with a validity window and scope.
5. **Exceptions are decisions, not defaults.** Departures from policy rules are approved only at Band C or above, with reasons recorded.

## 3. Net promotion investment

### 3.1 Definition

For a single-item price mechanic:

```
Net promotion investment (HKD)
  = (regular price − promotional price − recognised supplier funding per unit) × forecast units
```

where "recognised supplier funding per unit" is determined under the Promotional Pricing, Margin and Funding Policy (WTCHK-FIN-POL-021) section 5. Off-invoice cost reductions are reflected in unit cost, not in this formula. A negative result is treated as zero.

### 3.2 Multi-buy and value mechanics

| Mechanic | Investment basis |
|---|---|
| `MULTI_BUY_SAVE` | Saving per qualifying set × forecast qualifying sets, less recognised funding |
| `MULTI_BUY_2ND`, `BOGO` | Discount value on the discounted unit × forecast discounted units, less recognised funding |
| `GWP` | Gift unit cost × forecast gifts issued, less recognised funding |
| `MEMBER_PRICE` | As single-item price mechanic on forecast member units |
| `BONUS_POINTS` | Incremental points × point cost (HK$0.01 per point unless Loyalty confirms otherwise) × forecast qualifying transactions |
| `COUPON` | Face value × forecast redemptions, less recognised funding |
| `BUNDLE` | (Sum of component regular prices − bundle price − recognised funding) × forecast bundles |

### 3.3 Aggregation

Where a request covers several items, channels or mechanics under one campaign name, event code or item list, investment is **aggregated** across the request for banding. Splitting a campaign into several requests to remain within a lower band is a breach of this policy.

## 4. Approval bands

| Band | Net promotion investment | Reviewer | Approver | Informed |
|---|---|---|---|---|
| **A** | Up to HK$50,000 | — | Category Lead for the item's category | Head of Trading (monthly summary) |
| **B** | HK$50,001 to HK$200,000 | Finance Controller, Commercial | Head of Trading | Commercial Director (monthly summary) |
| **C** | HK$200,001 to HK$1,000,000, **or** any escalation condition in section 5 marked "Band C" | Finance Controller, Commercial | Commercial Director | Head of Trading |
| **D** | Above HK$1,000,000, or any promotion applying across more than one Business Unit | Finance Controller, Commercial and Group Finance | Managing Director | Commercial Director, Group Commercial |

Band A promotions are approved without prior Finance review. Finance may sample Band A approvals retrospectively.

## 5. Escalation conditions

The band determined by investment is raised as follows. Where several conditions apply, the highest resulting band applies.

| # | Condition | Effect | Source rule |
|---|---|---|---|
| 5.1 | Promotional margin below the applicable floor | **Band C** | Margin Policy §3 |
| 5.2 | Any policy exception requested (floor, depth, frequency, duration, stacking, clearance status) | **Band C** | SOP §10 |
| 5.3 | Unresolved calendar conflict or stacking on the same item, channel and dates | **Band C** unless resolved by re-scoping or withdrawal | SOP §6.5 |
| 5.4 | Discount depth above 40% of regular price (Clearance excluded) | Minimum **Band B** | Margin Policy §6 |
| 5.5 | Item exceeds the promotion frequency limit | Minimum **Band B** | Margin Policy §7 |
| 5.6 | Duration above 28 days | Minimum **Band B**; above 56 days **Band C** | SOP §2.2 |
| 5.7 | Hero SKU (as designated by Trading) with depth above 35% | Minimum **Band B** | Trading designation |
| 5.8 | Cut-off exception requested | Head of Trading approval of the exception in addition to band approval | SOP §5.2 |
| 5.9 | Restricted regulatory class or non-permitted comparative claim | Compliance review as a **parallel mandatory gate**; band unchanged | Guidelines §4, §5 |
| 5.10 | Stock cover below 110% of forecast | Supply Chain confirmation as a **parallel mandatory gate**; band unchanged | SOP §6.6 |

Parallel gates (5.9, 5.10) must be closed before the case may be released to setup, but they do not change who approves the commercial decision.

## 6. Segregation of duties and delegation

### 6.1 Segregation

- The requester may not act as reviewer or approver on the same case.
- Where the role-holder who would approve is the requester, the case is routed to the recorded delegate for that role. If no valid delegate exists, the case is routed to the next band's approver.
- At Band B and above, the reviewer and approver must be different people.

### 6.2 Delegation

- Delegations are recorded in the Authority Directory with: delegator, delegate, role, band scope, start and end dates, reason.
- A delegate exercises the same authority and the same limits as the delegator for the recorded scope only.
- Standing delegates (for example, Senior Category Manager for Category Lead) may be recorded for the full year. Absence delegates (leave, travel) are recorded per absence.
- Decisions taken by a delegate must record the delegation reference on the case.
- A delegate may not further delegate.

### 6.3 Availability

The Authority Directory records planned unavailability. Routing must resolve the approver as at the **expected decision date**, not the submission date, and must route to the delegate where the primary approver is unavailable for the full service-level window.

## 7. Flash and emergency approvals

A Flash promotion with net promotion investment up to HK$30,000 and no escalation condition may be approved by the Category Lead with the Head of Trading informed on the same day. Flash promotions above HK$30,000 follow the standard bands. There is no verbal approval; every decision must be recorded on the case before release to setup.

## 8. Authority of systems and AI agents

Workflow systems and AI agents may: collect and validate information; retrieve item, price, cost, stock, calendar, funding and directory data; perform calculations under approved formulas; apply this policy to determine band, escalations and named approvers; prepare decision packs; create and track approval tasks; record decisions taken by authorised humans; and create promotion drafts after approval.

They may **not**: approve, reject or conditionally approve a promotion; waive, reinterpret or relax any policy rule; alter thresholds; substitute estimated values for unavailable data; or represent simulated or test data as production evidence.

Any output that recommends a decision must be labelled as a recommendation and must cite the rule and data on which it is based.

## 9. Decision pack and records

The decision pack must contain, at minimum: case identifier; requester and role; item facts with sources and timestamps; promotion terms; regulatory screen result; funding recognition and evidence references; conflict, frequency and duration results; calculations with formulas and inputs; stock cover; reference price result; band, triggered escalation conditions and named reviewer/approver with delegation references; open parallel gates; recommendation with rule citations; versions of this policy, the Margin Policy, the Guidelines and the SOP applied. Decision records are retained for seven years.

## 10. Review

This policy is reviewed annually by the Commercial Director and Finance Controller, or earlier if trading conditions, organisation structure or regulation change.

## 11. Revision history

| Version | Date | Change |
|---|---|---|
| 3.0 | 1 July 2024 | Introduced investment-based bands A–C |
| 3.1 | 1 February 2025 | Band B upper limit HK$150,000; added segregation rules; added Flash approval |
| **3.2** | **15 August 2026** | **Band B upper limit raised to HK$200,000; added Band D; added escalation conditions 5.7–5.10; added section 8 on systems and AI agents; added availability rule 6.3** |
