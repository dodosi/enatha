#!/usr/bin/env python3
"""Rebuild HCW KAP profession-specific + Rwanda open-ended to HCW-KAP-v1.3 (TODAY 22/09/2026 review)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "database" / "samples" / "hcw_kap_survey.json"
AMR_CSV = ROOT / "database" / "dictionaries" / "who_antimicrobial_dictionary.csv"
ICD_CSV = ROOT / "database" / "dictionaries" / "who_icd11_clinical_conditions.csv"

EXTENT = [
    {"value": "0", "text": "Not at all"},
    {"value": "1", "text": "A little"},
    {"value": "2", "text": "Somewhat"},
    {"value": "3", "text": "A lot"},
    {"value": "99", "text": "Not sure"},
]

CULTURE_TIMING = [
    {
        "value": "routinely",
        "text": "Routinely when clinically indicated, before or at antimicrobial initiation",
    },
    {
        "value": "after_failure",
        "text": "Mainly following failure of initial antimicrobial treatment",
    },
    {
        "value": "both",
        "text": "Both, depending on the clinical situation",
    },
    {"value": "Other", "text": "Other — specify"},
]


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
    choices.extend(
        [
            {"value": "Other antimicrobial not found", "text": "Other antimicrobial not found — specify"},
            {"value": "It depends on the clinical circumstances", "text": "It depends on the clinical circumstances"},
            {"value": "Not sure", "text": "Not sure"},
        ]
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
    choices.append(
        {
            "value": "IND_OTHER",
            "text": "Other infection/clinical indication — specify",
        }
    )
    return choices


def keep_non_doctor_profession(elements: list[dict]) -> list[dict]:
    drop = {
        "culture_request_condition",
        "doctor_tx_pneumonia",
        "doctor_tx_cystitis",
        "doctor_tx_pyelonephritis",
        "doctor_tx_acute_pharyngitis",
    }
    return [e for e in elements if e.get("name") not in drop]


def doctor_elements(amr: list[dict], indications: list[dict]) -> list[dict]:
    return [
        {
            "type": "radiogroup",
            "name": "culture_request_timing",
            "title": (
                "When managing a patient with a suspected bacterial infection, when do you usually "
                "request a specimen for microbiological culture?"
            ),
            "visibleIf": "{profession} = 'Physician'",
            "isRequired": True,
            "choices": [
                {
                    "value": "A",
                    "text": (
                        "Routinely, when microbiological culture is clinically indicated, "
                        "before or at the time of initiating antimicrobial treatment"
                    ),
                },
                {
                    "value": "B",
                    "text": (
                        "Mainly when the patient does not respond to initial antimicrobial "
                        "treatment (treatment failure)"
                    ),
                },
                {
                    "value": "C",
                    "text": "In both situations, depending on the clinical condition",
                },
                {
                    "value": "D",
                    "text": "I rarely or never request microbiological culture",
                },
                {"value": "E", "text": "Other — specify"},
            ],
        },
        {
            "type": "text",
            "name": "culture_request_timing_other",
            "title": "Specify other culture-request approach",
            "visibleIf": "{profession} = 'Physician' and {culture_request_timing} = 'E'",
            "isRequired": True,
        },
        {
            "type": "checkbox",
            "name": "culture_request_conditions",
            "title": (
                "For which clinical conditions or suspected infections do you usually request "
                "microbiological culture? Select all that apply."
            ),
            "visibleIf": "{profession} = 'Physician' and {culture_request_timing} anyof ['A', 'B', 'C', 'E']",
            "isRequired": True,
            "choices": indications,
            "colCount": 1,
        },
        {
            "type": "text",
            "name": "culture_request_conditions_other",
            "title": "Specify other clinical condition for culture request",
            "visibleIf": "{culture_request_conditions} contains 'IND_OTHER'",
            "isRequired": True,
        },
        {
            "type": "matrix",
            "name": "culture_request_timing_by_condition",
            "title": "For each clinical condition selected above, when do you usually request microbiological culture?",
            "visibleIf": (
                "{profession} = 'Physician' and {culture_request_timing} anyof ['A', 'B', 'C', 'E'] "
                "and {culture_request_conditions} notempty"
            ),
            "isRequired": True,
            "rowsFromQuestion": "culture_request_conditions",
            "rowsFromQuestionMode": "selected",
            "columns": CULTURE_TIMING,
        },
        {
            "type": "comment",
            "name": "culture_request_timing_by_condition_other",
            "title": "If you selected Other for any condition above, please specify",
            "visibleIf": "{culture_request_timing_by_condition} notempty",
        },
        {
            "type": "dropdown",
            "name": "doctor_pneumonia_first_choice",
            "title": (
                "For an uncomplicated adult patient with pneumonia, with no known antimicrobial "
                "allergy or other major contraindication, which antimicrobial would you usually "
                "select as your first-choice treatment?"
            ),
            "visibleIf": "{profession} = 'Physician'",
            "isRequired": True,
            "searchEnabled": True,
            "choices": amr,
        },
        {
            "type": "text",
            "name": "doctor_pneumonia_first_choice_other",
            "title": "Specify other antimicrobial for pneumonia",
            "visibleIf": "{doctor_pneumonia_first_choice} = 'Other antimicrobial not found'",
            "isRequired": True,
        },
        {
            "type": "checkbox",
            "name": "doctor_pneumonia_adjuncts",
            "title": (
                "In addition to antimicrobial treatment, which adjunct treatment(s), if any, "
                "would you usually consider for this patient?"
            ),
            "visibleIf": "{profession} = 'Physician'",
            "isRequired": True,
            "choices": [
                "Antipyretic/analgesic treatment",
                "Fluids/hydration support",
                "Oxygen therapy, when clinically indicated",
                "Bronchodilator, when clinically indicated",
                "Other — specify",
                "No adjunct treatment",
            ],
        },
        {
            "type": "text",
            "name": "doctor_pneumonia_adjuncts_other",
            "title": "Specify other adjunct treatment",
            "visibleIf": "{doctor_pneumonia_adjuncts} contains 'Other — specify'",
            "isRequired": True,
        },
    ]


def rwanda_elements() -> list[dict]:
    return [
        {
            "type": "comment",
            "name": "q86_prescribing_decision_narrative",
            "title": (
                "Thinking about a recent patient you managed, please describe a situation in which "
                "you had to decide whether or not to prescribe an antibiotic. What influenced your decision?"
            ),
            "description": (
                "Please describe the situation and the main factors that influenced your decision. "
                "Do not include the patient's name or other identifying information."
            ),
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q86a_additional_context",
            "title": (
                "Is there anything else about your work setting, the patient, the health facility, "
                "or the local context that influenced this decision? Please explain."
            ),
        },
        {
            "type": "comment",
            "name": "q87_guideline_challenges_text",
            "title": (
                "What challenges, if any, do you experience when trying to follow recommended "
                "antibiotic treatment guidelines in your facility? Please describe."
            ),
            "description": 'You may answer "No challenges experienced".',
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q87a_local_context_text",
            "title": (
                "Are there any circumstances specific to your facility or local setting that make "
                "it easier or more difficult to follow these guidelines? Please explain."
            ),
        },
        {
            "type": "comment",
            "name": "q88_patient_response_no_antibiotic",
            "title": (
                "In your experience, how do patients typically respond when you decide that an "
                "antibiotic is not needed and do not prescribe one? Please describe."
            ),
            "description": 'You may answer "No particular reaction" or "I have not experienced this situation."',
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q88a_patient_expectations",
            "title": (
                "Is there anything about patients' expectations, beliefs, or circumstances that "
                "influences these interactions? Please explain."
            ),
        },
        {
            "type": "comment",
            "name": "q89_prescribing_support_needed",
            "title": (
                "What resources, tools, training, or other support would help you make antimicrobial "
                "prescribing decisions with greater confidence in your current practice? Please describe."
            ),
            "description": 'You may answer "No additional support needed".',
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q90_explain_amr_simple",
            "title": (
                "If a patient asked you what antimicrobial resistance (AMR) means, how would you "
                "explain it to them in simple terms?"
            ),
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q91_successful_ams",
            "title": (
                "In your view, what would a successful antimicrobial stewardship programme look like "
                "in your facility or local healthcare setting? Please describe."
            ),
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q92_amr_policy_gaps",
            "title": (
                "Based on your experience, are there any gaps between national antimicrobial resistance "
                "(AMR) policies or recommendations and what is implemented in your facility? If yes, please describe them."
            ),
            "description": (
                'You may answer "No gaps observed", "Not sure", or '
                '"I am not familiar enough with national AMR policies to assess this".'
            ),
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q92a_strengthen_policy_implementation",
            "title": (
                "What do you think could help strengthen the implementation of national AMR policies "
                "or recommendations in your facility? Please explain."
            ),
        },
        {
            "type": "comment",
            "name": "q93_provider_behaviour_change_text",
            "title": (
                "In your view, what changes in behaviour would be most important for reducing "
                "antimicrobial resistance (AMR) in your setting — among healthcare providers?"
            ),
            "description": 'You may answer "Not sure".',
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q93_community_behaviour_change_text",
            "title": (
                "In your view, what changes in behaviour would be most important for reducing "
                "antimicrobial resistance (AMR) in your setting — among patients and community members?"
            ),
            "description": 'You may answer "Not sure".',
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q94_system_challenges_rwanda",
            "title": (
                "In your view, what are the most important health-system-level challenges to controlling "
                "antimicrobial resistance (AMR) in Rwanda? Please describe."
            ),
            "description": 'You may answer "Not sure".',
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q95_digital_ai_role",
            "title": (
                "In your view, what role, if any, could digital technologies, including artificial "
                "intelligence (AI), play in supporting appropriate antimicrobial use in your healthcare setting? Please describe."
            ),
            "description": 'You may answer "I do not see a role", "Not sure", or equivalent.',
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q95a_digital_ai_concerns",
            "title": (
                "Do you have any concerns or conditions that should be considered when using such "
                "technologies to support antimicrobial prescribing in your setting? Please describe."
            ),
        },
        {
            "type": "comment",
            "name": "q96_mother_viral_request_response",
            "title": (
                "A mother requests antibiotics for her child after being informed that the illness is "
                "likely viral and that antibiotics are not indicated. How would you respond? Please describe what you would say or do."
            ),
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q97_animal_leftover_antibiotics_response",
            "title": (
                "A patient tells you that he has been using antibiotics left over from treating his "
                "animals to treat his own infection. How would you respond? Please describe what you would say or do."
            ),
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "q98_nonprescription_encounter",
            "title": (
                "Based on what patients tell you or what you learn during patient care, do you encounter "
                "patients who have obtained antibiotics without a prescription before seeking care at your facility?"
            ),
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure"],
        },
        {
            "type": "checkbox",
            "name": "q98a_nonprescription_sources",
            "title": (
                "Based on information provided by your patients, where do they usually obtain antibiotics "
                "without a prescription?"
            ),
            "visibleIf": "{q98_nonprescription_encounter} = 'Yes'",
            "isRequired": True,
            "choices": [
                "Pharmacy",
                "Drug shop/medicine retailer",
                "Leftover antibiotics from a previous illness or treatment",
                "Family members, friends, or neighbours",
                "Informal medicine seller/vendor",
                "Antibiotics originally obtained for animals/veterinary use",
                "Other — please specify",
                "Source not known/not disclosed by the patient",
            ],
        },
        {
            "type": "text",
            "name": "q98a_nonprescription_sources_other",
            "title": "Specify other non-prescription source",
            "visibleIf": "{q98a_nonprescription_sources} contains 'Other — please specify'",
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q98b_nonprescription_extra",
            "title": (
                "Is there anything else patients have told you about how or why they obtain antibiotics "
                "without a prescription? Please describe."
            ),
            "visibleIf": "{q98_nonprescription_encounter} = 'Yes'",
        },
        {
            "type": "radiogroup",
            "name": "q99_chw_collaboration",
            "title": (
                "In your current role, do you collaborate with Community Health Workers (CHWs/Binômes) "
                "on activities related to appropriate antibiotic use or antimicrobial resistance (AMR)?"
            ),
            "isRequired": True,
            "choices": ["Yes", "No", "Not applicable to my current role"],
        },
        {
            "type": "comment",
            "name": "q99a_chw_collaboration_how",
            "title": (
                "Please describe how you collaborate with CHWs/Binômes on appropriate antibiotic use or AMR."
            ),
            "visibleIf": "{q99_chw_collaboration} = 'Yes'",
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q99b_chw_collaboration_why_not",
            "title": (
                "What are the main reasons you do not currently collaborate with CHWs/Binômes on "
                "appropriate antibiotic use or AMR? Please describe."
            ),
            "visibleIf": "{q99_chw_collaboration} = 'No'",
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "q100_informal_vendors_present",
            "title": (
                "Based on your knowledge or experience, are informal medicine vendors in your area "
                "involved in providing or selling antibiotics?"
            ),
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure"],
        },
        {
            "type": "radiogroup",
            "name": "q100a_informal_vendor_training",
            "title": (
                "To your knowledge, have these informal medicine vendors received any training or "
                "information on appropriate antibiotic use or antimicrobial resistance (AMR)?"
            ),
            "visibleIf": "{q100_informal_vendors_present} = 'Yes'",
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure"],
        },
        {
            "type": "radiogroup",
            "name": "q100b_informal_vendor_regulation",
            "title": (
                "To your knowledge, are these informal medicine vendors subject to monitoring or "
                "regulation by relevant authorities regarding the sale or provision of antibiotics?"
            ),
            "visibleIf": "{q100_informal_vendors_present} = 'Yes'",
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure"],
        },
        {
            "type": "comment",
            "name": "q100c_informal_vendor_notes",
            "title": (
                "Please describe anything else you know about antibiotic provision by informal medicine "
                "vendors in your area, including any challenges or concerns."
            ),
            "visibleIf": "{q100_informal_vendors_present} = 'Yes'",
        },
        {
            "type": "radiogroup",
            "name": "q101_digital_tools_used",
            "title": (
                "In your current practice, do you use any digital system, platform, or application for "
                "activities related to antimicrobial use or antimicrobial resistance (AMR)?"
            ),
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure", "Not applicable to my current role"],
        },
        {
            "type": "comment",
            "name": "q101a_digital_systems_specify",
            "title": "Which digital system(s), platform(s), or application(s) do you use? Please specify.",
            "visibleIf": "{q101_digital_tools_used} = 'Yes'",
            "isRequired": True,
        },
        {
            "type": "checkbox",
            "name": "q101b_digital_systems_uses",
            "title": "What do you use the digital system(s) for?",
            "visibleIf": "{q101_digital_tools_used} = 'Yes'",
            "isRequired": True,
            "choices": [
                "Accessing treatment guidelines",
                "Recording or reporting antimicrobial use",
                "Recording or reporting microbiology/AMR information",
                "Accessing laboratory or AST results",
                "Patient care or clinical documentation",
                "Surveillance or monitoring",
                "Other — please specify",
            ],
        },
        {
            "type": "text",
            "name": "q101b_digital_systems_uses_other",
            "title": "Specify other digital system use",
            "visibleIf": "{q101b_digital_systems_uses} contains 'Other — please specify'",
            "isRequired": True,
        },
        {
            "type": "comment",
            "name": "q101c_digital_systems_challenges",
            "title": (
                "Please describe any challenges you experience when using these digital systems for "
                "antimicrobial use or AMR-related activities."
            ),
            "visibleIf": "{q101_digital_tools_used} = 'Yes'",
        },
        {
            "type": "radiogroup",
            "name": "q102_remoteness_affects_care",
            "title": (
                "In your experience, does the geographic location or remoteness of your facility affect "
                "your ability to manage infections appropriately?"
            ),
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure", "Not applicable"],
        },
        {
            "type": "comment",
            "name": "q102a_remoteness_how",
            "title": (
                "Please describe how the geographic location or remoteness of your facility affects "
                "the management of infections."
            ),
            "visibleIf": "{q102_remoteness_affects_care} = 'Yes'",
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "q103_traditional_remedies_belief",
            "title": (
                "Do you believe that traditional remedies can sometimes be used instead of antibiotics "
                "for the management of infections?"
            ),
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure"],
        },
        {
            "type": "comment",
            "name": "q103a_traditional_remedies_explain",
            "title": "Please explain your answer.",
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "q104_suggested_traditional_remedy",
            "title": (
                "Have you ever advised or suggested that a patient use a traditional remedy instead of "
                "an antibiotic for an infection?"
            ),
            "isRequired": True,
            "choices": ["Yes", "No", "Prefer not to answer"],
        },
        {
            "type": "comment",
            "name": "q104a_suggested_traditional_situation",
            "title": (
                "Please describe the situation, including the type of infection or health problem and "
                "the traditional remedy you advised or suggested."
            ),
            "description": "Do not include any information that could identify the patient.",
            "visibleIf": "{q104_suggested_traditional_remedy} = 'Yes'",
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "q105_cost_informal_influence",
            "title": (
                "Based on your experience, to what extent do you think the cost of seeking care at a "
                "clinic or health facility, even with Mutuelle de Santé, influences patients to obtain "
                "antibiotics without a prescription or from informal sources?"
            ),
            "isRequired": True,
            "choices": EXTENT,
        },
        {
            "type": "comment",
            "name": "q105a_cost_informal_explain",
            "title": (
                "Please explain your answer, based on what you have observed or what patients have told you."
            ),
        },
        {
            "type": "radiogroup",
            "name": "q106_strong_medicine_extent",
            "title": (
                "Based on your experience, to what extent do you think antibiotics are viewed as "
                '"strong medicine" (ubuvuzi bukomeye) among patients and community members in your setting?'
            ),
            "isRequired": True,
            "choices": EXTENT,
        },
        {
            "type": "comment",
            "name": "q106a_strong_medicine_meaning",
            "title": (
                'Please explain what "strong medicine" (ubuvuzi bukomeye) means in this context, based '
                "on what you have heard or observed among patients or community members."
            ),
        },
        {
            "type": "radiogroup",
            "name": "q107_local_amr_terms",
            "title": (
                "Based on your experience, are there any local words, expressions, or phrases that "
                "patients or community members use to describe antimicrobial resistance (AMR) or the "
                "idea that antimicrobial treatment is no longer effective?"
            ),
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure"],
        },
        {
            "type": "paneldynamic",
            "name": "q107_local_amr_terms_list",
            "title": "Local AMR-related terms and meanings",
            "visibleIf": "{q107_local_amr_terms} = 'Yes'",
            "isRequired": True,
            "panelCount": 1,
            "minPanelCount": 1,
            "panelAddText": "Add another term",
            "templateElements": [
                {
                    "type": "text",
                    "name": "local_term",
                    "title": "Local word, expression, or phrase",
                    "isRequired": True,
                },
                {
                    "type": "comment",
                    "name": "local_term_meaning",
                    "title": "What does this mean in the local context?",
                    "isRequired": True,
                },
            ],
        },
        {
            "type": "comment",
            "name": "q108_leader_influence",
            "title": (
                "Based on your experience, how do religious or community leaders influence "
                "health-seeking behaviour related to infections and the use of antibiotics in your "
                "community? Please describe."
            ),
            "description": 'You may answer "I have not observed any influence" or "Not sure".',
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "q109_pbf_influence",
            "title": (
                "In your experience, does performance-based financing (PBF) influence antimicrobial "
                "prescribing or other decisions related to antimicrobial use in your facility?"
            ),
            "isRequired": True,
            "choices": [
                "Yes",
                "No",
                "Not sure",
                "Not applicable or not familiar with PBF",
            ],
        },
        {
            "type": "comment",
            "name": "q109a_pbf_how",
            "title": (
                "Please describe how performance-based financing influences antimicrobial prescribing "
                "or other antimicrobial-use decisions in your facility."
            ),
            "visibleIf": "{q109_pbf_influence} = 'Yes'",
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "q110_mch_ams_integration",
            "title": (
                "In your experience, are antimicrobial stewardship or appropriate antimicrobial-use "
                "activities integrated into maternal and child health services in your facility?"
            ),
            "isRequired": True,
            "choices": ["Yes", "No", "Not sure", "Not applicable to my current role"],
        },
        {
            "type": "comment",
            "name": "q110a_mch_ams_how",
            "title": (
                "Please describe how antimicrobial stewardship or appropriate antimicrobial-use "
                "activities are integrated into maternal and child health services in your facility."
            ),
            "visibleIf": "{q110_mch_ams_integration} = 'Yes'",
            "isRequired": True,
        },
        {
            "type": "radiogroup",
            "name": "q111_cbhi_diagnostics_cover",
            "title": (
                "Based on your experience, does Mutuelle de Santé/Community-Based Health Insurance (CBHI) "
                "adequately cover diagnostic tests used to inform antimicrobial treatment decisions?"
            ),
            "isRequired": True,
            "choices": [
                "Yes, adequately",
                "Partially",
                "No",
                "Not sure",
                "Not applicable to my role",
            ],
        },
        {
            "type": "comment",
            "name": "q111a_cbhi_diagnostics_gaps",
            "title": (
                "Please describe which diagnostic tests or related costs are not adequately covered "
                "and how this affects patient care or antimicrobial treatment decisions."
            ),
            "visibleIf": "{q111_cbhi_diagnostics_cover} anyof ['Partially', 'No']",
            "isRequired": True,
        },
    ]


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    amr = load_antimicrobials()
    indications = load_indications()

    data["description"] = (
        "Stream A1 - Healthcare Provider KAP. IRB Ref. No. 279/CMHSIRB/2026. "
        "Form version HCW-KAP-v1.3 (TODAY 22/09/2026: doctor culture/pneumonia + Rwanda open-ended)."
    )
    data["showPreviewBeforeComplete"] = "showAllQuestions"
    data["previewText"] = "Review Answers"
    data["editText"] = "Edit"
    data["completeText"] = "Submit"

    for page in data["pages"]:
        if page.get("name") == "profession_specific":
            kept = keep_non_doctor_profession(page.get("elements", []))
            page["elements"] = doctor_elements(amr, indications) + kept
        elif page.get("name") == "open_ended_rwanda":
            page["title"] = "Open-ended and Rwanda context"
            page["elements"] = rwanda_elements()

    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {PATH}")
    for page in data["pages"]:
        if page["name"] in ("profession_specific", "open_ended_rwanda"):
            print(f"{page['name']}: {len(page['elements'])} elements")


if __name__ == "__main__":
    main()
