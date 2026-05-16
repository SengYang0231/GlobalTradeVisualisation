"""
FIT2179 A2 — Treemap Coordinate Pre-computation
Source: data/malaysia_exports_treemap.csv
Output: data/malaysia_treemap_coords.csv

Pre-computes squarify treemap layout so Vega-Lite can render
it using plain rect + text marks — no Vega spec required.

Requires: pip install squarify

NOTE: prep_dataset4.py sector detection was broken (all = 'Other').
This script applies correct sector classification manually.
Once prep_dataset4.py is fixed, this script can be updated
to read sector directly from the CSV.
"""

import squarify
import pandas as pd
import os

INPUT_FILE  = "data/malaysia_exports_treemap.csv"
OUTPUT_FILE = "data/malaysia_treemap_coords.csv"

W, H = 500, 400   # Must match width/height in chart9_treemap.vl.json

# ── Manual sector classification ─────────────────────────────────────────────
# (override broken 'Other' values from prep_dataset4.py)
SECTOR_MAP = {
    "Electrical & Electronic  Products (E&E)":              "Manufacturing",
    "Machinery, Equipment And Parts":                        "Manufacturing",
    "Manufacture Of Metal":                                  "Manufacturing",
    "Optical & Scientific Equipment":                        "Manufacturing",
    "Iron And Steel Products":                               "Manufacturing",
    "Manufacture Of Plastics":                               "Manufacturing",
    "Textiles,  Apparels And Footwear":                      "Manufacturing",
    "Transport Equipment":                                    "Manufacturing",
    "Non-Metallic Mineral Products":                         "Manufacturing",
    "Rubber Products":                                        "Manufacturing",
    "Jewellery":                                              "Manufacturing",
    "Other Manufactures":                                     "Manufacturing",
    "Petroleum Products":                                     "Energy & Mining",
    "Liquefied Natural Gas (LNG)":                           "Energy & Mining",
    "Crude Petroleum":                                        "Energy & Mining",
    "Condensates and other petroleum oil":                   "Energy & Mining",
    "Metalliferous Ores and Metal Scrap":                    "Energy & Mining",
    "Other Mining":                                           "Energy & Mining",
    "Tin":                                                    "Energy & Mining",
    "Palm Oil and Palm-Based Products":                      "Agriculture & Food",
    "Palm Oil-Based Manufactured Products":                  "Agriculture & Food",
    "Other Chemical And Chemical Products (Exclude Plastics In Non-Primary Forms)":
                                                              "Agriculture & Food",
    "Processed Food":                                        "Agriculture & Food",
    "Natural Rubber":                                         "Agriculture & Food",
    "Other Agriculture":                                      "Agriculture & Food",
    "Seafood, fresh, chilled or frozen":                     "Agriculture & Food",
    "Other Vegetables Oil":                                   "Agriculture & Food",
    "Beverages & Tobacco":                                    "Agriculture & Food",
    "Crude Fertilizers And Crude Minerals":                  "Agriculture & Food",
    "Sawn Timber & Moulding":                                "Agriculture & Food",
    "Wood Products":                                          "Agriculture & Food",
    "Sawlog":                                                 "Agriculture & Food",
    "Paper & Pulp Products":                                  "Agriculture & Food",
}

SECTOR_COLOUR = {
    "Manufacturing":      "#534AB7",
    "Energy & Mining":    "#D85A30",
    "Agriculture & Food": "#1D9E75",
}


# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading treemap data...")
df = pd.read_csv(INPUT_FILE)
df["sector"] = df["sub_sector"].map(SECTOR_MAP).fillna("Manufacturing")
print(f"  {len(df)} sub-sectors across {df['sector'].nunique()} sectors")


# ── Compute layout ────────────────────────────────────────────────────────────
print("Computing squarify layout...")

sector_totals = (
    df.groupby("sector")["value_rm_mil"]
    .sum()
    .reset_index()
    .sort_values("value_rm_mil", ascending=False)
    .reset_index(drop=True)
)

sector_rects = squarify.squarify(
    squarify.normalize_sizes(sector_totals["value_rm_mil"].tolist(), W, H),
    0, 0, W, H
)

rows = []
for i, srow in sector_totals.iterrows():
    sector = srow["sector"]
    sr     = sector_rects[i]

    sub_df = (
        df[df["sector"] == sector]
        .sort_values("value_rm_mil", ascending=False)
        .reset_index(drop=True)
    )
    sub_vals = sub_df["value_rm_mil"].tolist()
    if not sub_vals:
        continue

    sub_rects = squarify.squarify(
        squarify.normalize_sizes(sub_vals, sr["dx"], sr["dy"]),
        sr["x"], sr["y"], sr["dx"], sr["dy"]
    )

    for j, sub in sub_df.iterrows():
        r = sub_rects[j]
        rows.append({
            "sector":              sector,
            "sub_sector":          sub["sub_sector"],
            "value_rm_mil":        round(float(sub["value_rm_mil"]), 2),
            "share_total_pct":     sub["share_total_pct"],
            "share_in_sector_pct": sub["share_in_sector_pct"],
            "colour":              SECTOR_COLOUR.get(sector, "#B4B2A9"),
            "x0": round(r["x"],          2),
            "y0": round(r["y"],          2),
            "x1": round(r["x"] + r["dx"], 2),
            "y1": round(r["y"] + r["dy"], 2),
            "w":  round(r["dx"],          2),
            "h":  round(r["dy"],          2),
        })

out = pd.DataFrame(rows)
os.makedirs("data", exist_ok=True)
out.to_csv(OUTPUT_FILE, index=False)
print(f"  ✅ {len(out)} rows → {OUTPUT_FILE}")

# Summary
print("\nSector breakdown:")
for sector, grp in out.groupby("sector"):
    total = grp["value_rm_mil"].sum()
    print(f"  {sector:<22} {len(grp):>2} sub-sectors  {total:>10,.1f} RM mil")
