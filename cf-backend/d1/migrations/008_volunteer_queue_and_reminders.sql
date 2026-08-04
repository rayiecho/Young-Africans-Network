-- Fair rotation: whoever has gone longest without claiming a task (or never has)
-- gets notified first when a new one posts; claiming moves you to the back of the line.
CREATE TABLE volunteer_queue (
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  last_claimed_at INTEGER NOT NULL DEFAULT 0
);

-- Tracks which reminder tiers (5/3/1 days before) have already gone out for a session,
-- so the daily cron doesn't re-send the same reminder.
ALTER TABLE dept_sessions ADD COLUMN reminder_5_sent INTEGER NOT NULL DEFAULT 0;
ALTER TABLE dept_sessions ADD COLUMN reminder_3_sent INTEGER NOT NULL DEFAULT 0;
ALTER TABLE dept_sessions ADD COLUMN reminder_1_sent INTEGER NOT NULL DEFAULT 0;
