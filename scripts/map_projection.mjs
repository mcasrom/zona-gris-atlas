export function naturalEarth1(lon, lat, projection) {
  const D2R = Math.PI / 180;
  const lambda = lon * D2R;
  const phi = lat * D2R;
  const phi2 = phi * phi;
  const phi4 = phi2 * phi2;
  const x = lambda * (0.8707 - 0.131979 * phi2 + phi4 * (-0.013791 + phi4 * (0.003971 * phi2 - 0.001529 * phi4)));
  const y = phi * (1.007226 + phi2 * (0.015085 + phi4 * (-0.044475 + 0.028874 * phi2 - 0.005916 * phi4)));
  return [projection.scale * x + projection.translate[0], projection.translate[1] - projection.scale * y];
}
