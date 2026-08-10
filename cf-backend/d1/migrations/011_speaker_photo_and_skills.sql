-- Speaker/guest photo attached to a session, for whoever designs the poster to work
-- from - uploaded by the head, downloadable by admin and by volunteers picking up the
-- related poster task.
ALTER TABLE dept_sessions ADD COLUMN speaker_photo_url TEXT;

-- What each roster member is actually willing to help with (video recording, editing,
-- moderation, slides, posters, WhatsApp coordination, etc.) - captured on feedback.html
-- alongside "which months", carried onto the roster so admin can see who can do what,
-- not just who's available.
ALTER TABLE volunteer_roster ADD COLUMN skills TEXT;
