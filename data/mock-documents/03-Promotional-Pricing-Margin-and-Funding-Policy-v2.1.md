# Promotional Pricing, Margin and Funding Policy

| | |
|---|---|
| **Document ID** | WTCHK-FIN-POL-021 |
| **Version** | 2.1 |
| **Effective date** | 1 June 2026 |
| **Document owner** | Finance Controller, Commercial |
| **Approved by** | Commercial Director and Finance Director |
| **Classification** | Internal — **fictional demonstration content** |

---

## 1. Scope

This policy defines how promotional margin, discount depth, promotion frequency and supplier funding are measured and controlled for Watsons Hong Kong promotions. It applies to every promotion type and mechanic under SOP WTCHK-COM-SOP-014. Hong Kong has no sales tax or VAT; all prices and costs are tax-exclusive by construction.

## 2. Definitions

| Term | Definition |
|---|---|
| **Regular price** | Shelf price in ERP for the price zone at the promotion start date. |
| **Promotional price** | Customer price during the promotion. For multi-buy mechanics, the allocated price under section 8. |
| **Landed cost** | ERP unit cost including inbound freight, duty and handling, as at the promotion start date. |
| **Off-invoice adjustment** | A supplier cost reduction applied to purchase orders for a defined period. Reduces landed cost for promotion economics when `CONFIRMED` for the promotion period. |
| **Effective unit cost** | Landed cost less any confirmed off-invoice adjustment covering the promotion period. |
| **Scan-back funding** | Supplier payment per unit sold during the promotion, claimed after the promotion from scan data. |
| **Lump-sum funding** | Fixed supplier contribution for a promotion or period. |
| **Free goods** | Additional stock supplied without charge. Not recognised in promotion economics for approval purposes. |
| **Recognised funding per unit** | The supplier funding that may be counted in margin and investment, determined under section 5. |
| **Category group** | Grouping of the merchandise hierarchy used for margin floors (section 3). |

## 3. Margin floors

The **promotional margin** must be at or above the floor for the category group and promotion type. Own-brand items use the own-brand row regardless of category.

| Category group | Standard / Local / Event | Flash | Clearance |
|---|---:|---:|---:|
| Own brand (all categories) | 38% | 35% | 10% |
| Health — Vitamins & Supplements (third party) | 28% | 25% | 10% |
| Health — OTC Medicines (third party) | 24% | Not permitted | 10% |
| Health — Medical Devices & Tests | 26% | Not permitted | 10% |
| Beauty — Skincare | 32% | 28% | 10% |
| Beauty — Cosmetics | 30% | 27% | 10% |
| Beauty — Fragrance | 28% | 25% | 10% |
| Personal Care (oral, hair, body, shaving) | 25% | 22% | 10% |
| Baby — Nutrition (permitted stages only) | 15% | Not permitted | 10% |
| Baby — Care (nappies, wipes, toiletries) | 18% | 15% | 10% |
| Household & Lifestyle | 22% | 20% | 10% |

Floors are reviewed each half-year by the Finance Controller with the Head of Trading. A promotion below the floor is not automatically rejected; it is an exception under section 11 and routes at Band C under the Delegation of Authority policy.

## 4. Promotional margin

```
Promotional margin
  = (promotional price − effective unit cost + recognised funding per unit) ÷ promotional price
```

- **Effective unit cost** = landed cost − confirmed off-invoice adjustment for the promotion period (section 2).
- Where the promotional margin is below the floor, the checking step must also report:
  - **Minimum promotional price to meet the floor** = effective unit cost ÷ (1 − floor) − recognised funding per unit; and
  - **Minimum funding per unit to meet the floor at the requested price** = floor × promotional price − (promotional price − effective unit cost).
- Where the **regular** margin (at regular price with no funding) is already below the floor, the report must state this explicitly, because no promotional price can meet the floor without funding.
- Rounding: margins are reported to two decimal places; the floor test is applied on the unrounded value.

## 5. Recognition of supplier funding

### 5.1 Status

Only commitments with status `CONFIRMED` in the Trade Funding Register, backed by a confirmation document meeting the Supplier Trade Funding Procedure, are recognised. `DRAFT`, `AGREED_PENDING_EVIDENCE`, `EXPIRED`, `CANCELLED` and verbal or email-only agreements are recognised as **zero**.

### 5.2 Coverage

Funding is recognised only for the items, channels and dates it covers. If a commitment covers part of the promotion period or part of the channels, it is recognised as zero for approval purposes unless the supplier issues an extended or amended confirmation before approval. Partial coverage must be reported so the requester can seek an amendment.

### 5.3 Cap proration

Where a per-unit commitment carries a maximum funded quantity lower than forecast units:

```
recognised funding per unit = rate × min(forecast units, funded cap) ÷ forecast units
```

### 5.4 Lump-sum conversion

Lump-sum funding is converted to a per-unit amount by dividing by forecast units. If the lump sum relates to more than one item or period, only the share explicitly allocated in the confirmation to this item and period is used.

### 5.5 Off-invoice

Off-invoice adjustments reduce effective unit cost (section 4) and are **not** included in recognised funding per unit or in net promotion investment.

### 5.6 Free goods

Free goods are not recognised in promotion economics for approval. They may be described in the rationale.

## 6. Discount depth

```
Discount depth = (regular price − promotional price) ÷ regular price
```

- Maximum depth for Standard, Local, Event and Flash promotions is **50%**. Depth above 50% is an exception.
- Depth above **40%** raises the approval to at least Band B (DoA 5.4).
- `BOGO` is treated as 50% depth over two units. `MULTI_BUY_2ND` at 50% off the second item is treated as 25% depth over two units.
- Clearance promotions are exempt from the depth limit but subject to the 10% clearance floor.

## 7. Promotion frequency

An item may be on a Standard, Local, Event or Flash price promotion in a given channel for at most **6 weeks in any rolling 12-week window** ending on the requested start date. Each Flash promotion counts as one week. Exceeding the limit raises the approval to at least Band B (DoA 5.5) and requires the requester to state why the item is not being priced permanently lower.

## 8. Stacking and multi-buy allocation

### 8.1 Stacking

An item may carry only one price or value mechanic per channel for any given day. Overlaps with planned, approved or active promotions in PromoHub are blocking conflicts (SOP §6.5). Member bonus points stacked on a price promotion are permitted only where the points cost is included in investment.

### 8.2 Allocation for margin testing (multi-buy)

For `MULTI_BUY_SAVE`, `MULTI_BUY_2ND` and `BUNDLE`, the discount is allocated to each item **pro rata to regular price** within the qualifying set, and each item's allocated promotional price is tested against its own floor. Where mix-and-match is permitted, the test is applied to the **worst-case qualifying set** for each item — the combination of eligible items that gives that item the deepest allocated discount (in practice, pairing with the lowest-priced eligible items). An item failing the worst-case test must be removed from the list, funded, or approved as an exception.

## 9. Clearance

Clearance pricing applies only to items with lifecycle status `PHASE_OUT` or `DELISTED`. Clearance promotions are tested against the 10% floor and are exempt from the depth and frequency rules. They must be reviewed each cycle and closed when stock is exhausted.

## 10. Forecast plausibility

Forecast units are tested against a **benchmark** for the scope and period:

```
benchmark units = baseline weekly units for the scope × promotion weeks × category uplift benchmark
```

Category uplift benchmarks are published quarterly from Post-Promotion Evaluations. A forecast is flagged if it is above **130%** of the benchmark or below **80%** of baseline units for the period (which suggests a scope or unit error). A flagged forecast does not block the request; the requester must confirm or correct it, and the confirmation is recorded. Event modifiers published in the PPE may be applied where the request carries the corresponding event code. The check is not applied to multi-buy, `GWP`, `BONUS_POINTS` or `COUPON` mechanics in the current version.

## 11. Exceptions

A request that fails the floor, depth, frequency, duration or stacking rules may proceed only as an **exception** approved by the Commercial Director with Finance review (DoA 5.1–5.3). The exception request must state: the rule and the measured value; the commercial reason; the expected benefit; the proposed mitigation (for example, additional funding, shorter period, reduced scope); and the requester's and Category Lead's names. Approved exceptions are logged and reported monthly.

## 12. Calculation transparency

Every reported margin, depth, investment and plausibility result must show its inputs (with source system and timestamp), the formula applied and the policy version. Where a required input is unavailable, the calculation must be reported as **not computable** rather than estimated. No estimated or assumed value may be substituted for regular price, cost, funding or forecast.

## 13. Revision history

| Version | Date | Change |
|---|---|---|
| 1.0 | 1 July 2024 | Initial policy — floors by promotion type only |
| 2.0 | 1 December 2025 | Floors by category group; funding recognition rules; frequency rule |
| **2.1** | **1 June 2026** | **Added effective unit cost with off-invoice; cap proration; multi-buy allocation and worst-case test; forecast plausibility; calculation transparency** |
