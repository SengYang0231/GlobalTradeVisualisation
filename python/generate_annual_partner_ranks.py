"""
generate_annual_partner_ranks.py

Run from your project root:
    python generate_annual_partner_ranks.py

Reads  data/malaysia_partner_ranks.csv  (snapshot years only)
Writes data/malaysia_partner_ranks.csv  (annual 2000-2023, overwrites)

How it works:
- For each partner, linearly interpolates exports_usd_bn between
  the known snapshot years (2000, 2005, 2010, 2013, 2015, 2018, 2020, 2023)
- Recomputes rank per year from the interpolated values
  (rank 1 = highest exports that year)
"""

import pandas as pd

SRC = "data/malaysia_partner_ranks.csv"
OUT = "data/malaysia_partner_ranks.csv"   # overwrites in place

df = pd.read_csv(SRC)
df['year'] = df['year'].astype(int)

print(f"Input: {len(df)} rows, snapshot years: {sorted(df['year'].unique())}")

partners = df['partner'].unique()
all_years = list(range(2000, 2024))
rows = []

for partner in partners:
    sub = df[df['partner'] == partner].sort_values('year')
    known_years   = sub['year'].tolist()
    known_exports = dict(zip(sub['year'], sub['exports_usd_bn']))

    for year in all_years:
        lo = max((y for y in known_years if y <= year), default=None)
        hi = min((y for y in known_years if y >= year), default=None)

        if lo is None:
            val = known_exports[hi]
        elif hi is None:
            val = known_exports[lo]
        elif lo == hi:
            val = known_exports[lo]
        else:
            t   = (year - lo) / (hi - lo)
            val = known_exports[lo] + t * (known_exports[hi] - known_exports[lo])

        rows.append({'year': year, 'partner': partner, 'exports_usd_bn': round(val, 3)})

out = pd.DataFrame(rows)

# Recompute rank per year (1 = highest exports)
out['rank'] = (
    out.groupby('year')['exports_usd_bn']
       .rank(ascending=False, method='first')
       .astype(int)
)

out = out.sort_values(['year', 'rank']).reset_index(drop=True)
out.to_csv(OUT, index=False)

print(f"Output: {len(out)} rows, years: {sorted(out['year'].unique())}")
print("Done — data/malaysia_partner_ranks.csv updated.")
