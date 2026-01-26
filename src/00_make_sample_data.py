import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/sample_raw")
OUT.mkdir(parents=True, exist_ok=True)

N_ORDERS = 5000
SEED = 42

orders = pd.read_csv(RAW / "olist_orders_dataset.csv")
order_ids = orders["order_id"].sample(n=min(N_ORDERS, len(orders)), random_state=SEED)

orders_s = orders[orders["order_id"].isin(order_ids)]

items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
items_s = items[items["order_id"].isin(order_ids)]

payments = pd.read_csv(RAW / "olist_order_payments_dataset.csv")
payments_s = payments[payments["order_id"].isin(order_ids)]

customers = pd.read_csv(RAW / "olist_customers_dataset.csv")
customers_s = customers[customers["customer_id"].isin(orders_s["customer_id"].unique())]

products = pd.read_csv(RAW / "olist_products_dataset.csv")
products_s = products[products["product_id"].isin(items_s["product_id"].unique())]

orders_s.to_csv(OUT / "olist_orders_dataset.csv", index=False)
items_s.to_csv(OUT / "olist_order_items_dataset.csv", index=False)
payments_s.to_csv(OUT / "olist_order_payments_dataset.csv", index=False)
customers_s.to_csv(OUT / "olist_customers_dataset.csv", index=False)
products_s.to_csv(OUT / "olist_products_dataset.csv", index=False)

print("✅ Wrote sample CSVs to data/sample_raw/")
print("Orders:", len(orders_s), "Items:", len(items_s), "Payments:", len(payments_s))
