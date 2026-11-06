#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
SITE = yaml.safe_load((ROOT / "config" / "site.yaml").read_text(encoding="utf-8"))
DEMO = WEB / "assets" / "data" / "incidents.demo.json"
PUBLIC_DATA = WEB / "assets" / "data" / "incidents.json"
REPO = SITE["repo"].rstrip("/")
SITE_URL = SITE["url"].rstrip("/")


def kofi_button() -> str:
    if not SITE.get("kofi"):
        return ""
    return f'<a class="btn" href="{escape(SITE["kofi"])}">Apoyar en Ko-fi</a>'


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


def dataset_jsonld(demo: dict) -> str:
    incidents = demo.get("incidents", [])
    if any(not item.get("demo") for item in incidents):
        return ""
    return ""


def write_data() -> dict:
    demo = json.loads(DEMO.read_text(encoding="utf-8"))
    PUBLIC_DATA.write_text(json.dumps(demo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return demo


def write_feed(demo: dict) -> None:
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
    for incident in demo.get("incidents", []):
        url = f"{SITE_URL}/mapa.html#{escape(incident['id'])}"
        lines.extend(
            [
                "  <entry>",
                f"    <title>{escape(incident['title'])}</title>",
                f"    <id>{url}</id>",
                f'    <link href="{url}"/>',
                f"    <updated>{incident['event_date']}T00:00:00Z</updated>",
                f"    <summary>{escape(incident['summary'])}</summary>",
                "  </entry>",
            ]
        )
    lines.append("</feed>")
    (WEB / "feed.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sitemap() -> None:
    pages = ["", "mapa.html", "metodologia.html", "limites.html", "fuentes.html", "privacidad.html"]
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


def replace_tokens(demo: dict) -> None:
    replacements = {
        "{{SITE_URL}}": SITE_URL,
        "{{SITE_NAME}}": SITE["name"],
        "{{SITE_TITLE}}": SITE["title"],
        "{{SITE_DESC}}": SITE["description"],
        "{{AUTHOR}}": SITE["author"],
        "{{REPO}}": REPO,
        "{{KOFI_BUTTON}}": kofi_button(),
        "{{WEBSITE_JSONLD}}": website_jsonld(),
        "{{DATASET_JSONLD}}": dataset_jsonld(demo),
        "{{YEAR}}": str(datetime.now(timezone.utc).year),
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
    demo = write_data()
    write_feed(demo)
    write_sitemap()
    write_manifest()
    replace_tokens(demo)
    print(f"web ok · {len(demo.get('incidents', []))} incidentes demo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
