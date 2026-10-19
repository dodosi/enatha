<?php
/**
 * Role hierarchy and survey / team access helpers.
 *
 * Roles:
 * - super_admin: platform owner (all privileges)
 * - leader: team admin (own surveys + own enumerators/supervisors)
 * - supervisor: view team responses / take surveys
 * - enumerator: collect data
 */

function isSuperAdmin(): bool
{
    return hasRole('super_admin');
}

function isLeader(): bool
{
    return hasRole('leader');
}

/** Super admin or leader — manage users / surveys for their scope */
function canManageTeam(): bool
{
    return hasRole('super_admin', 'leader');
}

function canManageSurveyCatalog(): bool
{
    return hasRole('super_admin', 'leader');
}

function canViewAdminDashboard(): bool
{
    return hasRole('super_admin', 'leader', 'supervisor');
}

function canTakeSurveys(): bool
{
    return hasRole('super_admin', 'leader', 'supervisor', 'enumerator');
}

/**
 * Leader id that owns this user's team.
 * Leaders return their own id; team members return leader_id; super_admin returns null.
 */
function teamLeaderId(?array $user = null): ?int
{
    $user = $user ?? currentUser();
    if (!$user) {
        return null;
    }
    if (($user['role'] ?? '') === 'leader') {
        return (int) $user['id'];
    }
    if (!empty($user['leader_id'])) {
        return (int) $user['leader_id'];
    }
    return null;
}

/**
 * Whether current user may manage the given target user row.
 */
function canManageUserRow(array $target): bool
{
    if (isSuperAdmin()) {
        return true;
    }
    if (!isLeader()) {
        return false;
    }
    $myId = currentUserId();
    // Leaders manage their team members only (not themselves as "target" for delete, but OK for view)
    return isset($target['leader_id']) && (int) $target['leader_id'] === (int) $myId;
}

/**
 * Survey IDs the current user is allowed to take / open.
 * Super admin: all active surveys.
 * Leader: surveys they own.
 * Team member: owner's surveys, optionally restricted via user_survey_access.
 *
 * @return int[]|null null means unrestricted (all surveys)
 */
function accessibleSurveyIds(PDO $db, ?array $user = null): ?array
{
    $user = $user ?? currentUser();
    if (!$user) {
        return [];
    }

    if (($user['role'] ?? '') === 'super_admin') {
        return null; // all
    }

    if (($user['role'] ?? '') === 'leader') {
        $stmt = $db->prepare('SELECT id FROM surveys WHERE owner_id = ?');
        $stmt->execute([(int) $user['id']]);
        return array_map('intval', array_column($stmt->fetchAll(), 'id'));
    }

    $leaderId = !empty($user['leader_id']) ? (int) $user['leader_id'] : 0;
    if ($leaderId <= 0) {
        return [];
    }

    if (!empty($user['restrict_surveys'])) {
        $stmt = $db->prepare(
            'SELECT usa.survey_id
             FROM user_survey_access usa
             INNER JOIN surveys s ON s.id = usa.survey_id AND s.owner_id = ?
             WHERE usa.user_id = ?'
        );
        $stmt->execute([$leaderId, (int) $user['id']]);
        return array_map('intval', array_column($stmt->fetchAll(), 'id'));
    }

    $stmt = $db->prepare('SELECT id FROM surveys WHERE owner_id = ?');
    $stmt->execute([$leaderId]);
    return array_map('intval', array_column($stmt->fetchAll(), 'id'));
}

function userCanAccessSurvey(PDO $db, int $surveyId, ?array $user = null): bool
{
    if ($surveyId <= 0) {
        return false;
    }
    $ids = accessibleSurveyIds($db, $user);
    if ($ids === null) {
        return true;
    }
    return in_array($surveyId, $ids, true);
}

/**
 * SQL fragment + params to restrict surveys to the current user's scope.
 * Returns ['sql' => ' AND s.id IN (...)', 'params' => [...]] or empty sql if unrestricted.
 *
 * @return array{sql: string, params: array}
 */
function surveyScopeSql(string $surveyAlias = 's'): array
{
    $db = getDb();
    $ids = accessibleSurveyIds($db);
    if ($ids === null) {
        return ['sql' => '', 'params' => []];
    }
    if (empty($ids)) {
        return ['sql' => " AND 1=0", 'params' => []];
    }
    $placeholders = implode(',', array_fill(0, count($ids), '?'));
    return [
        'sql' => " AND {$surveyAlias}.id IN ($placeholders)",
        'params' => $ids,
    ];
}

/**
 * SQL fragment to restrict responses to the current user's team.
 * Super admin: no filter.
 * Leader/supervisor: responses from their team OR surveys they own.
 *
 * @return array{sql: string, params: array}
 */
function responseTeamScopeSql(string $responseAlias = 'r', string $enumeratorAlias = 'u'): array
{
    $user = currentUser();
    if (!$user) {
        return ['sql' => ' AND 1=0', 'params' => []];
    }
    if (($user['role'] ?? '') === 'super_admin') {
        return ['sql' => '', 'params' => []];
    }

    $leaderId = teamLeaderId($user);
    if ($leaderId === null || $leaderId <= 0) {
        return ['sql' => ' AND 1=0', 'params' => []];
    }

    // Team = leader themselves + members with leader_id = leader
    return [
        'sql' => " AND ({$enumeratorAlias}.id = ? OR {$enumeratorAlias}.leader_id = ?)",
        'params' => [$leaderId, $leaderId],
    ];
}

/**
 * Surveys the current leader (or super_admin) may administer in the catalog UI.
 *
 * @return array{sql: string, params: array}
 */
function managedSurveysSql(string $surveyAlias = 's'): array
{
    $user = currentUser();
    if (!$user) {
        return ['sql' => ' AND 1=0', 'params' => []];
    }
    if (($user['role'] ?? '') === 'super_admin') {
        return ['sql' => '', 'params' => []];
    }
    if (($user['role'] ?? '') === 'leader') {
        return [
            'sql' => " AND {$surveyAlias}.owner_id = ?",
            'params' => [(int) $user['id']],
        ];
    }
    // Supervisor: same as their leader's surveys
    $leaderId = teamLeaderId($user);
    if ($leaderId) {
        return [
            'sql' => " AND {$surveyAlias}.owner_id = ?",
            'params' => [$leaderId],
        ];
    }
    return ['sql' => ' AND 1=0', 'params' => []];
}
