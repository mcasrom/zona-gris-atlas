from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Place:
    name: str
    country_iso2: str
    lat: float
    lon: float


class Gazetteer:
    """Gazetteer offline basado en GeoNames cities15000.txt."""

    def __init__(self, rows: list[Place]):
        self.by_name: dict[str, list[Place]] = {}
        for place in rows:
            self.by_name.setdefault(place.name.casefold(), []).append(place)

    @classmethod
    def load(cls, path: Path) -> "Gazetteer":
        if not path.exists():
            return cls([])
        rows: list[Place] = []
        with path.open(encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.reader(handle, delimiter="\t")
            for parts in reader:
                if len(parts) < 9:
                    continue
                try:
                    rows.append(
                        Place(
                            name=parts[1],
                            lat=float(parts[4]),
                            lon=float(parts[5]),
                            country_iso2=parts[8],
                        )
                    )
                except ValueError:
                    continue
        return cls(rows)

    def lookup(self, name: str, country_iso2: str | None = None) -> Place | None:
        candidates = self.by_name.get(name.casefold(), [])
        if country_iso2:
            candidates = [p for p in candidates if p.country_iso2.upper() == country_iso2.upper()]
        return candidates[0] if candidates else None


def geocode(name: str, country_iso2: str | None = None, path: Path | None = None) -> Place | None:
    gazetteer_path = path or Path("data/raw/cities15000.txt")
    return Gazetteer.load(gazetteer_path).lookup(name, country_iso2)
