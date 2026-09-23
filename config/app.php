<?php
/**
 * Application configuration
 */

define('APP_NAME', 'Enatha Survey Platform');
define('APP_VERSION', '1.0.0');

// Base URL - adjust for production (no trailing slash)
define('BASE_URL', '/Enatha');

// Paths
define('ROOT_PATH', dirname(__DIR__));
define('UPLOAD_PATH', ROOT_PATH . '/assets/uploads');
define('MAX_UPLOAD_SIZE', 5 * 1024 * 1024); // 5MB

// Session
define('SESSION_LIFETIME', 3600 * 8); // 8 hours
define('SESSION_NAME', 'enatha_session');

// Security
define('CSRF_TOKEN_NAME', 'csrf_token');

// Autosave interval (seconds)
define('AUTOSAVE_INTERVAL', 30);

// Timezone
date_default_timezone_set('UTC');

// Error reporting - disable display in production
if (getenv('APP_ENV') === 'production') {
    ini_set('display_errors', '0');
    error_reporting(E_ALL);
} else {
    ini_set('display_errors', '1');
    error_reporting(E_ALL);
}
