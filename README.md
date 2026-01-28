# 📊 KPI Trust Dashboard — Metric Reconciliation

An end-to-end analytics project that **detects, explains, and audits KPI mismatches** between Finance and Growth revenue definitions using **DuckDB, SQL pipelines, and an interactive Streamlit dashboard**.

---

## 🚩 Problem Statement

In real organizations, **different teams often report different numbers for the same KPI**.

For example:
- **Finance** defines revenue using *actual payments received*
- **Growth / Product** defines revenue using *item price + freight*
- Both definitions are valid — but **when numbers don’t match, trust breaks down**

This project simulates that **exact real-world analytics problem** and builds a system to:

- Compute KPIs using **independent definitions**
- Detect **daily mismatches**
- Quantify the **impact**
- Explain **why mismatches occur**
- Enable **auditability and reproducible rebuilds**

---

## 🎯 What This Project Solves

✔ KPI definition conflicts  
✔ Data trust issues between teams  
✔ “Why do dashboards disagree?” questions  
✔ Lack of explainability in analytics  
✔ Non-reproducible pipelines  

---

## 🧠 Solution Overview

The system is built as an **end-to-end analytics workflow**:

1. **Raw transactional data** is loaded into DuckDB
2. Two independent KPI pipelines are computed:
   - Finance Revenue (payments-based)
   - Growth Revenue (item + freight-based)
3. Daily revenue values are reconciled
4. Mismatches are classified and quantified
5. Results are surfaced in an interactive dashboard with drilldowns

---

## 🏗️ Architecture
```
Raw CSV Data
↓
DuckDB (Analytical DB)
↓
SQL Pipelines (Finance / Growth)
↓
Reconciliation Logic
↓
Streamlit Dashboard
```

Key design decisions:
- DuckDB for fast, in-process analytics
- SQL-first transformations for transparency
- Idempotent pipeline rebuilds
- Cloud-safe database bootstrapping (`/tmp` on Streamlit Cloud)

---

## 📸 Dashboard Screenshots

### 1️⃣ KPI Overview & Filters
![KPI Overview](reports/screenshots/Screenshot%202026-01-28%20at%205.00.14%20PM.png)

---

### 2️⃣ Drilldown & Auto Explanation
![Drilldown](reports/screenshots/Screenshot%202026-01-28%20at%205.00.41%20PM.png)

---

### 3️⃣ Mismatch-Only View
![Mismatch View](reports/screenshots/Screenshot%202026-01-28%20at%205.01.06%20PM.png)

---

## 🔍 Revenue Definitions

### Finance Revenue
- Source: `order_payments`
- Uses `payment_value`
- Excludes canceled / unavailable orders
- Represents **actual cash collected**

### Growth Revenue
- Source: `order_items`
- Uses `price + freight_value`
- Captures **gross transactional value**

### Why mismatches occur
- Timing differences
- Partial payments
- Canceled orders
- Definition scope differences

The dashboard **explains these differences automatically** for each mismatched day.

---

## 🧪 Key Features

- 📅 Date-range filtering
- ⚠️ Mismatch-only views
- 🔎 Worst-day drilldowns
- 🧠 Auto-generated explanations
- 📥 CSV export for audits
- 🔁 Rebuildable SQL pipelines

---

## 🛠️ Tech Stack

- **Python**
- **DuckDB**
- **SQL**
- **Pandas**
- **Streamlit**
- **Plotly**
- **GitHub / Streamlit Cloud**

---

## ▶️ Run Locally

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build DuckDB from raw or sample data
python src/02_load_to_duckdb.py

# Build KPI tables
duckdb data/db/olist.duckdb < sql/00_build_all.sql

# Run dashboard
streamlit run dashboards/trust_dashboard.py
```
## ☁️ Deployment Notes

- The app automatically builds the DuckDB database on first run
- Uses /tmp/olist.duckdb on Streamlit Cloud
- No large raw datasets are committed to GitHub
- Sample data enables fast, reproducible demos

## 💼 Why This Project Matters (Recruiter Perspective)

- This project demonstrates:
- Real-world KPI reconciliation problems
- SQL-first analytics engineering
- Data quality & trust workflows
- Cloud-safe deployment practices
- Explainable analytics, not just charts

