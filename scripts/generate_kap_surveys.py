#!/usr/bin/env python3
"""Generate Stream A1 and A2 KAP SurveyJS JSON files for testing."""

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "database" / "samples"

LIKERT5 = [
    "Strongly agree",
    "Agree",
    "Neutral",
    "Disagree",
    "Strongly disagree",
]
KNOW5 = [
    {"value": 1, "text": "1 - Least confident"},
    {"value": 2, "text": "2"},
    {"value": 3, "text": "3"},
    {"value": 4, "text": "4"},
    {"value": 5, "text": "5 - Very confident"},
]
CONF5 = [
    {"value": 1, "text": "1 - Very confident"},
    {"value": 2, "text": "2 - Confident"},
    {"value": 3, "text": "3 - Unsure"},
    {"value": 4, "text": "4 - Unconfident"},
    {"value": 5, "text": "5 - Very unconfident"},
]


def build_hcw():
    return {
        "title": "Healthcare Provider KAP Survey on Antimicrobial Resistance",
        "description": (
            "Stream A1 - Healthcare Provider KAP. IRB Ref. No. 279/CMHSIRB/2026. "
            "Form version HCW-KAP-v1.0"
        ),
        "showProgressBar": "top",
        "progressBarType": "pages",
        "showPreviewBeforeComplete": "showAllQuestions",
        "previewText": "Review Answers",
        "editText": "Edit",
        "completeText": "Submit",
        "completedHtml": (
            "<h3>Thank you.</h3><p>Your responses will contribute to research aimed at "
            "optimising rational antimicrobial use and antimicrobial stewardship.</p>"
        ),
        "pages": [
            {
                "name": "consent",
                "title": "Consent and Screening",
                "elements": [
                    {
                        "type": "html",
                        "name": "consent_info",
                        "html": (
                            "<p>We will collect your name and telephone number to enable "
                            "the research team to contact you if clarification or "
                            "study-related follow-up is required. This identifying "
                            "information will be kept confidential and will only be "
                            "accessible to authorized members of the research team. "
                            "Your name and telephone number will be stored separately "
                            "from the research dataset and linked to your responses "
                            "using a unique Study Participant ID.</p>"
                        ),
                    },
                    {
                        "type": "text",
                        "name": "participant_name",
                        "title": "Participant full name (restricted contact field)",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "participant_telephone",
                        "title": "Telephone number (restricted contact field)",
                        "inputType": "tel",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "site_code",
                        "title": "Study site code",
                        "isRequired": True,
                    },
                    {
                        "type": "radiogroup",
                        "name": "consent_status",
                        "title": "Do you consent to participate in this study?",
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "html",
                        "name": "consent_stop",
                        "visibleIf": "{consent_status} = 'No'",
                        "html": (
                            '<div class="alert alert-warning">Consent declined. '
                            "Do not continue enrolment.</div>"
                        ),
                    },
                    {
                        "type": "dropdown",
                        "name": "profession",
                        "title": "What is your professional cadre?",
                        "isRequired": True,
                        "visibleIf": "{consent_status} = 'Yes'",
                        "choices": [
                            "Medical Doctor",
                            "Nurse",
                            "Laboratory Technician",
                            "Pharmacist",
                        ],
                    },
                ],
            },
            {
                "name": "demographics",
                "title": "Demographics",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "radiogroup",
                        "name": "gender",
                        "title": "What is your sex?",
                        "isRequired": True,
                        "choices": ["Male", "Female"],
                    },
                    {
                        "type": "text",
                        "name": "date_of_birth",
                        "title": "What is your Date of Birth?",
                        "inputType": "date",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "graduation_year",
                        "title": "In what year did you graduate?",
                        "inputType": "number",
                        "isRequired": True,
                        "validators": [
                            {"type": "numeric", "minValue": 1960, "maxValue": 2030}
                        ],
                    },
                    {
                        "type": "text",
                        "name": "first_institution",
                        "title": (
                            "At which University/College/Institute did you obtain "
                            "your first degree or diploma?"
                        ),
                    },
                    {
                        "type": "checkbox",
                        "name": "doctor_qualification",
                        "title": "What qualification did you obtain? (Doctors only)",
                        "visibleIf": "{profession} = 'Medical Doctor'",
                        "isRequired": True,
                        "choices": [
                            "MBChB",
                            "Master of Medicine",
                            "Doctorate (PhD in Medicine)",
                            "Specialist (Fellow of College)",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "doctor_qualification_other",
                        "title": "Specify other doctor qualification",
                        "visibleIf": "{doctor_qualification} contains 'Other'",
                    },
                    {
                        "type": "checkbox",
                        "name": "pharmacist_qualification",
                        "title": "What qualification did you obtain? (Pharmacists only)",
                        "visibleIf": "{profession} = 'Pharmacist'",
                        "isRequired": True,
                        "choices": [
                            "Bachelor of Pharmacy",
                            "Master of Pharmacy",
                            "Doctorate (PhD in Pharmacy)",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "pharmacist_qualification_other",
                        "title": "Specify other pharmacist qualification",
                        "visibleIf": "{pharmacist_qualification} contains 'Other'",
                    },
                    {
                        "type": "checkbox",
                        "name": "nurse_qualification",
                        "title": "What qualification did you obtain? (Nurses only)",
                        "visibleIf": "{profession} = 'Nurse'",
                        "isRequired": True,
                        "choices": [
                            "Diploma in Nursing",
                            "Bachelor in Nursing",
                            "Master of Nursing",
                            "Doctorate or PhD in Nursing",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "nurse_qualification_other",
                        "title": "Specify other nurse qualification",
                        "visibleIf": "{nurse_qualification} contains 'Other'",
                    },
                    {
                        "type": "dropdown",
                        "name": "field_of_practice",
                        "title": "What is your field of practice?",
                        "isRequired": True,
                        "choices": [
                            "Public: Primary or community health centre",
                            "Public: District hospital",
                            "Public: Regional hospital",
                            "Public: Tertiary hospital",
                            "Private: Community",
                            "Private: Pharmacy",
                            "Academia",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "field_of_practice_other",
                        "title": "Specify other field of practice",
                        "visibleIf": "{field_of_practice} = 'Other'",
                    },
                    {
                        "type": "radiogroup",
                        "name": "practice_setting",
                        "title": "Where do you practice?",
                        "isRequired": True,
                        "choices": ["Urban area", "Peri-urban area", "Rural area"],
                    },
                    {
                        "type": "html",
                        "name": "practice_location_note",
                        "html": (
                            "<strong>Practice location</strong> "
                            "(cascading Rwanda administrative locations)"
                        ),
                    },
                    {
                        "type": "dropdown",
                        "name": "province_id",
                        "title": "Province",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "district_id",
                        "title": "District",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "sector_id",
                        "title": "Sector",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "cell_id",
                        "title": "Cell",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "village_id",
                        "title": "Village",
                        "isRequired": True,
                    },
                ],
            },
            {
                "name": "knowledge",
                "title": "Knowledge",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "matrix",
                        "name": "amr_seriousness",
                        "title": (
                            "Would you consider antimicrobial resistance "
                            "as a serious problem?"
                        ),
                        "isRequired": True,
                        "rows": [
                            {"value": "globally", "text": "Globally"},
                            {"value": "in_rwanda", "text": "In Rwanda"},
                            {
                                "value": "in_hospital_or_area",
                                "text": "In your hospital or area of practice",
                            },
                        ],
                        "columns": LIKERT5,
                    },
                    {
                        "type": "matrix",
                        "name": "knowledge_confidence",
                        "title": (
                            "How confident are you on your knowledge of antimicrobials, "
                            "antimicrobial resistance and antimicrobial stewardship? "
                            "(1 = least confident; 5 = very confident)"
                        ),
                        "isRequired": True,
                        "rows": [
                            {"value": "antimicrobials", "text": "Antimicrobials"},
                            {"value": "amr", "text": "Antimicrobial resistance"},
                            {"value": "ams", "text": "Antimicrobial stewardship"},
                        ],
                        "columns": KNOW5,
                    },
                    {
                        "type": "radiogroup",
                        "name": "antimicrobials_viral",
                        "title": (
                            "Are antimicrobial drugs effective in treating "
                            "acute viral infections?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "cold_flu_cause",
                        "title": "Common colds or flu are caused by:",
                        "isRequired": True,
                        "choices": ["Viruses", "Bacteria"],
                    },
                    {
                        "type": "checkbox",
                        "name": "amr_contributors",
                        "title": (
                            "Please select the factors you believe to be the most "
                            "contributory towards antimicrobial resistance:"
                        ),
                        "choices": [
                            "Overusage by prescriptions",
                            "Overusage without prescriptions",
                            "Errors in medical prescriptions/dose/duration/"
                            "self-medication/non-completion",
                            "Inadequate hand washing",
                            "Lack of AMR/AMS campaigns",
                            "Lack of new antimicrobial drugs",
                            "Sub-standard antimicrobials",
                            "Antimicrobials as animal growth promoters",
                            "Patient pressure",
                            "Limited consultation time",
                            "OTC access",
                            "Weak supply chain/substandard/falsified antimicrobials",
                            "Lack of laboratory capacity",
                            "Lack of up-to-date prescribing knowledge",
                            "Lack of treatment guidelines",
                            "Unreliable/absent AMR and antimicrobial-use surveillance",
                            "Unregulated OTC use/poor AMS",
                            "Limited AMR teaching resources",
                            "Private pharmacy owners provide antimicrobials "
                            "without prescription to make more money",
                        ],
                    },
                    {
                        "type": "matrix",
                        "name": "information_sources",
                        "title": (
                            "Which sources do you refer to for information on "
                            "appropriate usage of antimicrobials? Rate 1-5 "
                            "(1 = lowest preference; 5 = highest preference)."
                        ),
                        "rows": [
                            {
                                "value": "senior_colleagues",
                                "text": "Senior experienced colleagues",
                            },
                            {
                                "value": "rwanda_formulary",
                                "text": "Rwanda Medicines Formulary",
                            },
                            {"value": "merck_manual", "text": "The Merck Manual"},
                            {
                                "value": "journals_websites",
                                "text": "Medical journals or websites",
                            },
                            {
                                "value": "standard_guidelines",
                                "text": "Standard guidelines",
                            },
                            {
                                "value": "international_guidelines",
                                "text": (
                                    "International guidelines/professional "
                                    "society guidelines"
                                ),
                            },
                        ],
                        "columns": KNOW5,
                    },
                    {
                        "type": "matrix",
                        "name": "prescribing_confidence",
                        "title": (
                            "Please assess your levels of confidence when prescribing "
                            "antimicrobials (1 = very confident; 5 = very unconfident)."
                        ),
                        "isRequired": True,
                        "rows": [
                            {
                                "value": "accurate_diagnosis",
                                "text": "Accurate diagnosis",
                            },
                            {
                                "value": "decision_not_to_prescribe",
                                "text": (
                                    "Decision not to prescribe when fever/"
                                    "no serious criteria/uncertain diagnosis"
                                ),
                            },
                            {
                                "value": "correct_antimicrobial",
                                "text": "Correct antimicrobial",
                            },
                            {"value": "correct_dosage", "text": "Correct dosage"},
                            {"value": "correct_interval", "text": "Correct interval"},
                            {"value": "correct_duration", "text": "Correct duration"},
                            {
                                "value": "combination_therapy",
                                "text": "Combination therapy",
                            },
                            {
                                "value": "interpreting_microbiology",
                                "text": "Interpreting microbiology results",
                            },
                            {
                                "value": "stop_or_change_therapy",
                                "text": "When to stop/change therapy",
                            },
                            {"value": "iv_vs_oral", "text": "IV vs oral"},
                        ],
                        "columns": CONF5,
                    },
                    {
                        "type": "radiogroup",
                        "name": "irrational_use_risks",
                        "title": (
                            "Do you think there are risks associated with "
                            "irrational use of antimicrobials?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "I do not know"],
                    },
                    {
                        "type": "comment",
                        "name": "irrational_use_risks_list",
                        "title": "Please list the risks.",
                        "visibleIf": "{irrational_use_risks} = 'Yes'",
                        "isRequired": True,
                    },
                    {
                        "type": "radiogroup",
                        "name": "restrict_usage",
                        "title": (
                            "Do you think restricting antimicrobial usage is "
                            "necessary to reduce antimicrobial resistance?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Maybe"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "ams_training",
                        "title": (
                            "Have you attended any workshops or had training on "
                            "antimicrobials and antimicrobial stewardship?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "wants_training",
                        "title": (
                            "Would you like more education and training on "
                            "antimicrobial use, antimicrobial resistance and "
                            "antimicrobial stewardship?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "text",
                        "name": "resistant_bacteria_rank_1",
                        "title": "Most resistant bacterium you are aware of (Rank 1)",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "resistant_bacteria_rank_2",
                        "title": "Second most resistant bacterium (Rank 2)",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "resistant_bacteria_rank_3",
                        "title": "Third most resistant bacterium (Rank 3)",
                        "isRequired": True,
                    },
                    {
                        "type": "radiogroup",
                        "name": "inappropriate_use_percent",
                        "title": (
                            "What percentage of clinical antimicrobial use is "
                            "unnecessary or inappropriate in Rwanda?"
                        ),
                        "isRequired": True,
                        "choices": [
                            "1-20%",
                            "21-40%",
                            "41-60%",
                            "61-80%",
                            "81-100%",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "heard_ddd",
                        "title": (
                            "Have you heard of the term Defined Daily Dose (DDD) "
                            "as used by WHO?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "ceftriaxone_ddd",
                        "title": (
                            "What is the DDD value assigned by WHO for ceftriaxone "
                            "in adult patients?"
                        ),
                        "isRequired": True,
                        "choices": ["500 mg", "1 g", "2 g", "I don't know"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "ddd_purpose",
                        "title": "Do you know the purpose of the WHO DDD metric?",
                        "isRequired": True,
                        "choices": [
                            "For patient dosing",
                            "For policy and surveillance of antibiotic use",
                            "For pharmacy stock control",
                            "I don't know",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "know_national_guidelines",
                        "title": (
                            "Do you know the national guidelines for prescribing "
                            "antibiotics for common infections (e.g., UTI, pneumonia)?"
                        ),
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "text",
                        "name": "ast_test_name",
                        "title": (
                            "What laboratory test is used to determine if a bacterial "
                            "infection is resistant to antibiotics?"
                        ),
                    },
                ],
            },
            {
                "name": "attitudes",
                "title": "Attitudes",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "radiogroup",
                        "name": "antimicrobials_safe",
                        "title": (
                            "Antimicrobials are safe drugs that can be "
                            "commonly prescribed?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "unnecessary_prescribing_harm",
                        "title": (
                            "Prescribing antimicrobials to a patient who does not "
                            "really need them may ultimately have a negative impact "
                            "on their health."
                        ),
                        "isRequired": True,
                        "choices": LIKERT5,
                    },
                    {
                        "type": "radiogroup",
                        "name": "amr_direction",
                        "title": (
                            "In your opinion, do you think the problem of "
                            "antimicrobial resistance is getting better or worse?"
                        ),
                        "isRequired": True,
                        "choices": ["Better", "Worse"],
                    },
                    {
                        "type": "checkbox",
                        "name": "amr_strategies",
                        "title": (
                            "What do you think are the important strategies to "
                            "combat antimicrobial resistance?"
                        ),
                        "isRequired": True,
                        "choices": [
                            "Educational campaigns",
                            "Use of therapeutic guidelines",
                            "Vaccination/AMR campaigns",
                            "Improved infection control",
                            "Reducing antimicrobial use in agriculture and animals",
                            "Better control on antimicrobial sales",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "amr_strategies_other",
                        "title": "Specify other strategy",
                        "visibleIf": "{amr_strategies} contains 'Other'",
                    },
                    {
                        "type": "radiogroup",
                        "name": "missed_doses_amr",
                        "title": (
                            "Do you believe a patient skipping or missing one or two "
                            "doses of antimicrobials contributes to the development "
                            "of antimicrobial resistance?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "new_classes_future",
                        "title": (
                            "Do you believe that new classes of antimicrobials will "
                            "be developed in the next 5-10 years?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "personal_contribution",
                        "title": (
                            "Do you believe that you may personally be contributing "
                            "towards antimicrobial resistance?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Maybe"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "ddd_improve_prescribing",
                        "title": (
                            "Do you believe knowing the DDD of antibiotics can help "
                            "improve prescribing practices?"
                        ),
                        "isRequired": True,
                        "choices": [
                            "Strongly agree",
                            "Agree",
                            "Disagree",
                            "Strongly disagree",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "ddd_in_guidelines",
                        "title": (
                            "Should national guidelines include WHO DDD values "
                            "for training and awareness?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Maybe"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "prescribe_if_patient_insists",
                        "title": (
                            'Do you agree or disagree: "It is acceptable to prescribe '
                            "antibiotics without laboratory confirmation if the "
                            'patient insists"?'
                        ),
                        "isRequired": True,
                        "choices": [
                            "Strongly disagree",
                            "Disagree",
                            "Neutral",
                            "Agree",
                            "Strongly agree",
                            "In some situations or conditions",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "ast_importance",
                        "title": (
                            "How important is AST in guiding your "
                            "antibiotic prescription?"
                        ),
                        "choices": ["Very important", "Important", "Not important"],
                    },
                ],
            },
            {
                "name": "practice",
                "title": "Practice",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "radiogroup",
                        "name": "pharmacist_prescribing_permit",
                        "title": (
                            "In addition to your Bachelor of Pharmacy degree, do you "
                            "possess a permit allowing you to prescribe for primary "
                            "care drug treatment?"
                        ),
                        "visibleIf": "{profession} = 'Pharmacist'",
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "nurse_prescribing_permit",
                        "title": (
                            "Do you possess a concession permit to prescribe "
                            "medicines to patients?"
                        ),
                        "visibleIf": "{profession} = 'Nurse'",
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "prescribes_antimicrobials",
                        "title": (
                            "Do you prescribe antimicrobial drugs to your patients?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Not applicable"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "patients_prescribed_per_day",
                        "title": (
                            "Please select the average number of patients to whom "
                            "you prescribe antimicrobials per day."
                        ),
                        "visibleIf": "{prescribes_antimicrobials} = 'Yes'",
                        "isRequired": True,
                        "choices": [
                            "Not applicable",
                            "Less than 5",
                            "6-10",
                            "11-20",
                            "21-30",
                            "31-40",
                            "Greater than 40",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "empirical_prescribing",
                        "title": (
                            "Do you prescribe antimicrobials empirically "
                            "(based on observation and experience)?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Not applicable"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "send_microbiology",
                        "title": (
                            "Before initiating antimicrobial therapy, do you send "
                            "samples for microbiology testing to inform the need for "
                            "and/or choice of antimicrobial therapy?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Not applicable"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "has_latest_stg",
                        "title": (
                            "Do you possess the latest Rwanda Standard "
                            "Treatment Guidelines?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "uses_guidelines_frequency",
                        "title": (
                            "How often do you use the antimicrobial treatment "
                            "guidelines when deciding upon antimicrobials "
                            "for a patient?"
                        ),
                        "isRequired": True,
                        "choices": ["Always", "Sometimes", "Never", "Not applicable"],
                    },
                    {
                        "type": "text",
                        "name": "top_antimicrobial_1",
                        "title": "Antimicrobial you prescribe most (1)",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "top_antimicrobial_2",
                        "title": "Antimicrobial you prescribe most (2)",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "top_antimicrobial_3",
                        "title": "Antimicrobial you prescribe most (3)",
                        "isRequired": True,
                    },
                    {
                        "type": "radiogroup",
                        "name": "changed_prescribing_5y",
                        "title": (
                            "Have you changed your prescribing behaviour in light of "
                            "antimicrobial resistance in the past 5 years?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Not applicable"],
                    },
                    {
                        "type": "comment",
                        "name": "changed_prescribing_how",
                        "title": "How have you changed your prescribing behaviour?",
                        "visibleIf": "{changed_prescribing_5y} = 'Yes'",
                    },
                    {
                        "type": "checkbox",
                        "name": "patient_advice",
                        "title": (
                            "What advice do you impart to patients on "
                            "antimicrobial usage?"
                        ),
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
                    {
                        "type": "checkbox",
                        "name": "ceftriaxone_factors",
                        "title": (
                            "When prescribing antibiotics like ceftriaxone, "
                            "what factors do you consider most?"
                        ),
                        "isRequired": True,
                        "choices": [
                            "Clinical presentation",
                            "Local guidelines",
                            "AST results",
                            "DDD benchmarks",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "uses_ddd_data",
                        "title": (
                            "Do you currently use DDD-based data or reports "
                            "in your decision-making?"
                        ),
                        "choices": ["Yes", "No", "Not sure"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "no_ast_frequency_month",
                        "title": (
                            "In the past month, how often have you prescribed "
                            "antibiotics without conducting or receiving AST results?"
                        ),
                        "choices": ["Always", "Sometimes", "Never"],
                    },
                    {
                        "type": "comment",
                        "name": "no_ast_reason_1",
                        "title": "Main reason for prescribing without AST (1)",
                        "visibleIf": (
                            "{no_ast_frequency_month} anyof ['Always', 'Sometimes']"
                        ),
                    },
                    {
                        "type": "comment",
                        "name": "no_ast_reason_2",
                        "title": "Main reason for prescribing without AST (2)",
                        "visibleIf": (
                            "{no_ast_frequency_month} anyof ['Always', 'Sometimes']"
                        ),
                    },
                    {
                        "type": "comment",
                        "name": "no_ast_reason_3",
                        "title": "Main reason for prescribing without AST (3)",
                        "visibleIf": (
                            "{no_ast_frequency_month} anyof ['Always', 'Sometimes']"
                        ),
                    },
                    {
                        "type": "radiogroup",
                        "name": "viral_antibiotic_prescribing",
                        "title": (
                            "Have you prescribed antibiotics for conditions you "
                            "suspected to be viral in origin?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "guideline_following_frequency",
                        "title": (
                            "How often do you follow national or WHO guidelines "
                            "when prescribing antimicrobials?"
                        ),
                        "choices": [
                            "Always",
                            "Often",
                            "Sometimes",
                            "Rarely",
                            "Never",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "document_indication_dose",
                        "title": (
                            "Do you routinely document the diagnosis, antibiotic "
                            "indication, and dosage in the patient file?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Sometimes"],
                    },
                    {
                        "type": "comment",
                        "name": "first_line_antibiotics",
                        "title": (
                            "Which antibiotics do you most frequently prescribe "
                            "as first-line treatment?"
                        ),
                        "isRequired": True,
                    },
                ],
            },
            {
                "name": "profession_specific",
                "title": "Profession-specific antimicrobial treatment",
                "visibleIf": (
                    "{consent_status} = 'Yes' and {profession} anyof "
                    "['Medical Doctor', 'Pharmacist', 'Nurse', 'Laboratory Technician']"
                ),
                "elements": [
                    {
                        "type": "matrix",
                        "name": "culture_request_condition",
                        "title": (
                            "For which conditions do you request laboratory culture? "
                            "(Doctors only)"
                        ),
                        "visibleIf": "{profession} = 'Medical Doctor'",
                        "isRequired": True,
                        "rows": [
                            {
                                "value": "acute_pharyngitis",
                                "text": "Acute pharyngitis",
                            },
                            {"value": "nasopharyngitis", "text": "Nasopharyngitis"},
                            {
                                "value": "acute_otitis_media",
                                "text": "Acute otitis media",
                            },
                            {
                                "value": "chronic_otitis_media",
                                "text": "Chronic otitis media",
                            },
                            {"value": "acute_sinusitis", "text": "Acute sinusitis"},
                            {"value": "bronchitis", "text": "Bronchitis"},
                            {"value": "pneumonia", "text": "Pneumonia"},
                            {"value": "cystitis", "text": "Cystitis"},
                            {"value": "pyelonephritis", "text": "Pyelonephritis"},
                        ],
                        "columns": ["Always (A)", "On treatment failure (B)"],
                    },
                    {
                        "type": "comment",
                        "name": "doctor_tx_pneumonia",
                        "title": (
                            "First choice antimicrobials and adjunct treatment "
                            "for Pneumonia (Doctors)"
                        ),
                        "visibleIf": "{profession} = 'Medical Doctor'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "doctor_tx_cystitis",
                        "title": (
                            "First choice antimicrobials and adjunct treatment "
                            "for Cystitis (Doctors)"
                        ),
                        "visibleIf": "{profession} = 'Medical Doctor'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "doctor_tx_pyelonephritis",
                        "title": (
                            "First choice antimicrobials and adjunct treatment "
                            "for Pyelonephritis (Doctors)"
                        ),
                        "visibleIf": "{profession} = 'Medical Doctor'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "doctor_tx_acute_pharyngitis",
                        "title": (
                            "First choice antimicrobials and adjunct treatment "
                            "for Acute pharyngitis (Doctors)"
                        ),
                        "visibleIf": "{profession} = 'Medical Doctor'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "pharmacist_authorised_uti_uncomplicated",
                        "title": (
                            "Antimicrobials you are authorised to prescribe for "
                            "uncomplicated cystitis in adults (Pharmacists)"
                        ),
                        "visibleIf": "{profession} = 'Pharmacist'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "pharmacist_authorised_pneumonia",
                        "title": (
                            "Antimicrobials you are authorised to prescribe for "
                            "uncomplicated pneumonia (Pharmacists)"
                        ),
                        "visibleIf": "{profession} = 'Pharmacist'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "pharmacist_authorised_acute_bronchitis",
                        "title": (
                            "Antimicrobials you are authorised to prescribe for "
                            "acute bronchitis (Pharmacists)"
                        ),
                        "visibleIf": "{profession} = 'Pharmacist'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "nurse_authorised_uti_uncomplicated",
                        "title": (
                            "Antimicrobials you are authorised to prescribe for "
                            "uncomplicated UTI (Nurses)"
                        ),
                        "visibleIf": "{profession} = 'Nurse'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "nurse_authorised_acute_otitis_media",
                        "title": (
                            "Antimicrobials you are authorised to prescribe for "
                            "Acute otitis media (Nurses)"
                        ),
                        "visibleIf": "{profession} = 'Nurse'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "nurse_authorised_acute_bronchitis",
                        "title": (
                            "Antimicrobials you are authorised to prescribe for "
                            "Acute bronchitis (Nurses)"
                        ),
                        "visibleIf": "{profession} = 'Nurse'",
                        "isRequired": True,
                    },
                    {
                        "type": "radiogroup",
                        "name": "lab_ast_involved",
                        "title": (
                            "Are you directly involved in antimicrobial "
                            "susceptibility testing (AST)?"
                        ),
                        "visibleIf": "{profession} = 'Laboratory Technician'",
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "checkbox",
                        "name": "lab_specimen_types",
                        "title": (
                            "Which types of patient specimens do you routinely "
                            "process for culture and/or AST?"
                        ),
                        "visibleIf": "{profession} = 'Laboratory Technician'",
                        "choices": [
                            "Blood",
                            "Urine",
                            "Respiratory",
                            "Stool",
                            "Wound",
                            "CSF",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "lab_specimen_types_other",
                        "title": "Specify other specimen type",
                        "visibleIf": "{lab_specimen_types} contains 'Other'",
                    },
                    {
                        "type": "radiogroup",
                        "name": "lab_ast_availability",
                        "title": (
                            "How often is AST available when requested for "
                            "clinical decision-making?"
                        ),
                        "visibleIf": "{profession} = 'Laboratory Technician'",
                        "choices": [
                            "Always",
                            "Often",
                            "Sometimes",
                            "Rarely",
                            "Never",
                        ],
                    },
                    {
                        "type": "comment",
                        "name": "lab_ast_challenges",
                        "title": (
                            "What are the main challenges you experience when "
                            "performing AST or other microbiological testing?"
                        ),
                        "visibleIf": "{profession} = 'Laboratory Technician'",
                    },
                    {
                        "type": "comment",
                        "name": "lab_ast_reporting",
                        "title": (
                            "How are AST results reported to clinicians or other "
                            "healthcare providers in your facility?"
                        ),
                        "visibleIf": "{profession} = 'Laboratory Technician'",
                    },
                    {
                        "type": "comment",
                        "name": "lab_ast_communication_challenges",
                        "title": (
                            "What challenges affect timely communication or "
                            "clinical use of AST results?"
                        ),
                        "visibleIf": "{profession} = 'Laboratory Technician'",
                    },
                    {
                        "type": "comment",
                        "name": "lab_clinician_use_ast",
                        "title": (
                            "In your experience, how do clinicians respond to "
                            "or use AST results?"
                        ),
                        "visibleIf": "{profession} = 'Laboratory Technician'",
                    },
                    {
                        "type": "comment",
                        "name": "lab_support_needed",
                        "title": (
                            "What laboratory resources, training, systems or support "
                            "would improve AST testing and reporting in your setting?"
                        ),
                        "visibleIf": "{profession} = 'Laboratory Technician'",
                    },
                ],
            },
            {
                "name": "open_ended_rwanda",
                "title": "Open-ended and Rwanda context",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "comment",
                        "name": "recent_antibiotic_decision",
                        "title": (
                            "Can you describe a recent situation where you had to "
                            "decide whether or not to prescribe antibiotics? What "
                            "factors influenced your decision?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "guideline_challenges",
                        "title": (
                            "What challenges do you face when trying to follow "
                            "antibiotic guidelines in your facility?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "patient_reaction_no_antibiotic",
                        "title": (
                            "How do patients typically react when you decide "
                            "not to prescribe antibiotics?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "needed_prescribing_support",
                        "title": (
                            "What resources or support would help you feel more "
                            "confident in antimicrobial prescribing?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "explain_amr_patient",
                        "title": (
                            "How would you explain antimicrobial resistance "
                            "to a patient in simple terms?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "successful_ams_program",
                        "title": (
                            "What would a successful antimicrobial stewardship "
                            "program look like in your context?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "policy_implementation_gaps",
                        "title": (
                            "Can you describe the gaps between national AMR policies "
                            "and implementation at health facilities?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "behavior_change_needed",
                        "title": (
                            "What kind of behavior change is needed at the community "
                            "or provider level to reduce AMR?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "system_challenges_amr",
                        "title": (
                            "What do you think are the biggest system-level "
                            "challenges to controlling AMR in Rwanda?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "ai_role_amu",
                        "title": (
                            "How do you see the role of technology, like AI, "
                            "in improving antimicrobial use?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "radiogroup",
                        "name": "mother_insists_viral_fever",
                        "title": (
                            "A mother insists on antibiotics for her child's viral "
                            "fever. How would you respond?"
                        ),
                        "isRequired": True,
                        "choices": [
                            "Prescribe to satisfy her",
                            "Explain AMR risks",
                            "Suggest alternatives",
                        ],
                    },
                    {
                        "type": "comment",
                        "name": "farmer_leftover_animal_antibiotics",
                        "title": (
                            "A farmer uses leftover animal antibiotics for his own "
                            "infection. How would you advise him?"
                        ),
                    },
                    {
                        "type": "comment",
                        "name": "nonprescription_antibiotic_frequency",
                        "title": (
                            "How often do patients in your community obtain "
                            "antibiotics without prescriptions?"
                        ),
                    },
                    {
                        "type": "comment",
                        "name": "chw_collaboration",
                        "title": (
                            "Do you collaborate with community health workers "
                            "(Binomes) to address inappropriate antibiotic use? "
                            "If not, why?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "informal_vendor_training",
                        "title": (
                            "Are informal vendors in your area trained on AMR risks "
                            "or regulated by local authorities?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "digital_tools_amr",
                        "title": (
                            "Do you use e-Ubuzima or other digital tools to report "
                            "AMR cases or access treatment guidelines?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "remoteness_impact",
                        "title": (
                            "How does geographic remoteness impact your ability "
                            "to manage infections appropriately?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "traditional_remedies_belief",
                        "title": (
                            "Do you believe traditional remedies "
                            "(e.g., umuravumba, igikakarubamba) can cure infections "
                            "without antibiotics?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "suggested_traditional_medicine",
                        "title": (
                            "Have you ever suggested to your patients traditional "
                            "medicine instead of antibiotics?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "cost_informal_antibiotics",
                        "title": (
                            "Do you think the cost of visiting a clinic (even with "
                            "Mutuelle de Sante) can influence patients to buy "
                            "antibiotics informally?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "antibiotics_strong_medicine",
                        "title": (
                            'Do you think antibiotics are seen as "strong medicine" '
                            "(ubuvuzi bukomeye) in your community?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "local_amr_terms",
                        "title": (
                            "Are there local terms or phrases that describe AMR "
                            "(e.g., medicine that no longer works)?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "religious_leader_influence",
                        "title": (
                            "How do religious or community leaders influence "
                            "health-seeking behaviors?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "pbf_prescribing",
                        "title": (
                            "How does performance-based financing affect "
                            "antibiotic prescribing habits?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "mch_amr_integration",
                        "title": (
                            "Are maternal and child health programs (e.g., PMTCT) "
                            "integrated with AMR stewardship efforts?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "insurance_diagnostics",
                        "title": (
                            "Do community health insurance schemes "
                            "(Mutuelle de Sante) cover diagnostic tests to reduce "
                            "unnecessary antibiotic use?"
                        ),
                        "isRequired": True,
                    },
                ],
            },
        ],
    }


def build_chw():
    return {
        "title": "CHW and Patient KAP Survey on Antimicrobial Resistance",
        "description": (
            "Stream A2 - Community KAP & Drivers. IRB Ref. No. 279/CMHSIRB/2026. "
            "Form version CHW-PATIENT-KAP-v1.0"
        ),
        "showProgressBar": "top",
        "progressBarType": "pages",
        "showPreviewBeforeComplete": "showAllQuestions",
        "previewText": "Review Answers",
        "editText": "Edit",
        "completeText": "Submit",
        "completedHtml": (
            "<h3>Thank you.</h3><p>Your responses will contribute to research aimed "
            "at improving rational antimicrobial use and antimicrobial stewardship "
            "in Rwanda.</p>"
        ),
        "pages": [
            {
                "name": "consent_routing",
                "title": "Consent and Respondent Category",
                "elements": [
                    {
                        "type": "html",
                        "name": "consent_info",
                        "html": (
                            "<p>We will collect your name and telephone number to "
                            "enable the research team to contact you if clarification "
                            "or study-related follow-up is required. This identifying "
                            "information will be kept confidential and will only be "
                            "accessible to authorized members of the research team. "
                            "Your name and telephone number will be stored separately "
                            "from the research dataset and linked to your responses "
                            "using a unique Study Participant ID.</p>"
                        ),
                    },
                    {
                        "type": "text",
                        "name": "participant_name",
                        "title": "Participant full name (restricted contact field)",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "participant_telephone",
                        "title": "Telephone number (restricted contact field)",
                        "inputType": "tel",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "site_code",
                        "title": "Study site / community code",
                        "isRequired": True,
                    },
                    {
                        "type": "radiogroup",
                        "name": "consent_status",
                        "title": "Do you consent to participate in this study?",
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "html",
                        "name": "consent_stop",
                        "visibleIf": "{consent_status} = 'No'",
                        "html": (
                            '<div class="alert alert-warning">Consent declined. '
                            "Do not continue enrolment.</div>"
                        ),
                    },
                    {
                        "type": "radiogroup",
                        "name": "participant_category",
                        "title": (
                            "Select which category you belong to in your community."
                        ),
                        "isRequired": True,
                        "visibleIf": "{consent_status} = 'Yes'",
                        "choices": ["Community Health Worker", "Patient"],
                    },
                ],
            },
            {
                "name": "demographics",
                "title": "Demographics and Residence",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "radiogroup",
                        "name": "sex",
                        "title": "What is your sex?",
                        "isRequired": True,
                        "choices": ["Female", "Male"],
                    },
                    {
                        "type": "text",
                        "name": "date_of_birth",
                        "title": "What is your date of birth?",
                        "inputType": "date",
                        "isRequired": True,
                    },
                    {
                        "type": "radiogroup",
                        "name": "age_finished_education",
                        "title": (
                            "How old in years were you when you finished "
                            "your education?"
                        ),
                        "choices": ["<15", "16-19", "20+", "Still studying"],
                    },
                    {
                        "type": "dropdown",
                        "name": "socio_professional_category",
                        "title": "What is your socio-professional category?",
                        "choices": [
                            "Self-employed",
                            "Managers",
                            "Other white office worker",
                            "Manual workers",
                            "House persons",
                            "Unemployed",
                            "Retired",
                            "Students",
                            "Other",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "difficulty_paying_bills",
                        "title": "How often do you have difficulties paying bills?",
                        "isRequired": True,
                        "choices": [
                            "Most of the time",
                            "From time to time",
                            "Almost never/Never",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "residence_setting",
                        "title": (
                            "How would you describe the area where you currently live?"
                        ),
                        "choices": ["Rural", "Urban", "Peri-urban", "Other"],
                    },
                    {
                        "type": "html",
                        "name": "residence_location_note",
                        "html": (
                            "<strong>Residence location</strong> "
                            "(cascading Rwanda administrative locations)"
                        ),
                    },
                    {
                        "type": "dropdown",
                        "name": "province_id",
                        "title": "Province",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "district_id",
                        "title": "District",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "sector_id",
                        "title": "Sector",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "cell_id",
                        "title": "Cell",
                        "isRequired": True,
                    },
                    {
                        "type": "dropdown",
                        "name": "village_id",
                        "title": "Village",
                        "isRequired": True,
                    },
                    {
                        "type": "text",
                        "name": "travel_time_first_care",
                        "title": "Approximate travel time to first healthcare facility",
                        "inputType": "number",
                    },
                    {
                        "type": "dropdown",
                        "name": "travel_time_unit",
                        "title": "Travel time unit",
                        "choices": ["Minutes", "Hours"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "health_insurance_status",
                        "title": "Do you currently have health insurance?",
                        "choices": ["Yes", "No", "Don't know/Not sure"],
                    },
                    {
                        "type": "text",
                        "name": "health_insurance_scheme",
                        "title": "Insurance scheme (e.g., Mutuelle de Sante)",
                        "visibleIf": "{health_insurance_status} = 'Yes'",
                    },
                ],
            },
            {
                "name": "knowledge_attitudes",
                "title": "Knowledge and Attitudes",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "matrix",
                        "name": "antibiotic_knowledge_tf",
                        "title": (
                            "For each statement, indicate whether you think "
                            "it is true or false."
                        ),
                        "isRequired": True,
                        "rows": [
                            {
                                "value": "antibiotics_kill_viruses",
                                "text": "Antibiotics kill viruses",
                            },
                            {
                                "value": "antibiotics_effective_colds",
                                "text": "Antibiotics are effective against colds",
                            },
                            {
                                "value": "unnecessary_use_ineffective",
                                "text": (
                                    "Unnecessary use makes antibiotics "
                                    "become ineffective"
                                ),
                            },
                            {
                                "value": "side_effects_diarrhoea",
                                "text": (
                                    "Taking antibiotics often has side-effects "
                                    "such as diarrhoea"
                                ),
                            },
                        ],
                        "columns": ["True", "False"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "when_stop_antibiotics",
                        "title": (
                            "When do you think you should stop taking antibiotics "
                            "once you have begun a course of treatment?"
                        ),
                        "choices": [
                            "When you feel better",
                            (
                                "When you have taken all antibiotics as directed "
                                "by your doctor"
                            ),
                            "Do not know",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "when_stop_antibiotics_other",
                        "title": "Specify other answer",
                        "visibleIf": "{when_stop_antibiotics} = 'Other'",
                    },
                    {
                        "type": "radiogroup",
                        "name": "received_info_unnecessary_use",
                        "title": (
                            "In the last 12 months, do you remember getting any "
                            "information about not taking antibiotics unnecessarily, "
                            "for example for a cold?"
                        ),
                        "choices": ["Yes", "No", "I do not know"],
                    },
                    {
                        "type": "checkbox",
                        "name": "topics_more_information",
                        "title": (
                            "On which topics, if any, would you like to receive "
                            "more information?"
                        ),
                        "choices": [
                            "Resistance to antibiotics",
                            "How to use antibiotics",
                            "Medical conditions for which antibiotics are used",
                            "Prescription of antibiotics",
                            (
                                "Links between human, animal and "
                                "environmental health"
                            ),
                            "I don't want more information",
                            "Don't know",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "topics_more_information_other",
                        "title": "Specify other topic",
                        "visibleIf": "{topics_more_information} contains 'Other'",
                    },
                    {
                        "type": "checkbox",
                        "name": "trusted_information_sources",
                        "title": (
                            "Which sources would you use to get trustworthy "
                            "information on antibiotics?"
                        ),
                        "isRequired": True,
                        "choices": [
                            "Doctor",
                            "Nurse",
                            "Pharmacist",
                            "Hospital",
                            "Another health care facility",
                            "Family/friends",
                            "Official health-related website",
                            "Another health-related website",
                            "Online social networks",
                            "TV",
                            "Radio",
                            "Not interested",
                            "Don't know",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "trusted_information_sources_other",
                        "title": "Specify other source",
                        "visibleIf": "{trusted_information_sources} contains 'Other'",
                    },
                    {
                        "type": "radiogroup",
                        "name": "level_to_tackle_amr",
                        "title": (
                            "At what level do you believe it is most effective "
                            "to tackle resistance to antibiotics?"
                        ),
                        "isRequired": True,
                        "choices": [
                            "Individual/family",
                            "Regional",
                            "National",
                            "Global",
                            "Action at all levels",
                            "Don't know",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "sick_animals_antibiotics",
                        "title": (
                            "To what extent do you agree or disagree that sick farm "
                            "animals should be treated with antibiotics if this is "
                            "the most appropriate treatment?"
                        ),
                        "choices": LIKERT5,
                    },
                    {
                        "type": "radiogroup",
                        "name": "one_health_excess_use",
                        "title": (
                            "Do you know that consuming products such as meat or milk "
                            "from animals treated with excessive antibiotics, or "
                            "fruits/vegetables treated with excessive pesticides, "
                            "can contribute to antimicrobial resistance?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Maybe", "Don't know"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "information_changed_views",
                        "title": (
                            "Did the information that you received change your "
                            "views on using antibiotics?"
                        ),
                        "visibleIf": "{received_info_unnecessary_use} = 'Yes'",
                        "isRequired": True,
                        "choices": ["Yes", "No", "Don't know"],
                    },
                    {
                        "type": "checkbox",
                        "name": "source_unnecessary_use_info",
                        "title": (
                            "Where did you get information about not taking "
                            "antibiotics unnecessarily?"
                        ),
                        "visibleIf": "{received_info_unnecessary_use} = 'Yes'",
                        "isRequired": True,
                        "choices": [
                            "Doctor",
                            "Pharmacist",
                            "Other health professional/nurse",
                            "Family/friend",
                            "TV advertisement",
                            "Internet/social networks",
                            "Leaflet/poster",
                            "Newspaper",
                            "TV news/programmes",
                            "Radio",
                            "Don't know",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "source_unnecessary_use_info_other",
                        "title": "Specify other information source",
                        "visibleIf": "{source_unnecessary_use_info} contains 'Other'",
                    },
                ],
            },
            {
                "name": "antibiotic_use",
                "title": "Antibiotic Use Pathway",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "checkbox",
                        "name": "cold_flu_antibiotic_source",
                        "title": (
                            "If you suffered from a cold or flu, did you take "
                            "any antibiotics?"
                        ),
                        "isRequired": True,
                        "choices": [
                            "No, I did not take antibiotics",
                            "Yes, from a medical prescription",
                            "Yes, administered by a medical practitioner",
                            "Yes, leftover from a previous course",
                            "Yes, without prescription from a pharmacy",
                            "Don't remember",
                            "Don't know",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "antibiotics_last_12m",
                        "title": (
                            "Have you taken any antibiotics orally such as tablets, "
                            "powder or syrup in the last 12 months?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No", "Don't know"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "last_antibiotic_source",
                        "title": (
                            "How did you obtain the last course of antibiotics "
                            "that you used?"
                        ),
                        "visibleIf": "{antibiotics_last_12m} = 'Yes'",
                        "choices": [
                            "Medical prescription",
                            "Administered by medical practitioner",
                            "Left over from previous course",
                            "Without prescription from pharmacy",
                            "Without prescription from elsewhere",
                            "Don't remember",
                            "Don't know",
                        ],
                    },
                    {
                        "type": "checkbox",
                        "name": "last_antibiotic_reason",
                        "title": (
                            "What was the reason for last taking the antibiotics "
                            "that you used?"
                        ),
                        "visibleIf": "{antibiotics_last_12m} = 'Yes'",
                        "choices": [
                            "Pneumonia",
                            "Bronchitis",
                            "Rhinopharyngitis",
                            "Flu",
                            "Colds",
                            "Sore throat",
                            "Cough",
                            "Fever",
                            "Headache",
                            "Diarrhoea",
                            "UTI",
                            "Skin/wound infection",
                            "COVID-19",
                            "Other",
                            "Don't know",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "last_antibiotic_reason_other",
                        "title": "Specify other reason",
                        "visibleIf": "{last_antibiotic_reason} contains 'Other'",
                    },
                    {
                        "type": "radiogroup",
                        "name": "diagnostic_test_before_antibiotic",
                        "title": (
                            "Did you have a test (e.g., blood/urine test or throat "
                            "swab) to find out what was causing your illness before "
                            "or when you started antibiotics?"
                        ),
                        "visibleIf": "{antibiotics_last_12m} = 'Yes'",
                        "choices": ["Yes", "No", "Don't remember", "Don't know"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "antibiotic_expectation_request",
                        "title": (
                            "Have you ever asked for or expected an antibiotic when "
                            "a healthcare provider did not recommend one?"
                        ),
                        "visibleIf": "{participant_category} = 'Patient'",
                        "choices": ["Yes", "No", "Don't remember/Not sure"],
                    },
                    {
                        "type": "radiogroup",
                        "name": "last_course_completed",
                        "title": (
                            "Thinking about the most recent antibiotic course "
                            "prescribed for you, did you take it for the full "
                            "duration as instructed?"
                        ),
                        "visibleIf": "{participant_category} = 'Patient'",
                        "choices": [
                            "Yes",
                            "No",
                            "Don't remember",
                            "Not applicable/no previous prescribed course",
                        ],
                    },
                    {
                        "type": "checkbox",
                        "name": "noncompletion_reason",
                        "title": (
                            "What was the main reason you did not complete "
                            "the antibiotic course?"
                        ),
                        "visibleIf": (
                            "{participant_category} = 'Patient' and "
                            "{last_course_completed} = 'No'"
                        ),
                        "choices": [
                            "Felt better",
                            "Side effects",
                            "Forgot/missed doses",
                            "Could not obtain/afford full course",
                            "Advice from another person",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "noncompletion_reason_other",
                        "title": "Specify other reason",
                        "visibleIf": "{noncompletion_reason} contains 'Other'",
                    },
                    {
                        "type": "radiogroup",
                        "name": "previous_resistance_experience",
                        "title": (
                            "Have you ever been told by a healthcare provider that "
                            "an infection you had was resistant to an antibiotic, "
                            "or that an antibiotic was not working against "
                            "the infection?"
                        ),
                        "visibleIf": "{participant_category} = 'Patient'",
                        "choices": ["Yes", "No", "Don't know/Don't remember"],
                    },
                ],
            },
            {
                "name": "one_health",
                "title": "One Health / Livestock Exposure",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "radiogroup",
                        "name": "livestock_exposure",
                        "title": (
                            "Do you or anyone in your household currently keep "
                            "livestock, or do you regularly work with livestock?"
                        ),
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "checkbox",
                        "name": "livestock_types",
                        "title": (
                            "Which animals do you/your household keep or "
                            "regularly work with?"
                        ),
                        "visibleIf": "{livestock_exposure} = 'Yes'",
                        "choices": [
                            "Cattle",
                            "Goats",
                            "Sheep",
                            "Pigs",
                            "Poultry",
                            "Rabbits",
                            "Other",
                        ],
                    },
                    {
                        "type": "radiogroup",
                        "name": "animal_antimicrobial_use",
                        "title": (
                            "In the past 6 months, have antimicrobials/antibiotics "
                            "been used for these animals?"
                        ),
                        "visibleIf": "{livestock_exposure} = 'Yes'",
                        "choices": ["Yes", "No", "Don't know"],
                    },
                    {
                        "type": "checkbox",
                        "name": "animal_antimicrobial_purpose",
                        "title": (
                            "For what purpose were the antimicrobials/"
                            "antibiotics used?"
                        ),
                        "visibleIf": "{animal_antimicrobial_use} = 'Yes'",
                        "choices": [
                            "Treatment of sick animals",
                            "Prevention of disease",
                            "Growth promotion",
                            "Other",
                            "Don't know",
                        ],
                    },
                    {
                        "type": "checkbox",
                        "name": "animal_antimicrobial_source_advice",
                        "title": (
                            "Who usually advises or provides the antimicrobial/"
                            "antibiotic used for the animals?"
                        ),
                        "visibleIf": "{animal_antimicrobial_use} = 'Yes'",
                        "choices": [
                            "Veterinary professional/animal-health worker",
                            "Pharmacy/agro-vet/drug shop",
                            "Farmer/household decision",
                            "Other",
                            "Don't know",
                        ],
                    },
                ],
            },
            {
                "name": "rwanda_context",
                "title": "Rwanda Context Questions",
                "visibleIf": "{consent_status} = 'Yes'",
                "elements": [
                    {
                        "type": "comment",
                        "name": "informal_antibiotic_access",
                        "title": (
                            "How often do people in your community obtain antibiotics "
                            "without prescriptions (e.g., from a local pharmacy, "
                            "health facility or animal-care facility)?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "traditional_remedies_belief",
                        "title": (
                            "Do you believe traditional remedies "
                            "(e.g., umuravumba, igikakarubamba) can cure infections "
                            "without antibiotics? Please explain your view."
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "suggest_traditional_medicine",
                        "title": (
                            "Have you ever suggested traditional medicine instead "
                            "of antibiotics? Please explain."
                        ),
                        "visibleIf": (
                            "{participant_category} = 'Community Health Worker'"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "used_traditional_medicine",
                        "title": (
                            "Have you ever used traditional medicine instead of "
                            "antibiotics? Please explain."
                        ),
                        "visibleIf": "{participant_category} = 'Patient'",
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "cost_informal_purchase",
                        "title": (
                            "Do you think the cost of visiting a clinic, even with "
                            "Mutuelle de Sante, can influence people to buy "
                            "antibiotics informally? Please explain."
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "antibiotics_strong_medicine",
                        "title": (
                            "Do you think antibiotics are seen as 'strong medicine' "
                            "(ubuvuzi bukomeye) in your community? Please explain."
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "local_amr_terms",
                        "title": (
                            "Are there local terms or phrases that describe "
                            "antimicrobial resistance "
                            "(e.g., medicine that no longer works)?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "leader_influence",
                        "title": (
                            "How do religious or community leaders influence "
                            "health-seeking behaviours, including decisions "
                            "about antibiotics?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "insurance_diagnostics",
                        "title": (
                            "In your experience, does Mutuelle de Sante cover "
                            "diagnostic tests that may help reduce unnecessary "
                            "antibiotic use? Please explain."
                        ),
                        "isRequired": True,
                    },
                ],
            },
            {
                "name": "chw_experience",
                "title": "CHW-Specific Experience",
                "visibleIf": (
                    "{consent_status} = 'Yes' and "
                    "{participant_category} = 'Community Health Worker'"
                ),
                "elements": [
                    {
                        "type": "radiogroup",
                        "name": "chw_antibiotic_counselling",
                        "title": (
                            "In your CHW role, do you provide patients or households "
                            "with advice about appropriate antibiotic use?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "comment",
                        "name": "chw_antibiotic_counselling_describe",
                        "title": "Please describe the advice you provide.",
                        "visibleIf": "{chw_antibiotic_counselling} = 'Yes'",
                    },
                    {
                        "type": "checkbox",
                        "name": "chw_referral_infection",
                        "title": (
                            "When you suspect that a community member has an "
                            "infection requiring assessment or treatment, where "
                            "do you usually refer them?"
                        ),
                        "choices": [
                            "Health post",
                            "Health centre",
                            "District hospital",
                            "Private clinic",
                            "Pharmacy",
                            "Other",
                        ],
                    },
                    {
                        "type": "text",
                        "name": "chw_referral_infection_other",
                        "title": "Specify other referral destination",
                        "visibleIf": "{chw_referral_infection} contains 'Other'",
                    },
                    {
                        "type": "comment",
                        "name": "chw_nonprescription_experience",
                        "title": (
                            "What situations have you observed in which people "
                            "obtain or use antibiotics without a prescription?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "radiogroup",
                        "name": "chw_adherence_support",
                        "title": (
                            "Do you provide advice or follow-up to help patients "
                            "take prescribed antibiotics correctly?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "comment",
                        "name": "chw_adherence_support_describe",
                        "title": "Please describe the advice or follow-up.",
                        "visibleIf": "{chw_adherence_support} = 'Yes'",
                    },
                    {
                        "type": "radiogroup",
                        "name": "chw_amr_education",
                        "title": (
                            "Have you received training or educational materials "
                            "on antibiotics or antimicrobial resistance for "
                            "your CHW work?"
                        ),
                        "isRequired": True,
                        "choices": ["Yes", "No"],
                    },
                    {
                        "type": "comment",
                        "name": "chw_amr_education_source",
                        "title": "What was the source/type of training or materials?",
                        "visibleIf": "{chw_amr_education} = 'Yes'",
                    },
                    {
                        "type": "comment",
                        "name": "chw_community_barriers",
                        "title": (
                            "What are the main challenges you face when trying to "
                            "promote appropriate antibiotic use in your community?"
                        ),
                        "isRequired": True,
                    },
                    {
                        "type": "comment",
                        "name": "chw_amr_support_needed",
                        "title": (
                            "What training, tools, information or support would help "
                            "you address inappropriate antibiotic use and AMR "
                            "in your community?"
                        ),
                        "isRequired": True,
                    },
                ],
            },
        ],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hcw = build_hcw()
    chw = build_chw()
    hcw_path = OUT / "hcw_kap_survey.json"
    chw_path = OUT / "chw_patient_kap_survey.json"
    hcw_path.write_text(json.dumps(hcw, ensure_ascii=False, indent=2), encoding="utf-8")
    chw_path.write_text(json.dumps(chw, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {hcw_path}")
    print(f"Wrote {chw_path}")
    print(f"HCW pages: {len(hcw['pages'])}")
    print(f"CHW pages: {len(chw['pages'])}")


if __name__ == "__main__":
    main()
