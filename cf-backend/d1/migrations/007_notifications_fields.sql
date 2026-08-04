ALTER TABLE notifications ADD COLUMN type TEXT;
ALTER TABLE notifications ADD COLUMN posted_by TEXT;
ALTER TABLE notifications ADD COLUMN department TEXT;
CREATE INDEX idx_notif_department ON notifications(department);
