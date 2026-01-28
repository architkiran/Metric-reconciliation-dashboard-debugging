import os
import subprocess
import sys
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="KPI Trust Dashboard", layout="wide")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_ALL_SQL = PROJECT_ROOT / "sql" / "00_build_all.sql"

# --- DuckDB path handling (CRITICAL for Streamlit Cloud) ---
# Streamlit Cloud runs in a container where repo paths are read-only-ish for outputs.
# Always write the DB to /tmp on Cloud.
if os.environ.get("STREAMLIT_SERVER_RUNNING") == "true":
    DB_PATH = Path("/tmp/olist.duckdb")
else:
    DB_PATH = PROJECT_ROOT / "data" / "db" / "olist.duckdb"


def df_query(con, q: str) -> pd.DataFrame:
    return con.execute(q).df()


def run_sql_file(con, path: Path) -> None:
    """
    Executes a DuckDB SQL file that may contain:
      - normal SQL statements terminated by ';'
      - DuckDB CLI meta commands like: .read relative/path.sql

    This makes sql/00_build_all.sql work both in CLI and in Python/Streamlit.
    """
    path = path.resolve()
    base_dir = path.parent

    sql_buffer = ""

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()

        # skip empty lines and comments
        if not line or line.startswith("--"):
            continue

        # handle DuckDB CLI include command
        if line.lower().startswith(".read "):
            # flush any pending SQL before reading another file
            if sql_buffer.strip():
                con.execute(sql_buffer)
                sql_buffer = ""

            include_rel = line.split(None, 1)[1].strip().strip("'").strip('"')
            include_path = (base_dir / include_rel).resolve()
            run_sql_file(con, include_path)
            continue

        # accumulate SQL until ';'
        sql_buffer += raw_line + "\n"
        if ";" in raw_line:
            # execute complete statement(s) in buffer
            parts = sql_buffer.split(";")
            for stmt in parts[:-1]:
                stmt = stmt.strip()
                if stmt:
                    con.execute(stmt)
            sql_buffer = parts[-1]  # remainder after last ';'

    # flush remaining buffer
    if sql_buffer.strip():
        con.execute(sql_buffer)

def ensure_tables(con) -> None:
    tables = {t[0] for t in con.execute("SHOW TABLES").fetchall()}
    required = {"finance_revenue_daily", "growth_revenue_daily", "revenue_mismatch_daily"}
    if not required.issubset(tables):
        if not BUILD_ALL_SQL.exists():
            st.error("Missing sql/00_build_all.sql. Create it first.")
            st.stop()
        st.info("Building KPI tables from sql/00_build_all.sql ...")
        run_sql_file(con, BUILD_ALL_SQL)
        st.success("Build complete.")


st.title("KPI Trust Dashboard — Metric Reconciliation")
st.caption("Finance vs Growth revenue definitions, mismatch detection, and drilldowns (DuckDB + SQL pipelines).")

# Sidebar (show DB path for debugging)
st.sidebar.header("Filters")
st.sidebar.write("DB:", str(DB_PATH))

# --- Auto-build DuckDB if missing (Cloud + first run) ---
# This expects your loader script to support:
#   SAMPLE=1  -> use data/sample_raw
#   DB_PATH   -> where to write duckdb file
if not DB_PATH.exists():
    st.warning(f"DuckDB not found at {DB_PATH}. Building demo DB from sample data...")

    os.environ["SAMPLE"] = "1"
    os.environ["DB_PATH"] = str(DB_PATH)

    try:
        subprocess.check_call(
            [sys.executable, str(PROJECT_ROOT / "src" / "02_load_to_duckdb.py")]
        )
        st.success("Demo DB build complete.")
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to build DuckDB database. Error: {e}")
        st.stop()

# Connect
try:
    con = duckdb.connect(str(DB_PATH), read_only=False)
except Exception as e:
    st.error(f"Failed to open DuckDB at {DB_PATH}: {e}")
    st.stop()

# Ensure KPI tables exist (runs SQL pipelines if needed)
ensure_tables(con)

# Load mismatch first (master filter table)
mismatch = df_query(con, """
    SELECT day, revenue_finance, revenue_growth, diff, status
    FROM revenue_mismatch_daily
    ORDER BY day
""")

# Sidebar date range + mismatch-only
min_day = pd.to_datetime(mismatch["day"].min()).date()
max_day = pd.to_datetime(mismatch["day"].max()).date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_day, max_day),
    min_value=min_day,
    max_value=max_day
)

show_mismatch_only = st.sidebar.checkbox("Show mismatch days only", value=False)
topN = st.sidebar.slider("Top mismatch days to list", 5, 50, 10)

# Apply filters
start, end = date_range
mismatch = mismatch[
    (pd.to_datetime(mismatch["day"]).dt.date >= start) &
    (pd.to_datetime(mismatch["day"]).dt.date <= end)
]

if show_mismatch_only:
    mismatch = mismatch[mismatch["status"] == "mismatch"]

# Build chart DF from filtered mismatch
df = mismatch[["day", "revenue_finance", "revenue_growth"]].copy()
df["diff"] = df["revenue_growth"] - df["revenue_finance"]

# Header KPIs
c1, c2, c3, c4 = st.columns(4)
total_days = int(mismatch.shape[0])
mismatch_days = int((mismatch["status"] == "mismatch").sum())
match_days = int((mismatch["status"] == "match").sum())
missing_finance_days = int((mismatch["status"] == "missing_finance").sum())
c1.metric("Total Days (filtered)", total_days)
c2.metric("Mismatch Days", mismatch_days)
c3.metric("Match Days", match_days)
c4.metric("Missing Finance Days", missing_finance_days)

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("Revenue Over Time (Filtered)")
    if df.empty:
        st.warning("No rows in the selected filter range.")
    else:
        chart_df = df.melt(
            id_vars=["day"],
            value_vars=["revenue_finance", "revenue_growth"],
            var_name="metric",
            value_name="revenue"
        )
        fig = px.line(chart_df, x="day", y="revenue", color="metric")
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Mismatch Status (Days)")
    if mismatch.empty:
        st.warning("No data for selected filters.")
    else:
        status_counts = mismatch["status"].value_counts().reset_index()
        status_counts.columns = ["status", "days"]
        fig2 = px.bar(status_counts, x="status", y="days")
        st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Drilldown")

# Compute top mismatch days
mismatch_only = mismatch[mismatch["status"] == "mismatch"].copy()
if not mismatch_only.empty:
    mismatch_only["abs_diff"] = mismatch_only["diff"].abs()
    top_mismatch = mismatch_only.sort_values("abs_diff", ascending=False).head(topN)
    drill_options = top_mismatch["day"].tolist()
    default_choice = drill_options[0]
else:
    drill_options = mismatch["day"].tolist()
    default_choice = drill_options[0] if drill_options else None

if default_choice is None:
    st.warning("No drilldown days available with current filters.")
    con.close()
    st.stop()

choice = st.selectbox(
    "Pick a day (defaults to worst mismatch in current filters)",
    options=drill_options,
    index=0
)

day_str = pd.to_datetime(choice).strftime("%Y-%m-%d")

day_row = df_query(con, f"""
    SELECT *
    FROM revenue_mismatch_daily
    WHERE day = DATE '{day_str}'
""")

st.write("### Selected Day KPI Snapshot")
st.dataframe(day_row, use_container_width=True)

# Auto explanation panel
st.markdown("### Explanation (auto)")
if day_row.empty:
    st.info("No row returned for selected day (unexpected).")
else:
    row = day_row.iloc[0].to_dict()
    status = row.get("status")
    diff_val = row.get("diff")

    if status == "match":
        st.success("Finance and Growth definitions align for this day (difference ~ 0).")
    elif status == "missing_finance":
        st.warning("Finance revenue is missing for this day — likely a pipeline coverage/join issue.")
    elif status == "missing_growth":
        st.warning("Growth revenue is missing for this day — likely a pipeline coverage/join issue.")
    else:
        st.info(
            "Mismatch is expected when definitions differ:\n"
            "- Growth uses item price + freight (order_items)\n"
            "- Finance uses payment_value (order_payments) and excludes unavailable/canceled\n"
            f"\nToday’s difference (Growth − Finance): **{diff_val:,.2f}**"
        )

st.write(f"### Top {topN} Mismatch Days (within current filters)")
if mismatch_only.empty:
    st.write("No mismatch days in current filter range.")
else:
    st.dataframe(
        top_mismatch[["day", "revenue_finance", "revenue_growth", "diff"]].reset_index(drop=True),
        use_container_width=True
    )

# Optional canonical section
tables = {t[0] for t in con.execute("SHOW TABLES").fetchall()}
if "canonical_revenue_daily" in tables:
    st.divider()
    st.subheader("Canonical SSOT Comparison (Optional)")

    canonical = df_query(con, """
        SELECT day, revenue_canonical
        FROM canonical_revenue_daily
        ORDER BY day
    """)

    canonical = canonical[
        (pd.to_datetime(canonical["day"]).dt.date >= start) &
        (pd.to_datetime(canonical["day"]).dt.date <= end)
    ]

    if canonical.empty:
        st.warning("No canonical data in the selected date range.")
    else:
        merged = canonical.merge(
            df[["day", "revenue_finance", "revenue_growth"]],
            on="day",
            how="left"
        )

        fig3 = px.line(
            merged.melt(
                id_vars=["day"],
                value_vars=["revenue_canonical", "revenue_finance", "revenue_growth"],
                var_name="metric",
                value_name="revenue"
            ),
            x="day", y="revenue", color="metric"
        )
        st.plotly_chart(fig3, use_container_width=True)

con.close()
