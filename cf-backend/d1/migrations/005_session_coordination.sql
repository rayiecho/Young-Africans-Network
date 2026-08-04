-- Internal leadership/ops calendar: which department is leading the weekly Google Meet
-- training session, distinct from trainingSessions (member-facing training content).
-- Since sessions run on Google Meet (not embedded in the platform), attendance is a
-- self-check-in, not automatically verified.

CREATE TABLE dept_sessions (
  id TEXT PRIMARY KEY,
  session_date TEXT NOT NULL,        -- ISO date, e.g. '2026-08-12'
  department TEXT NOT NULL,
  topic TEXT NOT NULL,
  meet_link TEXT,
  assigned_head_id TEXT REFERENCES users(id),
  status TEXT NOT NULL DEFAULT 'awaiting_confirmation',
    -- awaiting_confirmation | confirmed | needs_help | completed | cancelled
  prep_complete INTEGER NOT NULL DEFAULT 0,
  needs_assistance INTEGER NOT NULL DEFAULT 0,
  assistance_note TEXT,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE INDEX idx_dept_sessions_date ON dept_sessions(session_date);
CREATE INDEX idx_dept_sessions_head ON dept_sessions(assigned_head_id);

CREATE TABLE session_guests (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES dept_sessions(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  contact TEXT,
  confirmed INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_session_guests_session ON session_guests(session_id);

-- Roles are defined per-session (not a fixed list) - head/admin types in whatever a
-- given session needs (Tech Support, Photographer, MC, ...) and volunteers claim one.
CREATE TABLE session_roles (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES dept_sessions(id) ON DELETE CASCADE,
  role_name TEXT NOT NULL,
  filled_by TEXT REFERENCES users(id),
  notes TEXT
);
CREATE INDEX idx_session_roles_session ON session_roles(session_id);

CREATE TABLE session_attendance (
  session_id TEXT NOT NULL REFERENCES dept_sessions(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  checked_in_at INTEGER NOT NULL,
  marked_by TEXT,   -- 'self', or the uid of a head/admin who marked it manually
  PRIMARY KEY (session_id, user_id)
);
