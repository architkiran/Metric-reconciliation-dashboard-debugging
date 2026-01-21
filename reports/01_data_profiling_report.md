# Data Profiling Report (Raw Olist)

This report summarizes row counts, duplicates, missingness, and ID uniqueness checks.

## olist_orders_dataset.csv

- Rows: **99441**
- Columns: **8**
- Exact duplicate rows: **0**

**Top missing columns (% null):**

- `order_delivered_customer_date`: 2.98%
- `order_delivered_carrier_date`: 1.79%
- `order_approved_at`: 0.16%
- `order_id`: 0.00%
- `customer_id`: 0.00%
- `order_status`: 0.00%
- `order_purchase_timestamp`: 0.00%
- `order_estimated_delivery_date`: 0.00%

**ID columns (unique counts):**

- `order_id`: 99441
- `customer_id`: 99441

---

## olist_order_items_dataset.csv

- Rows: **112650**
- Columns: **7**
- Exact duplicate rows: **0**

**Top missing columns (% null):**

- `order_id`: 0.00%
- `order_item_id`: 0.00%
- `product_id`: 0.00%
- `seller_id`: 0.00%
- `shipping_limit_date`: 0.00%
- `price`: 0.00%
- `freight_value`: 0.00%

**ID columns (unique counts):**

- `order_id`: 98666
- `order_item_id`: 21
- `product_id`: 32951
- `seller_id`: 3095

---

## olist_order_payments_dataset.csv

- Rows: **103886**
- Columns: **5**
- Exact duplicate rows: **0**

**Top missing columns (% null):**

- `order_id`: 0.00%
- `payment_sequential`: 0.00%
- `payment_type`: 0.00%
- `payment_installments`: 0.00%
- `payment_value`: 0.00%

**ID columns (unique counts):**

- `order_id`: 99440

---

## olist_customers_dataset.csv

- Rows: **99441**
- Columns: **5**
- Exact duplicate rows: **0**

**Top missing columns (% null):**

- `customer_id`: 0.00%
- `customer_unique_id`: 0.00%
- `customer_zip_code_prefix`: 0.00%
- `customer_city`: 0.00%
- `customer_state`: 0.00%

**ID columns (unique counts):**

- `customer_id`: 99441
- `customer_unique_id`: 96096

---

## olist_products_dataset.csv

- Rows: **32951**
- Columns: **9**
- Exact duplicate rows: **0**

**Top missing columns (% null):**

- `product_category_name`: 1.85%
- `product_name_lenght`: 1.85%
- `product_description_lenght`: 1.85%
- `product_photos_qty`: 1.85%
- `product_weight_g`: 0.01%
- `product_length_cm`: 0.01%
- `product_height_cm`: 0.01%
- `product_width_cm`: 0.01%
- `product_id`: 0.00%

**ID columns (unique counts):**

- `product_id`: 32951

---

