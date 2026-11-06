import fs from "node:fs";
import path from "node:path";
import { naturalEarth1 } from "./map_projection.mjs";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const projection = JSON.parse(fs.readFileSync(path.join(root, "web/assets/data/projection.json"), "utf8"));
const fixtures = JSON.parse(fs.readFileSync(path.join(root, "scripts/map_fixtures.json"), "utf8"));
let maxError = 0;
for (const point of fixtures) {
  const got = naturalEarth1(point.lon, point.lat, projection);
  const error = Math.max(Math.abs(got[0] - point.xy[0]), Math.abs(got[1] - point.xy[1]));
  maxError = Math.max(maxError, error);
}
if (maxError > 0.01) {
  throw new Error(`proyección fuera de tolerancia: ${maxError}`);
}
console.log(`proyección OK · 5 puntos · error máximo ${maxError.toFixed(6)} px`);
