-- Head Panel posts (headPostToFeed) tag a post with the head's department for
-- department-scoped views (loadHeadOverview's count, department-filtered feed).
ALTER TABLE posts ADD COLUMN department TEXT;
CREATE INDEX idx_posts_department ON posts(department);
