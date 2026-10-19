# Enatha Survey Platform

Lightweight, production-ready web-based survey/data collection platform for institutional field research.

## Stack

- Plain PHP 7.4+ (PDO, sessions)
- MySQL / MariaDB
- SurveyJS (CDN)
- Bootstrap 5
- Vanilla JavaScript

## System Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Browser   │────▶│  PHP Pages   │────▶│  MySQL (PDO)    │
│ SurveyJS UI │     │  + API/*.php │     │  users, surveys │
└─────────────┘     └──────────────┘     │  versions, etc. │
                           │              └─────────────────┘
                           ▼
                    Session + CSRF
```

### Data flow

1. **Survey design (offline)** – Admin designs questionnaire in SurveyJS Creator, exports JSON.
2. **Import** – Admin uploads JSON → new row in `survey_versions` (immutable; version number increments).
3. **Activation** – One version per survey is `active`; enumerators always get the latest active version.
4. **Collection** – `take_survey.php` loads JSON via `api/load_survey.php`; autosave every 30s to `drafts`.
5. **Submission** – `api/submit_survey.php` creates `responses` + flattened `answers` with version linkage.
6. **Export** – `api/export_csv.php` produces Excel-friendly UTF-8 CSV with metadata + dynamic question columns.
7. **Paper form** – `surveys/print_survey.php` renders any version as a printable A4 form (Print → Save as PDF). All conditional questions are printed with an "Answer only if …" instruction; database-loaded questions (locations, facilities) and long dictionaries are printed as write-in lines.

### Rwanda Administrative Locations

Large location lists should not be hardcoded in SurveyJS JSON. The app supports database-backed cascading dropdowns using these exact SurveyJS field names:

```text
province_id -> district_id -> sector_id -> cell_id -> village_id
```

When a survey contains these fields, `assets/js/survey-app.js` automatically loads choices from `api/locations.php`. Selecting a province loads only its districts; selecting a district loads only its sectors; then cells and villages follow the same pattern.

The location tables are:

```text
provinces, districts, sectors, cells, villages
```

Study site facilities use a separate master list (`health_facilities`). Surveys with a `facility_code` dropdown load choices from `api/facilities.php` when that table is populated; otherwise embedded JSON choices are kept.

To import location data from CSV:

```bash
php scripts/import_locations.php database/locations/rwanda_locations_sample.csv
```

For the AMR study districts only (Gasabo, Bugesera, Gakenke):

```bash
# Clear old regions first (SQL): database/locations/clear_locations.sql
php scripts/import_locations.php database/locations/rwanda_study_districts.csv
```

Use `database/locations/rwanda_locations_sample.csv` as the template. Replace it with the complete official Rwanda hierarchy when ready. The CSV header must be:

```text
province,district,sector,cell,village
```

Import study facilities (Gasabo / Bugesera / Gakenke) with:

```bash
mysql -u root your_database < database/locations/health_facilities_seed.sql
```

WHO reference dictionaries used by HCW KAP first-line antibiotic questions:

```text
database/dictionaries/who_antimicrobial_dictionary.csv
database/dictionaries/who_icd11_clinical_conditions.csv
```

Live dropdown refresh endpoints: `api/antimicrobials.php`, `api/indications.php`.

### Versioning (critical)

- Never update `json_definition` on an existing version row.
- Each upload creates `version_number = MAX + 1`.
- Responses store `survey_id`, `survey_version_id`, and `survey_version_number` for audit consistency.

## Folder Structure

```
/config          database.php, app.php
/includes        bootstrap, auth, middleware, functions, layouts
/api             login, logout, load_survey, locations, facilities, antimicrobials, indications, save_draft, submit_survey, export_csv
/admin           dashboard, surveys, upload, responses, users
/surveys         select_survey, take_survey
/assets          css, js, uploads
/database        schema.sql, samples/, locations/
/scripts         create_admin.php, import_locations.php
index.php        login
```

## Quick Start (XAMPP)

1. Place project in `C:\xampp\htdocs\Enatha`
2. Start Apache and MySQL in XAMPP
3. Import database:
   ```bash
   mysql -u root < database/schema.sql
   ```
   Or use phpMyAdmin → Import → `database/schema.sql`
4. Edit [`config/database.php`](config/database.php) if needed (default: root, no password)
5. Create admin password:
   ```bash
   php scripts/create_admin.php
   ```
6. Open http://localhost/Enatha/
7. Optional: import sample location hierarchy:
   ```bash
   php scripts/import_locations.php database/locations/rwanda_locations_sample.csv
   ```
8. Optional: import study facilities:
   ```bash
   mysql -u root your_database < database/locations/health_facilities_seed.sql
   ```
9. Upload sample survey: Admin → Upload Survey JSON → use `database/samples/sample_survey.json`
10. For cascading location testing, upload `database/samples/sample_location_survey.json`
11. For Stream A2 CHW/Patient KAP (reviewer v1.1), upload `database/samples/chw_patient_kap_survey.json` as a **new** survey version (code `CHW_PATIENT_KAP`)
12. For Stream A1 HCW KAP (reviewer Practice v1.2 + TODAY 22/09/2026 v1.3), upload `database/samples/hcw_kap_survey.json` as a **new** survey version (code `HCW_KAP`)
13. For medical data extraction (Prof Nadine 30/09/2026 v3.0, regenerated by `scripts/rebuild_ams_mr_extraction_v3.py`), upload `database/samples/antimicrobial_stewardship_data_collection_survey.json` as a **new** survey version (code `AMS_MR_EXTRACTION` or update `AMS_DATA_COLLECTION`)
14. For pharmacy retrospective data extraction (AMS-PHARMACY-EXTRACTION-v1.0, regenerated by `scripts/build_ams_pharmacy_extraction_v1.py`), upload `database/samples/ams_pharmacy_extraction_survey.json` as a **new** survey (code `AMS_PHARMACY_EXTRACTION`)
15. For Reproductive Health Instrument A — Participant Questionnaire (RH-PARTICIPANT-v1.0, regenerated by `scripts/build_rh_participant_v1.py`), upload `database/samples/reproductive_health_participant_survey.json` as a **new** survey (code `RH_PARTICIPANT`)

## Roles

| Role         | Capabilities                                                                 |
|--------------|------------------------------------------------------------------------------|
| super_admin  | Create leaders; full platform access; sees all surveys/responses             |
| leader       | Create enumerators for their team; upload/manage own surveys; assign access  |
| supervisor   | Legacy; dashboard, surveys, responses, export, take survey (scoped)          |
| enumerator   | Select & fill assigned surveys (default: all of their leader’s forms)        |

**Hierarchy:** `super_admin` → `leader` → `enumerator`. Each survey has an `owner_id` (the leader who uploaded it). Enumerators inherit all of their leader’s surveys unless **Restrict survey access** is enabled and specific surveys are assigned under **Assign surveys**.

### Migration (existing databases)

Run after upgrading:

```bash
mysql -u USER -p DATABASE < database/migrations/001_leader_hierarchy.sql
```

Or import `database/migrations/001_leader_hierarchy.sql` in phpMyAdmin. Then re-login so session roles refresh.

## Security Best Practices

- All DB access via PDO prepared statements
- Passwords hashed with `PASSWORD_DEFAULT` (bcrypt)
- CSRF token on forms and API POST (`X-CSRF-Token` header for JSON)
- Session cookie: HttpOnly, SameSite=Lax, Secure on HTTPS
- Output escaped with `e()` helper
- `.htaccess` blocks direct access to `config/`, `includes/`, `database/`
- Survey JSON validated before storage
- Upload size limited (`MAX_UPLOAD_SIZE` in `config/app.php`)

## Deployment on Bluehost / cPanel

1. **Create MySQL database** in cPanel → MySQL Databases
2. **Import** `database/schema.sql` via phpMyAdmin (select your DB first)
3. **Upload files** via File Manager or FTP to `public_html/Enatha` (or subdomain folder)
4. **Configure** [`config/database.php`](config/database.php):
   - `DB_HOST` – often `localhost`
   - `DB_NAME`, `DB_USER`, `DB_PASS` from cPanel
5. **Set BASE_URL** in [`config/app.php`](config/app.php):
   - Example: `define('BASE_URL', '');` if app is at domain root
   - Example: `define('BASE_URL', '/survey');` if in subfolder
6. **Permissions**: folders `assets/uploads` writable (755 or 775)
7. **PHP version**: Select PHP 7.4+ or 8.x in cPanel MultiPHP Manager
8. **HTTPS**: Enable SSL; session cookies will use Secure flag automatically
9. **Create admin**: SSH or cPanel Terminal:
   ```bash
   php scripts/create_admin.php
   ```
10. **Production**: Set environment variable `APP_ENV=production` in `.htaccess` or hosting panel if supported

## Backup Strategy

| What              | How often   | Method                          |
|-------------------|------------|----------------------------------|
| Full database     | Weekly      | cPanel → Backup / phpMyAdmin export |
| Before new version| Each upload | DB already stores JSON in `survey_versions` |
| Field checkpoints | Weekly      | CSV export from Responses page   |
| Off-site copy     | Weekly      | Download backups to cloud storage |

Restore: import SQL dump into empty database, redeploy PHP files, verify `config/database.php`.

## Future Enhancements

- Offline PWA with IndexedDB sync
- Supervisor approval workflow
- Response detail view with JSON pretty-print
- Dashboard charts (Chart.js)
- PDF export
- Survey locale files
- Email notifications on submission
- Rate limiting on API endpoints
- 2FA for admin accounts

## Troubleshooting

- **Blank page**: Enable errors temporarily in `config/app.php` or check Apache `error_log`
- **CSRF failed**: Refresh page before submit; ensure cookies enabled
- **No surveys listed**: Upload JSON and activate a version
- **SurveyJS not loading**: Check CDN access; consider hosting SurveyJS files locally under `assets/vendor/`

## License

Internal institutional use – adjust as needed.
