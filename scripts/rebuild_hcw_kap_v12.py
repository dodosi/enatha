#!/usr/bin/env python3
"""Rebuild HCW KAP Practice section to HCW-KAP-v1.2 per reviewer Word notes."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "database" / "samples" / "hcw_kap_survey.json"
AMR_CSV = ROOT / "database" / "dictionaries" / "who_antimicrobial_dictionary.csv"
ICD_CSV = ROOT / "database" / "dictionaries" / "who_icd11_clinical_conditions.csv"

FREQ5 = ["Never", "Rarely", "Sometimes", "Often", "Always"]
FREQ_EMPIRIC = ["Rarely", "Sometimes", "Often", "Very often", "Almost always"]
VOLUME = ["Less than 5", "5-10", "11-20", "21-30", "31-40", "More than 40"]


def load_antimicrobials() -> list[dict]:
    choices = []
    with AMR_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("antimicrobial_name_standardized") or "").strip()
            if not name:
                continue
            atc = (row.get("atc_code") or "").strip()
            aware = (row.get("aware_category") or "").strip()
            label = name
            extras = []
            if atc:
                extras.append(atc)
            if aware:
                extras.append(f"AWaRe: {aware}")
            if extras:
                label = f"{name} ({', '.join(extras)})"
            choices.append({"value": name, "text": label})
    choices.append({"value": "Other antibiotic", "text": "Other antibiotic — specify"})
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
    # Reviewer category-style options also useful as fallbacks
    for value, text in [
        ("IND_URI", "Respiratory: Upper respiratory tract infection"),
        ("IND_LRI", "Respiratory: Lower respiratory tract infection"),
        ("IND_PNEU", "Respiratory: Pneumonia"),
        ("IND_UTI", "Urinary: Urinary tract infection"),
        ("IND_GI", "Gastrointestinal: Gastrointestinal infection / infectious diarrhoeal disease"),
        ("IND_SSTI", "Skin/wound: Skin and soft-tissue infection"),
        ("IND_WOUND", "Skin/wound: Wound infection"),
        ("IND_SSI", "Skin/wound: Surgical-site infection"),
        ("IND_SEPSIS", "Blood/systemic: Suspected bloodstream infection / sepsis"),
        ("IND_STI", "Genital/reproductive: Sexually transmitted infection / genital tract infection"),
        ("IND_CNS", "CNS: Suspected meningitis / central nervous system infection"),
        ("IND_BONE", "Bone/joint: Bone or joint infection"),
        ("IND_DENTAL", "Dental/oral: Dental/oral infection"),
        ("IND_OTHER", "Other infection/clinical indication — specify"),
    ]:
        if not any(c["value"] == value for c in choices):
            choices.append({"value": value, "text": text})
    return choices


def practice_elements(amr_choices: list[dict], indication_choices: list[dict]) -> list[dict]:
    ceftriaxone_choices = [
        {
            "value": "clinical_presentation",
            "text": "Patient's clinical presentation and suspected/confirmed diagnosis",
        },
        {
            "value": "rwanda_stg",
            "text": "Rwanda Standard Treatment Guidelines or other approved clinical guidelines",
        },
        {
            "value": "microbiology_culture",
            "text": "Microbiology/culture results, when available",
        },
        {
            "value": "ast_results",
            "text": "Antimicrobial susceptibility testing (AST) results, when available",
        },
        {
            "value": "local_amr_patterns",
            "text": "Local antimicrobial resistance patterns/antibiogram, when available",
        },
        {
            "value": "previous_antimicrobial_use",
            "text": "Previous antimicrobial use or treatment response",
        },
        {
            "value": "severity",
            "text": "Severity of the patient's clinical condition",
        },
        {
            "value": "patient_factors",
            "text": "Patient-specific factors (e.g., allergy, comorbidities, pregnancy, renal/hepatic considerations)",
        },
        {
            "value": "availability",
            "text": "Availability of ceftriaxone or alternative antimicrobials",
        },
        {
            "value": "cost",
            "text": "Cost/affordability of treatment",
        },
        {
            "value": "clinical_experience",
            "text": "Previous clinical experience",
        },
        {"value": "Other", "text": "Other — specify"},
    ]

    return [
        {
            "type": "radiogroup",
            "name": "pharmacist_prescribing_permit",
            "title": "In addition to your Bachelor of Pharmacy degree, do you possess a permit allowing you to prescribe medicines?",
            "visibleIf": "{profession} = 'Pharmacist'",
            "isRequired": True,
            "choices": ["Yes", "No"],
        },
        {
            "type": "radiogroup",
            "name": "nurse_prescribing_permit",
            "title": "Do you possess a concession permit to prescribe medicines to patients?",
            "visibleIf": "{profession} = 'Nurse'",
            "isRequired": True,
            "choices": ["Yes", "No"],
        },
        {
            "type": "radiogroup",
            "name": "prescribes_antimicrobials",
            "title": "Do you prescribe antimicrobial drugs to your patients?",
            "isRequired": True,
            "choices": ["Yes", "No", "Not applicable"],
        },
        # Q51
        {
            "type": "radiogroup",
            "name": "patients_managed_per_day",
            "title": "On average, approximately how many patients do you personally consult or manage during a typical working day?",
            "visibleIf": "{prescribes_antimicrobials} anyof ['Yes', 'No']",
            "isRequired": True,
            "choices": VOLUME,
        },
        # Q52 volume prescribed
        {
            "type": "radiogroup",
            "name": "patients_prescribed_per_day",
            "title": "Of the patients you consult or manage during a typical working day, approximately how many do you prescribe an antimicrobial for?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": ["None"] + VOLUME,
        },
        # Empirical Q52 restructure
        {
            "type": "radiogroup",
            "name": "empirical_prescribing",
            "title": "Do you prescribe antimicrobials empirically, that is, before laboratory or microbiological confirmation is available?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": ["Yes", "No", "Not applicable"],
        },
        {
            "type": "radiogroup",
            "name": "empirical_prescribing_frequency",
            "title": "How often do you prescribe antimicrobials empirically?",
            "visibleIf": "{empirical_prescribing} = 'Yes'",
            "isRequired": True,
            "choices": FREQ_EMPIRIC,
        },
        {
            "type": "checkbox",
            "name": "empirical_prescribing_reasons",
            "title": "What are the main reasons you prescribe antimicrobials empirically?",
            "visibleIf": "{empirical_prescribing} = 'Yes'",
            "isRequired": True,
            "choices": [
                "Clinical signs and symptoms are considered sufficient to initiate treatment",
                "Laboratory testing is not available",
                "Laboratory testing is available but not readily accessible",
                "Laboratory results take too long to become available",
                "Patient's condition requires treatment before results are available",
                "Previous clinical experience guides treatment",
                "Local/national treatment guidelines support empirical treatment",
                "Cost of laboratory testing to the patient",
                "Patient expectation or request for treatment",
                "High patient workload/time constraints",
                "Other — specify",
            ],
        },
        {
            "type": "text",
            "name": "empirical_prescribing_reasons_other",
            "title": "Specify other reason for empirical prescribing",
            "visibleIf": "{empirical_prescribing_reasons} contains 'Other — specify'",
            "isRequired": True,
        },
        # Q53 microbiology
        {
            "type": "radiogroup",
            "name": "send_microbiology",
            "title": "When microbiological testing is clinically indicated, do you request appropriate specimens for microbiology testing to help inform the need for and/or choice of antimicrobial therapy?",
            "visibleIf": "{prescribes_antimicrobials} anyof ['Yes', 'No']",
            "isRequired": True,
            "choices": ["Yes", "No", "Not applicable to my current practice"],
        },
        {
            "type": "radiogroup",
            "name": "microbiology_request_frequency",
            "title": "How often do you request microbiological testing before initiating antimicrobial therapy when such testing is clinically indicated?",
            "visibleIf": "{send_microbiology} = 'Yes'",
            "isRequired": True,
            "choices": FREQ_EMPIRIC,
        },
        {
            "type": "checkbox",
            "name": "microbiology_barriers",
            "title": "What factors may prevent or limit you from requesting microbiological testing before initiating antimicrobial therapy?",
            "visibleIf": "{send_microbiology} anyof ['Yes', 'No']",
            "isRequired": True,
            "choices": [
                "Microbiology testing is not available at my facility",
                "Appropriate specimen collection is not available/feasible",
                "Laboratory services are not readily accessible",
                "Results take too long to become available",
                "Cost to the patient",
                "Clinical condition requires treatment before results are available",
                "Testing is not considered necessary for the clinical presentation",
                "Previous clinical experience is considered sufficient",
                "Guidelines recommend empirical treatment for the condition",
                "High patient workload/time constraints",
                "Patient declines testing",
                "Other — specify",
                "No major barriers",
            ],
        },
        {
            "type": "text",
            "name": "microbiology_barriers_other",
            "title": "Specify other microbiology barrier",
            "visibleIf": "{microbiology_barriers} contains 'Other — specify'",
            "isRequired": True,
        },
        # Q54 STG
        {
            "type": "radiogroup",
            "name": "has_latest_stg",
            "title": "Do you currently have access to the latest Rwanda Standard Treatment Guidelines (STGs) for use in your clinical practice?",
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure"],
        },
        {
            "type": "checkbox",
            "name": "stg_access_methods",
            "title": "How do you access the Rwanda Standard Treatment Guidelines?",
            "visibleIf": "{has_latest_stg} = 'Yes'",
            "isRequired": True,
            "choices": [
                "Personal printed copy",
                "Shared printed copy at the health facility",
                "Electronic/PDF copy",
                "Online/web-based version",
                "Mobile phone/application",
                "Other — specify",
            ],
        },
        {
            "type": "text",
            "name": "stg_access_methods_other",
            "title": "Specify other STG access method",
            "visibleIf": "{stg_access_methods} contains 'Other — specify'",
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "stg_consult_frequency",
            "title": "How often do you consult the Rwanda Standard Treatment Guidelines when making decisions about antimicrobial treatment?",
            "visibleIf": "{has_latest_stg} = 'Yes'",
            "isRequired": True,
            "choices": FREQ5,
        },
        {
            "type": "radiogroup",
            "name": "stg_no_access_reason",
            "title": "What is the main reason you do not currently have access to the latest Rwanda Standard Treatment Guidelines?",
            "visibleIf": "{has_latest_stg} = 'No'",
            "isRequired": True,
            "choices": [
                "Not available at my facility",
                "I do not have a personal/electronic copy",
                "I am not aware of the latest version",
                "Difficulty accessing the electronic/online version",
                "Other — specify",
            ],
        },
        {
            "type": "text",
            "name": "stg_no_access_reason_other",
            "title": "Specify other reason for no STG access",
            "visibleIf": "{stg_no_access_reason} = 'Other — specify'",
            "isRequired": True,
        },
        # Keep top antimicrobials but as searchable dictionary dropdowns (bridge to Q67)
        {
            "type": "dropdown",
            "name": "top_antimicrobial_1",
            "title": "Antimicrobial you prescribe most (1)",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choicesLazyLoadEnabled": False,
            "choices": amr_choices,
        },
        {
            "type": "dropdown",
            "name": "top_antimicrobial_2",
            "title": "Antimicrobial you prescribe most (2)",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": amr_choices,
        },
        {
            "type": "dropdown",
            "name": "top_antimicrobial_3",
            "title": "Antimicrobial you prescribe most (3)",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": amr_choices,
        },
        {
            "type": "text",
            "name": "top_antimicrobial_other",
            "title": "If you selected Other antibiotic above, please specify",
            "visibleIf": "{top_antimicrobial_1} = 'Other antibiotic' or {top_antimicrobial_2} = 'Other antibiotic' or {top_antimicrobial_3} = 'Other antibiotic'",
        },
        # Q59
        {
            "type": "radiogroup",
            "name": "changed_prescribing_5y",
            "title": "In the past 5 years, have you changed your antimicrobial prescribing practices in response to concerns about antimicrobial resistance (AMR)?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": [
                "Yes",
                "No",
                "Not applicable — I have not been prescribing antimicrobials for the past 5 years",
            ],
        },
        {
            "type": "checkbox",
            "name": "changed_prescribing_how",
            "title": "In what ways have you changed your antimicrobial prescribing practices in response to AMR?",
            "visibleIf": "{changed_prescribing_5y} = 'Yes'",
            "isRequired": True,
            "choices": [
                "I prescribe antimicrobials less frequently",
                "I more carefully assess whether an antimicrobial is necessary before prescribing",
                "I use microbiology/diagnostic testing more often when clinically indicated",
                "I use culture and AST results more often to guide antimicrobial selection",
                "I consult treatment guidelines more often",
                "I have changed the types/classes of antimicrobials I prescribe",
                "I avoid unnecessarily broad-spectrum antimicrobials when appropriate",
                "I review or modify antimicrobial treatment when laboratory/AST results become available",
                "I pay more attention to dose and treatment duration",
                "I provide patients with more counselling on appropriate antimicrobial use",
                "Other — specify",
            ],
        },
        {
            "type": "text",
            "name": "changed_prescribing_how_other",
            "title": "Specify other prescribing change",
            "visibleIf": "{changed_prescribing_how} contains 'Other — specify'",
            "isRequired": True,
        },
        {
            "type": "checkbox",
            "name": "changed_prescribing_no_reasons",
            "title": "What is the main reason your antimicrobial prescribing practices have not changed in response to AMR?",
            "visibleIf": "{changed_prescribing_5y} = 'No'",
            "isRequired": True,
            "choices": [
                "Current prescribing already follows recommended practice",
                "Insufficient local AMR information",
                "Limited access to microbiology/AST",
                "Limited alternative antimicrobials",
                "Guidelines have not changed my practice",
                "AMR has not substantially influenced my prescribing decisions",
                "Other — specify",
            ],
        },
        {
            "type": "text",
            "name": "changed_prescribing_no_reasons_other",
            "title": "Specify other reason prescribing has not changed",
            "visibleIf": "{changed_prescribing_no_reasons} contains 'Other — specify'",
            "isRequired": True,
        },
        {
            "type": "checkbox",
            "name": "patient_advice",
            "title": "What advice do you impart to patients on antimicrobial usage?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": [
                "Complete full course",
                "Take at correct intervals",
                "Never share treatment",
                "Do not stop when feeling better",
                "Save remaining antimicrobials for next illness",
                "Dispose of remaining antimicrobials appropriately",
            ],
        },
        # Q61 ceftriaxone
        {
            "type": "checkbox",
            "name": "ceftriaxone_factors",
            "title": "When considering prescribing ceftriaxone, which factors influence your prescribing decision?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": ceftriaxone_choices,
        },
        {
            "type": "text",
            "name": "ceftriaxone_factors_other",
            "title": "Specify other ceftriaxone prescribing factor",
            "visibleIf": "{ceftriaxone_factors} contains 'Other'",
            "isRequired": True,
        },
        {
            "type": "dropdown",
            "name": "ceftriaxone_factor_main",
            "title": "Of the factors you selected above, which one most strongly influences your decision to prescribe ceftriaxone?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes' and {ceftriaxone_factors} notempty",
            "isRequired": True,
            "choicesFromQuestion": "ceftriaxone_factors",
            "choicesFromQuestionMode": "selected",
        },
        # Q62 DDD
        {
            "type": "radiogroup",
            "name": "uses_ddd_data",
            "title": "Do you currently use Defined Daily Dose (DDD)-based antimicrobial use data or reports to inform antimicrobial stewardship or prescribing-related decisions in your practice or facility?",
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure", "Not applicable to my current role"],
        },
        {
            "type": "checkbox",
            "name": "ddd_data_uses",
            "title": "How do you use DDD-based antimicrobial use data or reports?",
            "visibleIf": "{uses_ddd_data} = 'Yes'",
            "isRequired": True,
            "choices": [
                "To monitor antimicrobial use or consumption over time",
                "To compare antimicrobial use across wards, departments, facilities, or time periods",
                "To identify high or increasing use of particular antimicrobials",
                "To support antimicrobial stewardship activities",
                "To review or improve prescribing practices",
                "To support audits, feedback, or quality-improvement activities",
                "To inform facility-level antimicrobial policies or guidelines",
                "Other — specify",
            ],
        },
        {
            "type": "text",
            "name": "ddd_data_uses_other",
            "title": "Specify other DDD data use",
            "visibleIf": "{ddd_data_uses} contains 'Other — specify'",
            "isRequired": True,
        },
        # Q63 AST timing
        {
            "type": "radiogroup",
            "name": "no_ast_frequency_month",
            "title": "In the past month, how often have you prescribed antibiotics before antimicrobial susceptibility testing (AST) results were available?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": FREQ5
            + ["Not applicable — I did not prescribe antibiotics in the past month"],
        },
        {
            "type": "checkbox",
            "name": "no_ast_reasons",
            "title": "What were the main reasons for prescribing antibiotics before AST results were available?",
            "visibleIf": "{no_ast_frequency_month} anyof ['Rarely', 'Sometimes', 'Often', 'Always']",
            "isRequired": True,
            "choices": [
                "AST was not clinically indicated",
                "AST was not available at the facility",
                "Appropriate specimen could not be collected",
                "AST had been requested, but results were still pending",
                "Laboratory turnaround time was too long",
                "The patient's clinical condition required treatment before results were available",
                "Clinical guidelines supported empirical treatment",
                "Previous clinical experience guided treatment",
                "Cost or affordability of laboratory testing",
                "Patient declined testing",
                "Other — specify",
                "Not sure",
            ],
        },
        {
            "type": "text",
            "name": "no_ast_reasons_other",
            "title": "Specify other reason for prescribing before AST",
            "visibleIf": "{no_ast_reasons} contains 'Other — specify'",
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "viral_antibiotic_prescribing",
            "title": "Have you prescribed antibiotics for conditions you suspected to be viral in origin?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": ["Yes", "No"],
        },
        # Q65 guideline adherence
        {
            "type": "radiogroup",
            "name": "guideline_following_frequency",
            "title": "How often do you follow national or WHO guidelines when prescribing antimicrobials?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "choices": FREQ5 + ["Not applicable — I do not prescribe antimicrobials"],
        },
        {
            "type": "checkbox",
            "name": "guideline_following_barriers",
            "title": "What factors may limit your ability to follow national or WHO antimicrobial treatment guidelines?",
            "visibleIf": "{guideline_following_frequency} anyof ['Never', 'Rarely', 'Sometimes']",
            "isRequired": True,
            "choices": [
                "Guidelines are not readily available or accessible",
                "I am not familiar with the relevant recommendations",
                "Guidelines are not sufficiently up to date",
                "Recommended diagnostic tests are unavailable",
                "Recommended antimicrobial(s) are unavailable",
                "Patient-specific clinical circumstances require a different approach",
                "Local antimicrobial resistance patterns influence the choice of treatment",
                "Laboratory/AST results indicate a different treatment",
                "Cost or affordability of recommended treatment",
                "High workload or limited consultation time",
                "Other — specify",
            ],
        },
        {
            "type": "text",
            "name": "guideline_following_barriers_other",
            "title": "Specify other guideline adherence barrier",
            "visibleIf": "{guideline_following_barriers} contains 'Other — specify'",
            "isRequired": True,
        },
        # Q66 documentation matrix
        {
            "type": "matrix",
            "name": "document_indication_dose",
            "title": "When prescribing an antibiotic, how often do you document the following information in the patient record?",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "rows": [
                {"value": "clinical_diagnosis", "text": "Clinical diagnosis"},
                {"value": "antibiotic_indication", "text": "Indication for the antibiotic"},
                {"value": "antibiotic_dose", "text": "Antibiotic dose"},
            ],
            "columns": FREQ5,
        },
        # Q67 first-line searchable (up to 3) + indications
        {
            "type": "tagbox",
            "name": "first_line_antibiotics",
            "title": "Which antibiotics do you most frequently prescribe as first-line treatment for common infections in your practice? Select up to three antibiotics.",
            "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
            "isRequired": True,
            "maxSelectedChoices": 3,
            "searchEnabled": True,
            "choices": amr_choices,
        },
        {
            "type": "text",
            "name": "first_line_antibiotics_other",
            "title": "Specify other first-line antibiotic",
            "visibleIf": "{first_line_antibiotics} contains 'Other antibiotic'",
            "isRequired": True,
        },
        {
            "type": "dropdown",
            "name": "first_line_indication_1",
            "title": "For the 1st selected antibiotic, which clinical condition/indication do you most frequently prescribe it for as first-line treatment?",
            "visibleIf": "{first_line_antibiotics.length} >= 1",
            "isRequired": True,
            "searchEnabled": True,
            "choices": indication_choices,
        },
        {
            "type": "text",
            "name": "first_line_indication_1_other",
            "title": "Specify other indication for 1st antibiotic",
            "visibleIf": "{first_line_indication_1} = 'IND_OTHER'",
            "isRequired": True,
        },
        {
            "type": "dropdown",
            "name": "first_line_indication_2",
            "title": "For the 2nd selected antibiotic, which clinical condition/indication do you most frequently prescribe it for as first-line treatment?",
            "visibleIf": "{first_line_antibiotics.length} >= 2",
            "isRequired": True,
            "searchEnabled": True,
            "choices": indication_choices,
        },
        {
            "type": "text",
            "name": "first_line_indication_2_other",
            "title": "Specify other indication for 2nd antibiotic",
            "visibleIf": "{first_line_indication_2} = 'IND_OTHER'",
            "isRequired": True,
        },
        {
            "type": "dropdown",
            "name": "first_line_indication_3",
            "title": "For the 3rd selected antibiotic, which clinical condition/indication do you most frequently prescribe it for as first-line treatment?",
            "visibleIf": "{first_line_antibiotics.length} >= 3",
            "isRequired": True,
            "searchEnabled": True,
            "choices": indication_choices,
        },
        {
            "type": "text",
            "name": "first_line_indication_3_other",
            "title": "Specify other indication for 3rd antibiotic",
            "visibleIf": "{first_line_indication_3} = 'IND_OTHER'",
            "isRequired": True,
        },
    ]


def replace_profession_labels(obj):
    """Map Medical Doctor -> Physician across titles/choices/visibleIf."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str):
                obj[k] = v.replace("Medical Doctor", "Physician")
            else:
                replace_profession_labels(v)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str):
                obj[i] = item.replace("Medical Doctor", "Physician")
            else:
                replace_profession_labels(item)


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    amr = load_antimicrobials()
    indications = load_indications()

    data["description"] = (
        "Stream A1 - Healthcare Provider KAP. IRB Ref. No. 279/CMHSIRB/2026. "
        "Form version HCW-KAP-v1.2 (reviewer Practice restructuring + WHO dictionaries)."
    )
    data["showPreviewBeforeComplete"] = "showAllQuestions"
    data["previewText"] = "Review Answers"
    data["editText"] = "Edit"
    data["completeText"] = "Submit"

    # Cadre labels
    for page in data["pages"]:
        for el in page.get("elements", []):
            if el.get("name") == "profession":
                el["title"] = "Select which healthcare provider category you belong to"
                el["choices"] = [
                    "Physician",
                    "Nurse",
                    "Laboratory Technician",
                    "Pharmacist",
                ]

    # Replace practice page elements
    for page in data["pages"]:
        if page.get("name") == "practice":
            page["elements"] = practice_elements(amr, indications)

    replace_profession_labels(data)

    # Ensure profession_specific visibility uses Physician
    for page in data["pages"]:
        if page.get("name") == "profession_specific":
            page["visibleIf"] = (
                "{consent_status} = 'Yes' and {profession} anyof "
                "['Physician', 'Pharmacist', 'Nurse', 'Laboratory Technician']"
            )

    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {PATH}")
    print(f"Antimicrobials: {len(amr)}")
    print(f"Indications: {len(indications)}")
    practice = next(p for p in data["pages"] if p["name"] == "practice")
    print(f"Practice questions: {len(practice['elements'])}")


if __name__ == "__main__":
    main()
