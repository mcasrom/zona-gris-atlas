#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import yaml
from build_events_data import merge

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
SITE = yaml.safe_load((ROOT / "config" / "site.yaml").read_text(encoding="utf-8"))
REGISTROS = WEB / "assets" / "data" / "registros.json"
EVENTS = ROOT / "data" / "events" / "2026-11-06" / "events.jsonl"
EVENTS_AUTO = ROOT / "data" / "events" / "auto" / "events.jsonl"
EVENTS_WEB = WEB / "assets" / "data" / "events.json"
PRIMARY = ROOT / "data" / "events" / "primary" / "documents.json"
PRIMARY_WEB = WEB / "assets" / "data" / "primary.json"
REPO = SITE["repo"].rstrip("/")
SITE_URL = SITE["url"].rstrip("/")


def kofi_button() -> str:
    if not SITE.get("kofi"):
        return ""
    return f'<a class="kofi-link" href="{escape(SITE["kofi"])}">Apoyar en Ko-fi</a>'


def website_jsonld() -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": SITE["name"],
            "url": SITE_URL + "/",
            "description": SITE["description"],
            "inLanguage": "es",
        },
        ensure_ascii=False,
    )


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_events() -> None:
    # Los curados tienen prioridad. Los automáticos se incorporan después y
    # solo si no repiten una URL ni un titular ya presente.
    curated = _jsonl(EVENTS)
    automatic = _jsonl(EVENTS_AUTO)
    assert curated
    rows = merge(curated, automatic)
    generated_at = max((row.get("captured_at") or "" for row in rows), default="")
    payload = {
        "generated_at": generated_at or "2026-11-06T16:00:00Z",
        "count": len(rows),
        "events": rows,
    }
    EVENTS_WEB.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_primary() -> None:
    if PRIMARY.exists():
        payload = json.loads(PRIMARY.read_text(encoding="utf-8"))
    else:
        payload = {"count": 0, "documents": [], "source": "CERT-EU", "license": "CC BY 4.0"}
    PRIMARY_WEB.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_feed() -> None:
    docs = []
    if REGISTROS.exists():
        docs = json.loads(REGISTROS.read_text(encoding="utf-8")).get("documents", [])
        # La promoción militar es un documento B13, no una noticia del Atlas.
        # Se excluye de la superficie pública de novedades, sin tocar B13/B14.
        docs = [doc for doc in docs if not any(term in doc.get("title", "") for term in ("promoción al empleo de General", "Adenda del Mando de Apoyo Logístico"))]
    updated = datetime.now(timezone.utc).isoformat()
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f"  <title>{escape(SITE['title'])}</title>",
        f'  <link href="{SITE_URL}/"/>',
        f"  <updated>{updated}</updated>",
        f"  <id>{SITE_URL}/feed.xml</id>",
        "  <author><name>Miguel</name></author>",
    ]
    for doc in docs:
        url = escape(doc["url"])
        lines.extend(
            [
                "  <entry>",
                f"    <title>{escape(doc['title'])}</title>",
                f"    <id>{url}</id>",
                f'    <link href="{url}"/>',
                f"    <updated>{escape(doc['published_at'])}</updated>",
                f"    <summary>{escape(doc['summary'])}</summary>",
                "    <source>",
                f"      <title>{escape(doc['source'])}</title>",
                f'      <link href="{url}"/>',
                "    </source>",
                "  </entry>",
            ]
        )
    lines.append("</feed>")
    (WEB / "feed.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sitemap() -> None:
    pages = ["", "mapa.html", "incidentes.html", "registros.html", "primarias.html", "metodologia.html", "limites.html", "fuentes.html", "privacidad.html", "avisos.html", "about.html"]
    today = datetime.now(timezone.utc).date().isoformat()
    rows = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for page in pages:
        rows.append(
            f"  <url><loc>{SITE_URL}/{page}</loc><lastmod>{today}</lastmod></url>"
        )
    rows.append("</urlset>")
    (WEB / "sitemap.xml").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (WEB / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )


def write_manifest() -> None:
    payload = {
        "name": SITE["title"],
        "short_name": SITE["name"],
        "description": SITE["description"],
        "lang": "es",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#12171D",
        "theme_color": "#12171D",
        "icons": [],
    }
    (WEB / "site.webmanifest").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_tokens() -> None:
    replacements = {
        "{{SITE_URL}}": SITE_URL,
        "{{SITE_NAME}}": SITE["name"],
        "{{SITE_TITLE}}": SITE["title"],
        "{{SITE_DESC}}": SITE["description"],
        "{{AUTHOR}}": SITE["author"],
        "{{REPO}}": REPO,
        "{{KOFI_BUTTON}}": kofi_button(),
        "{{WEBSITE_JSONLD}}": website_jsonld(),
        "{{YEAR}}": str(datetime.now(timezone.utc).year),
        "{{VERSION}}": str(SITE.get("version", "0.0.0")),
    }
    for path in WEB.rglob("*"):
        if path.suffix not in {".html", ".js", ".xml", ".txt", ".webmanifest"} or not path.is_file():
            continue
        if path.parent.name == "data":
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for token, value in replacements.items():
            updated = updated.replace(token, value)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def main() -> int:
    write_events()
    write_primary()
    write_feed()
    write_sitemap()
    write_manifest()
    replace_tokens()
    print("web ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
