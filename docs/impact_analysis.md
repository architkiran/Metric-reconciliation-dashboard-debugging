# KPI Mismatch Impact Analysis

## Summary
Out of 614 total days analyzed (2016-09-04 to 2018-09-03, full Olist dataset):
- 273 days (~44%) showed revenue mismatches between Finance and Growth dashboards
- 340 days (~55%) matched
- 1 day had missing Finance data

A day is flagged as a mismatch when the two daily totals differ by 1 cent or more, so this count includes rounding-level differences. The dollar size of the gap is quantified below.

## Dollar impact (full dataset, BRL)
Reproduce with `sql/01_dollar_impact.sql` after `sql/00_build_all.sql`.

| Measure | Value |
|---|---|
| Finance revenue (payments-based) | R$15,739,137 |
| Growth revenue (item price + freight) | R$15,737,668 |
| Net gap (Growth minus Finance) | -R$1,613 (-0.01% of Finance revenue) |
| Gross gap (sum of daily absolute differences) | R$5,823 (0.037% of Finance revenue) |
| Average absolute gap on mismatch days | R$21.33 |
| Largest single-day gap | R$1,193.01 (2016-10-05, a launch-period day with R$8.3K of revenue) |
| Mismatch days with gap of R$1 or more | 191 |
| Mismatch days with gap of R$10 or more | 99 |
| Mismatch days with gap of R$100 or more | 9 |
| Days where the gap is 1% or more of that day's revenue | 4 |

## What the numbers say
- The two dashboards disagree on almost half of the days, but almost always by small amounts. In total the definitions differ by 0.04% of revenue.
- The material gaps are rare: 9 days differ by R$100 or more, and several of the largest fall in the first weeks of data, when daily volume was low.
- The order-status filters differ (Finance excludes canceled and unavailable orders; Growth excludes only canceled). The effect is small: Growth counts R$2,140 of item revenue on orders with status "unavailable".

## Why This Matters
- Conflicting KPIs reduce trust in analytics, even when the dollar difference is small
- Without a documented reconciliation, nobody can say whether a daily gap is rounding or a real error
- Teams optimize against different numbers
- The financial exposure from the definition gap itself is small (see above), so the value of the canonical metric is auditability and a single source of truth, not recovered revenue

## Primary Drivers of Mismatch
1. Different revenue sources (payments vs items + freight)
2. Order status filtering differences
3. Multi-item orders inflating item-based revenue
4. Inclusion of freight in Growth but not Finance

Note: these describe how the two definitions differ. Only the order-status effect is quantified here (query 4 in `sql/01_dollar_impact.sql`); the remaining gap has not been decomposed by driver.
