CREATE OR REPLACE TABLE finance_revenue_daily AS
SELECT
  DATE_TRUNC('day', CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS day,
  SUM(p.payment_value) AS revenue_finance
FROM orders o
JOIN order_payments p ON o.order_id = p.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE TABLE growth_revenue_daily AS
SELECT
  DATE_TRUNC('day', CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS day,
  SUM(oi.price + oi.freight_value) AS revenue_growth
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status <> 'canceled'
GROUP BY 1
ORDER BY 1;

CREATE OR REPLACE TABLE revenue_mismatch_daily AS
SELECT
  COALESCE(f.day, g.day) AS day,
  f.revenue_finance,
  g.revenue_growth,
  (g.revenue_growth - f.revenue_finance) AS diff,
  CASE
    WHEN f.revenue_finance IS NULL THEN 'missing_finance'
    WHEN g.revenue_growth IS NULL THEN 'missing_growth'
    WHEN ABS(g.revenue_growth - f.revenue_finance) < 0.01 THEN 'match'
    ELSE 'mismatch'
  END AS status
FROM finance_revenue_daily f
FULL OUTER JOIN growth_revenue_daily g
  ON f.day = g.day
ORDER BY 1;
