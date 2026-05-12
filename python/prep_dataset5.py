"""
FIT2179 A2 — Dataset 5 Preprocessing
Source: OpenDOSM — Monthly Trade by SITC Section
Download from: https://open.dosm.gov.my/data-catalogue/trade_sitc_1d
               → Download → CSV  (save as trade_sitc_1d.csv)
Input files (place in same folder as this script):
  - trade_sitc_1d.csv
Outputs:
  - data/malaysia_exports_by_sitc_annual.csv  → Chart 11 (stacked area)
  - data/malaysia_export_mix_slope.csv        → Chart 10 (slope chart)
"""

import pandas as pd
import os

SITC_FILE  = "trade_sitc_1d.csv"
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MIN_YEAR = 2000
MAX_YEAR = 2023

# SITC 1-digit section labels (UN standard)
SITC_LABELS = {
    "0": "Food & Live Animals",
    "1": "Beverages & Tobacco",
    "2": "Crude Materials",
    "3": "Mineral Fuels & Petroleum",
    "4": "Animal & Vegetable Oils",
    "5": "Chemicals",
    "6": "Manufactured Goods",
    "7": "Machinery & Transport Equipment",
    "8": "Misc. Manufactured Articles",
    "9": "Other Commodities",
}

# Colour palette hint for Vega-Lite (optional — can override in spec)
SITC_COLOURS = {
    "0": "#4E79A7",
    "1": "#A0CBE8",
    "2": "#F28E2B",
    "3": "#FFBE7D",
    "4": "#59A14F",
    "5": "#8CD17D",
    "6": "#B6992D",
    "7": "#E15759",
    "8": "#FF9D9A",
    "9": "#79706E",
}


# ── Load and clean ────────────────────────────────────────────────────────────
print("Loading OpenDOSM SITC file...")
df = pd.read_csv(SITC_FILE)
print(f"  Raw shape:   {df.shape}")
print(f"  Columns:     {list(df.columns)}")

df["date"]    = pd.to_datetime(df["date"])
df["year"]    = df["date"].dt.year
df["exports"] = pd.to_numeric(df["exports"], errors="coerce")
df["imports"] = pd.to_numeric(df["imports"], errors="coerce")

# Remove the "overall" aggregate row — keep individual sections only
sections = df[df["section"] != "overall"].copy()
sections["section"]       = sections["section"].astype(str).str.strip()
sections["section_label"] = sections["section"].map(SITC_LABELS)
sections["colour"]        = sections["section"].map(SITC_COLOURS)

# Warn if any section codes are unmapped
unmapped = sections[sections["section_label"].isna()]["section"].unique()
if len(unmapped):
    print(f"  ⚠️  Unmapped SITC sections: {unmapped}")

print(f"  Date range:  {df['date'].min().date()} → {df['date'].max().date()}")
print(f"  SITC sections found: {sorted(sections['section'].unique())}")


# ── Aggregate monthly → annual ────────────────────────────────────────────────
annual = (
    sections
    .groupby(["year", "section", "section_label", "colour"])[["exports", "imports"]]
    .sum()
    .reset_index()
)

# Convert RM (raw units) → RM billions
annual["exports_rm_bil"] = (annual["exports"] / 1e9).round(3)
annual["imports_rm_bil"] = (annual["imports"] / 1e9).round(3)

# Filter to target year range
annual = annual[
    (annual["year"] >= MIN_YEAR) &
    (annual["year"] <= MAX_YEAR)
].drop(columns=["exports", "imports"]).reset_index(drop=True)

print(f"\n  Annual rows after filter: {len(annual)} ({MIN_YEAR}–{MAX_YEAR})")


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 1 — malaysia_exports_by_sitc_annual.csv  (Chart 11)
# Long format: one row per year × section
# Vega-Lite stacked area needs: year, section_label, exports_rm_bil
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding malaysia_exports_by_sitc_annual.csv...")

stacked = annual[
    ["year", "section", "section_label", "colour",
     "exports_rm_bil", "imports_rm_bil"]
].sort_values(["year", "section"]).reset_index(drop=True)

stacked.to_csv(f"{OUTPUT_DIR}/malaysia_exports_by_sitc_annual.csv", index=False)
print(f"  ✅ {len(stacked)} rows → {OUTPUT_DIR}/malaysia_exports_by_sitc_annual.csv")

# Show 2023 breakdown
print("\n  2023 export breakdown:")
snap23 = stacked[stacked["year"] == 2023].copy()
total23 = snap23["exports_rm_bil"].sum()
snap23["share_pct"] = (snap23["exports_rm_bil"] / total23 * 100).round(1)
print(
    snap23[["section_label", "exports_rm_bil", "share_pct"]]
    .sort_values("exports_rm_bil", ascending=False)
    .to_string(index=False)
)


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 2 — malaysia_export_mix_slope.csv  (Chart 10)
# Three snapshots: 2000, 2013, 2023 showing structural shift
# Vega-Lite slope chart needs: snapshot_year, section_label, share_pct
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding malaysia_export_mix_slope.csv...")

SNAPSHOT_YEARS = [2000, 2013, 2023]

slope_parts = []
for yr in SNAPSHOT_YEARS:
    snap = annual[annual["year"] == yr].copy()
    if snap.empty:
        print(f"  ⚠️  No data for snapshot year {yr} — skipping")
        continue
    total = snap["exports_rm_bil"].sum()
    snap["share_pct"]      = (snap["exports_rm_bil"] / total * 100).round(2)
    snap["snapshot_year"]  = yr
    slope_parts.append(
        snap[["snapshot_year", "section", "section_label",
              "colour", "exports_rm_bil", "share_pct"]]
    )

slope = pd.concat(slope_parts).reset_index(drop=True)
slope.to_csv(f"{OUTPUT_DIR}/malaysia_export_mix_slope.csv", index=False)
print(f"  ✅ {len(slope)} rows → {OUTPUT_DIR}/malaysia_export_mix_slope.csv")

# Show structural shift table
print("\n  Export share comparison (2000 → 2013 → 2023):")
pivot = slope.pivot(index="section_label", columns="snapshot_year", values="share_pct")
pivot["change_00_23"] = (pivot[2023] - pivot[2000]).round(2)
print(
    pivot
    .sort_values(2023, ascending=False)
    .rename(columns={2000: "2000 %", 2013: "2013 %", 2023: "2023 %", "change_00_23": "Δ (00→23)"})
    .to_string()
)


print("\n✅ Dataset 5 complete.")
print("   malaysia_exports_by_sitc_annual.csv → Chart 11 (stacked area)")
print("   malaysia_export_mix_slope.csv       → Chart 10 (slope chart)")
