#!/usr/bin/env python3
"""Rebuild AMS medical-record extraction survey per NOW 23/09/2026 review."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "database" / "samples" / "antimicrobial_stewardship_data_collection_survey.json"
AMR_CSV = ROOT / "database" / "dictionaries" / "who_antimicrobial_dictionary.csv"
ICD_CSV = ROOT / "database" / "dictionaries" / "who_icd11_clinical_conditions.csv"
PATH_CSV = ROOT / "database" / "dictionaries" / "pathogen_dictionary.csv"
FAC_CSV = ROOT / "database" / "locations" / "health_facilities.csv"

DOC_YN = ["Yes", "No / Not documented"]
YN_UNK = ["Yes", "No", "Not documented / Unknown"]

CLINICAL_INDICATIONS = [
    "Suspected bloodstream infection/sepsis",
    "Suspected urinary tract infection",
    "Suspected respiratory tract infection",
    "Suspected gastrointestinal infection",
    "Suspected skin / soft-tissue infection",
    "Suspected surgical-site infection",
    "Suspected central nervous system infection",
    "Suspected sexually transmitted / genital tract infection",
    "Suspected bone / joint infection",
    "Other suspected infection — specify",
    "Laboratory-confirmed infection",
    "Surgical/procedural prophylaxis",
    "Other non-treatment indication — specify",
    "Indication not documented / cannot be determined",
]


def load_facilities() -> list[dict]:
    choices = []
    with FAC_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            code = (row.get("facility_code") or "").strip()
            name = (row.get("name") or "").strip()
            district = (row.get("district_name") or "").strip()
            ftype = (row.get("facility_type") or "").strip()
            level = (row.get("facility_level") or "").strip()
            if not code:
                continue
            text = f"{code} — {name} ({district}, {ftype} {level})".strip()
            choices.append({"value": code, "text": text})
    return choices


def load_antimicrobials() -> list[dict]:
    choices = []
    with AMR_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("antimicrobial_name_standardized") or "").strip()
            if not name:
                continue
            atc = (row.get("atc_code") or "").strip()
            aware = (row.get("aware_category") or "").strip()
            extras = [x for x in (atc, f"AWaRe: {aware}" if aware else "") if x]
            text = f"{name} ({', '.join(extras)})" if extras else name
            choices.append({"value": name, "text": text})
    choices.append(
        {
            "value": "Antimicrobial not found in standardised list",
            "text": "Antimicrobial not found in standardised list",
        }
    )
    return choices


def load_indications() -> list[dict]:
    choices = []
    with ICD_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            cid = (row.get("condition_id") or "").strip()
            name = (row.get("condition_name_standardized") or "").strip()
            domain = (row.get("clinical_domain") or "").strip()
            if not cid or not name:
                continue
            text = f"{domain}: {name}" if domain else name
            choices.append({"value": cid, "text": text})
    choices.append({"value": "IND_OTHER", "text": "Other infection/clinical indication — specify"})
    return choices


def load_pathogens() -> list[dict]:
    choices = []
    with PATH_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            pid = (row.get("pathogen_id") or "").strip()
            name = (row.get("pathogen_name_standardized") or "").strip()
            if not pid or not name:
                continue
            choices.append({"value": pid, "text": name})
    return choices


def vitals_block() -> list[dict]:
    return [
        {
            "type": "radiogroup",
            "name": "bp_documented",
            "title": "Was blood pressure documented in the patient's medical record for this clinical episode?",
            "isRequired": True,
            "choices": DOC_YN,
        },
        {
            "type": "text",
            "name": "systolic_bp_mmhg",
            "title": "Systolic blood pressure (SBP) — mmHg",
            "inputType": "number",
            "isRequired": True,
            "visibleIf": "{bp_documented} = 'Yes'",
            "validators": [{"type": "numeric", "minValue": 40, "maxValue": 300}],
        },
        {
            "type": "text",
            "name": "diastolic_bp_mmhg",
            "title": "Diastolic blood pressure (DBP) — mmHg",
            "inputType": "number",
            "isRequired": True,
            "visibleIf": "{bp_documented} = 'Yes'",
            "validators": [{"type": "numeric", "minValue": 20, "maxValue": 200}],
        },
        {
            "type": "radiogroup",
            "name": "temperature_documented",
            "title": "Was body temperature documented in the patient's medical record for this clinical episode?",
            "isRequired": True,
            "choices": DOC_YN,
        },
        {
            "type": "text",
            "name": "body_temperature_c",
            "title": "Body temperature — °C",
            "inputType": "number",
            "isRequired": True,
            "visibleIf": "{temperature_documented} = 'Yes'",
            "validators": [{"type": "numeric", "minValue": 30, "maxValue": 45}],
        },
        {
            "type": "radiogroup",
            "name": "pulse_documented",
            "title": "Was pulse rate documented in the patient's medical record for this clinical episode?",
            "isRequired": True,
            "choices": DOC_YN,
        },
        {
            "type": "text",
            "name": "pulse_rate_bpm",
            "title": "Pulse rate — beats per minute (bpm)",
            "inputType": "number",
            "isRequired": True,
            "visibleIf": "{pulse_documented} = 'Yes'",
            "validators": [{"type": "numeric", "minValue": 20, "maxValue": 300}],
        },
        {
            "type": "radiogroup",
            "name": "respiratory_rate_documented",
            "title": "Was respiratory rate documented in the patient's medical record for this clinical episode?",
            "isRequired": True,
            "choices": DOC_YN,
        },
        {
            "type": "text",
            "name": "respiratory_rate_bpm",
            "title": "Respiratory rate — breaths per minute",
            "inputType": "number",
            "isRequired": True,
            "visibleIf": "{respiratory_rate_documented} = 'Yes'",
            "validators": [{"type": "numeric", "minValue": 5, "maxValue": 80}],
        },
    ]


def prior_antibiotic_panel(amr: list[dict]) -> list[dict]:
    return [
        {
            "type": "radiogroup",
            "name": "antibiotic_use_prior_30_days",
            "title": (
                "Is there documentation that the patient used any antibiotic within the 30 days "
                "before this clinical episode?"
            ),
            "isRequired": True,
            "choices": YN_UNK,
        },
        {
            "type": "text",
            "name": "prior_antibiotic_course_count",
            "title": "How many different antibiotic courses or antibiotic records are documented?",
            "inputType": "number",
            "isRequired": True,
            "visibleIf": "{antibiotic_use_prior_30_days} = 'Yes'",
            "validators": [{"type": "numeric", "minValue": 1, "maxValue": 20}],
        },
        {
            "type": "paneldynamic",
            "name": "prior_antibiotic_records",
            "title": "Prior antibiotic records (add each antibiotic separately)",
            "visibleIf": "{antibiotic_use_prior_30_days} = 'Yes'",
            "isRequired": True,
            "panelCount": 1,
            "minPanelCount": 1,
            "panelAddText": "Add another antibiotic",
            "panelRemoveText": "Remove antibiotic",
            "templateElements": [
                {
                    "type": "dropdown",
                    "name": "antibiotic_name",
                    "title": "Antibiotic name (searchable standardised list)",
                    "isRequired": True,
                    "searchEnabled": True,
                    "choices": amr,
                },
                {
                    "type": "text",
                    "name": "antibiotic_name_other",
                    "title": "If not found / other, write name as documented",
                    "visibleIf": "{panel.antibiotic_name} = 'Antimicrobial not found in standardised list'",
                    "isRequired": True,
                },
                {
                    "type": "text",
                    "name": "date_started",
                    "title": "Date started / approximate date (if documented)",
                    "inputType": "date",
                },
                {
                    "type": "text",
                    "name": "indication_reason",
                    "title": "Indication / reason for use (if documented)",
                },
                {"type": "text", "name": "dose", "title": "Dose (if documented)"},
                {"type": "text", "name": "frequency", "title": "Frequency (if documented)"},
                {
                    "type": "dropdown",
                    "name": "route",
                    "title": "Route of administration (if documented)",
                    "choices": ["Oral", "Intravenous", "Intramuscular", "Topical", "Other", "Not documented"],
                },
                {"type": "text", "name": "duration", "title": "Duration (if documented)"},
                {
                    "type": "text",
                    "name": "source_prescriber",
                    "title": "Source / prescriber (if documented)",
                },
                {
                    "type": "radiogroup",
                    "name": "course_completed",
                    "title": "Course completed",
                    "choices": ["Yes", "No", "Not documented"],
                },
                {"type": "comment", "name": "additional_notes", "title": "Additional notes (optional)"},
            ],
        },
    ]


def prior_hospitalization_panel(amr: list[dict]) -> list[dict]:
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
            "type": "text",
            "name": "prior_hospitalization_count",
            "title": "How many hospitalizations are documented within 12 months?",
            "description": 'If the exact number is not documented, enter 0 and note "Unknown" in additional notes of a panel, or use Unknown option below.',
            "inputType": "number",
            "visibleIf": "{previous_hospitalization_past_year} = 'Yes'",
            "validators": [{"type": "numeric", "minValue": 0, "maxValue": 20}],
        },
        {
            "type": "radiogroup",
            "name": "prior_hospitalization_count_unknown",
            "title": "Is the exact number of hospitalizations unknown?",
            "visibleIf": "{previous_hospitalization_past_year} = 'Yes'",
            "choices": ["No — number entered above", "Unknown"],
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
                {
                    "type": "text",
                    "name": "health_facility",
                    "title": "Health facility (if documented)",
                },
                {
                    "type": "comment",
                    "name": "reason_diagnosis",
                    "title": "Reason for hospitalization / diagnosis (if documented)",
                },
                {
                    "type": "text",
                    "name": "duration",
                    "title": "Duration of hospitalization (if documented)",
                },
                {
                    "type": "radiogroup",
                    "name": "antibiotics_during_hosp",
                    "title": "Antibiotics received during hospitalization",
                    "choices": ["Yes", "No", "Not documented"],
                },
                {
                    "type": "paneldynamic",
                    "name": "hospitalization_antibiotics",
                    "title": "Antibiotic exposures during this hospitalization (if documented)",
                    "visibleIf": "{panel.antibiotics_during_hosp} = 'Yes'",
                    "minPanelCount": 0,
                    "panelAddText": "Add antibiotic",
                    "templateElements": [
                        {
                            "type": "dropdown",
                            "name": "antibiotic_name",
                            "title": "Antibiotic name",
                            "searchEnabled": True,
                            "choices": amr,
                        },
                        {"type": "text", "name": "dose", "title": "Dose (if documented)"},
                        {"type": "text", "name": "duration", "title": "Duration (if documented)"},
                    ],
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


def prescription_page(amr: list[dict], indications: list[dict]) -> dict:
    return {
        "name": "antimicrobial_prescription",
        "title": "C. Antimicrobial Prescription Data",
        "description": "Was an antimicrobial prescribed for this clinical episode? Add each prescription separately.",
        "elements": [
            {
                "type": "radiogroup",
                "name": "antimicrobial_prescribed",
                "title": "Was an antimicrobial prescribed for this clinical episode?",
                "isRequired": True,
                "choices": YN_UNK,
            },
            {
                "type": "paneldynamic",
                "name": "antimicrobial_prescriptions",
                "title": "Antimicrobial prescriptions",
                "visibleIf": "{antimicrobial_prescribed} = 'Yes'",
                "isRequired": True,
                "panelCount": 1,
                "minPanelCount": 1,
                "panelAddText": "Add antimicrobial",
                "panelRemoveText": "Remove antimicrobial",
                "templateElements": [
                    {
                        "type": "text",
                        "name": "documented_name",
                        "title": "Antimicrobial name as documented in the medical record",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "standardized_name",
                        "title": "Standardized antimicrobial name (searchable WHO list)",
                        "isRequired": True,
                        "searchEnabled": True,
                        "choices": amr,
                    },
                    {
                        "type": "html",
                        "name": "aware_note",
                        "html": (
                            "<small>ATC code, antimicrobial class and WHO AWaRe category are linked "
                            "from the standardised name in analysis (WHO AWaRe 2019 dictionary).</small>"
                        ),
                    },
                    {
                        "type": "dropdown",
                        "name": "clinical_indication",
                        "title": "Clinical indication for this antimicrobial",
                        "isRequired": True,
                        "choices": CLINICAL_INDICATIONS,
                    },
                    {
                        "type": "text",
                        "name": "clinical_indication_other",
                        "title": "Specify other indication",
                        "visibleIf": (
                            "{panel.clinical_indication} anyof "
                            "['Other suspected infection — specify', 'Other non-treatment indication — specify']"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "indication_standardized",
                        "title": "Standardized clinical condition / indication (ICD-11 dictionary)",
                        "searchEnabled": True,
                        "choices": indications,
                    },
                    {
                        "type": "radiogroup",
                        "name": "indication_status",
                        "title": "What was the basis/status of the indication?",
                        "choices": [
                            "Suspected",
                            "Clinically diagnosed",
                            "Laboratory confirmed",
                            "Not documented",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "prescribing_purpose",
                        "title": "Prescribing purpose",
                        "choices": ["Treatment", "Prophylaxis", "Not documented"],
                    },
                    {
                        "type": "text",
                        "name": "documented_diagnosis_text",
                        "title": "Documented diagnosis text (as written in the record)",
                        "placeholder": 'Example: "Complicated UTI"',
                    },
                    {
                        "type": "text",
                        "name": "dose",
                        "title": "Dose",
                        "placeholder": "Example: 500 mg",
                    },
                    {
                        "type": "dropdown",
                        "name": "route",
                        "title": "Route of administration",
                        "choices": ["Oral", "Intravenous", "Intramuscular", "Topical", "Other", "Not documented"],
                    },
                    {"type": "text", "name": "frequency", "title": "Frequency"},
                    {
                        "type": "text",
                        "name": "duration_days",
                        "title": "Duration (days)",
                        "inputType": "number",
                    },
                    {
                        "type": "dropdown",
                        "name": "prescriber_cadre",
                        "title": "Prescriber cadre",
                        "choices": [
                            "Physician",
                            "Medical specialist",
                            "Clinical officer",
                            "Nurse",
                            "Pharmacist",
                            "Other",
                            "Not documented",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "prescription_date",
                        "title": "Prescription date",
                        "inputType": "date",
                    },
                    {
                        "type": "text",
                        "name": "dispensing_date",
                        "title": "Dispensing date",
                        "inputType": "date",
                    },
                ],
            },
        ],
    }


def replace_clinical_encounter(page: dict, facilities: list[dict], amr: list[dict]) -> None:
    elements = page.get("elements", [])
    new_elements: list[dict] = []
    skip_until_after_vitals = False
    i = 0
    while i < len(elements):
        el = elements[i]
        name = el.get("name")

        if name == "facility_id":
            # Replace facility_id, facility_name, type, level with coded facility
            new_elements.append(
                {
                    "type": "dropdown",
                    "name": "facility_code",
                    "title": "Study health facility (select from approved list)",
                    "isRequired": True,
                    "searchEnabled": True,
                    "choices": facilities,
                }
            )
            # skip old facility_id, facility_name, facility_type, facility_level
            while i < len(elements) and elements[i].get("name") in {
                "facility_id",
                "facility_name",
                "facility_type",
                "facility_level",
            }:
                i += 1
            continue

        if name == "vital_signs":
            new_elements.extend(vitals_block())
            i += 1
            continue

        if name == "antibiotic_use_prior_30_days":
            new_elements.extend(prior_antibiotic_panel(amr))
            # skip previous_antibiotics free text too
            i += 1
            if i < len(elements) and elements[i].get("name") == "previous_antibiotics":
                i += 1
            continue

        if name == "previous_antibiotics":
            i += 1
            continue

        if name == "previous_hospitalization_past_year":
            new_elements.extend(prior_hospitalization_panel(amr))
            i += 1
            continue

        new_elements.append(el)
        i += 1

    page["elements"] = new_elements


def update_lab_page(page: dict, amr: list[dict], pathogens: list[dict]) -> None:
    for el in page.get("elements", []):
        if el.get("name") != "microbiology_results":
            continue
        el["templateElements"] = [
            {
                "type": "dropdown",
                "name": "specimen_type",
                "title": "Specimen type",
                "choices": ["Blood", "Urine", "Sputum", "Wound swab", "Stool", "CSF", "Other"],
            },
            {
                "type": "text",
                "name": "sample_collection_date",
                "title": "Sample collection date",
                "inputType": "date",
            },
            {
                "type": "dropdown",
                "name": "organism_identified",
                "title": "Organism identified (searchable standardised pathogen list)",
                "searchEnabled": True,
                "choices": pathogens,
            },
            {
                "type": "text",
                "name": "organism_other",
                "title": "If Other pathogen, specify",
                "visibleIf": "{panel.organism_identified} = 'PATH_024'",
            },
            {
                "type": "matrixdynamic",
                "name": "ast_results",
                "title": "AST results (add each antibiotic tested)",
                "addRowText": "Add antibiotic tested",
                "columns": [
                    {
                        "name": "antibiotic_tested",
                        "title": "Antibiotic tested (standardised)",
                        "cellType": "dropdown",
                        "choices": amr,
                    },
                    {
                        "name": "interpretation",
                        "title": "Result",
                        "cellType": "dropdown",
                        "choices": ["Susceptible", "Intermediate", "Resistant", "Not tested"],
                    },
                    {"name": "mic", "title": "MIC", "cellType": "text"},
                ],
            },
        ]


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    facilities = load_facilities()
    amr = load_antimicrobials()
    indications = load_indications()
    pathogens = load_pathogens()

    data["title"] = "Retrospective Patient Medical Record Extraction Form (2020–Present)"
    data["description"] = (
        "Patient-Specific Medical Record Data Extraction Form: Antimicrobial Use, Clinical "
        "Characteristics and Antimicrobial Resistance in Rwandan Healthcare Facilities "
        "(2020–Date of Data Collection). Form version AMS-MR-EXTRACTION-v2.0 "
        "(NOW 23/09/2026 reviewer revisions)."
    )
    data["showPreviewBeforeComplete"] = "showAllQuestions"
    data["previewText"] = "Review Answers"
    data["editText"] = "Edit"
    data["completeText"] = "Submit"
    data["completedHtml"] = (
        "<h3>Thank you.</h3><p>The retrospective medical record extraction form has been submitted.</p>"
    )

    for page in data["pages"]:
        if page.get("name") == "patient_demographics":
            for el in page.get("elements", []):
                if el.get("name") == "district_id":
                    el["enableIf"] = "{province_id} notempty"
                if el.get("name") == "sector_id":
                    el["enableIf"] = "{district_id} notempty"
                if el.get("name") == "cell_id":
                    el["enableIf"] = "{sector_id} notempty"
                if el.get("name") == "village_id":
                    el["enableIf"] = "{cell_id} notempty"
                if el.get("name") == "health_insurance_category":
                    el["choices"] = [
                        "Mutuelle de Sante (CBHI)",
                        "RSSB",
                        "MMI",
                        "Private insurance",
                        "No insurance",
                        "Other",
                    ]

        if page.get("name") == "clinical_encounter":
            replace_clinical_encounter(page, facilities, amr)

        if page.get("name") == "antimicrobial_prescription":
            page.clear()
            page.update(prescription_page(amr, indications))

        if page.get("name") == "laboratory_data":
            update_lab_page(page, amr, pathogens)

    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {PATH}")
    print(f"Facilities: {len(facilities)}, Antimicrobials: {len(amr)}, Indications: {len(indications)}, Pathogens: {len(pathogens)}")
    for p in data["pages"]:
        print(f"  {p['name']}: {len(p.get('elements', []))} elements")


if __name__ == "__main__":
    main()
