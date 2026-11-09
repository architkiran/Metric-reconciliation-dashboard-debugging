-- ============================================================================
-- 01_dollar_impact.sql
-- Sizes the Finance vs Growth revenue gap in currency terms (BRL, R$).
-- Run AFTER sql/00_build_all.sql, against the FULL Olist dataset (data/raw).
-- The 5,000-order sample in data/sample_raw gives much smaller numbers
-- (18 of 592 days mismatch, R$110 gross gap); the figures quoted in
-- docs/impact_analysis.md come from the full dataset.
-- ============================================================================

-- 1) Headline: how many days differ, and how big is the gap in dollars?
SELECT
    COUNT(*)                                                         AS days_analyzed,
    COUNT(*) FILTER (WHERE status = 'mismatch')                      AS mismatch_days,
    ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'mismatch') / COUNT(*), 1) AS pct_days_mismatch,
    ROUND(SUM(revenue_finance), 0)                                   AS finance_revenue_total,
    ROUND(SUM(revenue_growth), 0)                                    AS growth_revenue_total,
    ROUND(SUM(diff), 0)                                              AS net_gap_growth_minus_finance,
    ROUND(SUM(ABS(diff)), 0)                                         AS gross_gap_sum_of_daily_abs_diff,
    ROUND(100.0 * SUM(ABS(diff)) / SUM(revenue_finance), 3)          AS gross_gap_pct_of_finance_revenue,
    ROUND(100.0 * SUM(diff) / SUM(revenue_finance), 3)               AS net_gap_pct_of_finance_revenue
FROM revenue_mismatch_daily;

-- 2) Materiality: is the 'mismatch' status counting rounding, or real money?
SELECT
    COUNT(*) FILTER (WHERE ABS(diff) >= 0.01)                        AS days_diff_ge_1_cent,
    COUNT(*) FILTER (WHERE ABS(diff) >= 1)                           AS days_diff_ge_R1,
    COUNT(*) FILTER (WHERE ABS(diff) >= 10)                          AS days_diff_ge_R10,
    COUNT(*) FILTER (WHERE ABS(diff) >= 100)                         AS days_diff_ge_R100,
    COUNT(*) FILTER (WHERE ABS(diff) >= 0.01 * revenue_finance)      AS days_diff_ge_1pct_of_day_revenue,
    ROUND(AVG(ABS(diff)) FILTER (WHERE status = 'mismatch'), 2)      AS avg_abs_diff_on_mismatch_days,
    ROUND(MAX(ABS(diff)), 2)                                         AS largest_single_day_gap
FROM revenue_mismatch_daily;

-- 3) Ten worst days by absolute dollar gap
SELECT CAST(day AS DATE) AS day,
       ROUND(revenue_finance, 2) AS finance, ROUND(revenue_growth, 2) AS growth, ROUND(diff, 2) AS diff
FROM revenue_mismatch_daily
ORDER BY ABS(diff) DESC NULLS LAST
LIMIT 10;

-- 4) What does the order-status filter difference cost?
--    (Finance excludes canceled + unavailable; Growth excludes only canceled.)
WITH items AS (
    SELECT order_id, SUM(price + freight_value) AS growth_basis FROM order_items GROUP BY 1
), pays AS (
    SELECT order_id, SUM(payment_value) AS payment_basis FROM order_payments GROUP BY 1
)
SELECT o.order_status,
       COUNT(*)                                         AS orders,
       ROUND(SUM(COALESCE(i.growth_basis, 0)), 0)       AS growth_basis_revenue,
       ROUND(SUM(COALESCE(p.payment_basis, 0)), 0)      AS payment_basis_revenue
FROM orders o
LEFT JOIN items i ON i.order_id = o.order_id
LEFT JOIN pays  p ON p.order_id = o.order_id
GROUP BY 1
ORDER BY orders DESC;
