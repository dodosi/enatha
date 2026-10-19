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
 * Build map of question name => title from SurveyJS JSON definition.
 *
 * @return array<string, string>
 */
function surveyQuestionTitleMap(string $jsonDefinition): array
{
    $decoded = json_decode($jsonDefinition, true);
    if (!is_array($decoded)) {
        return [];
    }
    $map = [];
    $walk = function ($elements) use (&$walk, &$map) {
        if (!is_array($elements)) {
            return;
        }
        foreach ($elements as $el) {
            if (!is_array($el)) {
                continue;
            }
            $name = isset($el['name']) ? (string) $el['name'] : '';
            if ($name !== '') {
                $title = $el['title'] ?? $name;
                if (is_array($title)) {
                    $title = $title['default'] ?? $title['en'] ?? reset($title) ?: $name;
                }
                $map[$name] = (string) $title;
            }
            if (!empty($el['elements'])) {
                $walk($el['elements']);
            }
            if (!empty($el['templateElements'])) {
                $walk($el['templateElements']);
            }
            if (!empty($el['columns']) && is_array($el['columns'])) {
                foreach ($el['columns'] as $col) {
                    if (is_array($col) && !empty($col['name'])) {
                        $ct = $col['title'] ?? $col['name'];
                        if (is_array($ct)) {
                            $ct = $ct['default'] ?? $ct['en'] ?? reset($ct) ?: $col['name'];
                        }
                        $map[(string) $col['name']] = (string) $ct;
                    }
                }
            }
        }
    };
    if (!empty($decoded['pages']) && is_array($decoded['pages'])) {
        foreach ($decoded['pages'] as $page) {
            if (is_array($page) && !empty($page['elements'])) {
                $walk($page['elements']);
            }
        }
    }
    if (!empty($decoded['elements'])) {
        $walk($decoded['elements']);
    }
    return $map;
}

/**
 * Human-readable label for a stored answer key (supports panel[0].field paths).
 */
function resolveQuestionLabel(string $questionName, array $titleMap): string
{
    if (isset($titleMap[$questionName])) {
        return $titleMap[$questionName];
    }
    if (preg_match('/^(.+)\[(\d+)\]\.(.+)$/', $questionName, $m)) {
        $panel = $m[1];
        $idx = (int) $m[2] + 1;
        $field = $m[3];
        $panelTitle = $titleMap[$panel] ?? $panel;
        $fieldTitle = $titleMap[$field] ?? $field;
        return $panelTitle . ' #' . $idx . ' — ' . $fieldTitle;
    }
    if (strpos($questionName, '.') !== false) {
        $parts = explode('.', $questionName);
        $last = end($parts);
        if (isset($titleMap[$last])) {
            return $titleMap[$last] . ' (' . $questionName . ')';
        }
    }
    return $questionName;
}

/**
 * Format stored answer_value for display.
 */
function formatAnswerDisplay(string $value, string $type = 'text'): string
{
    $trim = trim($value);
    if ($trim === '') {
        return '—';
    }
    if ($type === 'boolean' || $trim === 'true' || $trim === 'false') {
        if ($trim === 'true') {
            return 'Yes';
        }
        if ($trim === 'false') {
            return 'No';
        }
    }
    $decoded = json_decode($trim, true);
    if (json_last_error() === JSON_ERROR_NONE && is_array($decoded)) {
        if (array_is_list($decoded) && (empty($decoded) || !is_array($decoded[0] ?? null))) {
            return implode(', ', array_map('strval', $decoded));
        }
        return json_encode($decoded, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    }
    return $trim;
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
