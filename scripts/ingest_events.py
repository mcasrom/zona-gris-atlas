#!/usr/bin/env python3
"""Recolector automático de acontecimientos candidatos para el Atlas.

- Consulta Bing News RSS (sin claves).
- Conserva solo metadatos y un resumen corto; no descarga el artículo completo.
- Agrupa titulares parecidos del mismo día/categoría.
- Asigna un estado conservador: nunca CONFIRMADO de forma automática.
- Guarda una huella SHA-256 de la evidencia y metadatos de la fuente.
- No sustituye los registros curados manualmente.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "events" / "auto" / "events.jsonl"
DEFAULT_SOURCES = ROOT / "data" / "events" / "auto" / "sources.json"
DEFAULT_PLACES = ROOT / "data" / "event_places.json"
QUERY_MATRIX = ROOT / "config" / "queries.json"
GEO_COUNTRIES = ROOT / "config" / "geo_countries.json"
UA = "Mozilla/5.0 (compatible; AtlasZonaGris/0.3; +https://zonagris.pruebapublica.com/metodologia.html)"
MAX_BYTES = 2_500_000
QUERIES = (
    ("drones_aeropuertos", "airport drone"),
    ("amenazas_bomba", "bomb threat airport"),
    ("ciberataque", "cyberattack infrastructure"),
    ("ferroviario", "rail disruption"),
    ("gnss", "GPS jamming"),
    ("proteccion_civil", "airport emergency evacuation"),
    ("sabotaje_infraestructura", "sabotage infrastructure"),
    ("energia_telecom", "power outage telecom"),
)
def query_matrix() -> list[tuple[str, str, str]]:
    try:
        data = json.loads(QUERY_MATRIX.read_text(encoding="utf-8"))
        rows = [
            (region["id"], query["category"], query["query"])
            for region in data.get("regions", [])
            for query in region.get("queries", [])
            if region.get("id") and query.get("category") and query.get("query")
        ]
        if rows:
            return rows
    except (OSError, ValueError, KeyError):
        pass
    return [("global", category, query) for category, query in QUERIES]


CATEGORY_LABELS = {
    "drones_aeropuertos": "Drones e incursiones en aeropuertos",
    "amenazas_bomba": "Amenazas de bomba y evacuaciones aeroportuarias",
    "ciberataque": "Ciberataques contra infraestructuras y servicios",
    "ferroviario": "Incidentes ferroviarios y aeroportuarios",
    "gnss": "Interferencias GNSS y navegación",
    "proteccion_civil": "Alertas de seguridad civil y protección de infraestructuras",
    "sabotaje_infraestructura": "Sabotaje e interrupciones de infraestructuras",
    "energia_telecom": "Incidentes energéticos y de telecomunicaciones",
    "cables_submarinos": "Cables submarinos",
    "ia_ataques": "Ataques con IA",
    "migracion_instrumentalizada": "Instrumentalización migratoria",
}
CATEGORY_TERMS = {
    "drones_aeropuertos": ("drone", "dron", "uav", "airport", "aeropuerto"),
    "amenazas_bomba": ("bomb", "bomba", "explosive", "threat", "amenaza", "evacuat"),
    "ciberataque": ("cyber", "ciber", "ransom", "hack", "breach", "ddos", "outage"),
    "ferroviario": ("rail", "train", "ferrovi", "station", "estación", "renfe", "sncf"),
    "gnss": ("gps", "gnss", "jamming", "spoof", "navigation", "navegación"),
    "proteccion_civil": ("emergency", "evacuat", "civil protection", "protección civil", "sirena"),
    "sabotaje_infraestructura": ("sabotage", "sabotaje", "sabotaged", "saboteado"),
    "energia_telecom": ("power outage", "blackout", "apagón", "telecom", "telecomunicaciones", "grid"),
    "cables_submarinos": ("submarine cable", "subsea cable", "cable submarino", "cable cut", "cable break", "cable damage", "cable sabotage"),
    "ia_ataques": ("ai-powered", "ai attack", "artificial intelligence attack", "llm attack", "machine learning attack", "model poisoning", "prompt injection", "ai cyberattack"),
    "migracion_instrumentalizada": ("instrumentalized migration", "instrumentalised migration", "weaponized migration", "weaponised migration", "hybrid migration", "border pressure", "migratory pressure", "migration as a weapon", "state-sponsored migration"),
}
NOISE = re.compile(
    r"\b(opinion|opinión|analysis|análisis|explainer|explicador|what we know|lo que sabemos|"
    r"raise[sd]? concerns?|raise[sd]? questions?|rail works|engineering works|rail strike|"
    r"planned disruption|forecast|outlook|report says|according to (?:a )?report|study|survey|"
    r"on alert|must expect|to seek|project|completion|views?|post|podcast|editorial|"
    r"road closures|policing operation|integration|annual|guide|travel guide|risk[s]?|"
    r"warns?|warning|unverified|threat-sharing|gaps?)\b", re.I)
BLOCKED_DOMAINS = {"msn.com", "europesays.com", "nomadlawyer.org"}
OFFICIAL_DOMAINS = {
    "boe.es", "europa.eu", "ec.europa.eu", "cert.europa.eu", "easa.europa.eu",
    "eurocontrol.int", "cisa.gov", "nato.int", "interior.gob.es", "guardiacivil.es",
    "policia.es", "rtve.es", "efe.com",
}
CABLE_EVENT_TERMS = ("cut", "damage", "sabotage", "outage", "disrupt", "fault", "break", "severed")
CABLE_NOISE = ("market", "forecast", "size", "share", "trend", "connectivity", "investment", "contract", "launch", "report")
AI_ATTACK_TERMS = ("attack", "cyberattack", "exploit", "poison", "prompt injection", "malicious", "disrupt")
AI_TERMS = ("ai-powered", "artificial intelligence", "llm", "machine learning", "generative ai", "ai model")
STOP = set("the a an and or of to in on for with from by at as is are was were be been being this that these those it its de la el los las un una unos unas y o en por para con del al se su sus es son".split())


def fetch(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("feed too large")
    return raw


def text_of(node: ET.Element, name: str) -> str:
    value = node.findtext(name)
    return (value or "").strip()


def parse_date(value: str) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError, OverflowError):
        return value[:10] if re.match(r"\d{4}-\d{2}-\d{2}", value) else None


def clean_text(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return " ".join(value.split())[:900]


def decode_bing(link: str) -> str:
    parsed = urllib.parse.urlparse(link)
    if "bing.com" in parsed.netloc and parsed.path.endswith("apiclick.aspx"):
        values = urllib.parse.parse_qs(parsed.query).get("url", [])
        if values:
            return urllib.parse.unquote(values[0])
    return link


def domain(url: str) -> str:
    return urllib.parse.urlparse(url).netloc.casefold().removeprefix("www.")


def title_tokens(title: str) -> set[str]:
    # Quita el sufijo " - Medio" que añaden los agregadores.
    title = re.sub(r"\s+[-|–—]\s+[^-|–—]{2,40}$", "", title)
    words = re.findall(r"[a-z0-9áéíóúüñ]{3,}", title.casefold())
    return {w for w in words if w not in STOP and not w.isdigit()}


def similar(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def country_for(text: str) -> dict | None:
    """Solo asigna país si hay una preposición/locución de lugar explícita.

    No convierte "China-linked hackers" en un incidente en China.
    """
    try:
        countries = json.loads(GEO_COUNTRIES.read_text(encoding="utf-8"))["countries"]
    except (OSError, ValueError, KeyError):
        return None
    low = " " + text.casefold() + " "
    for country in countries:
        for alias in country.get("aliases", []):
            a = re.escape(alias.casefold())
            if re.search(rf"\b(?:in|at|near|across|from|inside|outside|throughout|over)\s+(?:the\s+)?{a}\b", low):
                return country
    return None


def query_relevant(category: str, text: str) -> bool:
    low = text.casefold()
    if category == "cables_submarinos":
        return any(term in low for term in CABLE_EVENT_TERMS) and not any(term in low for term in CABLE_NOISE)
    if category == "ia_ataques":
        return any(term in low for term in AI_TERMS) and any(term in low for term in AI_ATTACK_TERMS)
    if category == "migracion_instrumentalizada":
        return any(term in low for term in CATEGORY_TERMS["migracion_instrumentalizada"])
    return True


def classify(text: str) -> str:
    low = text.casefold()
    scores = {key: sum(1 for term in terms if term in low) for key, terms in CATEGORY_TERMS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "proteccion_civil"


def parse_feed(raw: bytes, category: str, region: str = "") -> list[dict]:
    root = ET.fromstring(raw)
    if root.tag not in {"rss", "feed"}:
        raise ValueError("feed RSS/Atom no reconocido")
    rows = []
    for item in root.findall(".//item") + root.findall(".//{http://www.w3.org/2005/Atom}entry"):
        title = clean_text(text_of(item, "title") or text_of(item, "{http://www.w3.org/2005/Atom}title"))
        title = re.sub(r"^(MAPPED|LIVE|UPDATE|BREAKING)\s*:\s*", "", title, flags=re.I)
        raw_link = text_of(item, "link") or text_of(item, "{http://www.w3.org/2005/Atom}link")
        raw_link = raw_link or (item.find("{http://www.w3.org/2005/Atom}link").get("href", "") if item.find("{http://www.w3.org/2005/Atom}link") is not None else "")
        if not title or not raw_link:
            continue
        description = clean_text(
            text_of(item, "description")
            or text_of(item, "{http://www.w3.org/2005/Atom}summary")
            or text_of(item, "{http://www.w3.org/2005/Atom}content")
        )
        if NOISE.search(title):
            continue
        url = decode_bing(raw_link)
        if domain(url) in BLOCKED_DOMAINS:
            continue
        if not query_relevant(category, title + " " + description):
            continue
        published = parse_date(text_of(item, "pubDate") or text_of(item, "{http://www.w3.org/2005/Atom}updated"))
        if not published:
            continue
        category_guess = classify(title + " " + description)
        if category and category_guess == "proteccion_civil":
            category_guess = category
        rows.append({
            "title": title,
            "description": description,
            "url": url,
            "domain": domain(url),
            "published_at": published,
            "category": category_guess,
            "query_scope": region,
            "source_name": "Bing News RSS",
            "digest": hashlib.sha256((title + description + decode_bing(raw_link)).encode()).hexdigest(),
        })
    return rows


def event_family(row: dict, place: dict | None) -> str | None:
    """Une la ola europea de amenazas de bomba sin fundir casos concretos.

    Un titular con un aeropuerto identificado sigue siendo un caso propio. Los
    titulares de alcance ("varios vuelos", "varios aeropuertos", "redacciones",
    "en toda Europa") se agrupan como un solo episodio.
    """
    if row.get("category") != "amenazas_bomba":
        return None
    text = (row.get("title", "") + " " + row.get("description", "")).casefold()
    if not re.search(r"\b(bomb|bombs|hoax|hoaxes)\b", text):
        return None
    if re.search(r"\b(several|multiple|newsrooms?|across europe|airports across|flights across)\b", text):
        return "bomb-europe-wave"
    return None


def group_rows(rows: list[dict], places: dict | None = None) -> list[list[dict]]:
    groups: list[list[dict]] = []
    for row in sorted(rows, key=lambda x: x["published_at"], reverse=True):
        tokens = title_tokens(row["title"])
        row_place = place_for(row["title"] + " " + row["description"], places) if places else None
        place_key = row_place["name"] if row_place else None
        target = None
        family = event_family(row, row_place)
        for group in groups:
            first = group[0]
            if first["category"] != row["category"]:
                continue
            first_place = place_for(first["title"] + " " + first["description"], places) if places else None
            first_family = event_family(first, first_place)
            same_place = bool(place_key and first_place and place_key == first_place["name"])
            family_match = bool(family and family == first_family)
            window = 5 if family_match else 2
            if abs((date.fromisoformat(first["published_at"]) - date.fromisoformat(row["published_at"])).days) > window:
                continue
            if family_match or similar(tokens, title_tokens(first["title"])) >= 0.58 or same_place:
                target = group
                break
        if target is None:
            groups.append([row])
        else:
            target.append(row)
    return groups


def assess(group: list[dict]) -> tuple[str, str]:
    """Un candidato automático nunca supera PENDIENTE.

    La promoción a DOCUMENTADO exige revisión humana. Varios dominios pueden
    compartir el mismo cable o la misma nota de prensa; contarlos como
    confirmación automática confundiría sindicación con independencia.
    """
    domains = {row["domain"] for row in group if row["domain"]}
    official = any(any(d == domain or d.endswith("." + domain) for d in domains) for domain in OFFICIAL_DOMAINS)
    if official:
        return "PENDIENTE", "fuente institucional identificada; pendiente de revisión humana"
    if len(domains) >= 2:
        return "PENDIENTE", f"{len(domains)} dominios citados; pendiente de revisión humana (posible sindicación)"
    return "PENDIENTE", "una sola fuente identificable; pendiente de revisión humana"


def place_for(text: str, places: dict) -> dict | None:
    low = text.casefold()
    # Coincidencia conservadora por nombre/alias completo, evitando subcadenas.
    candidates = []
    for entry in places.get("places", []):
        names = [entry["name"], *entry.get("aliases", [])]
        for name in names:
            if re.search(r"(?<!\w)" + re.escape(name.casefold()) + r"(?!\w)", low):
                candidates.append(entry)
                break
    return max(candidates, key=lambda item: len(item["name"]), default=None) if candidates else None


def build_events(groups: list[list[dict]], places: dict, captured_at: str, geo: bool = False, geo_shadow: bool = False) -> list[dict]:
    events = []
    for group in groups:
        first = group[0]
        source_rows = sorted(group, key=lambda x: x["published_at"], reverse=True)
        sources = []
        seen = set()
        for row in source_rows:
            if row["url"] in seen:
                continue
            seen.add(row["url"])
            sources.append({
                "title": row["title"],
                "url": row["url"],
                "type": "news",
                "published_at": row["published_at"],
                "source": row["source_name"],
            })
        status, reason = assess(group)
        place = place_for(first["title"] + " " + first["description"], places)
        geo_country = None
        if place is None and (geo or geo_shadow):
            geo_country = country_for(first["title"] + " " + first["description"])
        event_date = min(row["published_at"] for row in group)
        event_id = "AUTO-" + hashlib.sha256((sources[0]["url"] + "|" + first["title"]).encode()).hexdigest()[:12].upper()
        events.append({
            "id": event_id,
            "event_date": event_date,
            "published_at": sources[0]["published_at"],
            "captured_at": captured_at,
            "country": place["country"] if place else (geo_country["name"] if geo and geo_country else None),
            "country_iso2": place["country_iso2"] if place else (geo_country["iso2"] if geo and geo_country else None),
            "city": place["city"] if place else None,
            "place": place["place"] if place else (geo_country["name"] if geo and geo_country else "No documentado"),
            "lat": place["lat"] if place else None,
            "lon": place["lon"] if place else None,
            "geo_precision": place["precision"] if place else ("country" if geo and geo_country else None),
            "geo_method": "gazetteer" if place else ("explicit_country" if geo and geo_country else None),
            "geo_suggestion": (
                {"country": geo_country["name"], "country_iso2": geo_country["iso2"], "method": "explicit_country"}
                if geo_shadow and geo_country else None
            ),
            "category": first["category"],
            "category_label": CATEGORY_LABELS[first["category"]],
            "query_scope": first.get("query_scope") or None,
            "title": first["title"],
            "description": first["description"] or "Titular y resumen disponibles en la fuente original.",
            "infrastructure": "No especificada en la fuente",
            "consequences": "No cuantificadas en la fuente",
            "sources": sources[:8],
            "contrast_sources": [],
            "verification_status": status,
            "status_reason": reason,
            "attribution": {"status": "none", "claimed_by": None, "note": "No se atribuye autoría ni intención."},
            "observations": "Registro automático: metadatos y resumen de la fuente; no implica confirmación oficial ni atribución. Revisar el enlace original.",
            "reviewed_by_human": False,
            "automated": True,
            "source_sha256": first["digest"],
        })
    return sorted(events, key=lambda item: (item["event_date"], item["title"]), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Recolector automático de acontecimientos")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--places", type=Path, default=DEFAULT_PLACES)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--limit", type=int, default=120)
    parser.add_argument("--source", choices=["bing"], default="bing", help="fuente de descubrimiento")
    parser.add_argument("--geo", action="store_true", help="activa extracción conservadora de país")
    parser.add_argument("--geo-shadow", action="store_true", help="calcula sugerencias de país sin publicarlas")
    parser.add_argument("--cached-dir", type=Path, help="XML de Bing ya descargados; no usa red")
    args = parser.parse_args()
    places = json.loads(args.places.read_text(encoding="utf-8"))
    captured_at = datetime.now(timezone.utc).isoformat()
    rows, source_runs = [], []
    if args.cached_dir:
        for path in sorted(args.cached_dir.glob("*.xml")):
            try:
                part = parse_feed(path.read_bytes(), "")
                rows.extend(part)
                source_runs.append({"source": str(path), "http": None, "records": len(part), "error": None})
            except Exception as exc:
                source_runs.append({"source": str(path), "http": None, "records": 0, "error": str(exc)})
    else:
        for region, category, query in query_matrix():
            url = "https://www.bing.com/news/search?" + urllib.parse.urlencode({"q": query, "format": "RSS"})
            try:
                part = parse_feed(fetch(url), category, region)
                rows.extend(part)
                source_runs.append({"source": "Bing News RSS", "tier": "discovery", "region": region, "query": query, "http": 200, "records": len(part), "error": None})
            except Exception as exc:
                print(f"error: {url}: {exc}", file=sys.stderr)
                source_runs.append({"source": "Bing News RSS", "tier": "discovery", "region": region, "query": query, "http": None, "records": 0, "error": str(exc)})
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=args.days - 1)
    rows = [row for row in rows if date.fromisoformat(row["published_at"]) >= cutoff]
    # Una misma URL puede aparecer en varias consultas; se conserva una sola categoría.
    unique = {}
    for row in rows:
        unique.setdefault(row["url"].split("#")[0].rstrip("/"), row)
    rows = list(unique.values())
    groups = group_rows(rows, places)
    if args.geo_shadow and args.out == DEFAULT_OUT:
        parser.error("--geo-shadow requiere --out distinto de data/events/auto/events.jsonl")
    events = build_events(groups, places, captured_at, geo=args.geo, geo_shadow=args.geo_shadow)[: args.limit]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n", encoding="utf-8")
    args.sources.parent.mkdir(parents=True, exist_ok=True)
    args.sources.write_text(json.dumps({"captured_at": captured_at, "runs": source_runs}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"eventos automáticos: {len(events)} de {len(rows)} candidatos → {args.out}")
    return 0 if events else 1


if __name__ == "__main__":
    raise SystemExit(main())
