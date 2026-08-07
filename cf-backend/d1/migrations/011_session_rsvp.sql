-- Pre-session attendance confirmation, separate from session_attendance (which records
-- who actually showed up). A member gets a personal one-click link (no login, no typed
-- name/email - the link itself identifies them) and taps Attending / Not Attending.
CREATE TABLE IF NOT EXISTS session_rsvps (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES dept_sessions(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  attending INTEGER NOT NULL,
  responded_at INTEGER NOT NULL,
  UNIQUE(session_id, user_id)
);

-- Tracks whether the head's "N members confirmed" pre-session alert has already fired,
-- same one-shot-per-session pattern as the existing reminder_5/3/1_sent columns.
ALTER TABLE dept_sessions ADD COLUMN attendance_alert_sent INTEGER NOT NULL DEFAULT 0;
