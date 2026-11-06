PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    licence TEXT,
    enabled INTEGER NOT NULL DEFAULT 0 CHECK (enabled IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS raw_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL REFERENCES sources(id),
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    text TEXT,
    language TEXT,
    published_at TEXT,
    captured_at TEXT NOT NULL DEFAULT (datetime('now')),
    url_hash TEXT NOT NULL,
    text_hash TEXT,
    UNIQUE (source_id, url_hash)
);

CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    domain TEXT NOT NULL CHECK (domain IN ('CIB','INF','AER','GNS','SAB','DES','ECO','MIG')),
    scale_position TEXT NOT NULL CHECK (scale_position IN ('competencia','zona_gris','hostilidad_hibrida')),
    severity TEXT NOT NULL CHECK (severity IN ('baja','media','alta')),
    reality TEXT NOT NULL CHECK (reality IN ('probable','dudoso','descartado')),
    lat REAL,
    lon REAL,
    place TEXT,
    country_iso2 TEXT,
    event_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','reviewed','published','rejected')),
    demo INTEGER NOT NULL DEFAULT 0 CHECK (demo IN (0, 1)),
    reviewed_by_human INTEGER NOT NULL DEFAULT 0 CHECK (reviewed_by_human IN (0, 1)),
    reviewed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS incident_items (
    incident_id TEXT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    raw_item_id INTEGER NOT NULL REFERENCES raw_items(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL DEFAULT 'supporting',
    PRIMARY KEY (incident_id, raw_item_id)
);

CREATE TABLE IF NOT EXISTS attributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('none','official','claimed')),
    attributed_by TEXT,
    attributed_by_type TEXT CHECK (attributed_by_type IN ('government','agency','vendor','other') OR attributed_by_type IS NULL),
    source_url TEXT,
    confidence TEXT NOT NULL CHECK (confidence IN ('low','medium','high')),
    quote TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    model_version TEXT NOT NULL,
    domain_scores TEXT NOT NULL,
    severity TEXT NOT NULL,
    reality TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS changelog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT,
    field TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_raw_items_url_hash ON raw_items(url_hash);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_domain ON incidents(domain);
CREATE INDEX IF NOT EXISTS idx_incidents_event_date ON incidents(event_date);
CREATE INDEX IF NOT EXISTS idx_attributions_incident ON attributions(incident_id);
