<?php
/**
 * Render a SurveyJS definition as a printable (paper / PDF) form.
 *
 * Every question is printed, including conditional ones; their visibleIf rule is
 * shown as an "Answer only if ..." instruction. Questions whose choices come from
 * the database at runtime (locations, facilities) or from long dictionaries are
 * printed as open write-in questions.
 */

class SurveyPrintRenderer
{
    /** Questions whose choices are loaded from the database by survey-app.js */
    const DB_LOADED_QUESTIONS = ['province_id', 'district_id', 'sector_id', 'cell_id', 'village_id', 'facility_code'];

    /** Choice lists longer than this are printed as write-in lines */
    const OPEN_CHOICE_LIMIT = 40;

    /** Minimum number of blank entries printed for repeatable panels */
    const MIN_PANEL_COPIES = 2;

    /** Minimum number of blank rows printed for dynamic matrices */
    const MIN_MATRIX_ROWS = 5;

    /** @var array */
    private $definition;

    /** @var array<string, string> scope key => printed number (e.g. "Q12", "Q40.3") */
    private $numbers = [];

    /** @var array<string, array> scope key => element */
    private $elements = [];

    public function __construct(array $definition)
    {
        $this->definition = $definition;
        $counter = 0;
        foreach ($this->pages() as $page) {
            $this->index($page['elements'] ?? [], '', 'Q', $counter);
        }
    }

    public function render(): string
    {
        $html = '';
        foreach ($this->pages() as $i => $page) {
            $title = $this->text($page['title'] ?? '') ?: $this->humanize((string) ($page['name'] ?? 'Section ' . ($i + 1)));
            $html .= '<section class="sp-section">';
            $html .= '<h2 class="sp-section-title">' . e($title) . '</h2>';
            if (!empty($page['visibleIf'])) {
                $html .= '<div class="sp-cond sp-cond-section">Complete this section only if '
                    . e($this->describeCondition((string) $page['visibleIf'], '')) . '. Otherwise skip to the next section.</div>';
            }
            if (!empty($page['description'])) {
                $html .= '<p class="sp-section-desc">' . e($this->text($page['description'])) . '</p>';
            }
            $html .= $this->renderElements($page['elements'] ?? [], '', 0);
            $html .= '</section>';
        }
        return $html;
    }

    /* ------------------------------------------------------------------ */
    /* Indexing / numbering                                                */
    /* ------------------------------------------------------------------ */

    private function pages(): array
    {
        if (!empty($this->definition['pages']) && is_array($this->definition['pages'])) {
            return $this->definition['pages'];
        }
        return [['name' => 'questions', 'elements' => $this->definition['elements'] ?? []]];
    }

    private function index(array $elements, string $scope, string $prefix, int &$counter): void
    {
        foreach ($elements as $el) {
            if (!is_array($el) || empty($el['name'])) {
                continue;
            }
            $type = $el['type'] ?? '';
            if ($type === 'panel') {
                $this->index($el['elements'] ?? [], $scope, $prefix, $counter);
                continue;
            }
            $key = $this->key($scope, (string) $el['name']);
            $this->elements[$key] = $el;
            if ($type === 'html' || $type === 'image') {
                continue;
            }
            $counter++;
            $number = $prefix . $counter;
            $this->numbers[$key] = $number;
            if ($type === 'paneldynamic') {
                $childCounter = 0;
                $this->index($el['templateElements'] ?? [], $key, $number . '.', $childCounter);
            }
        }
    }

    private function key(string $scope, string $name): string
    {
        return $scope === '' ? $name : $scope . '/' . $name;
    }

    /* ------------------------------------------------------------------ */
    /* Element rendering                                                   */
    /* ------------------------------------------------------------------ */

    private function renderElements(array $elements, string $scope, int $depth): string
    {
        $html = '';
        foreach ($elements as $el) {
            if (is_array($el) && !empty($el['name'])) {
                $html .= $this->renderElement($el, $scope, $depth);
            }
        }
        return $html;
    }

    private function renderElement(array $el, string $scope, int $depth): string
    {
        $type = $el['type'] ?? '';

        if ($type === 'html') {
            $text = $this->htmlToText((string) ($el['html'] ?? ''));
            return $text === '' ? '' : '<div class="sp-note">' . nl2br(e($text)) . '</div>';
        }
        if ($type === 'image') {
            return '';
        }
        if ($type === 'panel') {
            return $this->renderStaticPanel($el, $scope, $depth);
        }
        if ($type === 'paneldynamic') {
            return $this->renderDynamicPanel($el, $scope, $depth);
        }

        $key = $this->key($scope, (string) $el['name']);
        $html = '<div class="sp-q">' . $this->questionHeader($el, $key, $scope);
        $html .= $this->questionBody($el, $scope);
        return $html . '</div>';
    }

    private function questionHeader(array $el, string $key, string $scope): string
    {
        $title = $this->text($el['title'] ?? '') ?: $this->humanize((string) $el['name']);
        $html = '<div class="sp-q-head"><span class="sp-num">' . e($this->numbers[$key] ?? '') . '</span> '
            . '<span class="sp-title">' . e($title) . '</span>';
        if (!empty($el['isRequired'])) {
            $html .= ' <span class="sp-req" title="Required">*</span>';
        }
        $html .= '</div>';
        if (!empty($el['visibleIf'])) {
            $html .= '<div class="sp-cond">&#8627; Answer only if '
                . e($this->describeCondition((string) $el['visibleIf'], $scope)) . '</div>';
        }
        if (!empty($el['description'])) {
            $html .= '<div class="sp-desc">' . e($this->text($el['description'])) . '</div>';
        }
        return $html;
    }

    private function questionBody(array $el, string $scope): string
    {
        $type = $el['type'] ?? 'text';
        switch ($type) {
            case 'radiogroup':
            case 'dropdown':
            case 'imagepicker':
                return $this->choiceBody($el, $scope, false);
            case 'checkbox':
            case 'tagbox':
                return $this->choiceBody($el, $scope, true);
            case 'boolean':
                return $this->choiceList([
                    $this->text($el['labelTrue'] ?? '') ?: 'Yes',
                    $this->text($el['labelFalse'] ?? '') ?: 'No',
                ], 'Tick one');
            case 'rating':
                return $this->ratingBody($el);
            case 'ranking':
                return $this->rankingBody($el, $scope);
            case 'matrix':
                return $this->matrixBody($el, $scope);
            case 'matrixdropdown':
            case 'matrixdynamic':
                return $this->matrixDropdownBody($el, $scope);
            case 'multipletext':
                return $this->multipleTextBody($el);
            case 'comment':
                return $this->lines(max(3, (int) ($el['rows'] ?? 3)));
            case 'signaturepad':
                return '<div class="sp-box-large"></div>';
            case 'file':
                return '<div class="sp-hint">Attachment reference:</div>' . $this->lines(1);
            case 'expression':
                return '<div class="sp-hint">Calculated automatically in the electronic form &mdash; leave blank.</div>';
            case 'text':
            default:
                return $this->textBody($el);
        }
    }

    private function textBody(array $el): string
    {
        $inputType = $el['inputType'] ?? 'text';
        $range = $this->rangeHint($el);
        switch ($inputType) {
            case 'date':
                return '<div class="sp-date">____ / ____ / ________ <span class="sp-hint">(DD / MM / YYYY)</span></div>';
            case 'datetime-local':
                return '<div class="sp-date">____ / ____ / ________ &nbsp; ____ : ____ <span class="sp-hint">(DD / MM / YYYY &nbsp; HH : MM)</span></div>';
            case 'time':
                return '<div class="sp-date">____ : ____ <span class="sp-hint">(HH : MM)</span></div>';
            case 'number':
            case 'range':
                return '<div class="sp-short-line"></div>' . ($range ? ' <span class="sp-hint">' . e($range) . '</span>' : '');
            default:
                return $this->lines(1);
        }
    }

    private function choiceBody(array $el, string $scope, bool $multi): string
    {
        $name = (string) $el['name'];
        $source = $this->choiceSource($el, $scope);
        $choices = $source['choices'];
        $max = (int) ($el['maxSelectedChoices'] ?? 0);

        $isOpen = in_array($name, self::DB_LOADED_QUESTIONS, true)
            || !empty($el['choicesByUrl'])
            || count($choices) === 0
            || count($choices) > self::OPEN_CHOICE_LIMIT;

        if ($isOpen) {
            $hint = 'Write in';
            if (count($choices) > self::OPEN_CHOICE_LIMIT) {
                $hint = 'Write the name as documented; it is coded from the standardised list during data entry';
            }
            $lineCount = $multi ? max(1, $max ?: 3) : 1;
            $html = '<div class="sp-hint">' . e($hint) . ($multi && $lineCount > 1 ? ' (one per line)' : '') . ':</div>';
            if ($multi && $lineCount > 1) {
                $html .= '<ol class="sp-write-list">';
                for ($i = 0; $i < $lineCount; $i++) {
                    $html .= '<li><div class="sp-line"></div></li>';
                }
                return $html . '</ol>';
            }
            return $html . $this->lines(1);
        }

        $labels = array_map(function ($c) {
            return $this->choiceLabel($c);
        }, $choices);

        if ($multi) {
            $hint = $max > 0 ? 'Tick up to ' . $max : 'Tick all that apply';
        } else {
            $hint = 'Tick one';
        }
        if ($source['from'] !== '') {
            $hint .= ' (only options ticked in ' . $source['from'] . ')';
        }

        if (!empty($el['showNoneItem']) || !empty($el['hasNone'])) {
            $labels[] = $this->text($el['noneText'] ?? '') ?: 'None';
        }
        $other = !empty($el['showOtherItem']) || !empty($el['hasOther']);
        return $this->choiceList($labels, $hint, $other ? ($this->text($el['otherText'] ?? '') ?: 'Other (specify)') : '');
    }

    private function choiceList(array $labels, string $hint, string $otherLabel = ''): string
    {
        $long = false;
        foreach ($labels as $label) {
            if (mb_strlen($label) > 38) {
                $long = true;
                break;
            }
        }
        $cols = (!$long && count($labels) > 5) ? ' sp-cols' : '';
        $html = '<div class="sp-hint">' . e($hint) . ':</div><ul class="sp-choices' . $cols . '">';
        foreach ($labels as $label) {
            $html .= '<li><span class="sp-box"></span>' . e($label) . '</li>';
        }
        if ($otherLabel !== '') {
            $html .= '<li class="sp-other"><span class="sp-box"></span>' . e($otherLabel) . ': <span class="sp-inline-line"></span></li>';
        }
        return $html . '</ul>';
    }

    private function ratingBody(array $el): string
    {
        $values = [];
        if (!empty($el['rateValues']) && is_array($el['rateValues'])) {
            foreach ($el['rateValues'] as $v) {
                $values[] = $this->choiceLabel($v);
            }
        } else {
            $min = (int) ($el['rateMin'] ?? 1);
            $max = (int) ($el['rateMax'] ?? 5);
            $step = max(1, (int) ($el['rateStep'] ?? 1));
            for ($v = $min; $v <= $max; $v += $step) {
                $values[] = (string) $v;
            }
        }
        $html = '<div class="sp-hint">Circle one:</div><div class="sp-rating">';
        if (!empty($el['minRateDescription'])) {
            $html .= '<span class="sp-hint">' . e($this->text($el['minRateDescription'])) . '</span> ';
        }
        foreach ($values as $v) {
            $html .= '<span class="sp-rate">' . e($v) . '</span>';
        }
        if (!empty($el['maxRateDescription'])) {
            $html .= ' <span class="sp-hint">' . e($this->text($el['maxRateDescription'])) . '</span>';
        }
        return $html . '</div>';
    }

    private function rankingBody(array $el, string $scope): string
    {
        $choices = $this->choiceSource($el, $scope)['choices'];
        $html = '<div class="sp-hint">Write the rank (1 = highest) next to each option:</div><ul class="sp-choices">';
        foreach ($choices as $c) {
            $html .= '<li><span class="sp-rank-box"></span>' . e($this->choiceLabel($c)) . '</li>';
        }
        return $html . '</ul>';
    }

    private function matrixBody(array $el, string $scope): string
    {
        $columns = array_map(function ($c) {
            return $this->choiceLabel($c);
        }, $this->asList($el['columns'] ?? []));

        $rows = $this->asList($el['rows'] ?? []);
        $note = '';
        if (!empty($el['rowsFromQuestion'])) {
            $sourceKey = $this->resolveKey((string) $el['rowsFromQuestion'], $scope);
            $sourceEl = $this->elements[$sourceKey] ?? [];
            $rows = $sourceEl ? $this->choiceSource($sourceEl, $scope)['choices'] : [];
            $note = 'Complete only the rows for options ticked in ' . ($this->numbers[$sourceKey] ?? $el['rowsFromQuestion']) . '.';
        }

        $html = '<div class="sp-hint">' . e($note !== '' ? $note . ' Tick one per row.' : 'Tick one per row.') . '</div>';
        $html .= '<table class="sp-table"><thead><tr><th></th>';
        foreach ($columns as $c) {
            $html .= '<th>' . e($c) . '</th>';
        }
        $html .= '</tr></thead><tbody>';

        if (count($rows) === 0 || count($rows) > self::OPEN_CHOICE_LIMIT) {
            for ($i = 0; $i < self::MIN_MATRIX_ROWS; $i++) {
                $html .= '<tr><td class="sp-write-cell"></td>' . str_repeat('<td class="sp-cell"><span class="sp-box"></span></td>', count($columns)) . '</tr>';
            }
        } else {
            foreach ($rows as $r) {
                $html .= '<tr><td>' . e($this->choiceLabel($r)) . '</td>'
                    . str_repeat('<td class="sp-cell"><span class="sp-box"></span></td>', count($columns)) . '</tr>';
            }
        }
        return $html . '</tbody></table>';
    }

    private function matrixDropdownBody(array $el, string $scope): string
    {
        $columns = $this->asList($el['columns'] ?? []);
        $html = '<table class="sp-table sp-table-grid"><thead><tr>';
        $rows = $this->asList($el['rows'] ?? []);
        if ($rows) {
            $html .= '<th></th>';
        }
        foreach ($columns as $col) {
            $title = $this->text($col['title'] ?? '') ?: $this->humanize((string) ($col['name'] ?? ''));
            $choices = $this->asList($col['choices'] ?? ($el['choices'] ?? []));
            $cellType = $col['cellType'] ?? ($el['cellType'] ?? 'dropdown');
            $sub = '';
            if (in_array($cellType, ['dropdown', 'radiogroup', 'checkbox', 'tagbox'], true)) {
                if ($choices && count($choices) <= 8) {
                    $sub = implode(' / ', array_map(function ($c) {
                        return $this->choiceLabel($c);
                    }, $choices));
                } elseif ($choices) {
                    $sub = 'write name as documented';
                }
            } elseif ($cellType === 'boolean') {
                $sub = 'Yes / No';
            }
            $html .= '<th>' . e($title) . ($sub !== '' ? '<div class="sp-th-sub">' . e($sub) . '</div>' : '') . '</th>';
        }
        $html .= '</tr></thead><tbody>';

        $cells = str_repeat('<td class="sp-write-cell"></td>', count($columns));
        if ($rows) {
            foreach ($rows as $r) {
                $html .= '<tr><td>' . e($this->choiceLabel($r)) . '</td>' . $cells . '</tr>';
            }
        } else {
            $count = max(self::MIN_MATRIX_ROWS, (int) ($el['rowCount'] ?? 0));
            for ($i = 0; $i < $count; $i++) {
                $html .= '<tr>' . $cells . '</tr>';
            }
        }
        $html .= '</tbody></table>';
        if (!$rows) {
            $html .= '<div class="sp-hint">Add rows on an extra sheet if needed.</div>';
        }
        return $html;
    }

    private function multipleTextBody(array $el): string
    {
        $html = '<table class="sp-table sp-table-plain"><tbody>';
        foreach ($this->asList($el['items'] ?? []) as $item) {
            $title = $this->text($item['title'] ?? '') ?: $this->humanize((string) ($item['name'] ?? ''));
            $html .= '<tr><td class="sp-mt-label">' . e($title) . '</td><td><div class="sp-line"></div></td></tr>';
        }
        return $html . '</tbody></table>';
    }

    private function renderStaticPanel(array $el, string $scope, int $depth): string
    {
        $html = '<div class="sp-panel">';
        $title = $this->text($el['title'] ?? '');
        if ($title !== '') {
            $html .= '<div class="sp-panel-title">' . e($title) . '</div>';
        }
        if (!empty($el['visibleIf'])) {
            $html .= '<div class="sp-cond">&#8627; Answer the questions below only if '
                . e($this->describeCondition((string) $el['visibleIf'], $scope)) . '</div>';
        }
        if (!empty($el['description'])) {
            $html .= '<div class="sp-desc">' . e($this->text($el['description'])) . '</div>';
        }
        $html .= $this->renderElements($el['elements'] ?? [], $scope, $depth);
        return $html . '</div>';
    }

    private function renderDynamicPanel(array $el, string $scope, int $depth): string
    {
        $key = $this->key($scope, (string) $el['name']);
        $number = $this->numbers[$key] ?? '';
        $copies = max(self::MIN_PANEL_COPIES, (int) ($el['panelCount'] ?? 0), (int) ($el['minPanelCount'] ?? 0));
        if (!empty($el['maxPanelCount'])) {
            $copies = min($copies, (int) $el['maxPanelCount']);
        }

        $html = '<div class="sp-repeat">' . $this->questionHeader($el, $key, $scope);
        $html .= '<div class="sp-hint">Complete one entry per item (' . $copies
            . ' entries printed). Continue on an extra sheet using the same numbering if more are needed.</div>';
        for ($i = 1; $i <= $copies; $i++) {
            $html .= '<div class="sp-entry sp-depth-' . min($depth, 2) . '">';
            $html .= '<div class="sp-entry-head">' . e($number) . ' &mdash; Entry ' . $i . '</div>';
            $html .= $this->renderElements($el['templateElements'] ?? [], $key, $depth + 1);
            $html .= '</div>';
        }
        return $html . '</div>';
    }

    /* ------------------------------------------------------------------ */
    /* Conditions                                                          */
    /* ------------------------------------------------------------------ */

    private function describeCondition(string $expr, string $scope): string
    {
        $parts = preg_split('/(\'[^\']*\'|"[^"]*")/', $expr, -1, PREG_SPLIT_DELIM_CAPTURE);
        foreach ($parts as $i => $part) {
            if ($i % 2 === 0) {
                $part = preg_replace('/\s+and\s+/i', ' AND ', $part);
                $parts[$i] = preg_replace('/\s+or\s+/i', ' OR ', $part);
            }
        }
        $expr = implode('', $parts);

        $expr = preg_replace_callback(
            '/\{([^}]+)\}\s+(notempty|empty)\b/i',
            function ($m) use ($scope) {
                $label = $this->refLabel($m[1], $scope);
                return strtolower($m[2]) === 'empty' ? $label . ' is not answered' : $label . ' is answered';
            },
            $expr
        );

        $expr = preg_replace_callback(
            '/\{([^}]+)\}\s*(!=|<>|==|=|>=|<=|>|<|notcontains|contains|anyof|allof|noneof)\s*'
            . '(\[[^\]]*\]|\'[^\']*\'|"[^"]*"|-?\d+(?:\.\d+)?|true|false)/i',
            function ($m) use ($scope) {
                return $this->describeComparison($m[1], strtolower($m[2]), $m[3], $scope);
            },
            $expr
        );

        $expr = preg_replace_callback('/\{([^}]+)\}/', function ($m) use ($scope) {
            return $this->refLabel($m[1], $scope);
        }, $expr);

        return trim($expr);
    }

    private function describeComparison(string $ref, string $op, string $operand, string $scope): string
    {
        $label = $this->refLabel($ref, $scope);
        $isLength = substr($ref, -7) === '.length';
        $el = $this->elements[$this->resolveKey($isLength ? substr($ref, 0, -7) : $ref, $scope)] ?? null;
        if (!$el && !$isLength && ($row = $this->matrixRowRef($ref, $scope))) {
            $el = ['type' => 'radiogroup', 'choices' => $this->asList($row['matrix']['columns'] ?? [])];
        }

        $values = [];
        if ($operand !== '' && $operand[0] === '[') {
            preg_match_all('/\'([^\']*)\'|"([^"]*)"|(-?\d+(?:\.\d+)?)/', $operand, $mm, PREG_SET_ORDER);
            foreach ($mm as $x) {
                $values[] = $x[1] !== '' ? $x[1] : (isset($x[2]) && $x[2] !== '' ? $x[2] : ($x[3] ?? ''));
            }
        } else {
            $values[] = trim($operand, '\'"');
        }

        $quoted = (!$isLength && ($operand[0] === '\'' || $operand[0] === '"' || $operand[0] === '['));
        $texts = array_map(function ($v) use ($el, $quoted) {
            $text = $el ? $this->choiceTextForValue($el, $v) : $v;
            return $quoted ? '"' . $text . '"' : $text;
        }, $values);
        $joined = $this->joinList($texts, $op === 'allof' ? 'and' : 'or');

        $phrases = [
            '='           => 'is',
            '=='          => 'is',
            '!='          => 'is not',
            '<>'          => 'is not',
            '>'           => 'is more than',
            '<'           => 'is less than',
            '>='          => 'is at least',
            '<='          => 'is at most',
            'contains'    => 'includes',
            'notcontains' => 'does not include',
            'anyof'       => 'is',
            'allof'       => 'includes',
            'noneof'      => 'is not',
        ];
        return $label . ' ' . ($phrases[$op] ?? $op) . ' ' . $joined;
    }

    private function refLabel(string $ref, string $scope): string
    {
        if (substr($ref, -7) === '.length') {
            $base = substr($ref, 0, -7);
            return 'the number of options ticked in ' . $this->refLabel($base, $scope);
        }
        $key = $this->resolveKey($ref, $scope);
        if (isset($this->numbers[$key])) {
            return $this->numbers[$key];
        }
        $row = $this->matrixRowRef($ref, $scope);
        if ($row) {
            return $row['number'] . ' (row "' . $row['label'] . '")';
        }
        return $ref;
    }

    /**
     * Resolve "{matrix_name.row_value}" references.
     *
     * @return array{matrix: array, number: string, label: string}|null
     */
    private function matrixRowRef(string $ref, string $scope): ?array
    {
        $dot = strrpos($ref, '.');
        if ($dot === false || strpos($ref, 'panel.') === 0) {
            return null;
        }
        $key = $this->resolveKey(substr($ref, 0, $dot), $scope);
        $matrix = $this->elements[$key] ?? null;
        if (!$matrix || ($matrix['type'] ?? '') !== 'matrix') {
            return null;
        }
        $rowValue = substr($ref, $dot + 1);
        $label = $rowValue;
        foreach ($this->asList($matrix['rows'] ?? []) as $r) {
            if ((is_array($r) ? (string) ($r['value'] ?? '') : (string) $r) === $rowValue) {
                $label = $this->choiceLabel($r);
                break;
            }
        }
        return ['matrix' => $matrix, 'number' => $this->numbers[$key] ?? $key, 'label' => $label];
    }

    private function resolveKey(string $ref, string $scope): string
    {
        if (strpos($ref, 'panel.') === 0) {
            return $this->key($scope, substr($ref, 6));
        }
        return $ref;
    }

    /* ------------------------------------------------------------------ */
    /* Choice helpers                                                      */
    /* ------------------------------------------------------------------ */

    /**
     * @return array{choices: array, from: string}
     */
    private function choiceSource(array $el, string $scope): array
    {
        if (!empty($el['choicesFromQuestion'])) {
            $sourceKey = $this->resolveKey((string) $el['choicesFromQuestion'], $scope);
            $source = $this->elements[$sourceKey] ?? null;
            if ($source) {
                return [
                    'choices' => $this->asList($source['choices'] ?? []),
                    'from'    => $this->numbers[$sourceKey] ?? (string) $el['choicesFromQuestion'],
                ];
            }
        }
        return ['choices' => $this->asList($el['choices'] ?? []), 'from' => ''];
    }

    private function choiceTextForValue(array $el, string $value): string
    {
        if (($el['type'] ?? '') === 'boolean') {
            if ($value === 'true') {
                return $this->text($el['labelTrue'] ?? '') ?: 'Yes';
            }
            if ($value === 'false') {
                return $this->text($el['labelFalse'] ?? '') ?: 'No';
            }
        }
        foreach ($this->choiceSource($el, '')['choices'] as $c) {
            if (is_array($c) && isset($c['value']) && (string) $c['value'] === $value) {
                return $this->choiceLabel($c);
            }
        }
        return $value;
    }

    /**
     * @param mixed $choice
     */
    private function choiceLabel($choice): string
    {
        if (is_array($choice)) {
            $text = $this->text($choice['text'] ?? '');
            return $text !== '' ? $text : (string) ($choice['value'] ?? '');
        }
        return (string) $choice;
    }

    /**
     * @param mixed $value
     */
    private function asList($value): array
    {
        return is_array($value) ? array_values($value) : [];
    }

    /* ------------------------------------------------------------------ */
    /* Text helpers                                                        */
    /* ------------------------------------------------------------------ */

    /**
     * @param mixed $value localisable SurveyJS string
     */
    private function text($value): string
    {
        if (is_array($value)) {
            $value = $value['default'] ?? $value['en'] ?? reset($value);
        }
        return trim((string) $value);
    }

    private function humanize(string $name): string
    {
        return ucfirst(str_replace('_', ' ', $name));
    }

    private function htmlToText(string $html): string
    {
        $html = preg_replace('/<\s*br\s*\/?>/i', "\n", $html);
        $html = preg_replace('/<\/\s*(p|div|li|h[1-6])\s*>/i', "\n", $html);
        $text = html_entity_decode(strip_tags($html), ENT_QUOTES, 'UTF-8');
        return trim(preg_replace("/\n{2,}/", "\n", $text));
    }

    private function rangeHint(array $el): string
    {
        foreach ($this->asList($el['validators'] ?? []) as $v) {
            if (($v['type'] ?? '') === 'numeric' && (isset($v['minValue']) || isset($v['maxValue']))) {
                $min = isset($v['minValue']) ? (string) $v['minValue'] : '';
                $max = isset($v['maxValue']) ? (string) $v['maxValue'] : '';
                if ($min !== '' && $max !== '') {
                    return '(' . $min . ' – ' . $max . ')';
                }
                return $min !== '' ? '(minimum ' . $min . ')' : '(maximum ' . $max . ')';
            }
        }
        return '';
    }

    private function joinList(array $items, string $conjunction): string
    {
        if (count($items) <= 1) {
            return (string) ($items[0] ?? '');
        }
        $last = array_pop($items);
        return implode(', ', $items) . ' ' . $conjunction . ' ' . $last;
    }

    private function lines(int $count): string
    {
        return str_repeat('<div class="sp-line"></div>', max(1, $count));
    }
}
