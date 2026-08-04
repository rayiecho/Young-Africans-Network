-- Async content-production task board (posters, video edits, slides, etc.), separate
-- from the department leadership calendar (dept_sessions) though a task can optionally
-- originate from a session (a head's "needs assistance" flag).

CREATE TABLE volunteer_tasks (
  id TEXT PRIMARY KEY,
  task_type TEXT NOT NULL,           -- poster | video_edit | slides | other (free text tag)
  title TEXT NOT NULL,
  brief TEXT,
  related_session_id TEXT REFERENCES dept_sessions(id),
  raw_file_url TEXT,
  status TEXT NOT NULL DEFAULT 'open',
    -- open | claimed | submitted | approved | changes_requested
  claimed_by TEXT REFERENCES users(id),
  submitted_file_url TEXT,
  review_note TEXT,
  due_date TEXT,
  points_awarded INTEGER NOT NULL DEFAULT 0,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE INDEX idx_volunteer_tasks_status ON volunteer_tasks(status);
CREATE INDEX idx_volunteer_tasks_claimed ON volunteer_tasks(claimed_by);
