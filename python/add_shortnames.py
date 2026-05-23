"""
Run this once after generating malaysia_treemap_coords.csv.
Adds a short_name column for display labels in the treemap.
Adjust the mapping dict if your exact sub_sector values differ.
"""
import pandas as pd

SHORT_NAMES = {
    "Electrical & Electronic Products":         "E&E Products",
    "Petroleum Products":                       "Petroleum",
    "Liquefied Natural Gas":                    "LNG",
    "Palm Oil and Palm-Based Products":         "Palm Oil",
    "Palm Oil-Based Manufactures":              "Palm Oil Mfg.",
    "Other Manufactures":                       "Other Mfg.",
    "Manufacture Of Metal Products":            "Metal Products",
    "Chemical And Chemical Products":           "Chemicals",
    "Machinery, Equipment And Parts":           "Machinery & Equip.",
    "Optical & Scientific Equipment":           "Optical & Scientific",
    "Transport Equipment":                      "Transport Equip.",
    "Rubber Products":                          "Rubber",
    "Wood Products":                            "Wood Products",
    "Textiles And Clothing":                    "Textiles",
    "Food Preparations":                        "Food",
}

df = pd.read_csv("data/malaysia_treemap_coords.csv")

# Map to short name; fall back to original if not in dict
df["short_name"] = df["sub_sector"].map(SHORT_NAMES).fillna(df["sub_sector"])

df.to_csv("data/malaysia_treemap_coords.csv", index=False)
print("Done — short_name column added.")
print(df[["sub_sector", "short_name"]].drop_duplicates().to_string())
