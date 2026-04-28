"""
FIT2179 A2 — Dataset 1 Preprocessing (Fixed)
Source: Our World in Data
Outputs:
  - choropleth_exports.csv     → Chart 1 (world choropleth)
  - top10_exporters.csv        → Chart 2 (bar chart)
  - trade_openness_gdp.csv     → Chart 3 (scatterplot)
"""

import pandas as pd
import os

# ── File paths ───────────────────────────────────────────────────────────────
TRADE_GDP_FILE    = "trade-as-share-of-gdp.csv"
GDP_CAPITA_FILE   = "gdp-per-capita-worldbank.csv"
MERCH_EXPORT_FILE = "merchandise-exports-gdp-cepii.csv"

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_YEAR = 2022
MIN_YEAR    = 2000
MAX_YEAR    = 2023


# ── Load files ────────────────────────────────────────────────────────────────
print("Loading files...")
trade = pd.read_csv(TRADE_GDP_FILE)
gdp   = pd.read_csv(GDP_CAPITA_FILE)
merch = pd.read_csv(MERCH_EXPORT_FILE)

print(f"  Trade % GDP columns:    {list(trade.columns)}")
print(f"  GDP per capita columns: {list(gdp.columns)}")
print(f"  Merchandise columns:    {list(merch.columns)}")


# ── Helper: extract one numeric value column ──────────────────────────────────
def extract_value(df, value_col):
    """
    Standardise OWID dataframe to: country, code, year, value
    value_col: exact column name of the numeric column to keep
    """
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]

    # Rename entity/code/year
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

    # Keep only country, code, year + the one value column
    df = df[["country", "code", "year", value_col]].copy()
    df = df.rename(columns={value_col: "value"})

    # Drop aggregate rows (no 3-letter ISO code)
    df = df[df["code"].notna() & (df["code"].str.len() == 3)]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    return df


# ── Identify the correct value column in each file ───────────────────────────
SKIP_COLS = {"entity", "code", "year", "owid_region"}

# Trade % GDP — first non-standard column
trade_val_col = [c for c in trade.columns if c.lower() not in SKIP_COLS][0]
print(f"\n  Using trade value column:   '{trade_val_col}'")

# GDP per capita — first numeric non-standard column
gdp_val_col = next(
    c for c in gdp.columns
    if c.lower() not in SKIP_COLS
    and pd.to_numeric(gdp[c], errors="coerce").notna().sum() > 100
)
print(f"  Using GDP value column:     '{gdp_val_col}'")

# Merchandise exports — first non-standard column
merch_val_col = [c for c in merch.columns if c.lower() not in SKIP_COLS][0]
print(f"  Using merchandise column:   '{merch_val_col}'")


# ── Standardise ───────────────────────────────────────────────────────────────
trade = extract_value(trade, trade_val_col)
gdp   = extract_value(gdp,   gdp_val_col)
merch = extract_value(merch, merch_val_col)

print(f"\n  Rows after clean — trade: {len(trade)}, gdp: {len(gdp)}, merch: {len(merch)}")


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 1 — choropleth_exports.csv
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
print(f"  Saved {len(choro)} rows → {OUTPUT_DIR}/choropleth_exports.csv")


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 2 — top10_exporters.csv
# Top 10 countries by trade % of GDP + Malaysia always included
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding top10_exporters.csv...")

latest_trade = (
    trade[trade["year"] <= TARGET_YEAR]
    .sort_values("year", ascending=False)
    .drop_duplicates(subset="code")
    .rename(columns={"value": "trade_pct_gdp"})
)

top10    = latest_trade.nlargest(10, "trade_pct_gdp")
malaysia = latest_trade[latest_trade["code"] == "MYS"]

top10_final = (
    pd.concat([top10, malaysia])
    .drop_duplicates(subset="code")
    .sort_values("trade_pct_gdp", ascending=False)
    .reset_index(drop=True)
)
top10_final["highlight"] = top10_final["code"] == "MYS"

top10_final.to_csv(f"{OUTPUT_DIR}/top10_exporters.csv", index=False)
print(f"  Saved {len(top10_final)} rows → {OUTPUT_DIR}/top10_exporters.csv")
print(top10_final[["country", "code", "trade_pct_gdp", "highlight"]].to_string(index=False))


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 3 — trade_openness_gdp.csv
# Scatterplot: trade % GDP vs GDP per capita, all countries, latest year
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding trade_openness_gdp.csv...")

latest_gdp = (
    gdp[gdp["year"] <= TARGET_YEAR]
    .sort_values("year", ascending=False)
    .drop_duplicates(subset="code")
    .rename(columns={"value": "gdp_per_capita"})
    [["code", "gdp_per_capita"]]
)

scatter = (
    latest_trade[["country", "code", "year", "trade_pct_gdp"]]
    .merge(latest_gdp, on="code", how="inner")
    .dropna()
    .reset_index(drop=True)
)

scatter["highlight"] = scatter["code"] == "MYS"

# Safe scalar sqrt transform using pandas vectorised ops — no lambda needed
scatter["gdp_sqrt"] = scatter["gdp_per_capita"].clip(lower=0).pow(0.5).round(2)

scatter.to_csv(f"{OUTPUT_DIR}/trade_openness_gdp.csv", index=False)
print(f"  Saved {len(scatter)} rows → {OUTPUT_DIR}/trade_openness_gdp.csv")


# ── Summary ───────────────────────────────────────────────────────────────────
print("\n✅ Dataset 1 complete. Files in /data/:")
print("   choropleth_exports.csv  → Chart 1")
print("   top10_exporters.csv     → Chart 2")
print("   trade_openness_gdp.csv  → Chart 3")

print("\nMalaysia row in scatterplot:")
print(scatter[scatter["code"] == "MYS"].to_string(index=False))