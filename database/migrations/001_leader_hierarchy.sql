-- Leader hierarchy + survey assignment
-- Run once in phpMyAdmin (select your Enatha database first).
-- Safe to re-run: uses IF NOT EXISTS / conditional patterns where possible.

-- 1) Expand roles (temporarily keep 'admin' for migration)
ALTER TABLE users
    MODIFY COLUMN role ENUM('super_admin', 'leader', 'supervisor', 'enumerator', 'admin')
    NOT NULL DEFAULT 'enumerator';

-- Existing platform admins become super admins
UPDATE users SET role = 'super_admin' WHERE role = 'admin';

-- Drop legacy admin value
ALTER TABLE users
    MODIFY COLUMN role ENUM('super_admin', 'leader', 'supervisor', 'enumerator')
    NOT NULL DEFAULT 'enumerator';

-- 2) Team membership: enumerators/supervisors belong to a leader
ALTER TABLE users
    ADD COLUMN leader_id INT UNSIGNED NULL AFTER role,
    ADD COLUMN restrict_surveys TINYINT(1) NOT NULL DEFAULT 0 AFTER leader_id;

-- Add FK only if missing (ignore error on re-run if constraint exists)
-- Leaders and super_admins have leader_id = NULL
-- Team members have leader_id = their leader's user id

ALTER TABLE users
    ADD INDEX idx_users_leader (leader_id);

-- 3) Survey ownership (which leader's team owns the form)
ALTER TABLE surveys
    ADD COLUMN owner_id INT UNSIGNED NULL AFTER description,
    ADD INDEX idx_surveys_owner (owner_id);

-- Assign existing surveys to the first super_admin (or first user) so they remain visible
UPDATE surveys s
SET s.owner_id = (
    SELECT u.id FROM users u WHERE u.role = 'super_admin' ORDER BY u.id LIMIT 1
)
WHERE s.owner_id IS NULL;

-- 4) Optional per-user survey restrictions
-- When users.restrict_surveys = 0 → all surveys owned by their leader (default)
-- When users.restrict_surveys = 1 → only rows in user_survey_access
CREATE TABLE IF NOT EXISTS user_survey_access (
    user_id INT UNSIGNED NOT NULL,
    survey_id INT UNSIGNED NOT NULL,
    granted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, survey_id),
    INDEX idx_usa_survey (survey_id),
    CONSTRAINT fk_usa_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_usa_survey FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
