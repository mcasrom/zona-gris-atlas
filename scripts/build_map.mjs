// Genera el mapa de puntos y el fixture de proyección.
// Dependencias en una carpeta temporal; no se instala nada global.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const TMP = path.join(os.tmpdir(), "zona-gris-map");
fs.mkdirSync(TMP, { recursive: true });
const marker = path.join(TMP, "node_modules", "d3-geo");
if (!fs.existsSync(marker)) {
  execFileSync("npm", ["install", "--prefix", TMP, "--silent", "d3-geo@3.1.1", "topojson-client@3.1.0", "world-atlas@2.0.2"], {
    stdio: "inherit",
  });
}
const require = createRequire(path.join(TMP, "package.json"));
const { geoNaturalEarth1, geoContains } = require("d3-geo");
const { feature } = require("topojson-client");
const world = require("world-atlas/countries-110m.json");
const land = feature(world, world.objects.countries);
const width = 1000;
const height = 435;
const projection = geoNaturalEarth1().fitExtent([[0, 0], [width, height]], { type: "Sphere" });

const rows = [];
for (let y = 0; y <= height; y += 10) {
  let start = null;
  for (let x = 0; x <= width; x += 10) {
    const ll = projection.invert([x, y]);
    const inside = ll && ll[1] >= -57 && geoContains(land, ll);
    if (inside && start === null) start = x;
    if (!inside && start !== null) {
      if (x - 10 >= start) rows.push(`M${start} ${y}H${x - 10}`);
      start = null;
    }
  }
  if (start !== null) rows.push(`M${start} ${y}H${width}`);
}

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Mapa mundial de puntos"><g fill="none" stroke="#323D4A" stroke-width="4.2" stroke-linecap="round" stroke-dasharray="0 10">${rows.map((d) => `<path d="${d}"/>`).join("")}</g></svg>`;
fs.writeFileSync(path.join(ROOT, "web/assets/img/world-dots.svg"), svg);
fs.writeFileSync(
  path.join(ROOT, "web/assets/data/projection.json"),
  JSON.stringify({ width, height, scale: projection.scale(), translate: projection.translate() }, null, 2) + "\n"
);
const points = [
  [-3.7038, 40.4168],
  [32.97, 34.85],
  [13.405, 52.52],
  [-5.32, 35.88],
  [151.21, -33.86],
];
const fixtures = points.map(([lon, lat]) => ({ lon, lat, xy: projection([lon, lat]) }));
fs.writeFileSync(path.join(ROOT, "scripts/map_fixtures.json"), JSON.stringify(fixtures, null, 2) + "\n");
console.log(`mapa: ${rows.length} tramos · ${Buffer.byteLength(svg)} bytes`);
