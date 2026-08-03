-- Correct events/gallery/team/stories to match the actual fields the public pages
-- render (discovered by reading events.html/gallery.html/team.html/Journey_Stories.html),
-- rather than the generic first-pass shape from the initial schema.

DROP TABLE IF EXISTS events;
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  photo_url TEXT,
  status TEXT DEFAULT 'upcoming',   -- upcoming | past
  event_date TEXT,                  -- free-text date label (e.g. "March 2027")
  lead TEXT,
  description TEXT,
  video_url TEXT,
  created_at INTEGER NOT NULL
);

DROP TABLE IF EXISTS gallery;
CREATE TABLE gallery (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL DEFAULT 'photo',   -- photo | video
  url TEXT NOT NULL,
  caption TEXT,
  category TEXT,
  created_at INTEGER NOT NULL
);

DROP TABLE IF EXISTS team;
CREATE TABLE team (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT,
  category TEXT,       -- Leadership | DeptHead | Volunteer
  department TEXT,
  country TEXT,
  email TEXT,
  photo_url TEXT,
  sort_order INTEGER DEFAULT 0
);

DROP TABLE IF EXISTS stories;
CREATE TABLE stories (
  id TEXT PRIMARY KEY,
  name TEXT,
  role TEXT,
  country TEXT,
  photo_url TEXT,
  tag TEXT,
  quote TEXT,
  message TEXT,
  created_at INTEGER NOT NULL
);

-- join.html/contact.html both spread the entire submitted form ({...formObj}) into
-- Firestore rather than a fixed field set, so keep the full submission as JSON and
-- promote name/email as columns for quick admin listing/search.
DROP TABLE IF EXISTS join_requests;
CREATE TABLE join_requests (
  id TEXT PRIMARY KEY,
  name TEXT,
  email TEXT,
  data_json TEXT NOT NULL,
  source TEXT,
  status TEXT DEFAULT 'pending',
  created_at INTEGER NOT NULL
);

DROP TABLE IF EXISTS contact_submissions;
CREATE TABLE contact_submissions (
  id TEXT PRIMARY KEY,
  name TEXT,
  email TEXT,
  data_json TEXT NOT NULL,
  source TEXT,
  status TEXT DEFAULT 'unread',
  created_at INTEGER NOT NULL
);
