-- 2026 Leadership & Management Recruitment applications (leadership-application.html).
-- Same shape as join_requests (raw form kept as JSON, key fields pulled out for admin
-- list/search) since the full form has ~30 fields across executive/directorate/program
-- roles and D1 doesn't need a rigid column per field.
CREATE TABLE IF NOT EXISTS leadership_applications (
  id TEXT PRIMARY KEY,
  name TEXT,
  email TEXT,
  position TEXT,
  data_json TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at INTEGER NOT NULL
);
