/**
 * Survey taking - SurveyJS integration, autosave, submit
 */
(function () {
    'use strict';

    var config = window.SURVEY_CONFIG || {};
    var surveyId = config.surveyId;
    var csrfToken = config.csrfToken;
    var baseUrl = config.baseUrl || '';
    var autosaveInterval = config.autosaveInterval || 30;
    var startedAt = new Date().toISOString();
    var surveyModel = null;
    var versionMeta = {};
    var autosaveTimer = null;
    var locationChain = [
        { name: 'province_id', level: 'provinces', parent: null, label: 'Province' },
        { name: 'district_id', level: 'districts', parent: 'province_id', label: 'District' },
        { name: 'sector_id', level: 'sectors', parent: 'district_id', label: 'Sector' },
        { name: 'cell_id', level: 'cells', parent: 'sector_id', label: 'Cell' },
        { name: 'village_id', level: 'villages', parent: 'cell_id', label: 'Village' }
    ];

    function apiUrl(path) {
        return baseUrl.replace(/\/$/, '') + '/' + path.replace(/^\//, '');
    }

    function updateAutosaveStatus(text) {
        var el = document.getElementById('autosaveStatus');
        if (el) el.textContent = text;
    }

    function getDeviceInfo() {
        return navigator.userAgent.substring(0, 500);
    }

    function getQuestion(name) {
        return surveyModel ? surveyModel.getQuestionByName(name) : null;
    }

    function hasLocationQuestions() {
        return locationChain.some(function (item) {
            return !!getQuestion(item.name);
        });
    }

    function setQuestionChoices(questionName, choices, emptyText) {
        var question = getQuestion(questionName);
        if (!question) return;

        // Keep IDs as numbers so parent_id cascading stays consistent
        question.choices = (choices || []).map(function (choice) {
            return {
                value: typeof choice.value === 'string' && /^\d+$/.test(choice.value)
                    ? parseInt(choice.value, 10)
                    : choice.value,
                text: choice.text
            };
        });
        question.placeholder = emptyText || 'Select an option';
    }

    function setQuestionEnabled(questionName, enabled) {
        var question = getQuestion(questionName);
        if (!question) return;

        // Prefer SurveyJS enableIf on the question; only clear readOnly when enabling
        // so cascade never leaves district/sector stuck disabled after parent select.
        if (enabled) {
            question.readOnly = false;
        } else if (!question.enableIf) {
            question.readOnly = true;
        }
    }

    var clearingLocations = false;

    function clearDownstream(parentName) {
        var parentIndex = locationChain.findIndex(function (item) {
            return item.name === parentName;
        });
        if (parentIndex === -1) return;

        clearingLocations = true;
        try {
            locationChain.slice(parentIndex + 1).forEach(function (item) {
                if (getQuestion(item.name)) {
                    surveyModel.setValue(item.name, null);
                    setQuestionChoices(item.name, [], 'Select ' + item.label.toLowerCase());
                    setQuestionEnabled(item.name, false);
                }
            });
        } finally {
            clearingLocations = false;
        }
    }

    function loadLocationChoices(item, parentId) {
        var url = apiUrl('api/locations.php?level=' + encodeURIComponent(item.level));
        if (parentId !== null && parentId !== undefined && parentId !== '') {
            url += '&parent_id=' + encodeURIComponent(parentId);
        }

        return fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin'
        })
            .then(function (r) { return r.json(); })
            .then(function (res) {
                if (!res.success) {
                    throw new Error(res.message || 'Failed to load locations');
                }
                setQuestionChoices(item.name, res.choices || [], 'Select ' + item.label.toLowerCase());
                setQuestionEnabled(item.name, true);
                return res.choices || [];
            });
    }

    function refreshLocationItem(item) {
        if (!getQuestion(item.name)) {
            return Promise.resolve();
        }

        if (!item.parent) {
            return loadLocationChoices(item, null);
        }

        var parentValue = surveyModel.getValue(item.parent);
        if (parentValue === null || parentValue === undefined || parentValue === '') {
            setQuestionChoices(item.name, [], 'Select ' + item.label.toLowerCase());
            setQuestionEnabled(item.name, false);
            return Promise.resolve();
        }

        return loadLocationChoices(item, parentValue);
    }

    function restoreLocationChoicesFromDraft() {
        var sequence = Promise.resolve();

        locationChain.forEach(function (item) {
            sequence = sequence.then(function () {
                return refreshLocationItem(item);
            });
        });

        return sequence.catch(function (err) {
            updateAutosaveStatus('Location list loading failed');
            console.error(err);
        });
    }

    function setupLocationCascades() {
        if (!hasLocationQuestions()) return;

        locationChain.forEach(function (item) {
            if (item.parent && getQuestion(item.name) && !surveyModel.getValue(item.parent)) {
                setQuestionEnabled(item.name, false);
            }
        });

        surveyModel.onValueChanged.add(function (sender, options) {
            if (clearingLocations) return;

            var changed = options.name;
            var changedItem = locationChain.find(function (item) {
                return item.name === changed;
            });

            if (!changedItem) return;

            clearDownstream(changed);

            var child = locationChain.find(function (item) {
                return item.parent === changed;
            });
            if (child) {
                refreshLocationItem(child).catch(function (err) {
                    updateAutosaveStatus('Failed to load ' + child.label.toLowerCase() + ' list');
                    console.error(err);
                });
            }
        });

        restoreLocationChoicesFromDraft();
    }

    function loadFacilityChoices() {
        var question = getQuestion('facility_code');
        if (!question) return;

        fetch(apiUrl('api/facilities.php'), {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (r) { return r.json(); })
            .then(function (res) {
                if (!res.success || !res.choices || !res.choices.length) {
                    return;
                }
                var current = surveyModel.getValue('facility_code');
                setQuestionChoices('facility_code', res.choices, 'Select study health facility');
                if (current) {
                    surveyModel.setValue('facility_code', current);
                }
            })
            .catch(function () {
                // Keep embedded JSON choices if facilities API is unavailable
            });
    }

    function applyDictionaryChoices(questionNames, endpoint) {
        var targets = questionNames.filter(function (name) {
            return !!getQuestion(name);
        });
        if (!targets.length) return;

        fetch(apiUrl(endpoint), {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (r) { return r.json(); })
            .then(function (res) {
                if (!res.success || !res.choices || !res.choices.length) {
                    return;
                }
                targets.forEach(function (name) {
                    var current = surveyModel.getValue(name);
                    setQuestionChoices(name, res.choices, 'Search and select');
                    if (current) {
                        surveyModel.setValue(name, current);
                    }
                });
            })
            .catch(function () {
                // Keep embedded dictionary choices from survey JSON
            });
    }

    function loadDictionaryChoices() {
        applyDictionaryChoices(
            [
                'top_antimicrobial_1',
                'top_antimicrobial_2',
                'top_antimicrobial_3',
                'first_line_antibiotics',
                'doctor_pneumonia_first_choice'
            ],
            'api/antimicrobials.php'
        );
        applyDictionaryChoices(
            [
                'first_line_indication_1',
                'first_line_indication_2',
                'first_line_indication_3',
                'culture_request_conditions'
            ],
            'api/indications.php'
        );

        // AMS MR extraction panels embed dictionary choices in JSON;
        // facility_code is refreshed via loadFacilityChoices().
    }

    function saveDraft(data) {
        if (!versionMeta.id) return;
        fetch(apiUrl('api/save_draft.php'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                survey_id: surveyId,
                survey_version_id: versionMeta.id,
                data: data
            })
        })
            .then(function (r) { return r.json(); })
            .then(function (res) {
                if (res.success) {
                    updateAutosaveStatus('Draft saved at ' + (res.saved_at || 'now'));
                }
            })
            .catch(function () {
                updateAutosaveStatus('Autosave failed');
            });
    }

    function startAutosave() {
        if (autosaveTimer) clearInterval(autosaveTimer);
        autosaveTimer = setInterval(function () {
            if (surveyModel) {
                saveDraft(surveyModel.data);
            }
        }, autosaveInterval * 1000);
    }

    function submitSurvey(sender) {
        var data = sender.data;
        var payload = {
            survey_id: surveyId,
            survey_version_id: versionMeta.id,
            survey_version_number: versionMeta.version_number,
            data: data,
            started_at: startedAt,
            device_info: getDeviceInfo()
        };

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function (pos) {
                    payload.latitude = pos.coords.latitude;
                    payload.longitude = pos.coords.longitude;
                    doSubmit(payload);
                },
                function () { doSubmit(payload); },
                { timeout: 5000, maximumAge: 60000 }
            );
        } else {
            doSubmit(payload);
        }
    }

    function doSubmit(payload) {
        updateAutosaveStatus('Submitting...');
        fetch(apiUrl('api/submit_survey.php'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload)
        })
            .then(function (r) { return r.json(); })
            .then(function (res) {
                if (res.success) {
                    if (autosaveTimer) clearInterval(autosaveTimer);
                    alert('Survey submitted successfully.');
                    window.location.href = res.redirect || apiUrl('surveys/select_survey.php');
                } else {
                    alert(res.message || 'Submission failed');
                    updateAutosaveStatus('');
                }
            })
            .catch(function () {
                alert('Network error. Please try again.');
                updateAutosaveStatus('');
            });
    }

    function initSurvey(definition, draft) {
        surveyModel = new Survey.Model(definition);

        // Always allow respondents to preview answers before final submit
        surveyModel.showPreviewBeforeComplete = 'showAllQuestions';
        surveyModel.previewText = surveyModel.previewText || 'Review Answers';
        surveyModel.editText = surveyModel.editText || 'Edit';
        surveyModel.completeText = surveyModel.completeText || 'Submit';

        if (draft && typeof draft === 'object') {
            surveyModel.data = draft;
            updateAutosaveStatus('Draft restored');
        }

        setupLocationCascades();
        loadFacilityChoices();
        loadDictionaryChoices();

        surveyModel.onComplete.add(submitSurvey);
        surveyModel.onValueChanged.add(function () {
            updateAutosaveStatus('Unsaved changes');
        });

        document.getElementById('surveyElement').innerHTML = '';
        surveyModel.render(document.getElementById('surveyElement'));
        var container = document.getElementById('surveyContainer');
        if (container) container.classList.remove('d-none');
        var loading = document.getElementById('surveyLoading');
        if (loading) loading.classList.add('d-none');
        startAutosave();
    }

    function loadSurvey() {
        document.getElementById('surveyLoading').classList.remove('d-none');
        fetch(apiUrl('api/load_survey.php?survey_id=' + surveyId), {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (r) { return r.json(); })
            .then(function (res) {
                document.getElementById('surveyLoading').classList.add('d-none');
                if (!res.success) {
                    document.getElementById('surveyError').textContent = res.message || 'Failed to load survey';
                    document.getElementById('surveyError').classList.remove('d-none');
                    return;
                }
                versionMeta = res.version;
                if (res.csrf_token) csrfToken = res.csrf_token;
                document.getElementById('surveyTitle').textContent =
                    res.survey.title + ' (v' + res.version.version_number + ')';
                initSurvey(res.definition, res.draft);
            })
            .catch(function () {
                document.getElementById('surveyLoading').classList.add('d-none');
                document.getElementById('surveyError').textContent = 'Network error loading survey';
                document.getElementById('surveyError').classList.remove('d-none');
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadSurvey);
    } else {
        loadSurvey();
    }
})();
