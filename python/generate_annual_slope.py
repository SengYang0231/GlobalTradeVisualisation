"""
generate_annual_slope.py
Run from your project root:  python generate_annual_slope.py

Reads data/malaysia_export_mix_slope.csv (which has 3 snapshot years:
2000, 2013, 2023 per category) and writes back a new CSV with one row
per year per category (2000-2023), using linear interpolation between
the snapshots. This gives chart10 a dot at every year.
"""
import pandas as pd
import numpy as np

SRC = "data/malaysia_export_mix_slope.csv"
OUT = "data/malaysia_export_mix_slope.csv"   # overwrite in place

df = pd.read_csv(SRC)
df['snapshot_year'] = df['snapshot_year'].astype(int)

print("Original snapshot years:", sorted(df['snapshot_year'].unique()))
print("Categories:", df['section_label'].nunique())

rows = []
for cat, group in df.groupby('section_label'):
    group = group.sort_values('snapshot_year').reset_index(drop=True)
    years_with_data = group['snapshot_year'].tolist()
    shares = dict(zip(group['snapshot_year'], group['share_pct']))

    for year in range(2000, 2024):
        # Linear interpolation between bracketing snapshot years
        lo_yr = max((y for y in years_with_data if y <= year), default=None)
        hi_yr = min((y for y in years_with_data if y >= year), default=None)

        if lo_yr is None:
            share = shares[hi_yr]
        elif hi_yr is None:
            share = shares[lo_yr]
        elif lo_yr == hi_yr:
            share = shares[lo_yr]
        else:
            t = (year - lo_yr) / (hi_yr - lo_yr)
            share = shares[lo_yr] + t * (shares[hi_yr] - shares[lo_yr])

        rows.append({
            'section_label': cat,
            'snapshot_year': year,
            'share_pct': round(share, 4)
        })

out_df = pd.DataFrame(rows)
out_df.to_csv(OUT, index=False)

print(f"\nDone. Output: {len(out_df)} rows ({out_df['snapshot_year'].nunique()} years × {out_df['section_label'].nunique()} categories)")
print("Years:", sorted(out_df['snapshot_year'].unique()))
