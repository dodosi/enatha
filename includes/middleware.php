<?php
/**
 * Request middleware / guards
 */

/**
 * Require authenticated user
 */
function requireAuth(): void
{
    if (!isLoggedIn()) {
        if (isApiRequest()) {
            jsonResponse(['success' => false, 'message' => 'Unauthorized'], 401);
        }
        redirect('index.php');
    }
}

/**
 * Require specific role(s)
 */
function requireRole(...$roles): void
{
    requireAuth();
    if (!hasRole(...$roles)) {
        if (isApiRequest()) {
            jsonResponse(['success' => false, 'message' => 'Forbidden'], 403);
        }
        setFlash('danger', 'You do not have permission to access this page.');
        redirect(hasRole('enumerator') && !canViewAdminDashboard()
            ? 'surveys/select_survey.php'
            : 'admin/dashboard.php');
    }
}

/**
 * Require super admin or leader (team management / survey upload)
 */
function requireAdmin(): void
{
    requireRole('super_admin', 'leader');
}

/**
 * Require super admin, leader, or supervisor (dashboard / responses)
 */
function requireAdminOrSupervisor(): void
{
    requireRole('super_admin', 'leader', 'supervisor');
}

/**
 * Require platform super admin only
 */
function requireSuperAdmin(): void
{
    requireRole('super_admin');
}

/**
 * Detect API/AJAX request
 */
function isApiRequest(): bool
{
    $uri = $_SERVER['REQUEST_URI'] ?? '';
    if (strpos($uri, '/api/') !== false) {
        return true;
    }
    $accept = $_SERVER['HTTP_ACCEPT'] ?? '';
    if (strpos($accept, 'application/json') !== false) {
        return true;
    }
    return (!empty($_SERVER['HTTP_X_REQUESTED_WITH'])
        && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest');
}

/**
 * Require CSRF for POST API
 */
function requireCsrf(): void
{
    if ($_SERVER['REQUEST_METHOD'] === 'POST' && !validateCsrf()) {
        jsonResponse(['success' => false, 'message' => 'Invalid CSRF token'], 403);
    }
}
