"""
FIT2179 A2 — Arc GeoJSON Generator
Source: data/malaysia_arc_map.csv
Output: data/malaysia_arcs.geojson

Antimeridian fix: for Americas destinations (lon < -30),
arc points keep longitudes in [180,270] range instead of
normalising to negative. Vega-Lite's equalEarth projection
handles this correctly and draws the arc westward.
"""

import json, math, pandas as pd, os

INPUT_FILE  = "data/malaysia_arc_map.csv"
OUTPUT_FILE = "data/malaysia_arcs.geojson"
TOP_N       = 10


def to_rad(d): return d * math.pi / 180
def to_deg(r): return r * 180 / math.pi


def great_circle_points(lon1, lat1, lon2, lat2, n=60):
    """
    Compute n+1 points along a great circle arc.
    For Americas destinations (lon2 < -30), keeps longitudes
    above 180 so Vega-Lite draws the arc across the Pacific.
    """
    force_west = lon2 < -30
    lon2_adj   = lon2 + 360 if force_west else lon2

    r1 = to_rad(lon1);  rlat1 = to_rad(lat1)
    r2 = to_rad(lon2_adj); rlat2 = to_rad(lat2)

    d = math.acos(max(-1.0, min(1.0,
        math.sin(rlat1)*math.sin(rlat2) +
        math.cos(rlat1)*math.cos(rlat2)*math.cos(r2-r1)
    )))

    if d < 1e-6:
        return [[lon1, lat1], [lon2_adj if force_west else lon2, lat2]]

    points = []
    for i in range(n + 1):
        f = i / n
        A = math.sin((1-f)*d) / math.sin(d)
        B = math.sin(f*d)     / math.sin(d)
        x = A*math.cos(rlat1)*math.cos(r1) + B*math.cos(rlat2)*math.cos(r2)
        y = A*math.cos(rlat1)*math.sin(r1) + B*math.cos(rlat2)*math.sin(r2)
        z = A*math.sin(rlat1)              + B*math.sin(rlat2)
        lat = to_deg(math.atan2(z, math.sqrt(x*x + y*y)))
        lon = to_deg(math.atan2(y, x))
        # For westward arcs, keep lon in [0,360] — do NOT normalise to negative
        if force_west and lon < 0:
            lon += 360
        # For all other arcs, keep in [-180,180]
        elif not force_west:
            while lon >  180: lon -= 360
            while lon < -180: lon += 360
        points.append([round(lon, 4), round(lat, 4)])

    return points


def scale_width(val, min_val, max_val, min_w=2.0, max_w=12.0):
    if max_val == min_val:
        return (min_w + max_w) / 2
    return round(min_w + (val-min_val)/(max_val-min_val)*(max_w-min_w), 2)


print("Loading arc data...")
df = pd.read_csv(INPUT_FILE)
df = df.nlargest(TOP_N, "exports_usd_bn").reset_index(drop=True)
print(f"  Generating {len(df)} arcs")

min_exp = df["exports_usd_bn"].min()
max_exp = df["exports_usd_bn"].max()

features = []
for _, row in df.iterrows():
    arc_pts = great_circle_points(
        row["origin_lon"], row["origin_lat"],
        row["dest_lon"],   row["dest_lat"],
        n=60
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
    west = "← PACIFIC" if row["dest_lon"] < -30 else ""
    print(f"  ✓ {row['partner']:25} {row['exports_usd_bn']:5.1f} bn  "
          f"w={scale_width(row['exports_usd_bn'],min_exp,max_exp):4.1f}  {west}")

geojson = {"type": "FeatureCollection", "features": features}
os.makedirs("data", exist_ok=True)
with open(OUTPUT_FILE, "w") as f:
    json.dump(geojson, f, indent=2)

print(f"\n✅ {len(features)} arcs → {OUTPUT_FILE}")