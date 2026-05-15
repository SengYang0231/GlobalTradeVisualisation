"""
FIT2179 A2 — Dataset 3
Source: WITS Partner Timeseries (exports + imports by partner)
Outputs:
  - malaysia_arc_map.csv          → Chart 6 (arc flow map)
  - malaysia_partner_ranks.csv    → Chart 7 (bump/rank chart)
  - malaysia_partner_balance.csv  → Chart 8 (dot plot surplus/deficit)
"""

import pandas as pd
import os
from openpyxl import load_workbook

EXPORT_FILE = "WITS-Partner-Timeseries-export.xlsx"
IMPORT_FILE = "WITS-Partner-Timeseries-import.xlsx"
OUTPUT_DIR  = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Top N partners to keep for charts
TOP_N       = 15
LATEST_YEAR = 2023

# Skip regional aggregates — not individual countries
SKIP_PARTNERS = {
    "World", "East Asia & Pacific", "Europe & Central Asia",
    "North America", "South Asia", "Sub-Saharan Africa",
    "Latin America & Caribbean", "Middle East & North Africa",
    "Low income", "High income", "Upper middle income",
    "Lower middle income", "Low & middle income", "OECD members",
    "Euro area", "European Union", "ASEAN",
}

# Country centroids for arc map (lat, lon)
# Covers Malaysia's top trading partners
COORDS = {
    "Malaysia":          (4.21,   109.45),
    "Singapore":         (1.35,   103.82),
    "China":             (35.86,  104.19),
    "United States":     (37.09,  -95.71),
    "Japan":             (36.20,  138.25),
    "Thailand":          (15.87,  100.99),
    "Korea, Rep.":       (35.91,  127.77),
    "Vietnam":           (14.06,  108.28),
    "Indonesia":         (-0.79,  113.92),
    "Australia":         (-25.27, 133.78),
    "India":             (20.59,   78.96),
    "Hong Kong, China":  (22.40,  114.11),
    "Germany":           (51.17,   10.45),
    "Netherlands":       (52.13,    5.29),
    "Taiwan":            (23.70,  121.00),
    "Philippines":       (12.88,  121.77),
    "United Kingdom":    (55.38,   -3.44),
    "France":            (46.23,    2.21),
    "Italy":             (41.87,   12.57),
    "Mexico":            (23.63,  -102.55),
    "Brazil":            (-14.24, -51.93),
    "Saudi Arabia":      (23.89,   45.08),
    "United Arab Emirates": (23.42, 53.85),
    "Pakistan":          (30.38,   69.35),
}


# ── Helper: extract all partner rows ─────────────────────────────────────────
def extract_partners(filepath, flow_label):
    wb = load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active
    rows         = list(ws.iter_rows(values_only=True))
    header       = rows[0]
    year_cols    = [c for c in header if str(c).isdigit()]
    year_indices = [list(header).index(y) for y in year_cols]

    records = []
    for row in rows[1:]:
        partner = str(row[1]).strip() if row[1] else ""
        if not partner or partner in SKIP_PARTNERS:
            continue
        rec = {"partner": partner}
        for i, y in enumerate(year_cols):
            val = row[year_indices[i]]
            rec[int(y)] = float(val) if val is not None and isinstance(val, (int, float)) else None
        records.append(rec)

    df = pd.DataFrame(records)
    return df


print("Loading WITS partner files...")
exp_df = extract_partners(EXPORT_FILE, "export")
imp_df = extract_partners(IMPORT_FILE, "import")
print(f"  Export rows: {len(exp_df)} | Import rows: {len(imp_df)}")


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 1 — malaysia_arc_map.csv  (Chart 6)
# One row per top partner: export value, import value, lat, lon
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding malaysia_arc_map.csv...")

# Get latest year values
exp_latest = (
    exp_df[["partner", LATEST_YEAR]]
    .dropna()
    .rename(columns={LATEST_YEAR: "exports_usd_thou"})
    .nlargest(TOP_N, "exports_usd_thou")
)

imp_latest = (
    imp_df[["partner", LATEST_YEAR]]
    .dropna()
    .rename(columns={LATEST_YEAR: "imports_usd_thou"})
)

arc = exp_latest.merge(imp_latest, on="partner", how="left")
arc["balance_usd_thou"]   = arc["exports_usd_thou"] - arc["imports_usd_thou"]
arc["trade_type"]         = arc["balance_usd_thou"].apply(
    lambda x: "Export-heavy" if x > 0 else "Import-heavy"
)

# Convert to USD billions
arc["exports_usd_bn"] = (arc["exports_usd_thou"] / 1_000_000).round(2)
arc["imports_usd_bn"] = (arc["imports_usd_thou"] / 1_000_000).round(2)
arc["balance_usd_bn"] = (arc["balance_usd_thou"] / 1_000_000).round(2)

# Add coordinates
arc["dest_lat"] = arc["partner"].map(lambda p: COORDS.get(p, (None, None))[0])
arc["dest_lon"] = arc["partner"].map(lambda p: COORDS.get(p, (None, None))[1])

# Malaysia origin coords
arc["origin_lat"] = 4.21
arc["origin_lon"] = 109.45
arc["year"]       = LATEST_YEAR

# Drop partners without coordinates
missing_coords = arc[arc["dest_lat"].isna()]["partner"].tolist()
if missing_coords:
    print(f"  ⚠️  No coords for: {missing_coords}")
arc = arc.dropna(subset=["dest_lat", "dest_lon"])

arc = arc[["partner", "year", "origin_lat", "origin_lon", "dest_lat", "dest_lon",
           "exports_usd_bn", "imports_usd_bn", "balance_usd_bn", "trade_type"]]
arc.to_csv(f"{OUTPUT_DIR}/malaysia_arc_map.csv", index=False)
print(f"  Saved {len(arc)} rows → {OUTPUT_DIR}/malaysia_arc_map.csv")
print(arc[["partner", "exports_usd_bn", "imports_usd_bn", "trade_type"]].to_string(index=False))


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 2 — malaysia_partner_ranks.csv  (Chart 7 — bump chart)
# Long format: year, partner, export_value, rank
# Use selected years for cleaner bump chart
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding malaysia_partner_ranks.csv...")

BUMP_YEARS = [2000, 2005, 2010, 2013, 2015, 2018, 2020, 2023]

# Get top partners based on 2023 to keep chart readable
top_partners = (
    exp_df[["partner", 2023]]
    .dropna()
    .nlargest(8, 2023)["partner"]
    .tolist()
)
print(f"  Tracking partners: {top_partners}")

rank_records = []
for year in BUMP_YEARS:
    if year not in exp_df.columns:
        continue
    year_data = (
        exp_df[["partner", year]]
        .dropna()
        .sort_values(year, ascending=False)
        .reset_index(drop=True)
    )
    year_data["rank"] = year_data.index + 1
    year_data["year"] = year

    # Keep only our tracked top partners
    year_data = year_data[year_data["partner"].isin(top_partners)]
    year_data = year_data.rename(columns={year: "exports_usd_thou"})
    year_data["exports_usd_bn"] = (year_data["exports_usd_thou"] / 1_000_000).round(2)
    rank_records.append(year_data[["year", "partner", "rank", "exports_usd_bn"]])

ranks_df = pd.concat(rank_records).sort_values(["partner", "year"]).reset_index(drop=True)
ranks_df.to_csv(f"{OUTPUT_DIR}/malaysia_partner_ranks.csv", index=False)
print(f"  Saved {len(ranks_df)} rows → {OUTPUT_DIR}/malaysia_partner_ranks.csv")
print(ranks_df.to_string(index=False))


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT 3 — malaysia_partner_balance.csv  (Chart 8 — dot plot)
# One row per top partner: exports, imports, bilateral balance
# ════════════════════════════════════════════════════════════════════════════
print("\nBuilding malaysia_partner_balance.csv...")

exp_bal = (
    exp_df[["partner", LATEST_YEAR]]
    .dropna()
    .rename(columns={LATEST_YEAR: "exports_usd_thou"})
)
imp_bal = (
    imp_df[["partner", LATEST_YEAR]]
    .dropna()
    .rename(columns={LATEST_YEAR: "imports_usd_thou"})
)

balance_df = exp_bal.merge(imp_bal, on="partner", how="inner")
balance_df["balance_usd_thou"] = balance_df["exports_usd_thou"] - balance_df["imports_usd_thou"]
balance_df["exports_usd_bn"]   = (balance_df["exports_usd_thou"] / 1_000_000).round(2)
balance_df["imports_usd_bn"]   = (balance_df["imports_usd_thou"] / 1_000_000).round(2)
balance_df["balance_usd_bn"]   = (balance_df["balance_usd_thou"] / 1_000_000).round(2)
balance_df["direction"]        = balance_df["balance_usd_bn"].apply(
    lambda x: "Surplus" if x >= 0 else "Deficit"
)
balance_df["year"] = LATEST_YEAR

# Keep top 20 by total trade volume
balance_df["total_trade"] = balance_df["exports_usd_bn"] + balance_df["imports_usd_bn"]
balance_df = balance_df.nlargest(20, "total_trade")
balance_df = balance_df.sort_values("balance_usd_bn", ascending=False)
balance_df = balance_df.drop(columns=["exports_usd_thou", "imports_usd_thou",
                                       "balance_usd_thou", "total_trade"])

# ── Region classification for Chart 8 East vs West grouping ──────────────────
# East = Asia-Pacific (Malaysia's geographic neighbourhood)
# West = Americas, Europe, Middle East & Africa
EAST_PARTNERS = {
    "China", "Singapore", "Japan", "Korea, Rep.", "Thailand",
    "Vietnam", "Indonesia", "India", "Hong Kong, China",
    "Philippines", "Other Asia, nes", "Taiwan", "Myanmar",
    "Bangladesh", "Brunei Darussalam", "Cambodia", "Pakistan",
}
balance_df["region"] = balance_df["partner"].apply(
    lambda p: "East" if p in EAST_PARTNERS else "West"
)

balance_df.to_csv(f"{OUTPUT_DIR}/malaysia_partner_balance.csv", index=False)
print(f"  Saved {len(balance_df)} rows → {OUTPUT_DIR}/malaysia_partner_balance.csv")
print(balance_df[["partner", "region", "exports_usd_bn",
                   "imports_usd_bn", "balance_usd_bn", "direction"]].to_string(index=False))

print("\n✅ Dataset 3 complete.")
print("   malaysia_arc_map.csv          → Chart 6")
print("   malaysia_partner_ranks.csv    → Chart 7")
print("   malaysia_partner_balance.csv  → Chart 8")