-- YAN D1 schema — relational mapping of the current Firestore collections.
-- Conventions: id TEXT PRIMARY KEY (uuid or migrated Firestore doc id), timestamps as
-- INTEGER unix-ms, booleans as INTEGER 0/1, arrays as join tables, rarely-queried
-- free-form structures as TEXT (JSON).

PRAGMA foreign_keys = ON;

-- ===================== CORE: USERS & AUTH =====================

CREATE TABLE users (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT,              -- NULL for Google-only accounts
  photo_url TEXT,
  role TEXT DEFAULT 'Member',
  department TEXT,
  country TEXT,
  whatsapp TEXT,
  dob TEXT,
  bio TEXT,
  is_admin INTEGER NOT NULL DEFAULT 0,
  is_dept_head INTEGER NOT NULL DEFAULT 0,
  is_exec INTEGER NOT NULL DEFAULT 0,
  is_mentor INTEGER NOT NULL DEFAULT 0,
  email_verified INTEGER NOT NULL DEFAULT 0,
  profile_complete INTEGER NOT NULL DEFAULT 0,
  referred_by TEXT,
  joined_at INTEGER NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE INDEX idx_users_department ON users(department);
CREATE INDEX idx_users_country ON users(country);

CREATE TABLE auth_providers (         -- google.com / password, mirrors Firebase providerData
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  provider TEXT NOT NULL,             -- 'password' | 'google.com'
  provider_uid TEXT,                  -- Google sub id
  created_at INTEGER NOT NULL,
  UNIQUE(user_id, provider)
);

CREATE TABLE sessions (
  id TEXT PRIMARY KEY,                -- opaque session token (hashed)
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at INTEGER NOT NULL,
  expires_at INTEGER NOT NULL,
  user_agent TEXT,
  ip TEXT
);
CREATE INDEX idx_sessions_user ON sessions(user_id);

CREATE TABLE email_verification_tokens (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  used_at INTEGER
);

CREATE TABLE password_reset_tokens (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  used_at INTEGER
);

CREATE TABLE admin_verification (      -- was adminVerification/{uid}
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  code TEXT NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  expires_at INTEGER NOT NULL,
  verified_at INTEGER
);

CREATE TABLE head_access (              -- headAccess/{docId}
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  department TEXT,
  granted INTEGER NOT NULL DEFAULT 0,
  requested_at INTEGER NOT NULL,
  granted_at INTEGER
);

CREATE TABLE member_ids (                -- memberIds/{memberId}
  id TEXT PRIMARY KEY,                   -- e.g. YAN-XXXXXXXX
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT, role TEXT, department TEXT, country TEXT,
  status TEXT DEFAULT 'active'
);

CREATE TABLE push_subscriptions (
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  subscription_json TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE online_users (
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  last_seen INTEGER NOT NULL
);

-- ===================== FEED / SOCIAL =====================

CREATE TABLE posts (
  id TEXT PRIMARY KEY,
  author_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  category TEXT,
  link TEXT,
  youtube_id TEXT,
  image_url TEXT,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_created ON posts(created_at);

CREATE TABLE post_likes (
  post_id TEXT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at INTEGER NOT NULL,
  PRIMARY KEY (post_id, user_id)
);

CREATE TABLE post_replies (
  id TEXT PRIMARY KEY,
  post_id TEXT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  author_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_replies_post ON post_replies(post_id);

CREATE TABLE polls (
  id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  options_json TEXT NOT NULL,      -- [{id,text}]
  deadline TEXT,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE poll_votes (
  poll_id TEXT NOT NULL REFERENCES polls(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  option_id TEXT NOT NULL,
  voted_at INTEGER NOT NULL,
  PRIMARY KEY (poll_id, user_id)
);

CREATE TABLE notifications (
  id TEXT PRIMARY KEY,
  user_id TEXT REFERENCES users(id) ON DELETE CASCADE,   -- NULL = broadcast to all
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  url TEXT,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_notif_user ON notifications(user_id);

CREATE TABLE notification_reads (
  notification_id TEXT NOT NULL REFERENCES notifications(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  read_at INTEGER NOT NULL,
  PRIMARY KEY (notification_id, user_id)
);

CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  created_at INTEGER NOT NULL
);

CREATE TABLE conversation_participants (
  conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY (conversation_id, user_id)
);

CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  sender_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_messages_conv ON messages(conversation_id);

CREATE TABLE dept_chat_messages (        -- chat/{deptId}/messages
  id TEXT PRIMARY KEY,
  department TEXT NOT NULL,
  sender_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_deptchat_dept ON dept_chat_messages(department);

-- ===================== DEPARTMENTS / TRAINING / MATERIALS =====================

CREATE TABLE dept_materials (             -- departments/{deptId}/materials/{materialId}
  id TEXT PRIMARY KEY,
  department TEXT NOT NULL,
  title TEXT NOT NULL,
  content TEXT,
  file_url TEXT,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_deptmat_dept ON dept_materials(department);

CREATE TABLE dept_material_discussions (
  id TEXT PRIMARY KEY,
  material_id TEXT NOT NULL REFERENCES dept_materials(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE dept_material_quiz (
  id TEXT PRIMARY KEY,
  material_id TEXT NOT NULL REFERENCES dept_materials(id) ON DELETE CASCADE,
  questions_json TEXT NOT NULL
);

CREATE TABLE results (                    -- results/{userId}/materials/{materialId}
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  material_id TEXT NOT NULL,
  score REAL,
  data_json TEXT,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_results_user ON results(user_id);

CREATE TABLE training_programs (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  department TEXT,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE training_modules (
  id TEXT PRIMARY KEY,
  program_id TEXT NOT NULL REFERENCES training_programs(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  position INTEGER DEFAULT 0
);

CREATE TABLE training_lessons (
  id TEXT PRIMARY KEY,
  module_id TEXT NOT NULL REFERENCES training_modules(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT,
  position INTEGER DEFAULT 0
);

CREATE TABLE career_programs (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE career_modules (
  id TEXT PRIMARY KEY,
  program_id TEXT NOT NULL REFERENCES career_programs(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  position INTEGER DEFAULT 0
);

CREATE TABLE career_lessons (
  id TEXT PRIMARY KEY,
  module_id TEXT NOT NULL REFERENCES career_modules(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT,
  position INTEGER DEFAULT 0
);

CREATE TABLE training_partners (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  details_json TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE training_sessions (
  id TEXT PRIMARY KEY,
  program_id TEXT REFERENCES training_programs(id),
  title TEXT NOT NULL,
  scheduled_at INTEGER,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE program_assignments (
  id TEXT PRIMARY KEY,
  program_id TEXT,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'pending',
  feedback TEXT,
  submitted_at INTEGER,
  reviewed_at INTEGER
);
CREATE INDEX idx_progassign_user ON program_assignments(user_id);

CREATE TABLE learning_progress (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  program_id TEXT,
  progress_json TEXT,
  updated_at INTEGER NOT NULL
);

CREATE TABLE module_progress (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  module_id TEXT,
  completed INTEGER DEFAULT 0,
  updated_at INTEGER NOT NULL
);

CREATE TABLE module_discussions (
  id TEXT PRIMARY KEY,
  module_id TEXT NOT NULL,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE quiz_attempts (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  module_week TEXT,
  score REAL,
  passed INTEGER,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_quizattempt_user ON quiz_attempts(user_id);

CREATE TABLE quiz_failures (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  module_week TEXT,
  reset_at INTEGER,
  created_at INTEGER NOT NULL
);

CREATE TABLE member_grades (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  grade_json TEXT,
  created_at INTEGER NOT NULL
);

-- ===================== MENTORSHIP =====================

CREATE TABLE mentor_profiles (
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  bio TEXT,
  expertise_json TEXT,
  availability_json TEXT
);

CREATE TABLE mentorship_slots (
  id TEXT PRIMARY KEY,
  mentor_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  starts_at INTEGER NOT NULL,
  booked_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE mentorships (
  id TEXT PRIMARY KEY,
  mentor_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  mentee_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'active',
  created_at INTEGER NOT NULL
);

CREATE TABLE mentoring_sessions (
  id TEXT PRIMARY KEY,
  mentorship_id TEXT REFERENCES mentorships(id) ON DELETE CASCADE,
  scheduled_at INTEGER,
  notes TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE mentorship_meetings (
  id TEXT PRIMARY KEY,
  mentorship_id TEXT REFERENCES mentorships(id) ON DELETE CASCADE,
  meeting_url TEXT,
  scheduled_at INTEGER
);

CREATE TABLE session_notes (
  id TEXT PRIMARY KEY,
  mentor_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  mentee_id TEXT REFERENCES users(id),
  content TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE session_feedback (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  submitted_by TEXT,
  rating INTEGER,
  comments TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE peer_requests (
  id TEXT PRIMARY KEY,
  requested_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'open',
  details TEXT,
  created_at INTEGER NOT NULL
);

-- ===================== MEETINGS / ATTENDANCE =====================

CREATE TABLE meetings (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  room_url TEXT,
  scheduled_at INTEGER,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE attendance (                   -- attendance/{meetingId}/attendees/{userId}
  meeting_id TEXT NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  checked_in_at INTEGER NOT NULL,
  marked_by TEXT DEFAULT 'self',            -- 'self' | 'head' | 'admin'
  PRIMARY KEY (meeting_id, user_id)
);

-- ===================== SCHOLARSHIPS / APPLICATIONS / CAREER =====================

CREATE TABLE scholarships (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  details_json TEXT,
  deadline TEXT,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE applications (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  scholarship_id TEXT REFERENCES scholarships(id),
  status TEXT DEFAULT 'pending',
  data_json TEXT,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_applications_user ON applications(user_id);

CREATE TABLE program_applications (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  program_id TEXT,
  status TEXT DEFAULT 'pending',
  data_json TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE recommendations (
  id TEXT PRIMARY KEY,
  requested_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'pending',
  content TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE career_materials (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE career_jobs (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  company TEXT,
  details_json TEXT,
  posted_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at INTEGER NOT NULL
);

CREATE TABLE career_assignments (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'pending',
  feedback TEXT,
  submitted_at INTEGER,
  reviewed_at INTEGER
);

CREATE TABLE career_progress (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  progress_json TEXT,
  updated_at INTEGER NOT NULL
);

CREATE TABLE career_learning_progress (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  progress_json TEXT,
  updated_at INTEGER NOT NULL
);

-- ===================== CERTIFICATES / GRADES / REWARDS =====================

CREATE TABLE certificates (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  program_title TEXT,
  status TEXT DEFAULT 'pending',       -- pending | approved | rejected
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE INDEX idx_certs_user ON certificates(user_id);

CREATE TABLE member_points (
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  points INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE points_history (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  action TEXT,
  description TEXT,
  points INTEGER,
  created_at INTEGER NOT NULL
);
CREATE INDEX idx_pointshist_user ON points_history(user_id);

CREATE TABLE reward_redemptions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  reward TEXT,
  points_spent INTEGER,
  status TEXT DEFAULT 'pending',
  created_at INTEGER NOT NULL
);

-- ===================== COMMUNITY IMPACT / VOLUNTEERING =====================

CREATE TABLE community_tasks (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  details TEXT,
  created_by TEXT REFERENCES users(id),
  status TEXT DEFAULT 'open',
  created_at INTEGER NOT NULL
);

CREATE TABLE community_projects (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  proposed_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'proposed',
  created_at INTEGER NOT NULL
);

CREATE TABLE community_reports (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE community_impact (
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  hours REAL DEFAULT 0,
  impact_json TEXT
);

-- ===================== MENTAL HEALTH =====================

CREATE TABLE mental_posts (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL
);

CREATE TABLE mood_checkins (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  mood TEXT,
  note TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE mental_sessions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  scheduled_at INTEGER,
  created_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE mental_visitations (
  id TEXT PRIMARY KEY,
  posted_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  details TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE sos_reports (
  id TEXT PRIMARY KEY,
  name TEXT, email TEXT, urgency TEXT, message TEXT,
  created_at INTEGER NOT NULL
);

-- ===================== FINANCE (admin/head only) =====================

CREATE TABLE finance_income (
  id TEXT PRIMARY KEY,
  amount REAL NOT NULL,
  source TEXT,
  notes TEXT,
  recorded_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE finance_expenses (
  id TEXT PRIMARY KEY,
  amount REAL NOT NULL,
  category TEXT,
  notes TEXT,
  recorded_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE finance_loans (
  id TEXT PRIMARY KEY,
  amount REAL NOT NULL,
  lender TEXT,
  notes TEXT,
  recorded_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

-- ===================== COMMS / CONTENT / MEDIA =====================

CREATE TABLE social_calendar (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  scheduled_date TEXT,
  posted_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at INTEGER NOT NULL
);

CREATE TABLE content_tasks (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  brief TEXT,
  task_type TEXT,
  status TEXT DEFAULT 'open',
  posted_by TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE content_submissions (
  id TEXT PRIMARY KEY,
  task_id TEXT REFERENCES content_tasks(id) ON DELETE CASCADE,
  submitted_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  file_url TEXT,
  status TEXT DEFAULT 'submitted',
  created_at INTEGER NOT NULL
);

CREATE TABLE newsroom (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  posted_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at INTEGER NOT NULL
);

CREATE TABLE media_library (
  id TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  caption TEXT,
  uploaded_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at INTEGER NOT NULL
);

CREATE TABLE newsletters (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  created_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  sent_at INTEGER,
  created_at INTEGER NOT NULL
);

CREATE TABLE resources (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  url TEXT,
  downloads INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL
);

CREATE TABLE magazine (
  id TEXT PRIMARY KEY,
  edition TEXT NOT NULL,
  content_json TEXT,
  created_at INTEGER NOT NULL
);

-- ===================== PARTNERSHIPS =====================

CREATE TABLE yan_partners (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  details_json TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE partnership_opportunities (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  details TEXT,
  posted_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at INTEGER NOT NULL
);

CREATE TABLE partnership_proposals (
  id TEXT PRIMARY KEY,
  proposed_by TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  details TEXT,
  status TEXT DEFAULT 'pending',
  created_at INTEGER NOT NULL
);

-- ===================== PUBLIC SITE CONTENT =====================

CREATE TABLE team (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT,
  department TEXT,
  photo_url TEXT,
  is_leadership INTEGER DEFAULT 0,
  position INTEGER DEFAULT 0
);

CREATE TABLE events (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  details_json TEXT,
  event_date TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE gallery (
  id TEXT PRIMARY KEY,
  url TEXT NOT NULL,
  type TEXT DEFAULT 'photo',    -- photo | video
  caption TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE stories (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT,
  author_name TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE hubs (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  content_json TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE lab_listings (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  details_json TEXT,
  status TEXT DEFAULT 'pending',
  avg_rating REAL DEFAULT 0,
  review_count INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL
);

CREATE TABLE lab_reviews (
  id TEXT PRIMARY KEY,
  listing_id TEXT NOT NULL REFERENCES lab_listings(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  rating INTEGER NOT NULL,
  comment TEXT,
  created_at INTEGER NOT NULL
);

-- ===================== CAPSTONE =====================

CREATE TABLE capstone_projects (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  details_json TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE capstone_reviews (
  id TEXT PRIMARY KEY,
  project_id TEXT REFERENCES capstone_projects(id) ON DELETE CASCADE,
  reviewer_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  comments TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE capstone_submissions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  project_id TEXT REFERENCES capstone_projects(id),
  file_url TEXT,
  status TEXT DEFAULT 'submitted',
  created_at INTEGER NOT NULL
);

CREATE TABLE program_feedback (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT,
  created_at INTEGER NOT NULL
);

-- ===================== FORMS / SITE-WIDE SUBMISSIONS =====================

CREATE TABLE join_requests (
  id TEXT PRIMARY KEY,
  name TEXT, email TEXT, details_json TEXT,
  status TEXT DEFAULT 'pending',
  created_at INTEGER NOT NULL
);

CREATE TABLE contact_submissions (
  id TEXT PRIMARY KEY,
  name TEXT, email TEXT, message TEXT,
  status TEXT DEFAULT 'new',
  created_at INTEGER NOT NULL
);

CREATE TABLE form_submissions (
  id TEXT PRIMARY KEY,
  form_type TEXT,
  submitted_by TEXT REFERENCES users(id),
  data_json TEXT,
  created_at INTEGER NOT NULL
);

-- ===================== ADMIN / SYSTEM =====================

CREATE TABLE moderation_log (
  id TEXT PRIMARY KEY,
  actor_id TEXT REFERENCES users(id),
  action TEXT,
  target TEXT,
  created_at INTEGER NOT NULL
);

CREATE TABLE system_errors (
  id TEXT PRIMARY KEY,
  message TEXT,
  stack TEXT,
  user_id TEXT REFERENCES users(id),
  created_at INTEGER NOT NULL
);

CREATE TABLE ai_usage (
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  usage_json TEXT
);

CREATE TABLE config (                     -- config/publicStats, config/{docId}
  key TEXT PRIMARY KEY,
  value_json TEXT NOT NULL,
  updated_at INTEGER NOT NULL
);

-- ===================== YAN STUDIO (separate app, same DB) =====================

CREATE TABLE studio_users (
  user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  video_count INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL
);

CREATE TABLE studio_videos (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT,
  r2_key TEXT,               -- object key in R2 bucket
  created_at INTEGER NOT NULL
);

CREATE TABLE studio_feedback (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT,
  created_at INTEGER NOT NULL
);
