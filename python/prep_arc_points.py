"""
FIT2179 A2 — Arc Points CSV Generator (Bezier)
Source: data/malaysia_arc_map.csv
Output: data/malaysia_arc_points.csv

Uses quadratic bezier curves instead of great circles.
Avoids antimeridian splitting entirely:
  - Americas (lon < -30): westward route via Atlantic (ctrl at ~6°E)
  - All other partners: direct route elevated northward

Run: python prep_arc_points.py
"""

import math, pandas as pd, os

INPUT_FILE  = "data/malaysia_arc_map.csv"
OUTPUT_FILE = "data/malaysia_arc_points.csv"
TOP_N       = 15   # include Europe (Netherlands ~rank 12)
N_POINTS    = 60


def bezier_arc(lon1, lat1, lon2, lat2, n=N_POINTS):
    """
    Quadratic bezier arc from (lon1,lat1) to (lon2,lat2).
    For Americas destinations (lon2 < -30): go westward via Atlantic.
    For all others: take direct route elevated northward.
    """
    if lon2 < -30:
        # Westward Atlantic route — keep all lons in [-180, 180]
        ctrl_lon = (lon1 + lon2) / 2          # e.g. 6°E for Malaysia→US
        ctrl_lat = (lat1 + lat2) / 2 + 30     # elevated above Europe
    else:
        # Direct eastward/nearby route
        delta = lon2 - lon1
        if delta > 180:  delta -= 360
        if delta < -180: delta += 360
        lon2_adj = lon1 + delta
        ctrl_lon = (lon1 + lon2_adj) / 2
        ctrl_lat = (lat1 + lat2) / 2 + max(8, abs(delta) * 0.18)

    pts = []
    for i in range(n + 1):
        t    = i / n
        lon  = (1-t)**2 * lon1 + 2*t*(1-t) * ctrl_lon + t**2 * lon2
        lat  = (1-t)**2 * lat1 + 2*t*(1-t) * ctrl_lat + t**2 * lat2
        # Normalise to [-180, 180]
        while lon >  180: lon -= 360
        while lon < -180: lon += 360
        pts.append((round(lon, 4), round(lat, 4)))

    return pts


def scale_width(val, mn, mx, min_w=1.5, max_w=10.0):
    if mx == mn: return (min_w + max_w) / 2
    return round(min_w + (val-mn) / (mx-mn) * (max_w-min_w), 2)


print("Loading arc data...")
df = pd.read_csv(INPUT_FILE)
df = df.nlargest(TOP_N, "exports_usd_bn").reset_index(drop=True)
mn, mx = df["exports_usd_bn"].min(), df["exports_usd_bn"].max()
print(f"  Partners ({TOP_N}):")

rows = []
for _, row in df.iterrows():
    pts = bezier_arc(
        row["origin_lon"], row["origin_lat"],
        row["dest_lon"],   row["dest_lat"]
    )

    # Check no antimeridian crossing
    broken = any(abs(pts[i+1][0]-pts[i][0]) > 180 for i in range(len(pts)-1))
    sw     = scale_width(row["exports_usd_bn"], mn, mx)

    for step, (lon, lat) in enumerate(pts):
        rows.append({
            "partner":          row["partner"],
            "arc_id":           row["partner"],  # single arc per partner
            "step":             step,
            "lon":              lon,
            "lat":              lat,
            "trade_type":       row["trade_type"],
            "stroke_width":     sw,
            "exports_usd_bn":   row["exports_usd_bn"],
            "imports_usd_bn":   row["imports_usd_bn"],
            "balance_usd_bn":   row["balance_usd_bn"],
        })

    route = "← Atlantic" if row["dest_lon"] < -30 else ""
    warn  = " ⚠ BROKEN" if broken else ""
    print(f"  {row['partner']:28} {row['exports_usd_bn']:5.1f}bn  "
          f"w={sw:4.1f}  {route}{warn}")

out = pd.DataFrame(rows)
os.makedirs("data", exist_ok=True)
out.to_csv(OUTPUT_FILE, index=False)
print(f"\n✅ {len(out)} rows → {OUTPUT_FILE}")
print(f"   {TOP_N} partners × {N_POINTS+1} points each")