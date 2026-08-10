-- Real partners CMS - the public partners.html page was hardcoded to a single partner
-- because there was never an actual way to add one: admin only saw a count against a
-- Firestore collection nothing ever wrote to. This table is the real source of truth,
-- with a public GET (content-worker) and admin CRUD (ops-worker).
CREATE TABLE IF NOT EXISTS partners (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  logo_url TEXT,
  tagline TEXT,
  description TEXT,
  offerings TEXT,        -- JSON array of {icon, title, description}
  website_url TEXT,
  display_order INTEGER NOT NULL DEFAULT 0,
  active INTEGER NOT NULL DEFAULT 1,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
