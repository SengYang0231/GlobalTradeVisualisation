"""
FIT2179 A2 — Dataset 1 Preprocessing (Fixed)
Source: Our World in Data
Input files (place in same folder as this script):
  - trade-as-share-of-gdp.csv
  - gdp-per-capita-worldbank.csv
  - merchandise-exports-gdp-cepii.csv
Outputs:
  - data/choropleth_exports.csv     → Chart 1 (world choropleth)
  - data/top10_exporters.csv        → Chart 2 (bar chart)
  - data/trade_openness_gdp.csv     → Chart 3 (scatterplot)
"""

import pandas as pd
import os

# ── File paths ────────────────────────────────────────────────────────────────
TRADE_GDP_FILE    = "trade-as-share-of-gdp.csv"
GDP_CAPITA_FILE   = "gdp-per-capita-worldbank.csv"
MERCH_EXPORT_FILE = "merchandise-exports-gdp-cepii.csv"

OUTPUT_DIR  = "data"
TARGET_YEAR = 2022   # latest year with good global coverage
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Micro-states / territories to exclude from Chart 2 ───────────────────────
# These inflate trade % of GDP due to re-export or entrepôt effects
EXCLUDE_COUNTRIES = {
    "San Marino", "Djibouti", "Malta", "Cyprus", "Seychelles", "Guyana",
    "United States Virgin Islands", "Cayman Islands", "Macao SAR, China",
    "Bermuda", "Bahrain", "Panama", "Brunei Darussalam", "Equatorial Guinea",
    "Timor-Leste", "Montenegro", "North Macedonia", "Moldova",
    "Luxembourg",  # financial centre, not a real trading economy
}
# Also filter: GDP per capita between 5,000–80,000 USD (removes city-states
# and very poor economies whose % figure is unreliable)
GDP_MIN = 5_000
GDP_MAX = 80_000

# ── Columns to skip when detecting value column ───────────────────────────────
SKIP_COLS = {"entity", "code", "year", "owid_region"}


# ── Helper: standardise OWID file to country / code / year / value ────────────
def extract_value(df, value_col):
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    renames = {}
    for c in df.columns:
        cl = c.lower()
        if cl == "entity":
            renames[c] = "country"
        elif cl == "code":
            renames[c] = "code"
        elif cl == "year":
            renames[c] = "year"
    df = df.rename(columns=renames)
    df = df[["country", "code", "year", value_col]].copy()
    df = df.rename(columns={value_col: "value"})
    df = df[df["code"].notna() & (df["code"].str.len() == 3)]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    return df


# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading files...")
trade = pd.read_csv(TRADE_GDP_FILE)
gdp   = pd.read_csv(GDP_CAPITA_FILE)
merch = pd.read_csv(MERCH_EXPORT_FILE)

print(f"  Trade % GDP columns:    {list(trade.columns)}")
print(f"  GDP per capita columns: {list(gdp.columns)}")
print(f"  Merchandise columns:    {list(merch.columns)}")

# Auto-detect value columns
trade_val_col = [c for c in trade.columns if c.lower() not in SKIP_COLS][0]
gdp_val_col   = next(
    c for c in gdp.columns
    if c.lower() not in SKIP_COLS
    and pd.to_numeric(gdp[c], errors="coerce").notna().sum() > 100
)
merch_val_col = [c for c in merch.columns if c.lower() not in SKIP_COLS][0]

print(f"\n  Trade value column:       '{trade_val_col}'")
print(f"  GDP per capita column:    '{gdp_val_col}'")
print(f"  Merchandise column:       '{merch_val_col}'")

trade = extract_value(trade, trade_val_col)
gdp   = extract_value(gdp,   gdp_val_col)
merch = extract_value(merch, merch_val_col)
print(f"\n  Rows — trade: {len(trade)} | gdp: {len(gdp)} | merch: {len(merch)}")


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 1 — choropleth_exports.csv  (Chart 1)
# One row per country, latest year ≤ TARGET_YEAR
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding choropleth_exports.csv...")

choro = (
    merch[merch["year"] <= TARGET_YEAR]
    .sort_values("year", ascending=False)
    .drop_duplicates(subset="code")
    .rename(columns={"value": "exports_pct_gdp"})
    .reset_index(drop=True)
)
choro.to_csv(f"{OUTPUT_DIR}/choropleth_exports.csv", index=False)
print(f"  ✅ {len(choro)} rows → {OUTPUT_DIR}/choropleth_exports.csv")


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 2 — top10_exporters.csv  (Chart 2)
# Top 10 REAL trading economies by trade % of GDP
# Excludes micro-states / territories that distort the metric
# Malaysia always included even if outside top 10
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding top10_exporters.csv...")

latest_trade = (
    trade[trade["year"] <= TARGET_YEAR]
    .sort_values("year", ascending=False)
    .drop_duplicates(subset="code")
    .rename(columns={"value": "trade_pct_gdp"})
)

# Build GDP lookup for filtering
latest_gdp_lookup = (
    gdp[gdp["year"] <= TARGET_YEAR]
    .sort_values("year", ascending=False)
    .drop_duplicates(subset="code")
    .rename(columns={"value": "gdp_per_capita"})
    [["code", "gdp_per_capita"]]
)

# Merge GDP into trade for filtering
trade_with_gdp = latest_trade.merge(latest_gdp_lookup, on="code", how="left")

# Apply filters: GDP range + explicit exclusion list
filtered = trade_with_gdp[
    (trade_with_gdp["gdp_per_capita"] >= GDP_MIN) &
    (trade_with_gdp["gdp_per_capita"] <= GDP_MAX) &
    (~trade_with_gdp["country"].isin(EXCLUDE_COUNTRIES))
].copy()

top10    = filtered.nlargest(10, "trade_pct_gdp")
malaysia = filtered[filtered["code"] == "MYS"]

top10_final = (
    pd.concat([top10, malaysia])
    .drop_duplicates(subset="code")
    .sort_values("trade_pct_gdp", ascending=False)
    .reset_index(drop=True)
)
top10_final["highlight"] = top10_final["code"] == "MYS"
top10_final = top10_final[["country", "code", "year",
                            "trade_pct_gdp", "gdp_per_capita", "highlight"]]

top10_final.to_csv(f"{OUTPUT_DIR}/top10_exporters.csv", index=False)
print(f"  ✅ {len(top10_final)} rows → {OUTPUT_DIR}/top10_exporters.csv")
print(top10_final[["country", "code", "trade_pct_gdp", "highlight"]].to_string(index=False))


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 3 — trade_openness_gdp.csv  (Chart 3)
# Scatterplot: trade % GDP (Y) vs GDP per capita (X), all countries
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding trade_openness_gdp.csv...")

scatter = (
    latest_trade[["country", "code", "year", "trade_pct_gdp"]]
    .merge(latest_gdp_lookup, on="code", how="inner")
    .dropna()
    .reset_index(drop=True)
)
scatter["highlight"] = scatter["code"] == "MYS"
scatter["gdp_sqrt"]  = scatter["gdp_per_capita"].clip(lower=0).pow(0.5).round(2)

scatter.to_csv(f"{OUTPUT_DIR}/trade_openness_gdp.csv", index=False)
print(f"  ✅ {len(scatter)} rows → {OUTPUT_DIR}/trade_openness_gdp.csv")
print("\n  Malaysia row:")
print(scatter[scatter["code"] == "MYS"].to_string(index=False))


print("\n✅ Dataset 1 complete.")
print("   choropleth_exports.csv → Chart 1")
print("   top10_exporters.csv    → Chart 2")
print("   trade_openness_gdp.csv → Chart 3")