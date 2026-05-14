/* ─────────────────────────────────────────────
   FIT2179 A2 — charts.js
   Loads each Vega-Lite JSON spec from js/ folder
   and embeds into the corresponding <div> on index.html.
   Charts 6, 7, 9 are added when ready.
───────────────────────────────────────────── */

const SPECS = [
  { id: "chart1",  file: "js/chart1_choropleth.vl.json"   },
  { id: "chart2",  file: "js/chart2_bar.vl.json"          },
  { id: "chart3",  file: "js/chart3_scatter.vl.json"      },
  { id: "chart4",  file: "js/chart4_area.vl.json"         },
  { id: "chart5",  file: "js/chart5_lollipop.vl.json"     },
  { id: "chart8",  file: "js/chart8_dotplot.vl.json"      },
  { id: "chart10", file: "js/chart10_slope.vl.json"       },
  { id: "chart11", file: "js/chart11_stacked_area.vl.json"},
  /* Add when ready:
  { id: "chart6",  file: "js/chart6_arc_map.vl.json"      },
  { id: "chart7",  file: "js/chart7_bump.vl.json"         },
  { id: "chart9",  file: "js/chart9_treemap.vg.json"      },
  */
];

const OPTS = {
  actions: false,       /* hide export buttons — cleaner look */
  renderer: "svg",      /* SVG for crisp rendering */
  config: {
    font: "Inter, Segoe UI, sans-serif"
  }
};

SPECS.forEach(({ id, file }) => {
  vegaEmbed(`#${id}`, file, OPTS).catch(err => {
    console.error(`Chart ${id} failed to load: ${err}`);
    const el = document.getElementById(id);
    if (el) {
      el.innerHTML = `<p style="color:#D85A30;padding:16px;font-size:13px;">
        ⚠️ Could not load ${file}: ${err.message}
      </p>`;
    }
  });
});
