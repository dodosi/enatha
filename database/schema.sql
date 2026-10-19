-- Enatha Survey Platform - Database Schema
-- MySQL 5.7+ / MariaDB 10.2+

CREATE DATABASE IF NOT EXISTS enatha_survey
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE enatha_survey;

-- --------------------------------------------------------
-- users
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('super_admin', 'leader', 'supervisor', 'enumerator') NOT NULL DEFAULT 'enumerator',
    leader_id INT UNSIGNED NULL,
    restrict_surveys TINYINT(1) NOT NULL DEFAULT 0,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_status (status),
    INDEX idx_users_leader (leader_id),
    CONSTRAINT fk_users_leader FOREIGN KEY (leader_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- surveys (logical survey)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS surveys (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    survey_code VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    owner_id INT UNSIGNED NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_surveys_code (survey_code),
    INDEX idx_surveys_owner (owner_id),
    CONSTRAINT fk_surveys_owner FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- user_survey_access (optional restrictions; empty + restrict_surveys=0 = all leader surveys)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_survey_access (
    user_id INT UNSIGNED NOT NULL,
    survey_id INT UNSIGNED NOT NULL,
    granted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, survey_id),
    INDEX idx_usa_survey (survey_id),
    CONSTRAINT fk_usa_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_usa_survey FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- survey_versions (immutable SurveyJS JSON versions)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS survey_versions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    survey_id INT UNSIGNED NOT NULL,
    version_number INT UNSIGNED NOT NULL,
    json_definition LONGTEXT NOT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'inactive',
    created_by INT UNSIGNED NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_survey_version (survey_id, version_number),
    INDEX idx_sv_survey_status (survey_id, status),
    INDEX idx_sv_created (created_at),
    CONSTRAINT fk_sv_survey FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE RESTRICT,
    CONSTRAINT fk_sv_user FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- responses (one submission instance)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS responses (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    survey_id INT UNSIGNED NOT NULL,
    survey_version_id INT UNSIGNED NOT NULL,
    survey_version_number INT UNSIGNED NOT NULL,
    enumerator_id INT UNSIGNED NOT NULL,
    started_at DATETIME NULL,
    submitted_at DATETIME NULL,
    duration_seconds INT UNSIGNED NULL,
    status ENUM('draft', 'completed', 'abandoned') NOT NULL DEFAULT 'completed',
    latitude DECIMAL(10, 8) NULL,
    longitude DECIMAL(11, 8) NULL,
    device_info VARCHAR(500) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_resp_survey (survey_id),
    INDEX idx_resp_version (survey_version_id),
    INDEX idx_resp_enumerator (enumerator_id),
    INDEX idx_resp_submitted (submitted_at),
    INDEX idx_resp_status (status),
    CONSTRAINT fk_resp_survey FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE RESTRICT,
    CONSTRAINT fk_resp_version FOREIGN KEY (survey_version_id) REFERENCES survey_versions(id) ON DELETE RESTRICT,
    CONSTRAINT fk_resp_user FOREIGN KEY (enumerator_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- answers (flexible per-question storage)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS answers (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    response_id INT UNSIGNED NOT NULL,
    question_name VARCHAR(255) NOT NULL,
    question_type VARCHAR(50) NOT NULL DEFAULT 'text',
    answer_value TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ans_response (response_id),
    INDEX idx_ans_question (question_name),
    CONSTRAINT fk_ans_response FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- drafts (autosave)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS drafts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    survey_id INT UNSIGNED NOT NULL,
    survey_version_id INT UNSIGNED NOT NULL,
    draft_json LONGTEXT NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_draft_user_survey (user_id, survey_id),
    INDEX idx_draft_updated (updated_at),
    CONSTRAINT fk_draft_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_draft_survey FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE,
    CONSTRAINT fk_draft_version FOREIGN KEY (survey_version_id) REFERENCES survey_versions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Rwanda administrative locations
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS provinces (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_province_name (name),
    INDEX idx_provinces_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS districts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    province_id INT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_district_parent_name (province_id, name),
    INDEX idx_districts_province (province_id),
    INDEX idx_districts_status (status),
    CONSTRAINT fk_district_province FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sectors (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    district_id INT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_sector_parent_name (district_id, name),
    INDEX idx_sectors_district (district_id),
    INDEX idx_sectors_status (status),
    CONSTRAINT fk_sector_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS cells (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sector_id INT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_cell_parent_name (sector_id, name),
    INDEX idx_cells_sector (sector_id),
    INDEX idx_cells_status (status),
    CONSTRAINT fk_cell_sector FOREIGN KEY (sector_id) REFERENCES sectors(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS villages (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cell_id INT UNSIGNED NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_village_parent_name (cell_id, name),
    INDEX idx_villages_cell (cell_id),
    INDEX idx_villages_status (status),
    CONSTRAINT fk_village_cell FOREIGN KEY (cell_id) REFERENCES cells(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Study health facilities (selectable study sites)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS health_facilities (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    facility_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(50) NOT NULL,
    facility_level VARCHAR(80) NOT NULL,
    district_name VARCHAR(120) NOT NULL,
    sector_name VARCHAR(120) NULL,
    cell_name VARCHAR(120) NULL,
    village_name VARCHAR(120) NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hf_district (district_name),
    INDEX idx_hf_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- After import, run: php scripts/create_admin.php
-- to create the admin user with a secure password.
-- Also import: database/locations/health_facilities_seed.sql
