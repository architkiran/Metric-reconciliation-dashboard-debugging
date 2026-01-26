# Canonical Revenue Definition (Single Source of Truth)

## Metric Name
Canonical Revenue (Daily)

## Definition
Sum of `payment_value` for all orders that are not canceled or unavailable,
grouped by order purchase date.

## Rationale
- Payments reflect actual money collected
- Excluding canceled/unavailable orders prevents overstated revenue
- Purchase date provides a consistent, widely understood time anchor

## Trade-offs
- Does not reflect fulfillment timing
- May differ from item-level projections used by Growth

## Intended Usage
- Executive reporting
- Financial planning
- Company-wide KPI alignment
