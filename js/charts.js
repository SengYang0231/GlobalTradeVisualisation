/* ─────────────────────────────────────────────
   FIT2179 A2 — charts.js
   Colour palette (colour-blind safe, A1 lesson):
     Exports / surplus : #1D9E75  (teal)
     Imports / deficit : #D85A30  (coral)
     Malaysia highlight: #534AB7  (purple)
     Other countries   : #B4B2A9  (grey)
     Annotations       : #BA7517  (amber)
   Rules:
     - No red + green together
     - Each colour maps to ONE attribute only
     - Every chart has at least one annotation
     - {actions: false} on all embeds (clean UI)
───────────────────────────────────────────── */

/* ══════════════════════════════════════════════
   CHART 1 — World choropleth
   Data: data/choropleth_exports.csv
   Idiom: Map (required) — geoshape
   Join: world-110m numeric id → iso_numeric.csv
         → choropleth_exports.csv code
   Note: pending iso_numeric.csv (prep_iso_lookup.py)
══════════════════════════════════════════════ */
const spec1 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": "container",
  "height": 420,
  "config": { "font": "Inter, Segoe UI, sans-serif" },
  "layer": [
    {
      "data": {
        "url": "https://cdn.jsdelivr.net/npm/vega-datasets@1.31.1/data/world-110m.json",
        "format": { "type": "topojson", "feature": "countries" }
      },
      "transform": [
        {
          "lookup": "id",
          "from": {
            "data": { "url": "data/iso_numeric.csv" },
            "key": "numeric",
            "fields": ["alpha3"]
          }
        },
        {
          "lookup": "alpha3",
          "from": {
            "data": { "url": "data/choropleth_exports.csv" },
            "key": "code",
            "fields": ["exports_pct_gdp", "country"]
          }
        }
      ],
      "projection": { "type": "equalEarth" },
      "mark": {
        "type": "geoshape",
        "stroke": "#ffffff",
        "strokeWidth": 0.4
      },
      "encoding": {
        "color": {
          "condition": {
            "test": "datum.alpha3 === 'MYS'",
            "value": "#534AB7"
          },
          "field": "exports_pct_gdp",
          "type": "quantitative",
          "scale": {
            "scheme": "tealblues",
            "domain": [0, 150]
          },
          "legend": {
            "title": "Exports % of GDP",
            "orient": "bottom-right",
            "gradientLength": 120
          }
        },
        "tooltip": [
          { "field": "country", "type": "nominal", "title": "Country" },
          { "field": "exports_pct_gdp", "type": "quantitative",
            "format": ".1f", "title": "Exports % GDP" }
        ]
      }
    },
    {
      "data": {
        "values": [{ "note": "Malaysia" }]
      },
      "mark": {
        "type": "text",
        "text": "← Malaysia",
        "fontSize": 11,
        "fontWeight": "bold",
        "color": "#534AB7",
        "x": 730, "y": 270
      }
    }
  ]
};

vegaEmbed("#chart1", spec1, { actions: false }).catch(console.error);


/* ══════════════════════════════════════════════
   CHART 2 — Horizontal bar chart
   Data: data/top10_exporters.csv
   Idiom: Bar chart (standard)
   A1 lesson: Malaysia in purple, others in grey
              No red/green used
══════════════════════════════════════════════ */
const spec2 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": "container",
  "height": 320,
  "config": { "font": "Inter, Segoe UI, sans-serif", "view": { "stroke": null } },
  "data": { "url": "data/top10_exporters.csv" },
  "layer": [
    {
      "mark": { "type": "bar", "cornerRadiusEnd": 3 },
      "encoding": {
        "y": {
          "field": "country",
          "type": "nominal",
          "sort": "-x",
          "axis": {
            "title": null,
            "labelFontSize": 12,
            "labelLimit": 180
          }
        },
        "x": {
          "field": "trade_pct_gdp",
          "type": "quantitative",
          "axis": {
            "title": "Trade as % of GDP",
            "titleFontSize": 11,
            "grid": false,
            "tickCount": 5
          }
        },
        "color": {
          "condition": {
            "test": "datum.highlight == 'True'",
            "value": "#534AB7"
          },
          "value": "#B4B2A9"
        },
        "tooltip": [
          { "field": "country", "type": "nominal", "title": "Country" },
          { "field": "trade_pct_gdp", "type": "quantitative",
            "format": ".1f", "title": "Trade % of GDP" }
        ]
      }
    },
    {
      "transform": [{ "filter": "datum.highlight == 'True'" }],
      "mark": {
        "type": "text",
        "align": "left",
        "dx": 5,
        "fontSize": 11,
        "fontWeight": "bold",
        "color": "#534AB7"
      },
      "encoding": {
        "y": { "field": "country", "type": "nominal", "sort": "-x" },
        "x": { "field": "trade_pct_gdp", "type": "quantitative" },
        "text": { "value": "← Malaysia" }
      }
    }
  ]
};

vegaEmbed("#chart2", spec2, { actions: false }).catch(console.error);


/* ══════════════════════════════════════════════
   CHART 3 — Scatterplot
   Data: data/trade_openness_gdp.csv
   Idiom: Scatterplot (standard)
   X: GDP per capita (PPP USD)
   Y: Trade as % of GDP
   A1 lesson: Malaysia annotated, colour hierarchy
══════════════════════════════════════════════ */
const spec3 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": "container",
  "height": 320,
  "config": { "font": "Inter, Segoe UI, sans-serif", "view": { "stroke": null } },
  "data": { "url": "data/trade_openness_gdp.csv" },
  "layer": [
    {
      "mark": { "type": "point", "filled": true, "opacity": 0.55 },
      "encoding": {
        "x": {
          "field": "gdp_per_capita",
          "type": "quantitative",
          "scale": { "type": "log" },
          "axis": {
            "title": "GDP per capita, PPP (log scale)",
            "titleFontSize": 11,
            "tickCount": 5,
            "format": ",.0f"
          }
        },
        "y": {
          "field": "trade_pct_gdp",
          "type": "quantitative",
          "axis": {
            "title": "Trade as % of GDP",
            "titleFontSize": 11,
            "grid": true,
            "gridColor": "#f0ede8"
          }
        },
        "color": {
          "condition": {
            "test": "datum.highlight == 'True'",
            "value": "#534AB7"
          },
          "value": "#B4B2A9"
        },
        "size": {
          "condition": {
            "test": "datum.highlight == 'True'",
            "value": 120
          },
          "value": 40
        },
        "tooltip": [
          { "field": "country", "type": "nominal", "title": "Country" },
          { "field": "gdp_per_capita", "type": "quantitative",
            "format": ",.0f", "title": "GDP per capita (PPP)" },
          { "field": "trade_pct_gdp", "type": "quantitative",
            "format": ".1f", "title": "Trade % of GDP" }
        ]
      }
    },
    {
      "transform": [{ "filter": "datum.highlight == 'True'" }],
      "mark": {
        "type": "text",
        "align": "left",
        "dx": 10,
        "dy": -4,
        "fontSize": 12,
        "fontWeight": "bold",
        "color": "#534AB7"
      },
      "encoding": {
        "x": { "field": "gdp_per_capita", "type": "quantitative",
                "scale": { "type": "log" } },
        "y": { "field": "trade_pct_gdp", "type": "quantitative" },
        "text": { "value": "Malaysia" }
      }
    }
  ]
};

vegaEmbed("#chart3", spec3, { actions: false }).catch(console.error);


/* ══════════════════════════════════════════════
   CHART 4 — Dual-line area chart
   Data: data/malaysia_trade_timeseries.csv
   Idiom: Area chart (standard)
   Long format: metric = "Exports" | "Imports"
   A1 lesson: teal=exports, coral=imports, annotate events
══════════════════════════════════════════════ */
const spec4 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": "container",
  "height": 340,
  "config": { "font": "Inter, Segoe UI, sans-serif", "view": { "stroke": null } },
  "data": { "url": "data/malaysia_trade_timeseries.csv" },
  "layer": [
    {
      "mark": { "type": "area", "opacity": 0.15, "line": false },
      "encoding": {
        "x": {
          "field": "year", "type": "ordinal",
          "axis": { "title": null, "labelAngle": 0, "tickCount": 8 }
        },
        "y": {
          "field": "value_usd_bn",
          "type": "quantitative",
          "axis": { "title": "Trade value (USD billions)", "titleFontSize": 11,
                    "grid": true, "gridColor": "#f0ede8" }
        },
        "color": {
          "field": "metric", "type": "nominal",
          "scale": {
            "domain": ["Exports", "Imports"],
            "range":  ["#1D9E75", "#D85A30"]
          },
          "legend": null
        }
      }
    },
    {
      "mark": { "type": "line", "strokeWidth": 2.5 },
      "encoding": {
        "x": { "field": "year", "type": "ordinal" },
        "y": { "field": "value_usd_bn", "type": "quantitative" },
        "color": {
          "field": "metric", "type": "nominal",
          "scale": {
            "domain": ["Exports", "Imports"],
            "range":  ["#1D9E75", "#D85A30"]
          },
          "legend": {
            "title": null,
            "orient": "top-left",
            "labelFontSize": 12
          }
        }
      }
    },
    {
      "transform": [
        { "filter": "datum.event !== '' && datum.metric === 'Exports'" }
      ],
      "mark": {
        "type": "rule",
        "strokeDash": [4, 3],
        "strokeWidth": 1.2,
        "color": "#BA7517",
        "opacity": 0.7
      },
      "encoding": {
        "x": { "field": "year", "type": "ordinal" }
      }
    },
    {
      "transform": [
        { "filter": "datum.event !== '' && datum.metric === 'Exports'" }
      ],
      "mark": {
        "type": "text",
        "align": "left",
        "angle": 0,
        "dx": 4,
        "dy": -10,
        "fontSize": 10,
        "fontStyle": "italic",
        "color": "#BA7517"
      },
      "encoding": {
        "x": { "field": "year", "type": "ordinal" },
        "y": { "field": "value_usd_bn", "type": "quantitative" },
        "text": { "field": "event" }
      }
    }
  ]
};

vegaEmbed("#chart4", spec4, { actions: false }).catch(console.error);


/* ══════════════════════════════════════════════
   CHART 5 — Lollipop chart (trade balance)
   Data: data/malaysia_trade_balance.csv
   Idiom: Lollipop (standard — A1 lesson: size refined)
   A1 lesson: teal=surplus, coral=deficit
              Dot size 80, stroke 2 (explicit sizing)
══════════════════════════════════════════════ */
const spec5 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": "container",
  "height": 340,
  "config": { "font": "Inter, Segoe UI, sans-serif", "view": { "stroke": null } },
  "data": { "url": "data/malaysia_trade_balance.csv" },
  "layer": [
    {
      "mark": { "type": "rule", "strokeWidth": 2 },
      "encoding": {
        "y": {
          "field": "year", "type": "ordinal",
          "sort": "descending",
          "axis": { "title": null, "labelFontSize": 11 }
        },
        "x": {
          "field": "balance_usd_bn", "type": "quantitative",
          "axis": {
            "title": "Trade balance (USD billions)",
            "titleFontSize": 11,
            "grid": true,
            "gridColor": "#f0ede8"
          }
        },
        "x2": { "datum": 0 },
        "color": {
          "field": "direction", "type": "nominal",
          "scale": {
            "domain": ["Surplus", "Deficit"],
            "range":  ["#1D9E75", "#D85A30"]
          },
          "legend": null
        }
      }
    },
    {
      "mark": { "type": "point", "filled": true, "size": 80, "strokeWidth": 0 },
      "encoding": {
        "y": {
          "field": "year", "type": "ordinal",
          "sort": "descending"
        },
        "x": {
          "field": "balance_usd_bn", "type": "quantitative"
        },
        "color": {
          "field": "direction", "type": "nominal",
          "scale": {
            "domain": ["Surplus", "Deficit"],
            "range":  ["#1D9E75", "#D85A30"]
          },
          "legend": {
            "title": null,
            "orient": "bottom-right",
            "labelFontSize": 11
          }
        },
        "tooltip": [
          { "field": "year", "type": "ordinal", "title": "Year" },
          { "field": "balance_usd_bn", "type": "quantitative",
            "format": ".2f", "title": "Balance (USD bn)" },
          { "field": "direction", "type": "nominal", "title": "Status" }
        ]
      }
    },
    {
      "mark": { "type": "rule", "strokeWidth": 1, "color": "#918980",
                "strokeDash": [3, 2] },
      "encoding": { "x": { "datum": 0 } }
    },
    {
      "transform": [{ "filter": "datum.event !== ''" }],
      "mark": {
        "type": "text",
        "align": "right",
        "dx": -6,
        "fontSize": 10,
        "fontStyle": "italic",
        "color": "#BA7517"
      },
      "encoding": {
        "y": { "field": "year", "type": "ordinal", "sort": "descending" },
        "x": { "datum": 0 },
        "text": { "field": "event" }
      }
    }
  ]
};

vegaEmbed("#chart5", spec5, { actions: false }).catch(console.error);


/* ══════════════════════════════════════════════
   CHARTS 6–11 — TO BE BUILT
   (arc map, bump chart, dot plot,
    treemap, slope chart, stacked area)
══════════════════════════════════════════════ */

/* Chart 6 — Arc flow map (custom + map) */
/* TODO — built in next session */

/* Chart 7 — Bump/rank chart (custom) */
/* TODO — built in next session */

/* Chart 8 — Dot plot surplus/deficit */
const spec8 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": "container",
  "height": 360,
  "config": { "font": "Inter, Segoe UI, sans-serif", "view": { "stroke": null } },
  "data": { "url": "data/malaysia_partner_balance.csv" },
  "layer": [
    {
      "mark": { "type": "rule", "strokeWidth": 1, "color": "#918980",
                "strokeDash": [3, 2] },
      "encoding": { "x": { "datum": 0 } }
    },
    {
      "mark": { "type": "point", "filled": true, "size": 90 },
      "encoding": {
        "y": {
          "field": "partner", "type": "nominal",
          "sort": { "field": "balance_usd_bn", "order": "descending" },
          "axis": { "title": null, "labelFontSize": 11, "labelLimit": 130 }
        },
        "x": {
          "field": "balance_usd_bn", "type": "quantitative",
          "axis": {
            "title": "Bilateral balance (USD billions)",
            "titleFontSize": 11,
            "grid": true,
            "gridColor": "#f0ede8"
          }
        },
        "color": {
          "field": "direction", "type": "nominal",
          "scale": {
            "domain": ["Surplus", "Deficit"],
            "range": ["#1D9E75", "#D85A30"]
          },
          "legend": {
            "title": null, "orient": "bottom-right", "labelFontSize": 11
          }
        },
        "tooltip": [
          { "field": "partner", "type": "nominal", "title": "Partner" },
          { "field": "exports_usd_bn", "type": "quantitative",
            "format": ".2f", "title": "Exports (USD bn)" },
          { "field": "imports_usd_bn", "type": "quantitative",
            "format": ".2f", "title": "Imports (USD bn)" },
          { "field": "balance_usd_bn", "type": "quantitative",
            "format": ".2f", "title": "Balance (USD bn)" }
        ]
      }
    }
  ]
};

vegaEmbed("#chart8", spec8, { actions: false }).catch(console.error);


/* Chart 9 — Treemap (Vega, not Vega-Lite) */
/* TODO — built in next session */

/* Chart 10 — Slope chart (custom) */
const spec10 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": "container",
  "height": 400,
  "config": { "font": "Inter, Segoe UI, sans-serif", "view": { "stroke": null } },
  "data": { "url": "data/malaysia_export_mix_slope.csv" },
  "layer": [
    {
      "mark": { "type": "line", "strokeWidth": 1.8, "opacity": 0.75 },
      "encoding": {
        "x": {
          "field": "snapshot_year", "type": "ordinal",
          "axis": {
            "title": null,
            "labelFontSize": 13,
            "labelFontWeight": "bold"
          }
        },
        "y": {
          "field": "share_pct", "type": "quantitative",
          "axis": {
            "title": "Share of total exports (%)",
            "titleFontSize": 11,
            "grid": true,
            "gridColor": "#f0ede8"
          }
        },
        "color": {
          "field": "section_label", "type": "nominal",
          "scale": {
            "domain": [
              "Machinery & Transport Equipment",
              "Mineral Fuels & Petroleum",
              "Misc. Manufactured Articles",
              "Manufactured Goods",
              "Chemicals",
              "Animal & Vegetable Oils",
              "Food & Live Animals",
              "Crude Materials",
              "Other Commodities",
              "Beverages & Tobacco"
            ],
            "range": [
              "#534AB7","#D85A30","#1D9E75","#BA7517",
              "#185FA5","#9b59b6","#B4B2A9","#7f8c8d",
              "#e67e22","#2ecc71"
            ]
          },
          "legend": {
            "title": "Export category",
            "orient": "right",
            "labelFontSize": 11,
            "labelLimit": 200
          }
        },
        "detail": { "field": "section_label", "type": "nominal" }
      }
    },
    {
      "mark": { "type": "point", "filled": true, "size": 60, "opacity": 0.9 },
      "encoding": {
        "x": { "field": "snapshot_year", "type": "ordinal" },
        "y": { "field": "share_pct", "type": "quantitative" },
        "color": { "field": "section_label", "type": "nominal",
                   "legend": null }
      }
    },
    {
      "transform": [
        { "filter": "datum.snapshot_year === 2023" },
        { "filter": "datum.share_pct > 3" }
      ],
      "mark": {
        "type": "text",
        "align": "left",
        "dx": 6,
        "fontSize": 10
      },
      "encoding": {
        "x": { "field": "snapshot_year", "type": "ordinal" },
        "y": { "field": "share_pct", "type": "quantitative" },
        "text": { "field": "section_label", "type": "nominal" },
        "color": { "field": "section_label", "type": "nominal",
                   "legend": null }
      }
    }
  ]
};

vegaEmbed("#chart10", spec10, { actions: false }).catch(console.error);


/* Chart 11 — Stacked area chart */
const spec11 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "width": "container",
  "height": 360,
  "config": { "font": "Inter, Segoe UI, sans-serif", "view": { "stroke": null } },
  "data": { "url": "data/malaysia_exports_by_sitc_annual.csv" },
  "mark": { "type": "area", "opacity": 0.9 },
  "encoding": {
    "x": {
      "field": "year", "type": "ordinal",
      "axis": {
        "title": null,
        "labelAngle": 0,
        "tickCount": 8
      }
    },
    "y": {
      "field": "exports_rm_bil", "type": "quantitative",
      "stack": "zero",
      "axis": {
        "title": "Exports (RM billions)",
        "titleFontSize": 11,
        "grid": true,
        "gridColor": "#f0ede8"
      }
    },
    "color": {
      "field": "section_label", "type": "nominal",
      "scale": {
        "domain": [
          "Machinery & Transport Equipment",
          "Mineral Fuels & Petroleum",
          "Misc. Manufactured Articles",
          "Manufactured Goods",
          "Chemicals",
          "Animal & Vegetable Oils",
          "Food & Live Animals",
          "Crude Materials",
          "Other Commodities",
          "Beverages & Tobacco"
        ],
        "range": [
          "#534AB7","#D85A30","#1D9E75","#BA7517",
          "#185FA5","#9b59b6","#B4B2A9","#7f8c8d",
          "#e67e22","#2ecc71"
        ]
      },
      "legend": {
        "title": "Export category",
        "orient": "right",
        "labelFontSize": 11,
        "labelLimit": 220
      }
    },
    "order": {
      "field": "exports_rm_bil", "type": "quantitative",
      "sort": "descending"
    },
    "tooltip": [
      { "field": "year", "type": "ordinal", "title": "Year" },
      { "field": "section_label", "type": "nominal", "title": "Category" },
      { "field": "exports_rm_bil", "type": "quantitative",
        "format": ".1f", "title": "Exports (RM bn)" }
    ]
  }
};

vegaEmbed("#chart11", spec11, { actions: false }).catch(console.error);
