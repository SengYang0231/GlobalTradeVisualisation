"""
FIT2179 A2 — Arc GeoJSON Generator (Fixed)
Source: data/malaysia_arc_map.csv
Output: data/malaysia_arcs.geojson

Fixes:
  1. US/Mexico arcs forced westward via Pacific (antimeridian handling)
  2. Top 10 partners only — reduces crowding near Malaysia
  3. Stroke width range widened to [2, 12] for clearer thickness difference

Run: python prep_arc_geojson.py
"""

import json, math, pandas as pd, os

INPUT_FILE  = "data/malaysia_arc_map.csv"
OUTPUT_FILE = "data/malaysia_arcs.geojson"

# Only keep top N partners by export volume — reduces crowding
TOP_N = 10


def to_rad(d): return d * math.pi / 180
def to_deg(r): return r * 180 / math.pi


def great_circle_points(lon1, lat1, lon2, lat2, n=50, force_west=False):
    """
    Compute n+1 points along a great circle arc.
    force_west=True: go via Pacific (for Americas destinations from Asia).
    """
    if force_west:
        # Shift destination eastward by 360 to force western route,
        # then normalise longitudes back after interpolation
        lon2_adj = lon2 + 360
    else:
        lon2_adj = lon2

    r_lon1 = to_rad(lon1);  r_lat1 = to_rad(lat1)
    r_lon2 = to_rad(lon2_adj); r_lat2 = to_rad(lat2)

    d = math.acos(max(-1.0, min(1.0,
        math.sin(r_lat1) * math.sin(r_lat2) +
        math.cos(r_lat1) * math.cos(r_lat2) * math.cos(r_lon2 - r_lon1)
    )))

    if d < 1e-6:
        return [[lon1, lat1], [lon2, lat2]]

    points = []
    for i in range(n + 1):
        f = i / n
        A = math.sin((1 - f) * d) / math.sin(d)
        B = math.sin(f * d)       / math.sin(d)
        x = A * math.cos(r_lat1) * math.cos(r_lon1) + B * math.cos(r_lat2) * math.cos(r_lon2)
        y = A * math.cos(r_lat1) * math.sin(r_lon1) + B * math.cos(r_lat2) * math.sin(r_lon2)
        z = A * math.sin(r_lat1) + B * math.sin(r_lat2)
        lat = to_deg(math.atan2(z, math.sqrt(x * x + y * y)))
        lon = to_deg(math.atan2(y, x))
        # Normalise longitude to [-180, 180]
        while lon >  180: lon -= 360
        while lon < -180: lon += 360
        points.append([round(lon, 4), round(lat, 4)])

    return points


def scale_width(val, min_val, max_val, min_w=2.0, max_w=12.0):
    if max_val == min_val:
        return (min_w + max_w) / 2
    return round(min_w + (val - min_val) / (max_val - min_val) * (max_w - min_w), 2)


# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading arc data...")
df = pd.read_csv(INPUT_FILE)

# Keep top N by exports only
df = df.nlargest(TOP_N, "exports_usd_bn").reset_index(drop=True)
print(f"  Generating {len(df)} arcs (top {TOP_N} by export volume)")

min_exp = df["exports_usd_bn"].min()
max_exp = df["exports_usd_bn"].max()

# ── Build GeoJSON ─────────────────────────────────────────────────────────────
features = []
for _, row in df.iterrows():
    # Force westward route for Americas (US, Mexico, Brazil)
    # Detected when dest_lon < -30 (clearly in western hemisphere)
    force_west = row["dest_lon"] < -30

    arc_pts = great_circle_points(
        row["origin_lon"], row["origin_lat"],
        row["dest_lon"],   row["dest_lat"],
        n=60,
        force_west=force_west
    )

    feature = {
        "type": "Feature",
        "geometry": { "type": "LineString", "coordinates": arc_pts },
        "properties": {
            "partner":          str(row["partner"]),
            "exports_usd_bn":   float(row["exports_usd_bn"]),
            "imports_usd_bn":   float(row["imports_usd_bn"]),
            "balance_usd_bn":   float(row["balance_usd_bn"]),
            "trade_type":       str(row["trade_type"]),
            "stroke_width":     scale_width(row["exports_usd_bn"], min_exp, max_exp),
            "dest_lat":         float(row["dest_lat"]),
            "dest_lon":         float(row["dest_lon"]),
        }
    }
    features.append(feature)
    direction = "← PACIFIC" if force_west else ""
    print(f"  ✓ {row['partner']:25} {row['exports_usd_bn']:6.1f} bn  "
          f"width={scale_width(row['exports_usd_bn'], min_exp, max_exp):4.1f}  {direction}")

geojson = { "type": "FeatureCollection", "features": features }

os.makedirs("data", exist_ok=True)
with open(OUTPUT_FILE, "w") as f:
    json.dump(geojson, f, indent=2)

print(f"\n✅ Saved {len(features)} arcs → {OUTPUT_FILE}")