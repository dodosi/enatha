#!/usr/bin/env python3
"""Build the pharmacy retrospective data extraction survey (AMS-PHARMACY-EXTRACTION-v1.0).

Source: "Pharmacy Retrospective Data Extraction Module — Developer Brief", derived from
AMS-MR-EXTRACTION-v3.0 (Prof Nadine Rujeni, 30/09/2026 revisions).

Reuses the standardized antimicrobial dictionary, ICD-11 clinical-condition dictionary and
approved facility list used by the clinic extraction form. Safe to re-run.
"""

from __future__ import annotations

import json

from rebuild_ams_mr_extraction_v2 import (
    ROOT,
    YN_UNK,
    load_antimicrobials,
    load_facilities,
    load_indications,
)

FORM_VERSION = "AMS-PHARMACY-EXTRACTION-v1.0"
OUTPUT = ROOT / "database" / "samples" / "ams_pharmacy_extraction_survey.json"

NOT_DOCUMENTED = "Not documented"
NOT_FOUND = "Antimicrobial not found in standardised list"
EXTRACTION_PERIOD_START = "2020-01-01"
COMPLETE_RECORD = "Complete — all applicable variables documented"

TITLE = (
    "Pharmacy Retrospective Data Extraction Tool for AI-Supported Antimicrobial "
    "Stewardship in Rwandan Primary Healthcare"
)
DESCRIPTION = (
    "Patient-level extraction of antimicrobial dispensing records from participating "
    f"pharmacies (2020–2026). Form version {FORM_VERSION}, derived from "
    "AMS-MR-EXTRACTION-v3.0. Record only what is documented in the pharmacy's routine "
    "records; do not infer missing clinical information."
)

DATA_SOURCES = [
    "Pharmacy electronic system",
    "Pharmacy paper register",
    "Prescription or dispensing record",
    "Linked healthcare facility record",
    "Other",
]

PRESCRIBER_CATEGORIES = [
    "Physician",
    "Medical specialist",
    "Clinical officer",
    "Nurse",
    "Midwife",
    "Dentist",
    "Pharmacist",
    "Other",
    NOT_DOCUMENTED,
]

FORMULATIONS = [
    "Tablet",
    "Capsule",
    "Oral suspension / syrup",
    "Powder for oral suspension",
    "Injection",
    "Topical cream / ointment",
    "Eye / ear drops",
    "Suppository / pessary",
    "Other",
    NOT_DOCUMENTED,
]

ROUTES = ["Oral", "Intravenous", "Intramuscular", "Topical", "Other", NOT_DOCUMENTED]

PAYMENT_METHODS = [
    "Fully covered by insurance",
    "Partially covered by insurance",
    "Out-of-pocket (no insurance)",
    NOT_DOCUMENTED,
]

INSURANCE_CATEGORIES = [
    "Mutuelle de Sante (CBHI)",
    "RSSB",
    "MMI",
    "Private insurance",
    "No insurance",
    "Other",
    NOT_DOCUMENTED,
]

DISPENSING_ISSUES = [
    "Partial dispensing (less than the prescribed quantity)",
    "Substitution with another product",
    "Antimicrobial unavailable / out of stock",
]

OTHER_MEDICATION_STATUS = [
    "Prescribed and dispensed",
    "Prescribed — not dispensed",
    "Prescribed — dispensing status not documented",
    "Dispensed without a documented prescription",
]

PREVIOUS_USE_SOURCES = [
    "This pharmacy (earlier dispensing record)",
    "Another pharmacy",
    "Health facility",
    "Community health worker",
    "Other",
    NOT_DOCUMENTED,
]

PREVIOUS_USE_EVIDENCE = [
    "Dispensing record",
    "Prescription record",
    "Patient-reported (documented by pharmacy)",
    NOT_DOCUMENTED,
]


def other_text(name: str, title: str, visible_if: str) -> dict:
    return {
        "type": "text",
        "name": name,
        "title": title,
        "isRequired": True,
        "visibleIf": visible_if,
    }


def antimicrobial_dropdown(name: str, title: str, required: bool) -> dict:
    question = {
        "type": "dropdown",
        "name": name,
        "title": title,
        "searchEnabled": True,
        "choices": load_antimicrobials(),
    }
    if required:
        question["isRequired"] = True
    return question


def pharmacy_choices() -> list[dict]:
    pharmacies = [c for c in load_facilities() if c["value"].endswith("-PH")]
    if not pharmacies:
        raise ValueError("No pharmacies (-PH codes) found in the approved facility list")
    return pharmacies


def data_source_page() -> dict:
    return {
        "name": "data_source",
        "title": "A. Data Source and Record Identification",
        "description": (
            "Pharmacy data-source category. All variables must reflect what is documented "
            "in the pharmacy's routine records."
        ),
        "elements": [
            {
                "type": "checkbox",
                "name": "data_sources",
                "title": "What is the source of the information?",
                "isRequired": True,
                "choices": DATA_SOURCES,
            },
            other_text(
                "data_sources_other",
                "Other source — please specify",
                "{data_sources} contains 'Other'",
            ),
            {
                "type": "dropdown",
                "name": "pharmacy_facility_code",
                "title": "Pharmacy name (select from approved facility list)",
                "isRequired": True,
                "searchEnabled": True,
                "choices": pharmacy_choices(),
            },
            {
                "type": "text",
                "name": "dispensing_date",
                "title": "Date of dispensing or pharmacy visit",
                "inputType": "date",
                "isRequired": True,
                "min": EXTRACTION_PERIOD_START,
                "maxValueExpression": "today()",
            },
            {
                "type": "text",
                "name": "study_record_id",
                "title": "Unique anonymized study record ID",
                "description": "Enter the study record ID assigned by the study system.",
                "isRequired": True,
            },
            {
                "type": "text",
                "name": "pharmacy_source_record_reference",
                "title": "Pharmacy source-record reference, where available",
                "description": "Register page/line, invoice or electronic transaction number.",
            },
            {
                "type": "text",
                "name": "patient_medical_record_id",
                "title": "Patient medical-record number, where available",
                "description": (
                    "Restricted identifier: stored separately from the anonymized research "
                    "dataset and used only for approved record linkage."
                ),
            },
        ],
    }


def demographics_page() -> dict:
    return {
        "name": "patient_demographics",
        "title": "B. Patient Demographics",
        "description": (
            "Extract only what is documented. Select \"Not documented\" when a variable is "
            "absent from the pharmacy record."
        ),
        "elements": [
            {
                "type": "radiogroup",
                "name": "age_documentation",
                "title": "How is the patient's age documented?",
                "isRequired": True,
                "choices": [
                    "Date of birth documented",
                    "Age in years only",
                    NOT_DOCUMENTED,
                ],
            },
            {
                "type": "text",
                "name": "date_of_birth",
                "title": "Date of birth",
                "inputType": "date",
                "isRequired": True,
                "maxValueExpression": "today()",
                "visibleIf": "{age_documentation} = 'Date of birth documented'",
            },
            {
                "type": "text",
                "name": "age_years",
                "title": "Age in years",
                "inputType": "number",
                "isRequired": True,
                "visibleIf": "{age_documentation} = 'Age in years only'",
                "validators": [{"type": "numeric", "minValue": 0, "maxValue": 120}],
            },
            {
                "type": "radiogroup",
                "name": "gender",
                "title": "Sex / gender as recorded",
                "isRequired": True,
                "choices": ["Female", "Male", "Other as recorded", NOT_DOCUMENTED],
            },
            other_text(
                "gender_other",
                "Sex / gender as written in the record",
                "{gender} = 'Other as recorded'",
            ),
            {
                "type": "radiogroup",
                "name": "residence_documented",
                "title": "Is the patient's residence documented?",
                "isRequired": True,
                "choices": ["Yes", NOT_DOCUMENTED],
            },
            {
                "type": "html",
                "name": "patient_residence_location_note",
                "visibleIf": "{residence_documented} = 'Yes'",
                "html": (
                    "<strong>Patient residence location</strong><br>Select the documented "
                    "levels from Province down to Village. Leave lower levels blank if they "
                    "are not documented."
                ),
            },
            {
                "type": "dropdown",
                "name": "province_id",
                "title": "Province",
                "isRequired": True,
                "visibleIf": "{residence_documented} = 'Yes'",
            },
            {
                "type": "dropdown",
                "name": "district_id",
                "title": "District",
                "visibleIf": "{residence_documented} = 'Yes'",
                "enableIf": "{province_id} notempty",
            },
            {
                "type": "dropdown",
                "name": "sector_id",
                "title": "Sector",
                "visibleIf": "{residence_documented} = 'Yes'",
                "enableIf": "{district_id} notempty",
            },
            {
                "type": "dropdown",
                "name": "cell_id",
                "title": "Cell",
                "visibleIf": "{residence_documented} = 'Yes'",
                "enableIf": "{sector_id} notempty",
            },
            {
                "type": "dropdown",
                "name": "village_id",
                "title": "Village",
                "visibleIf": "{residence_documented} = 'Yes'",
                "enableIf": "{cell_id} notempty",
            },
            {
                "type": "dropdown",
                "name": "health_insurance_category",
                "title": "Health insurance category",
                "isRequired": True,
                "choices": INSURANCE_CATEGORIES,
            },
            other_text(
                "health_insurance_other",
                "Other health insurance — please specify",
                "{health_insurance_category} = 'Other'",
            ),
            {
                "type": "dropdown",
                "name": "occupation",
                "title": "Occupation",
                "isRequired": True,
                "choices": [
                    "Student",
                    "Non-skilled worker",
                    "Professional and managerial",
                    "Housewife / houseman",
                    "Farmer",
                    "Livestock keeper",
                    "Butcher",
                    "Veterinarian",
                    "Other",
                    NOT_DOCUMENTED,
                ],
            },
            other_text(
                "occupation_other",
                "Other occupation — please specify",
                "{occupation} = 'Other'",
            ),
            {
                "type": "dropdown",
                "name": "education_level",
                "title": "Education level",
                "isRequired": True,
                "choices": [
                    "No formal education",
                    "Primary",
                    "Secondary",
                    "TVET",
                    "University",
                    NOT_DOCUMENTED,
                ],
            },
            {
                "type": "dropdown",
                "name": "ubudehe_category",
                "title": "Socioeconomic / Ubudehe category",
                "isRequired": True,
                "choices": [
                    "Category 1",
                    "Category 2",
                    "Category 3",
                    "Category 4",
                    NOT_DOCUMENTED,
                ],
            },
        ],
    }


def prescription_page() -> dict:
    with_prescription = "{prescription_documented} = 'Yes'"
    return {
        "name": "prescription_encounter",
        "title": "C. Prescription and Pharmacy Encounter",
        "elements": [
            {
                "type": "radiogroup",
                "name": "prescription_documented",
                "title": (
                    "C1. Is there documentation of a prescription presented or received for "
                    "this dispensing encounter?"
                ),
                "isRequired": True,
                "choices": YN_UNK,
            },
            {
                "type": "panel",
                "name": "prescription_details",
                "title": "Prescription details (record where available)",
                "visibleIf": with_prescription,
                "elements": [
                    {
                        "type": "text",
                        "name": "prescription_date",
                        "title": "Prescription date",
                        "inputType": "date",
                        "maxValueExpression": "today()",
                    },
                    {
                        "type": "dropdown",
                        "name": "prescriber_category",
                        "title": "Prescribing healthcare professional category",
                        "choices": PRESCRIBER_CATEGORIES,
                    },
                    other_text(
                        "prescriber_category_other",
                        "Other prescriber category — please specify",
                        "{prescriber_category} = 'Other'",
                    ),
                    {
                        "type": "text",
                        "name": "prescribing_facility",
                        "title": "Prescribing healthcare facility",
                    },
                    {
                        "type": "text",
                        "name": "prescription_reference",
                        "title": "Prescription reference",
                    },
                    {
                        "type": "comment",
                        "name": "prescription_indication_text",
                        "title": "Clinical indication / diagnosis as written on the prescription",
                    },
                ],
            },
            {
                "type": "comment",
                "name": "encounter_reason_documented",
                "title": "Documented reason for the pharmacy encounter, where available",
                "description": "Record as written. Leave blank if no reason is documented.",
                "visibleIf": "{prescription_documented} = 'No'",
            },
            {
                "type": "radiogroup",
                "name": "antimicrobial_dispensed",
                "title": "C2. Was at least one antimicrobial dispensed?",
                "isRequired": True,
                "choices": YN_UNK,
            },
        ],
    }


def dispensing_page() -> dict:
    return {
        "name": "dispensing_details",
        "title": "D. Antimicrobial Dispensing Details",
        "description": (
            "Record each antimicrobial dispensed separately. Leave optional fields blank "
            "when they are not documented."
        ),
        "visibleIf": "{antimicrobial_dispensed} = 'Yes'",
        "elements": [
            {
                "type": "paneldynamic",
                "name": "antimicrobial_dispensing",
                "title": "Antimicrobials dispensed during this encounter",
                "isRequired": True,
                "panelCount": 1,
                "minPanelCount": 1,
                "panelAddText": "Add antimicrobial",
                "panelRemoveText": "Remove antimicrobial",
                "templateTitle": "Antimicrobial #{panelIndex}",
                "templateElements": [
                    {
                        "type": "expression",
                        "name": "antimicrobial_dispensing_id",
                        "title": "Antimicrobial_Dispensing_ID",
                        "expression": "{study_record_id} + '-AM' + ({panelIndex} + 1)",
                    },
                    {
                        "type": "text",
                        "name": "documented_name",
                        "title": "Antimicrobial name as documented",
                        "isRequired": True,
                    },
                    antimicrobial_dropdown(
                        "standardized_name",
                        "Standardized antimicrobial name (searchable dictionary)",
                        required=True,
                    ),
                    other_text(
                        "standardized_name_other",
                        "Antimicrobial not in the list — please specify",
                        f"{{panel.standardized_name}} = '{NOT_FOUND}'",
                    ),
                    {
                        "type": "text",
                        "name": "strength",
                        "title": "Strength",
                        "placeholder": "Example: 500 mg",
                    },
                    {
                        "type": "dropdown",
                        "name": "formulation",
                        "title": "Pharmaceutical formulation",
                        "choices": FORMULATIONS,
                    },
                    other_text(
                        "formulation_other",
                        "Other formulation — please specify",
                        "{panel.formulation} = 'Other'",
                    ),
                    {
                        "type": "text",
                        "name": "dose",
                        "title": "Dose, if documented",
                        "placeholder": "Example: 1 tablet",
                    },
                    {
                        "type": "text",
                        "name": "frequency",
                        "title": "Frequency, if documented",
                        "placeholder": "Example: 3 times daily",
                    },
                    {
                        "type": "dropdown",
                        "name": "route",
                        "title": "Route of administration",
                        "choices": ROUTES,
                    },
                    other_text(
                        "route_other",
                        "Other route — please specify",
                        "{panel.route} = 'Other'",
                    ),
                    {
                        "type": "text",
                        "name": "quantity_dispensed",
                        "title": "Quantity dispensed",
                        "placeholder": "Example: 21 tablets",
                    },
                    {
                        "type": "text",
                        "name": "duration_days",
                        "title": "Prescribed duration in days, if documented",
                        "inputType": "number",
                        "validators": [{"type": "numeric", "minValue": 0, "maxValue": 365}],
                    },
                    {
                        "type": "text",
                        "name": "item_dispensing_date",
                        "title": "Dispensing date",
                        "inputType": "date",
                        "defaultValueExpression": "{dispensing_date}",
                        "min": EXTRACTION_PERIOD_START,
                        "maxValueExpression": "today()",
                    },
                    {
                        "type": "radiogroup",
                        "name": "prescription_status",
                        "title": "Prescription status for this antimicrobial",
                        "isRequired": True,
                        "choices": [
                            "Prescription documented",
                            "No prescription documented",
                            "Unknown",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "indication_documented",
                        "title": "Indication or clinical condition as documented",
                        "description": "Leave blank if not documented. Do not infer.",
                    },
                    {
                        "type": "dropdown",
                        "name": "indication_standardized",
                        "title": "Standardized clinical condition (ICD-11 dictionary)",
                        "searchEnabled": True,
                        "visibleIf": "{panel.indication_documented} notempty",
                        "choices": load_indications(),
                    },
                    other_text(
                        "indication_standardized_other",
                        "Other clinical condition — please specify",
                        "{panel.indication_standardized} = 'IND_OTHER'",
                    ),
                    {
                        "type": "dropdown",
                        "name": "payment_method",
                        "title": "Payment / insurance coverage",
                        "choices": PAYMENT_METHODS,
                    },
                    {
                        "type": "text",
                        "name": "amount_paid_rwf",
                        "title": "Amount paid by the patient (RWF), if routinely recorded",
                        "inputType": "number",
                        "visibleIf": (
                            "{panel.payment_method} anyof "
                            "['Partially covered by insurance', 'Out-of-pocket (no insurance)']"
                        ),
                        "validators": [{"type": "numeric", "minValue": 0}],
                    },
                    {
                        "type": "checkbox",
                        "name": "dispensing_issues",
                        "title": (
                            "Documented partial dispensing, substitution or unavailability"
                        ),
                        "choices": DISPENSING_ISSUES,
                        "showNoneItem": True,
                        "noneText": "None documented",
                    },
                    {
                        "type": "comment",
                        "name": "dispensing_issues_details",
                        "title": "Details as documented",
                        "visibleIf": (
                            "{panel.dispensing_issues} anyof "
                            f"{json.dumps(DISPENSING_ISSUES, ensure_ascii=False)}"
                        ),
                    },
                ],
            },
        ],
    }


def other_medications_page() -> dict:
    return {
        "name": "other_medications",
        "title": "E. Other Medications",
        "elements": [
            {
                "type": "radiogroup",
                "name": "other_medications_documented",
                "title": (
                    "E1. Were other non-antimicrobial medications prescribed or dispensed "
                    "during this encounter?"
                ),
                "isRequired": True,
                "choices": YN_UNK,
            },
            {
                "type": "html",
                "name": "other_medications_note",
                "visibleIf": "{other_medications_documented} = 'Yes'",
                "html": (
                    "<small>Do not assume that every prescribed medication was dispensed. "
                    "Record the documented status of each medication.</small>"
                ),
            },
            {
                "type": "paneldynamic",
                "name": "other_medications",
                "title": "Other medications",
                "visibleIf": "{other_medications_documented} = 'Yes'",
                "isRequired": True,
                "panelCount": 1,
                "minPanelCount": 1,
                "panelAddText": "Add medication",
                "panelRemoveText": "Remove medication",
                "templateTitle": "Medication #{panelIndex}",
                "templateElements": [
                    {
                        "type": "text",
                        "name": "medication_name",
                        "title": "Medication name as documented",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "medication_status",
                        "title": "Prescribed or dispensed status",
                        "isRequired": True,
                        "choices": OTHER_MEDICATION_STATUS,
                    },
                    {
                        "type": "text",
                        "name": "medication_quantity",
                        "title": "Quantity, where documented",
                    },
                    {
                        "type": "text",
                        "name": "medication_dose",
                        "title": "Dose, where documented",
                    },
                ],
            },
        ],
    }


def previous_use_page() -> dict:
    return {
        "name": "previous_use",
        "title": "F. Previous Antimicrobial Use",
        "elements": [
            {
                "type": "radiogroup",
                "name": "previous_antimicrobial_use",
                "title": (
                    "F1. Is there documentation that the patient used or obtained another "
                    "antimicrobial within the 30 days preceding this pharmacy encounter?"
                ),
                "isRequired": True,
                "choices": YN_UNK,
            },
            {
                "type": "html",
                "name": "previous_use_note",
                "visibleIf": "{previous_antimicrobial_use} = 'Yes'",
                "html": (
                    "<small>Do not count the antimicrobial dispensed during the current "
                    "encounter as previous use.</small>"
                ),
            },
            {
                "type": "paneldynamic",
                "name": "previous_antimicrobials",
                "title": "Previous antimicrobials (within 30 days before this encounter)",
                "visibleIf": "{previous_antimicrobial_use} = 'Yes'",
                "isRequired": True,
                "panelCount": 1,
                "minPanelCount": 1,
                "panelAddText": "Add previous antimicrobial",
                "panelRemoveText": "Remove",
                "templateTitle": "Previous antimicrobial #{panelIndex}",
                "templateElements": [
                    {
                        "type": "text",
                        "name": "documented_name",
                        "title": "Antimicrobial name as documented",
                        "isRequired": True,
                    },
                    antimicrobial_dropdown(
                        "standardized_name",
                        "Standardized antimicrobial name (searchable dictionary)",
                        required=False,
                    ),
                    other_text(
                        "standardized_name_other",
                        "Antimicrobial not in the list — please specify",
                        f"{{panel.standardized_name}} = '{NOT_FOUND}'",
                    ),
                    {
                        "type": "text",
                        "name": "approximate_date",
                        "title": "Approximate date of use or acquisition",
                        "inputType": "date",
                        "maxValueExpression": "{dispensing_date}",
                    },
                    {
                        "type": "dropdown",
                        "name": "source",
                        "title": "Source",
                        "choices": PREVIOUS_USE_SOURCES,
                    },
                    other_text(
                        "source_other",
                        "Other source — please specify",
                        "{panel.source} = 'Other'",
                    ),
                    {
                        "type": "radiogroup",
                        "name": "evidence_type",
                        "title": "Type of documentation",
                        "choices": PREVIOUS_USE_EVIDENCE,
                    },
                    {
                        "type": "text",
                        "name": "indication_documented",
                        "title": "Indication, where documented",
                    },
                ],
            },
        ],
    }


def data_quality_page() -> dict:
    incomplete = (
        "{record_completeness} notempty and "
        f"{{record_completeness}} != '{COMPLETE_RECORD}'"
    )
    return {
        "name": "data_quality",
        "title": "G. Data Quality and Completion",
        "elements": [
            {
                "type": "text",
                "name": "data_collector_id",
                "title": "Data collector ID",
                "isRequired": True,
            },
            {
                "type": "text",
                "name": "extraction_date",
                "title": "Extraction date",
                "inputType": "date",
                "isRequired": True,
                "defaultValueExpression": "today()",
                "maxValueExpression": "today()",
            },
            {
                "type": "expression",
                "name": "source_record_reference_summary",
                "title": "Source record reference (from Section A)",
                "expression": "iif({pharmacy_source_record_reference} notempty, "
                "{pharmacy_source_record_reference}, 'Not recorded')",
            },
            {
                "type": "radiogroup",
                "name": "record_completeness",
                "title": "Record completeness status",
                "isRequired": True,
                "choices": [
                    COMPLETE_RECORD,
                    "Partially complete — some variables not documented",
                    "Minimal — most variables not documented",
                ],
            },
            {
                "type": "checkbox",
                "name": "missing_information_sections",
                "title": "Which information was missing from the source record?",
                "visibleIf": incomplete,
                "isRequired": True,
                "choices": [
                    "Patient demographics",
                    "Prescription details",
                    "Antimicrobial dispensing details",
                    "Other medications",
                    "Previous antimicrobial use",
                    "Other",
                ],
            },
            {
                "type": "comment",
                "name": "missing_information_details",
                "title": "Details of missing information",
                "visibleIf": incomplete,
            },
            {
                "type": "radiogroup",
                "name": "duplicate_check",
                "title": "Duplicate-record check against previously extracted records",
                "isRequired": True,
                "choices": [
                    "Checked — no duplicate found",
                    "Checked — possible duplicate",
                    "Not checked",
                ],
            },
            other_text(
                "duplicate_study_record_id",
                "Study record ID of the possible duplicate",
                "{duplicate_check} = 'Checked — possible duplicate'",
            ),
            {
                "type": "radiogroup",
                "name": "validation_status",
                "title": "Validation status",
                "isRequired": True,
                "defaultValue": "Not yet validated",
                "choices": [
                    "Not yet validated",
                    "Validated",
                    "Queried — correction needed",
                ],
            },
            other_text(
                "validated_by",
                "Validated by (ID)",
                "{validation_status} = 'Validated'",
            ),
            {
                "type": "comment",
                "name": "validation_query",
                "title": "Describe the query or correction needed",
                "isRequired": True,
                "visibleIf": "{validation_status} = 'Queried — correction needed'",
            },
        ],
    }


def build_survey() -> dict:
    return {
        "title": TITLE,
        "description": DESCRIPTION,
        "showProgressBar": "top",
        "progressBarType": "pages",
        "completedHtml": (
            "<h3>Thank you.</h3><p>The pharmacy data extraction form has been submitted.</p>"
        ),
        "pages": [
            data_source_page(),
            demographics_page(),
            prescription_page(),
            dispensing_page(),
            other_medications_page(),
            previous_use_page(),
            data_quality_page(),
        ],
        "showPreviewBeforeComplete": "showAllQuestions",
        "previewText": "Review Answers",
        "editText": "Edit",
        "completeText": "Submit",
    }


def main() -> None:
    survey = build_survey()
    OUTPUT.write_text(
        json.dumps(survey, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
