<?php
/**
 * Shared helper functions
 */

/**
 * Escape HTML output
 */
function e(?string $value): string
{
    return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
}

/**
 * Redirect to path relative to BASE_URL
 */
function redirect(string $path): void
{
    $url = rtrim(BASE_URL, '/') . '/' . ltrim($path, '/');
    header('Location: ' . $url);
    exit;
}

/**
 * Get full URL for asset or page
 */
function url(string $path = ''): string
{
    return rtrim(BASE_URL, '/') . '/' . ltrim($path, '/');
}

/**
 * Initialize secure session
 */
function initSession(): void
{
    if (session_status() === PHP_SESSION_ACTIVE) {
        return;
    }

    session_name(SESSION_NAME);
    session_set_cookie_params([
        'lifetime' => SESSION_LIFETIME,
        'path'     => '/',
        'secure'   => isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on',
        'httponly' => true,
        'samesite' => 'Lax',
    ]);
    session_start();

    if (!isset($_SESSION['created'])) {
        $_SESSION['created'] = time();
    } elseif (time() - $_SESSION['created'] > SESSION_LIFETIME) {
        session_regenerate_id(true);
        $_SESSION['created'] = time();
    }
}

/**
 * Generate CSRF token
 */
function csrfToken(): string
{
    if (empty($_SESSION[CSRF_TOKEN_NAME])) {
        $_SESSION[CSRF_TOKEN_NAME] = bin2hex(random_bytes(32));
    }
    return $_SESSION[CSRF_TOKEN_NAME];
}

/**
 * Validate CSRF token from POST or header
 */
function validateCsrf(?string $token = null): bool
{
    $token = $token ?? ($_POST[CSRF_TOKEN_NAME] ?? $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '');
    return !empty($_SESSION[CSRF_TOKEN_NAME])
        && hash_equals($_SESSION[CSRF_TOKEN_NAME], (string) $token);
}

/**
 * Output CSRF hidden input
 */
function csrfField(): string
{
    return '<input type="hidden" name="' . e(CSRF_TOKEN_NAME) . '" value="' . e(csrfToken()) . '">';
}

/**
 * JSON API response
 */
function jsonResponse(array $data, int $code = 200): void
{
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

/**
 * Validate SurveyJS JSON structure (basic)
 */
function isValidSurveyJson(string $json): bool
{
    $decoded = json_decode($json, true);
    if (json_last_error() !== JSON_ERROR_NONE || !is_array($decoded)) {
        return false;
    }
    // SurveyJS typically has pages or elements
    return isset($decoded['pages']) || isset($decoded['elements']);
}

/**
 * Flatten SurveyJS result data into answer rows
 */
function flattenSurveyAnswers(array $data, string $prefix = ''): array
{
    $answers = [];

    foreach ($data as $key => $value) {
        $name = $prefix === '' ? (string) $key : $prefix . '.' . $key;

        if (is_array($value)) {
            if (array_is_list($value) && !empty($value) && !is_array($value[0])) {
                $answers[] = [
                    'question_name' => $name,
                    'question_type' => 'array',
                    'answer_value'  => json_encode($value, JSON_UNESCAPED_UNICODE),
                ];
            } elseif (isset($value[0]) && is_array($value[0])) {
                // Panel dynamic or matrix rows
                foreach ($value as $i => $row) {
                    if (is_array($row)) {
                        $answers = array_merge($answers, flattenSurveyAnswers($row, $name . '[' . $i . ']'));
                    }
                }
            } else {
                $answers = array_merge($answers, flattenSurveyAnswers($value, $name));
            }
        } else {
            $type = 'text';
            if (is_bool($value)) {
                $type = 'boolean';
                $value = $value ? 'true' : 'false';
            } elseif (is_numeric($value)) {
                $type = 'number';
            }
            $answers[] = [
                'question_name' => $name,
                'question_type' => $type,
                'answer_value'  => (string) $value,
            ];
        }
    }

    return $answers;
}

/**
 * polyfill array_is_list for PHP 7.4
 */
if (!function_exists('array_is_list')) {
    function array_is_list(array $arr): bool
    {
        if ($arr === []) {
            return true;
        }
        $i = 0;
        foreach ($arr as $k => $_) {
            if ($k !== $i++) {
                return false;
            }
        }
        return true;
    }
}

/**
 * Get next version number for a survey
 */
function getNextVersionNumber(PDO $db, int $surveyId): int
{
    $stmt = $db->prepare('SELECT COALESCE(MAX(version_number), 0) + 1 AS next_ver FROM survey_versions WHERE survey_id = ?');
    $stmt->execute([$surveyId]);
    $row = $stmt->fetch();
    return (int) $row['next_ver'];
}

/**
 * Get latest active survey version
 */
function getLatestActiveVersion(PDO $db, int $surveyId): ?array
{
    $stmt = $db->prepare(
        'SELECT sv.*, s.title, s.survey_code
         FROM survey_versions sv
         JOIN surveys s ON s.id = sv.survey_id
         WHERE sv.survey_id = ? AND sv.status = ?
         ORDER BY sv.version_number DESC
         LIMIT 1'
    );
    $stmt->execute([$surveyId, 'active']);
    $row = $stmt->fetch();
    return $row ?: null;
}

/**
 * Flash message helpers
 */
function setFlash(string $type, string $message): void
{
    $_SESSION['flash'] = ['type' => $type, 'message' => $message];
}

function getFlash(): ?array
{
    if (empty($_SESSION['flash'])) {
        return null;
    }
    $flash = $_SESSION['flash'];
    unset($_SESSION['flash']);
    return $flash;
}
