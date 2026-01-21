import duckdb
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "db" / "olist.duckdb"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(str(DB_PATH))

FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
}

for table, fname in FILES.items():
    csv_path = RAW_DIR / fname
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing file: {csv_path}")

    print(f"Loading {csv_path.name} → table `{table}`")
    con.execute(f"""
        CREATE OR REPLACE TABLE {table} AS
        SELECT *
        FROM read_csv_auto('{csv_path.as_posix()}', ignore_errors=false)
    """)

print("\n✅ All tables loaded into DuckDB")

for table in FILES.keys():
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} rows")

con.close()
print(f"\nDB saved at: {DB_PATH}")
