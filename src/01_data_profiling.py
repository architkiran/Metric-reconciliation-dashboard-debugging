import os
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUT_DIR = Path("reports")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Keep this list small and core for now
FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_products_dataset.csv",
]

def profile_csv(path: Path, sample_rows: int = 0) -> dict:
    df = pd.read_csv(path)

    # Basic stats
    n_rows, n_cols = df.shape
    null_pct = (df.isna().mean() * 100).sort_values(ascending=False)
    null_top = null_pct.head(10)

    # Duplicate rows (exact duplicates)
    dup_rows = int(df.duplicated().sum())

    # Candidate unique key check (common id columns)
    id_cols = [c for c in df.columns if c.endswith("_id") or c in ("order_id", "customer_id", "product_id")]
    id_uniques = {}
    for c in id_cols:
        id_uniques[c] = int(df[c].nunique(dropna=True))

    result = {
        "file": path.name,
        "rows": n_rows,
        "cols": n_cols,
        "duplicate_rows": dup_rows,
        "top_null_columns": null_top.to_dict(),
        "id_columns_unique_counts": id_uniques,
        "columns": list(df.columns),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
    }

    if sample_rows > 0:
        sample = df.head(sample_rows)
        sample.to_csv(OUT_DIR / f"sample_{path.stem}.csv", index=False)

    return result

def main():
    missing = [f for f in FILES if not (RAW_DIR / f).exists()]
    if missing:
        print("❌ Missing expected files in data/raw:")
        for f in missing:
            print(" -", f)
        print("\nTip: keep filenames exactly as Kaggle provided.")
        return

    all_profiles = []
    for fname in FILES:
        p = RAW_DIR / fname
        print(f"Profiling {p} ...")
        all_profiles.append(profile_csv(p, sample_rows=5))

    # Write a readable markdown report
    md_path = OUT_DIR / "01_data_profiling_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Data Profiling Report (Raw Olist)\n\n")
        f.write("This report summarizes row counts, duplicates, missingness, and ID uniqueness checks.\n\n")

        for prof in all_profiles:
            f.write(f"## {prof['file']}\n\n")
            f.write(f"- Rows: **{prof['rows']}**\n")
            f.write(f"- Columns: **{prof['cols']}**\n")
            f.write(f"- Exact duplicate rows: **{prof['duplicate_rows']}**\n\n")

            f.write("**Top missing columns (% null):**\n\n")
            if prof["top_null_columns"]:
                for col, pct in prof["top_null_columns"].items():
                    f.write(f"- `{col}`: {pct:.2f}%\n")
            else:
                f.write("- (none)\n")

            f.write("\n**ID columns (unique counts):**\n\n")
            if prof["id_columns_unique_counts"]:
                for col, uniq in prof["id_columns_unique_counts"].items():
                    f.write(f"- `{col}`: {uniq}\n")
            else:
                f.write("- (none detected)\n")

            f.write("\n---\n\n")

    print(f"\n✅ Wrote report: {md_path}")

if __name__ == "__main__":
    main()
