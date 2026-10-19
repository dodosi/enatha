#!/usr/bin/env python3
"""Rebuild AMS medical-record extraction survey per Prof Nadine Rujeni 30/09/2026 comments.

Restructures v2.0 into v3.0:
- New title/description.
- Prescription and laboratory pages merged into B. Clinical Encounter (diagnosis -> tests -> treatment).
- Comorbidities / prior antibiotics / prior hospitalisation moved to C. Medical History.
- "Other — specify" text boxes on every list that has an Other option.
- Referral-in (from another facility) and referral-out questions; AI referral items removed.
- Outcome section gated on whether a follow-up / outcome assessment was documented.

Run after rebuild_ams_mr_extraction_v2.py output exists (reads the current JSON for
unchanged demographic, referral and outcome fields). Safe to re-run.
"""

from __future__ import annotations

import copy
import json

from rebuild_ams_mr_extraction_v2 import (
    PATH,
    YN_UNK,
    load_antimicrobials,
    load_facilities,
    load_indications,
    load_pathogens,
    prescription_page,
    prior_antibiotic_panel,
    update_lab_page,
    vitals_block,
)

FORM_VERSION = "AMS-MR-EXTRACTION-v3.0"

TITLE = (
    "Medical Data Extraction and Collection Tool for AI-Supported Antimicrobial "
    "Stewardship in Rwandan Primary Healthcare"
)
DESCRIPTION = (
    "Data extraction and collection questionnaire for AI-supported antimicrobial stewardship "
    f"in Rwandan primary healthcare. Form version {FORM_VERSION} "
    "(Prof Nadine Rujeni 30/09/2026 revisions)."
)

DATA_SOURCES = [
    "Rwanda Health Data Center / e-Ubuzima",
    "HMIS / DHIS2",
    "OpenMRS / CEMR",
    "Laboratory system",
    "Pharmacy system",
    "Referral system",
    "Facility records",
    "Other",
]

REASONS_FOR_CONSULTATION = [
    "Referral-related consultation",
    "Severe infection",
    "Follow-up",
    "Maternal and child health",
    "Chronic disease",
    "Preventive care",
    "Medication-related concern",
    "Request for medications, especially antibiotics",
    "Laboratory services / AST testing",
    "Persistent infection after treatment",
    "Other",
]

PRESENTING_SYMPTOMS = [
    "Fever",
    "Cough / respiratory symptoms",
    "Urinary symptoms",
    "Diarrhea / gastrointestinal infection",
    "Skin and soft tissue infection",
    "Wound infection",
    "STI symptoms",
    "Other",
]

REFERRAL_REASONS = [
    "Severe infection",
    "Suspected antimicrobial resistance",
    "Need for advanced diagnostics",
    "Laboratory testing",
    "Treatment failure",
    "Need for hospitalization",
    "Specialist review",
    "Other",
]

LAB_TEST_TYPES = [
    {"value": "routine", "text": "Routine laboratory tests (e.g. CBC, CRP, urinalysis, glucose, creatinine)"},
    {"value": "microbiology", "text": "Microbiology culture and antimicrobial susceptibility testing (AST)"},
    {"value": "other", "text": "Other laboratory or medical tests"},
]


def other_text(name: str, source: str, title: str, multi: bool = False) -> dict:
    op = "contains" if multi else "="
    return {
        "type": "text",
        "name": name,
        "title": title,
        "isRequired": True,
        "visibleIf": f"{{{source}}} {op} 'Other'",
    }


def index_elements(data: dict) -> dict[str, dict]:
    idx: dict[str, dict] = {}

    def walk(elements: list[dict]) -> None:
        for el in elements:
            if el.get("name"):
                idx[el["name"]] = el
            if el.get("type") == "panel":
                walk(el.get("elements", []))

    for page in data.get("pages", []):
        walk(page.get("elements", []))
    return idx


def pick(idx: dict[str, dict], name: str, **overrides) -> dict:
    if name not in idx:
        raise KeyError(f"Expected element '{name}' in current AMS JSON")
    el = copy.deepcopy(idx[name])
    el.update(overrides)
    return el


def data_source_page() -> dict:
    return {
        "name": "data_source",
        "title": "Data Source",
        "elements": [
            {
                "type": "checkbox",
                "name": "data_sources",
                "title": "Source(s) of data",
                "isRequired": True,
                "choices": DATA_SOURCES,
            },
            other_text("data_sources_other", "data_sources", "Other source name — please specify", multi=True),
        ],
    }


def demographics_page(idx: dict[str, dict]) -> dict:
    names = [
        "patient_study_id",
        "patient_medical_record_id",
        "telephone_number",
        "date_of_birth",
        "age_years",
        "gender",
        "pregnancy_status",
        "patient_residence_location_note",
        "province_id",
        "district_id",
        "sector_id",
        "cell_id",
        "village_id",
    ]
    elements = [pick(idx, n) for n in names]
    elements += [
        pick(idx, "health_insurance_category"),
        other_text(
            "health_insurance_other",
            "health_insurance_category",
            "Other health insurance — please specify",
        ),
        pick(idx, "occupation"),
        other_text("occupation_other", "occupation", "Other occupation — please specify"),
        pick(idx, "education_level"),
        pick(idx, "ubudehe_category"),
    ]
    return {
        "name": "patient_demographics",
        "title": "A. Patient Demographics",
        "description": "Patient demographics are essential for risk prediction models.",
        "elements": elements,
    }


def laboratory_block(amr: list[dict], pathogens: list[dict]) -> list[dict]:
    micro_page = {"elements": [{"type": "paneldynamic", "name": "microbiology_results"}]}
    update_lab_page(micro_page, amr, pathogens)
    micro_template = micro_page["elements"][0]["templateElements"]
    for i, el in enumerate(micro_template):
        if el["name"] == "specimen_type":
            micro_template.insert(
                i + 1,
                {
                    "type": "text",
                    "name": "specimen_type_other",
                    "title": "Other specimen type — please specify",
                    "isRequired": True,
                    "visibleIf": "{panel.specimen_type} = 'Other'",
                },
            )
            break

    return [
        {
            "type": "radiogroup",
            "name": "laboratory_tests_requested",
            "title": "Were any laboratory tests requested for this clinical episode?",
            "isRequired": True,
            "choices": YN_UNK,
        },
        {
            "type": "checkbox",
            "name": "laboratory_test_types",
            "title": "What laboratory tests were requested?",
            "isRequired": True,
            "visibleIf": "{laboratory_tests_requested} = 'Yes'",
            "choices": LAB_TEST_TYPES,
        },
        {
            "type": "paneldynamic",
            "name": "routine_laboratory_results",
            "title": "Routine laboratory tests and results (add each test separately)",
            "visibleIf": "{laboratory_test_types} contains 'routine'",
            "panelCount": 1,
            "minPanelCount": 1,
            "panelAddText": "Add routine lab test",
            "panelRemoveText": "Remove test",
            "templateElements": [
                {
                    "type": "dropdown",
                    "name": "test_name",
                    "title": "Test name",
                    "isRequired": True,
                    "choices": [
                        "CBC",
                        "CRP",
                        "ESR",
                        "Urinalysis",
                        "Blood glucose",
                        "Creatinine",
                        "Liver function test",
                        "Other",
                    ],
                },
                {
                    "type": "text",
                    "name": "test_name_other",
                    "title": "Other test — write as documented",
                    "isRequired": True,
                    "visibleIf": "{panel.test_name} = 'Other'",
                },
                {"type": "text", "name": "result_value", "title": "Result value (if documented)"},
                {"type": "text", "name": "unit", "title": "Unit"},
                {"type": "text", "name": "test_date", "title": "Test date", "inputType": "date"},
                {"type": "comment", "name": "interpretation", "title": "Interpretation / notes"},
            ],
        },
        {
            "type": "paneldynamic",
            "name": "microbiology_results",
            "title": "Microbiology culture and AST results (add each specimen separately)",
            "visibleIf": "{laboratory_test_types} contains 'microbiology'",
            "panelCount": 1,
            "minPanelCount": 1,
            "panelAddText": "Add microbiology / AST result",
            "panelRemoveText": "Remove result",
            "templateElements": micro_template,
        },
        {
            "type": "comment",
            "name": "other_tests_requested",
            "title": "Other laboratory or medical tests requested (as written in the medical record)",
            "isRequired": True,
            "visibleIf": "{laboratory_test_types} contains 'other'",
        },
        {
            "type": "comment",
            "name": "laboratory_diagnoses",
            "title": "What laboratory diagnoses were deduced? (list them, if any)",
            "description": "Leave blank if no laboratory diagnosis is documented.",
            "visibleIf": "{laboratory_tests_requested} = 'Yes'",
        },
    ]


def treatment_block(amr: list[dict], indications: list[dict]) -> list[dict]:
    prescribed, panel = prescription_page(amr, indications)["elements"]
    panel["title"] = (
        "What antimicrobial prescriptions were made? Record each antimicrobial as documented, "
        "then classify it from the searchable standardised list."
    )
    return [
        prescribed,
        panel,
        {
            "type": "comment",
            "name": "other_medications_prescribed",
            "title": "What other (non-antimicrobial) medications were prescribed?",
            "description": "List them as documented in the medical record. Leave blank if none.",
        },
    ]


def clinical_encounter_page(
    idx: dict[str, dict],
    amr: list[dict],
    indications: list[dict],
    pathogens: list[dict],
    facilities: list[dict],
) -> dict:
    elements: list[dict] = [
        pick(idx, "visit_date"),
        pick(idx, "facility_code", choices=facilities),
        pick(idx, "ward_department"),
        other_text("ward_department_other", "ward_department", "Other ward / department — please specify"),
        {
            "type": "radiogroup",
            "name": "referred_from_facility",
            "title": "Was this patient referred from another health facility?",
            "isRequired": True,
            "choices": ["Yes", "No"],
        },
        {
            "type": "text",
            "name": "referred_from_facility_name",
            "title": "From which health facility?",
            "isRequired": True,
            "visibleIf": "{referred_from_facility} = 'Yes'",
        },
        {
            "type": "checkbox",
            "name": "reasons_for_consultation",
            "title": "Reason(s) for consultation",
            "isRequired": True,
            "choices": REASONS_FOR_CONSULTATION,
        },
        other_text(
            "reasons_for_consultation_other",
            "reasons_for_consultation",
            "Other reason for consultation — please specify",
            multi=True,
        ),
        {
            "type": "checkbox",
            "name": "presenting_symptoms",
            "title": "Presenting symptoms",
            "isRequired": True,
            "choices": PRESENTING_SYMPTOMS,
        },
        other_text(
            "presenting_symptoms_other",
            "presenting_symptoms",
            "Other symptoms — please specify",
            multi=True,
        ),
        *vitals_block(),
        {
            "type": "comment",
            "name": "clinical_diagnosis_documented",
            "title": "What clinical diagnoses were made? (as documented in the medical record)",
            "description": 'Write "Not documented" if no diagnosis is recorded.',
            "isRequired": True,
        },
        pick(idx, "clinical_diagnosis", title="Clinical diagnosis category (for coding)"),
        other_text(
            "clinical_diagnosis_other",
            "clinical_diagnosis",
            "Other diagnosis category — please specify",
            multi=True,
        ),
        *laboratory_block(amr, pathogens),
        *treatment_block(amr, indications),
    ]
    return {
        "name": "clinical_encounter",
        "title": "B. Clinical Encounter Data",
        "description": (
            "Clinical encounter, clinical diagnosis, laboratory investigations and treatment "
            "(antimicrobial and other prescriptions) for this clinical episode."
        ),
        "elements": elements,
    }


def hospitalization_block(amr: list[dict]) -> list[dict]:
    return [
        {
            "type": "radiogroup",
            "name": "previous_hospitalization_past_year",
            "title": (
                "Is there documentation that the patient was hospitalized at any time during the "
                "12 months before this clinical episode?"
            ),
            "isRequired": True,
            "choices": YN_UNK,
        },
        {
            "type": "radiogroup",
            "name": "prior_hospitalization_count_documented",
            "title": "Is the number of hospitalizations within the 12 months documented?",
            "isRequired": True,
            "visibleIf": "{previous_hospitalization_past_year} = 'Yes'",
            "choices": ["Number documented", "Unknown"],
        },
        {
            "type": "text",
            "name": "prior_hospitalization_count",
            "title": "How many hospitalizations are documented within the 12 months?",
            "inputType": "number",
            "isRequired": True,
            "visibleIf": "{prior_hospitalization_count_documented} = 'Number documented'",
            "validators": [{"type": "numeric", "minValue": 1, "maxValue": 20}],
        },
        {
            "type": "paneldynamic",
            "name": "prior_hospitalization_records",
            "title": "Previous hospitalization(s) — add each separately",
            "visibleIf": "{previous_hospitalization_past_year} = 'Yes'",
            "panelCount": 1,
            "minPanelCount": 1,
            "panelAddText": "Add hospitalization",
            "panelRemoveText": "Remove hospitalization",
            "templateElements": [
                {
                    "type": "text",
                    "name": "hospitalization_date",
                    "title": "Date of hospitalization / approximate date (if documented)",
                    "inputType": "date",
                },
                {"type": "text", "name": "health_facility", "title": "Health facility (if documented)"},
                {
                    "type": "comment",
                    "name": "reason_diagnosis",
                    "title": "Reason for hospitalization / diagnosis (if documented)",
                },
                {"type": "text", "name": "duration", "title": "Duration of hospitalization (if documented)"},
                {
                    "type": "radiogroup",
                    "name": "antibiotics_during_hosp",
                    "title": "Were antibiotics used during this hospitalization?",
                    "isRequired": True,
                    "choices": YN_UNK,
                },
                {
                    "type": "paneldynamic",
                    "name": "hospitalization_antibiotics",
                    "title": "Antibiotics used during this hospitalization (add each separately)",
                    "visibleIf": "{panel.antibiotics_during_hosp} = 'Yes'",
                    "panelCount": 1,
                    "minPanelCount": 1,
                    "panelAddText": "Add antibiotic",
                    "panelRemoveText": "Remove antibiotic",
                    "templateElements": [
                        {
                            "type": "text",
                            "name": "documented_name",
                            "title": "Antibiotic name as documented in the medical record",
                            "isRequired": True,
                        },
                        {
                            "type": "dropdown",
                            "name": "antibiotic_name",
                            "title": "Standardized antibiotic name (searchable WHO list)",
                            "isRequired": True,
                            "searchEnabled": True,
                            "choices": amr,
                        },
                        {"type": "text", "name": "indication_reason", "title": "Indication (if documented)"},
                        {"type": "text", "name": "dose", "title": "Dose (if documented)"},
                        {
                            "type": "dropdown",
                            "name": "route",
                            "title": "Route of administration (if documented)",
                            "choices": ["Oral", "Intravenous", "Intramuscular", "Topical", "Other", "Not documented"],
                        },
                        {"type": "text", "name": "frequency", "title": "Frequency (if documented)"},
                        {"type": "text", "name": "duration", "title": "Duration (if documented)"},
                    ],
                },
                {
                    "type": "comment",
                    "name": "other_medications_during_hosp",
                    "title": "Any other medications used during this hospitalization (as documented)",
                },
                {
                    "type": "text",
                    "name": "procedure_surgery",
                    "title": "Relevant procedure or surgery (if documented)",
                },
                {"type": "comment", "name": "additional_notes", "title": "Additional notes (optional)"},
            ],
        },
    ]


def medical_history_page(idx: dict[str, dict], amr: list[dict]) -> dict:
    return {
        "name": "medical_history",
        "title": "C. Comorbidity and Medical History (including Hospitalisation)",
        "elements": [
            pick(idx, "comorbidities"),
            other_text(
                "comorbidities_other",
                "comorbidities",
                "Other comorbidity / medical history — please specify",
                multi=True,
            ),
            pick(idx, "recent_surgery_90_days"),
            *prior_antibiotic_panel(amr),
            *hospitalization_block(amr),
        ],
    }


def referral_page(idx: dict[str, dict]) -> dict:
    referred = "{patient_referred} = 'Yes'"
    return {
        "name": "referral_data",
        "title": "D. Referral Data",
        "elements": [
            pick(
                idx,
                "patient_referred",
                title="Was this patient referred to another health facility?",
                isRequired=True,
            ),
            pick(idx, "referral_date"),
            pick(idx, "referral_facility", title="Health facility referred to"),
            pick(idx, "referral_reasons", choices=REFERRAL_REASONS, isRequired=True),
            {
                "type": "text",
                "name": "referral_lab_test_requested",
                "title": "Which laboratory test did the treating doctor request?",
                "isRequired": True,
                "visibleIf": "{referral_reasons} contains 'Laboratory testing'",
            },
            other_text(
                "referral_reasons_other",
                "referral_reasons",
                "Other reason for referral — please specify",
                multi=True,
            ),
            pick(idx, "referral_urgency"),
            pick(idx, "transportation_available", visibleIf=referred),
            pick(idx, "referral_outcome"),
            pick(idx, "time_to_referral_value", visibleIf=referred),
            pick(idx, "time_to_referral_unit", visibleIf=referred),
        ],
    }


def outcome_page(idx: dict[str, dict]) -> dict:
    names = [
        "follow_up_date",
        "recovery_status",
        "readmission",
        "readmission_date",
        "readmission_cause",
        "hospitalization",
        "admission_date",
        "admission_diagnosis",
        "length_of_stay_days",
        "icu_admission",
        "icu_admission_date",
        "icu_stay_duration_days",
        "mortality_status",
        "date_of_death",
        "place_of_death",
        "infection_related_death",
        "treatment_failure",
        "treatment_failure_criteria",
        "date_failure_identified",
        "outcome_notes",
    ]
    return {
        "name": "outcome_data",
        "title": "E. Outcomes Data",
        "description": "Outcome measures evaluate effectiveness, safety, clinical utility, and public health impact.",
        "elements": [
            {
                "type": "radiogroup",
                "name": "outcome_documented",
                "title": (
                    "Did this patient's clinical episode have a follow-up or outcome assessment "
                    "documented?"
                ),
                "isRequired": True,
                "choices": ["Yes", "No"],
            },
            {
                "type": "panel",
                "name": "outcome_details",
                "visibleIf": "{outcome_documented} = 'Yes'",
                "elements": [pick(idx, n) for n in names],
            },
        ],
    }


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    idx = index_elements(data)
    facilities = load_facilities()
    amr = load_antimicrobials()
    indications = load_indications()
    pathogens = load_pathogens()

    data["title"] = TITLE
    data["description"] = DESCRIPTION
    data["showPreviewBeforeComplete"] = "showAllQuestions"
    data["previewText"] = "Review Answers"
    data["editText"] = "Edit"
    data["completeText"] = "Submit"
    data["completedHtml"] = "<h3>Thank you.</h3><p>The medical data extraction form has been submitted.</p>"
    data["pages"] = [
        data_source_page(),
        demographics_page(idx),
        clinical_encounter_page(idx, amr, indications, pathogens, facilities),
        medical_history_page(idx, amr),
        referral_page(idx),
        outcome_page(idx),
    ]

    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {PATH} ({FORM_VERSION})")
    print(
        f"Facilities: {len(facilities)}, Antimicrobials: {len(amr)}, "
        f"Indications: {len(indications)}, Pathogens: {len(pathogens)}"
    )
    for p in data["pages"]:
        print(f"  {p['name']}: {len(p.get('elements', []))} elements")


if __name__ == "__main__":
    main()
