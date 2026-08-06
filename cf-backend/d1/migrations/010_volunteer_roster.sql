-- Curated per-month volunteer roster. Previously the "who's available this month"
-- list was the raw feedback.html signup data (sessionFeedback.volunteerMonths in
-- Firestore) - anyone who ever ticked a month showed up automatically forever. Admin
-- now explicitly adds people from that signup list onto an actual roster per month,
-- and can remove them - that roster (not the raw signup list) is what task
-- notifications and the admin volunteer view are based on.
CREATE TABLE IF NOT EXISTS volunteer_roster (
  id TEXT PRIMARY KEY,
  month TEXT NOT NULL,
  user_id TEXT,
  email TEXT NOT NULL,
  name TEXT NOT NULL,
  added_by TEXT NOT NULL,
  added_at INTEGER NOT NULL,
  UNIQUE(month, email)
);
