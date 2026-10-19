#!/usr/bin/env python3
"""Build Reproductive Health Instrument A — Participant Questionnaire (RH-PARTICIPANT-v1.0).

Source: Reproductive_Health_Questionnaire_revised.docx
Instrument B (practitioners) is not included — the document has no B item table yet.

Run:
    python scripts/build_rh_participant_v1.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "database" / "samples" / "reproductive_health_participant_survey.json"

FORM_VERSION = "RH-PARTICIPANT-v1.0"
TITLE = (
    "Assessment of Reproductive Health Disorders in Reproductive-Age Women (18–49)"
)
DESCRIPTION = (
    "Instrument A — Participant Questionnaire. Self-reported features for early detection "
    "of reproductive and hormonal health conditions (PCOS, endometriosis, uterine fibroids, "
    f"thyroid problems and infertility). Form version {FORM_VERSION}."
)

CONSENT_HTML = (
    "<p>You are invited to take part in a study on the early detection of reproductive and "
    "hormonal health conditions such as PCOS, endometriosis, uterine fibroids, thyroid "
    "problems and infertility. We will ask about your menstrual history, symptoms, past "
    "pregnancies, infections, family history, lifestyle and your views on digital health "
    "tools. Some questions are personal; you may skip any question or stop at any time "
    "without consequence. No name, phone number, national ID, e-mail or date of birth is "
    "recorded; your answers are stored under a study code. Your answers may be linked to a "
    "clinical assessment by a health worker only if you give separate consent for that. "
    "Information will be used only for research and reported in aggregate.</p>"
)

YN = [{"value": 1, "text": "Yes"}, {"value": 0, "text": "No"}]
YN_NS = YN + [{"value": 2, "text": "Not sure"}]
YN_NS_PNA = YN_NS + [{"value": 9, "text": "Prefer not to answer"}]
YN_PNA = YN + [{"value": 9, "text": "Prefer not to answer"}]
LIKERT5 = [
    {"value": 1, "text": "Strongly disagree"},
    {"value": 2, "text": "Disagree"},
    {"value": 3, "text": "Neutral"},
    {"value": 4, "text": "Agree"},
    {"value": 5, "text": "Strongly agree"},
]
FH_CODING = [
    {"value": 0, "text": "No"},
    {"value": 1, "text": "Yes – first-degree"},
    {"value": 2, "text": "Yes – second-degree only"},
    {"value": 9, "text": "Don't know"},
]
FREQ5 = [
    {"value": 0, "text": "Never"},
    {"value": 1, "text": "Rarely"},
    {"value": 2, "text": "Sometimes"},
    {"value": 3, "text": "Often"},
    {"value": 4, "text": "Always"},
]

CONDITIONS = [
    ("pcos", "polycystic ovary syndrome (PCOS)"),
    ("fibroid", "uterine fibroids"),
    ("endo", "endometriosis"),
    ("hypothy", "underactive thyroid (hypothyroidism)"),
    ("hyperthy", "overactive thyroid (hyperthyroidism)"),
    ("goitre", "enlarged thyroid / goitre"),
    ("ovcyst", "ovarian cyst"),
    ("hyperprl", "high prolactin"),
    ("poi", "early menopause / premature ovarian insufficiency"),
    ("adenomyosis", "adenomyosis"),
]

# Symptom checklist — mixed presentation order (analysis clusters not shown to participant)
SYMPTOMS = [
    ("sym_fatigue", "Feeling unusually tired or low in energy most days"),
    ("sym_weight_gain", "Unexplained weight gain"),
    ("sym_cold_intol", "Feeling cold when others are comfortable"),
    ("sym_constip", "Constipation"),
    ("sym_dry_skin", "Dry skin"),
    ("sym_hair_thinning", "Thinning of scalp hair"),
    ("sym_swelling", "Swelling of hands, feet or face"),
    ("sym_weight_loss", "Unexplained weight loss"),
    ("sym_heat_intol", "Feeling hot when others are comfortable / heat intolerance"),
    ("sym_palpitations", "Heart racing or palpitations"),
    ("sym_tremor", "Shaking of the hands"),
    ("sym_sweating", "Excessive sweating"),
    ("sym_anxiety_irrit", "Feeling anxious, irritable or restless"),
    ("sym_neck_swelling", "Swelling or fullness at the front of the neck"),
    ("sym_hirsutism", "Excess hair on the face, chest or abdomen"),
    ("sym_acne", "Acne that continues after adolescence or is hard to treat"),
    ("sym_alopecia_androgen", "Thinning of hair at the crown or temples"),
    ("sym_weight_gain_central", "Weight gain mainly around the abdomen"),
    ("sym_skin_tags", "Skin tags (small soft growths on the skin)"),
    ("sym_oligomenorrhoea", "Fewer than 8 periods in a year"),
    ("sym_infertility_sym", "Difficulty becoming pregnant"),
    ("sym_pelvic_pain_chronic", "Pelvic or lower abdominal pain lasting 6 months or more"),
    ("sym_dyspareunia_deep", "Deep pain during intercourse"),
    ("sym_dyschezia", "Pain when passing stool, especially during periods"),
    ("sym_dysuria_cyclic", "Pain when passing urine that is worse during periods"),
    ("sym_cyclical_gi", "Bloating, diarrhoea or constipation that worsens with periods"),
    ("sym_cyclical_fatigue", "Marked tiredness that worsens with periods"),
    ("sym_infertility_endo", "Difficulty becoming pregnant with pelvic pain"),
    ("sym_acanthosis", "Darkened skin on the neck or armpits"),
    ("sym_abdominal_mass", "A feeling of a lump or swelling in the lower abdomen"),
    ("sym_pelvic_pressure", "Pressure, heaviness or fullness in the pelvis"),
    ("sym_urinary_freq", "Needing to pass urine more often than before"),
    ("sym_urinary_retention", "Difficulty emptying the bladder completely"),
    ("sym_back_pain", "Lower back pain not explained by work or injury"),
    ("sym_anaemia", "Dizziness, breathlessness on exertion, or told you have low blood (anaemia)"),
    ("sym_galactorrhoea", "Milky discharge from the breasts when not breastfeeding"),
    ("sym_hot_flushes", "Hot flushes or night sweats"),
    ("sym_vaginal_dryness", "Vaginal dryness", True),
    ("sym_low_libido", "Reduced sexual desire", True),
    ("sym_headache_visual", "Frequent headaches with visual disturbance"),
]


def coded(choices: list[dict]) -> list[dict]:
    return choices


def other_text(name: str, title: str, visible_if: str) -> dict:
    return {
        "type": "text",
        "name": name,
        "title": title,
        "isRequired": True,
        "visibleIf": visible_if,
    }


def radio(name: str, title: str, choices: list[dict], **kw) -> dict:
    q: dict = {
        "type": "radiogroup",
        "name": name,
        "title": title,
        "choices": choices,
    }
    q.update(kw)
    return q


def drop(name: str, title: str, choices: list[dict], **kw) -> dict:
    q: dict = {
        "type": "dropdown",
        "name": name,
        "title": title,
        "choices": choices,
    }
    q.update(kw)
    return q


def num(name: str, title: str, min_v=None, max_v=None, **kw) -> dict:
    q: dict = {
        "type": "text",
        "name": name,
        "title": title,
        "inputType": "number",
    }
    validators = []
    if min_v is not None or max_v is not None:
        v: dict = {"type": "numeric"}
        if min_v is not None:
            v["minValue"] = min_v
        if max_v is not None:
            v["maxValue"] = max_v
        validators.append(v)
    if validators:
        q["validators"] = validators
    q.update(kw)
    return q


def check(name: str, title: str, choices: list[dict], **kw) -> dict:
    q: dict = {
        "type": "checkbox",
        "name": name,
        "title": title,
        "choices": choices,
    }
    q.update(kw)
    return q


def page_admin() -> dict:
    return {
        "name": "a0_admin",
        "title": "A0. Administrative and consent",
        "elements": [
            {
                "type": "html",
                "name": "consent_info",
                "html": CONSENT_HTML,
            },
            {
                "type": "text",
                "name": "participant_id",
                "title": "Study participant code",
                "description": "Format RH-DD-SSSS-NNNN (district, sector, serial). Never a name or phone.",
                "isRequired": True,
            },
            {
                "type": "text",
                "name": "interview_date",
                "title": "Date of interview",
                "inputType": "date",
                "isRequired": True,
                "defaultValueExpression": "today()",
                "maxValueExpression": "today()",
            },
            drop(
                "interview_mode",
                "Mode of administration",
                [
                    {"value": 1, "text": "Self-administered online"},
                    {"value": 2, "text": "Self-administered paper"},
                    {"value": 3, "text": "Interviewer-assisted"},
                ],
                isRequired=True,
            ),
            {
                "type": "text",
                "name": "interviewer_id",
                "title": "Interviewer code",
                "visibleIf": "{interview_mode} = 3",
                "isRequired": True,
            },
            drop(
                "language",
                "Language of administration",
                [
                    {"value": 1, "text": "Kinyarwanda"},
                    {"value": 2, "text": "English"},
                    {"value": 3, "text": "French"},
                ],
                isRequired=True,
            ),
            radio(
                "consent_survey",
                "Do you consent to participate in this survey?",
                YN,
                isRequired=True,
            ),
            {
                "type": "html",
                "name": "consent_declined_msg",
                "visibleIf": "{consent_survey} = 0",
                "html": (
                    "<p><strong>Thank you.</strong> Because you did not consent, the "
                    "questionnaire will end here. No further answers will be collected.</p>"
                ),
            },
            radio(
                "eligible",
                "Does the participant meet eligibility (female, aged 18–49, resident in a study district)?",
                YN,
                isRequired=True,
                visibleIf="{consent_survey} = 1",
            ),
            {
                "type": "html",
                "name": "ineligible_msg",
                "visibleIf": "{consent_survey} = 1 and {eligible} = 0",
                "html": (
                    "<p><strong>Not eligible.</strong> The questionnaire ends here.</p>"
                ),
            },
            radio(
                "consent_clinical_link",
                "Do you consent to link your answers with a clinical assessment (Instrument B)?",
                YN,
                isRequired=True,
                visibleIf="{consent_survey} = 1 and {eligible} = 1",
            ),
        ],
    }


def page_socio() -> dict:
    eligible = "{consent_survey} = 1 and {eligible} = 1"
    return {
        "name": "a1_sociodemographic",
        "title": "A1. Sociodemographic characteristics",
        "visibleIf": eligible,
        "elements": [
            num(
                "age_years",
                "How old are you (completed years)?",
                18,
                49,
                isRequired=True,
            ),
            {
                "type": "html",
                "name": "residence_note",
                "html": (
                    "<strong>Residence</strong><br>Select Province, then District, then Sector "
                    "from the Rwanda administrative location lists."
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
                "title": "In which district do you live?",
                "isRequired": True,
                "enableIf": "{province_id} notempty",
            },
            {
                "type": "dropdown",
                "name": "sector_id",
                "title": "In which sector do you live?",
                "isRequired": True,
                "enableIf": "{district_id} notempty",
            },
            drop(
                "residence_type",
                "How would you describe where you live?",
                [
                    {"value": 1, "text": "Urban"},
                    {"value": 2, "text": "Peri-urban"},
                    {"value": 3, "text": "Rural"},
                ],
                isRequired=True,
            ),
            drop(
                "marital_status",
                "What is your current marital status?",
                [
                    {"value": 1, "text": "Single, never married"},
                    {"value": 2, "text": "Married"},
                    {"value": 3, "text": "Living with partner (cohabiting)"},
                    {"value": 4, "text": "Divorced / separated"},
                    {"value": 5, "text": "Widowed"},
                ],
                isRequired=True,
            ),
            drop(
                "education",
                "What is the highest level of education you completed?",
                [
                    {"value": 0, "text": "No formal schooling"},
                    {"value": 1, "text": "Primary"},
                    {"value": 2, "text": "Lower secondary"},
                    {"value": 3, "text": "Upper secondary"},
                    {"value": 4, "text": "TVET / vocational"},
                    {"value": 5, "text": "University or higher"},
                ],
                isRequired=True,
            ),
            drop(
                "occupation",
                "What is your main occupation?",
                [
                    {"value": 1, "text": "Not employed / homemaker"},
                    {"value": 2, "text": "Student"},
                    {"value": 3, "text": "Farmer"},
                    {"value": 4, "text": "Self-employed / business"},
                    {"value": 5, "text": "Salaried, public sector"},
                    {"value": 6, "text": "Salaried, private sector"},
                    {"value": 7, "text": "Casual / daily labour"},
                    {"value": 8, "text": "Other (specify)"},
                ],
                isRequired=True,
            ),
            other_text(
                "occupation_other",
                "Other occupation — please specify",
                "{occupation} = 8",
            ),
            drop(
                "insurance",
                "Which health insurance do you currently have?",
                [
                    {"value": 1, "text": "CBHI (Mutuelle de Santé)"},
                    {"value": 2, "text": "RSSB / RAMA"},
                    {"value": 3, "text": "MMI"},
                    {"value": 4, "text": "Private"},
                    {"value": 5, "text": "None"},
                    {"value": 6, "text": "Other (specify)"},
                ],
                isRequired=True,
            ),
            other_text(
                "insurance_other",
                "Other insurance — please specify",
                "{insurance} = 6",
            ),
            drop(
                "ubudehe_category",
                "What is your household's Ubudehe category?",
                [
                    {"value": 1, "text": "Category 1"},
                    {"value": 2, "text": "Category 2"},
                    {"value": 3, "text": "Category 3"},
                    {"value": 4, "text": "Category 4"},
                    {"value": 99, "text": "Don't know"},
                ],
            ),
            num(
                "height_cm_self",
                "What is your height (cm), if you know it?",
                130,
                200,
            ),
            num(
                "weight_kg_self",
                "What is your current weight (kg), if you know it?",
                30,
                200,
            ),
        ],
    }


def page_menstrual() -> dict:
    eligible = "{consent_survey} = 1 and {eligible} = 1"
    menstruating = "{menstruating_now} = 1"
    amenorrhoea = "{amenorrhoea_ever} = 1"
    dysmen = "{dysmenorrhoea} = 1"
    return {
        "name": "a2_menstrual",
        "title": "A2. Menstrual history (past 12 months unless stated)",
        "visibleIf": eligible,
        "elements": [
            num(
                "menarche_age",
                "At what age did you have your first menstrual period?",
                8,
                20,
                description="Enter 99 if you don't remember.",
            ),
            drop(
                "menstruating_now",
                "Have you had menstrual periods in the past 12 months?",
                [
                    {"value": 1, "text": "Yes"},
                    {"value": 2, "text": "No – currently pregnant"},
                    {
                        "value": 3,
                        "text": "No – breastfeeding / within 6 months of delivery",
                    },
                    {
                        "value": 4,
                        "text": "No – contraceptive method stopped periods",
                    },
                    {
                        "value": 5,
                        "text": "No – no period for 3 months or more for another reason",
                    },
                    {"value": 6, "text": "No – hysterectomy or menopause"},
                ],
                isRequired=True,
            ),
            num(
                "cycle_length_days",
                "Usually, how many days are there from the first day of one period to the first day of the next?",
                14,
                120,
                visibleIf=menstruating,
                description="Enter 99 if you don't know or it is too variable.",
            ),
            drop(
                "cycle_regularity",
                "How regular are your periods?",
                [
                    {
                        "value": 1,
                        "text": "Regular – start within about the same week each month (varies ≤ 7 days)",
                    },
                    {"value": 2, "text": "Irregular – varies by more than 7 days"},
                    {
                        "value": 3,
                        "text": "Unpredictable – cannot say when the next will come",
                    },
                ],
                visibleIf=menstruating,
            ),
            num(
                "periods_last_12m",
                "How many periods did you have in the past 12 months?",
                0,
                13,
                visibleIf=menstruating,
                description="Enter 99 if you don't know.",
            ),
            num(
                "longest_gap_days",
                "In the past 12 months, what was the longest number of days you went without a period (excluding pregnancy)?",
                14,
                365,
                visibleIf=menstruating,
                description="Enter 99 if you don't know.",
            ),
            radio(
                "amenorrhoea_ever",
                "Have you ever gone 3 months or more without a period when you were not pregnant, not breastfeeding and not on a contraceptive that stops periods?",
                YN_NS,
                isRequired=True,
            ),
            num(
                "amenorrhoea_months",
                "How long did the longest such episode last (months)?",
                3,
                120,
                visibleIf=amenorrhoea,
                isRequired=True,
            ),
            radio(
                "return_bleeding_heavy",
                "When periods returned after that episode, were they heavier or longer than usual?",
                YN_NS,
                visibleIf=amenorrhoea,
            ),
            num(
                "bleeding_days",
                "How many days does your menstrual bleeding usually last?",
                1,
                15,
                visibleIf=menstruating,
            ),
            drop(
                "flow_volume",
                "How would you describe your usual menstrual flow?",
                [
                    {"value": 1, "text": "Light"},
                    {"value": 2, "text": "Moderate"},
                    {"value": 3, "text": "Heavy"},
                    {"value": 4, "text": "Very heavy"},
                ],
                visibleIf=menstruating,
            ),
            num(
                "pads_heaviest_day",
                "On your heaviest day, how many pads or cloths do you change?",
                0,
                25,
                visibleIf=menstruating,
            ),
            radio("clots", "Do you pass blood clots larger than a 100-franc coin?", YN, visibleIf=menstruating),
            radio(
                "flooding",
                "Does bleeding soak through your clothes or bedding?",
                YN,
                visibleIf=menstruating,
            ),
            drop(
                "bleeding_limits_activity",
                "How often does your bleeding stop you from doing your normal activities (work, school, chores)?",
                FREQ5,
                visibleIf=menstruating,
            ),
            radio(
                "intermenstrual_bleeding",
                "In the past 12 months, have you had bleeding or spotting between periods?",
                YN,
                visibleIf=menstruating,
            ),
            drop(
                "postcoital_bleeding",
                "In the past 12 months, have you had bleeding after sexual intercourse?",
                [
                    {"value": 1, "text": "Yes"},
                    {"value": 0, "text": "No"},
                    {"value": 3, "text": "Not applicable"},
                    {"value": 9, "text": "Prefer not to answer"},
                ],
                visibleIf=menstruating,
            ),
            radio(
                "dysmenorrhoea",
                "Do you have pain with your periods?",
                YN,
                visibleIf=menstruating,
            ),
            num(
                "dysmenorrhoea_nrs",
                "On a scale of 0 (no pain) to 10 (worst pain imaginable), how bad is your period pain usually?",
                0,
                10,
                visibleIf=f"{menstruating} and {dysmen}",
            ),
            drop(
                "dysmenorrhoea_meds",
                "Do you take painkillers for period pain?",
                [
                    {"value": 0, "text": "Never"},
                    {"value": 1, "text": "Some periods"},
                    {"value": 2, "text": "Every period"},
                ],
                visibleIf=f"{menstruating} and {dysmen}",
            ),
            radio(
                "dysmenorrhoea_absence",
                "In the past 12 months, did period pain make you miss work, school or daily activities?",
                YN,
                visibleIf=f"{menstruating} and {dysmen}",
            ),
            radio(
                "chronic_pelvic_pain",
                "Have you had pain in the lower abdomen or pelvis on days when you are NOT menstruating, for 6 months or longer?",
                YN,
            ),
            drop(
                "dyspareunia",
                "Do you have pain during or after sexual intercourse?",
                [
                    {"value": 1, "text": "Yes"},
                    {"value": 0, "text": "No"},
                    {"value": 3, "text": "Not applicable / not sexually active"},
                    {"value": 9, "text": "Prefer not to answer"},
                ],
            ),
            radio(
                "dyschezia",
                "Do you have pain when passing stool during your periods?",
                YN,
                visibleIf=menstruating,
            ),
            radio(
                "dysuria_menses",
                "Do you have pain when passing urine during your periods?",
                YN,
                visibleIf=menstruating,
            ),
            drop(
                "premenstrual_symptoms",
                "In the week before your period, how severe are symptoms such as mood changes, breast tenderness or bloating?",
                [
                    {"value": 0, "text": "None"},
                    {"value": 1, "text": "Mild"},
                    {"value": 2, "text": "Moderate"},
                    {"value": 3, "text": "Severe"},
                ],
                visibleIf=menstruating,
            ),
            drop(
                "cycle_tracking",
                "Do you keep track of your periods?",
                [
                    {"value": 0, "text": "No"},
                    {"value": 1, "text": "Calendar or notebook"},
                    {"value": 2, "text": "Phone app"},
                    {"value": 3, "text": "From memory only"},
                ],
            ),
        ],
    }


def page_obstetric() -> dict:
    eligible = "{consent_survey} = 1 and {eligible} = 1"
    ever_preg = "{ever_pregnant} = 1"
    infert = "{infertility_12m} = 1"
    using_contraception = "{contraception_now} notempty and {contraception_now} != 0"
    return {
        "name": "a3_obstetric",
        "title": "A3. Obstetric, fertility and contraceptive history",
        "visibleIf": eligible,
        "elements": [
            radio("ever_pregnant", "Have you ever been pregnant?", YN, isRequired=True),
            num("gravida", "How many times have you been pregnant in total?", 1, 20, visibleIf=ever_preg, isRequired=True),
            num("live_births", "How many live births have you had?", 0, 20, visibleIf=ever_preg),
            num(
                "miscarriages",
                "How many pregnancies ended in miscarriage (loss before 6 months)?",
                0,
                20,
                visibleIf=ever_preg,
            ),
            num("stillbirths", "How many pregnancies ended in stillbirth?", 0, 20, visibleIf=ever_preg),
            radio(
                "ectopic",
                "Have you ever had a pregnancy outside the womb (ectopic)?",
                YN_NS,
                visibleIf=ever_preg,
            ),
            num(
                "months_since_last_birth",
                "How many months since your last delivery?",
                0,
                600,
                visibleIf=ever_preg,
                description="Enter 888 if more than 24 months ago.",
            ),
            radio(
                "breastfeeding_now",
                "Are you currently breastfeeding?",
                YN,
                visibleIf=ever_preg,
            ),
            radio("pregnant_now", "Are you currently pregnant?", YN_NS, isRequired=True),
            drop(
                "trying_to_conceive",
                "Are you currently trying to become pregnant?",
                [
                    {"value": 1, "text": "Yes"},
                    {"value": 0, "text": "No"},
                    {"value": 3, "text": "Not applicable"},
                ],
            ),
            drop(
                "infertility_12m",
                "Have you ever tried to become pregnant for 12 months or more, with regular unprotected intercourse, without success?",
                [
                    {"value": 1, "text": "Yes"},
                    {"value": 0, "text": "No"},
                    {"value": 3, "text": "Never tried / not applicable"},
                ],
                isRequired=True,
            ),
            drop(
                "infertility_type",
                "Had you ever been pregnant before that?",
                [
                    {"value": 1, "text": "No – never pregnant (primary)"},
                    {"value": 2, "text": "Yes – previously pregnant (secondary)"},
                ],
                visibleIf=infert,
                isRequired=True,
            ),
            num(
                "infertility_months",
                "For how many months in total have you tried without success?",
                12,
                300,
                visibleIf=infert,
            ),
            check(
                "fertility_tests",
                "Which fertility investigations have you had? (tick all that apply)",
                [
                    {"value": 0, "text": "None"},
                    {"value": 1, "text": "Blood hormone tests"},
                    {"value": 2, "text": "Pelvic ultrasound"},
                    {"value": 3, "text": "Tubal test (HSG / dye test)"},
                    {"value": 4, "text": "Partner semen analysis"},
                    {"value": 5, "text": "Other (specify)"},
                    {"value": 9, "text": "Don't know"},
                ],
                visibleIf=infert,
            ),
            other_text(
                "fertility_tests_other",
                "Other fertility investigation — please specify",
                "{fertility_tests} contains 5",
            ),
            radio(
                "tubal_block_told",
                "Have you ever been told by a health worker that your fallopian tubes are blocked?",
                YN_NS,
                visibleIf=infert,
            ),
            drop(
                "contraception_now",
                "Which contraceptive method are you using at the moment?",
                [
                    {"value": 0, "text": "None"},
                    {"value": 1, "text": "Combined pill"},
                    {"value": 2, "text": "Progestogen-only pill"},
                    {"value": 3, "text": "Injectable (Depo-Provera / Sayana Press)"},
                    {"value": 4, "text": "Implant"},
                    {"value": 5, "text": "Hormonal IUD"},
                    {"value": 6, "text": "Copper IUD"},
                    {"value": 7, "text": "Condoms only"},
                    {"value": 8, "text": "Natural / calendar / withdrawal"},
                    {"value": 9, "text": "Female or male sterilisation"},
                    {"value": 10, "text": "Other (specify)"},
                ],
                isRequired=True,
            ),
            other_text(
                "contraception_other",
                "Other contraceptive method — please specify",
                "{contraception_now} = 10",
            ),
            num(
                "contraception_months",
                "For how many months have you used this method continuously?",
                0,
                600,
                visibleIf=using_contraception,
            ),
            radio(
                "hormonal_contraception_12m",
                "In the past 12 months, have you used any hormonal method (pill, injectable, implant, hormonal IUD) at any time, even if you stopped?",
                YN,
                isRequired=True,
            ),
            check(
                "gyn_procedures",
                "Have you ever had any of the following? (tick all that apply)",
                [
                    {"value": 0, "text": "None"},
                    {"value": 1, "text": "Caesarean section"},
                    {"value": 2, "text": "Surgery on the womb (e.g. fibroid removal)"},
                    {"value": 3, "text": "Surgery on an ovary (e.g. cyst removal)"},
                    {"value": 4, "text": "Surgery on the tubes"},
                    {"value": 5, "text": "Removal of the womb (hysterectomy)"},
                    {
                        "value": 6,
                        "text": "Procedure after miscarriage (curettage / MVA)",
                    },
                    {"value": 7, "text": "Other (specify)"},
                ],
            ),
            other_text(
                "gyn_procedures_other",
                "Other procedure — please specify",
                "{gyn_procedures} contains 7",
            ),
            drop(
                "miscarriage_procedure",
                "If you had a procedure after miscarriage, which one?",
                [
                    {"value": 1, "text": "Curettage (D&C)"},
                    {"value": 2, "text": "Manual vacuum aspiration (MVA)"},
                    {"value": 3, "text": "Medication only"},
                    {"value": 9, "text": "Not sure"},
                ],
                visibleIf="{gyn_procedures} contains 6",
            ),
        ],
    }


def condition_panel(code: str, label: str) -> dict:
    dx = f"{code}_dx"
    treated = f"{code}_treated_now"
    return {
        "type": "panel",
        "name": f"panel_{code}",
        "title": label[0].upper() + label[1:],
        "elements": [
            radio(
                dx,
                f"Has a doctor or nurse ever told you that you have {label}?",
                YN_NS,
                isRequired=True,
            ),
            num(
                f"{code}_dx_year",
                "In which year was this diagnosed?",
                1990,
                2100,
                visibleIf=f"{{{dx}}} = 1",
                description="Enter 9999 if you don't know.",
            ),
            drop(
                f"{code}_dx_method",
                "How was it diagnosed?",
                [
                    {"value": 1, "text": "Ultrasound scan"},
                    {"value": 2, "text": "Blood test"},
                    {"value": 3, "text": "Examination only"},
                    {"value": 4, "text": "Surgery / laparoscopy"},
                    {"value": 5, "text": "Combination"},
                    {"value": 9, "text": "Don't know"},
                ],
                visibleIf=f"{{{dx}}} = 1",
            ),
            radio(
                treated,
                "Are you currently receiving treatment for it?",
                YN,
                visibleIf=f"{{{dx}}} = 1",
            ),
            {
                "type": "text",
                "name": f"{code}_treatment",
                "title": "What treatment? (name of medicine or procedure)",
                "visibleIf": f"{{{dx}}} = 1 and {{{treated}}} = 1",
            },
        ],
    }


def page_diagnoses() -> dict:
    eligible = "{consent_survey} = 1 and {eligible} = 1"
    elements = [
        {
            "type": "html",
            "name": "a4_intro",
            "html": (
                "<p>Ask about each condition separately. Answer for every condition below.</p>"
            ),
        }
    ]
    for code, label in CONDITIONS:
        elements.append(condition_panel(code, label))
    elements.extend(
        [
            drop(
                "thyroid_med_now",
                "Are you currently taking any medicine for the thyroid?",
                [
                    {"value": 0, "text": "No"},
                    {"value": 1, "text": "Levothyroxine"},
                    {"value": 2, "text": "Carbimazole / methimazole / PTU"},
                    {"value": 3, "text": "Other (specify)"},
                    {"value": 9, "text": "Taking but don't know the name"},
                ],
                isRequired=True,
            ),
            other_text(
                "thyroid_med_other",
                "Other thyroid medicine — please specify",
                "{thyroid_med_now} = 3",
            ),
            num(
                "thyroid_med_months",
                "For how many months have you taken it?",
                0,
                600,
                visibleIf="{thyroid_med_now} != 0",
            ),
        ]
    )
    return {
        "name": "a4_diagnoses",
        "title": "A4. Previously diagnosed reproductive and endocrine conditions",
        "visibleIf": eligible,
        "elements": elements,
    }


def page_symptoms() -> dict:
    eligible = "{consent_survey} = 1 and {eligible} = 1"
    elements: list[dict] = [
        {
            "type": "html",
            "name": "a5_intro",
            "html": (
                "<p>In the <strong>past 6 months</strong>, have you experienced any of the "
                "following? Answer Yes or No for each item.</p>"
            ),
        }
    ]
    for item in SYMPTOMS:
        name, title = item[0], item[1]
        sensitive = len(item) > 2 and item[2]
        elements.append(
            radio(
                name,
                title,
                YN_PNA if sensitive else YN,
                isRequired=True,
            )
        )
    return {
        "name": "a5_symptoms",
        "title": "A5. Symptom checklist (past 6 months)",
        "visibleIf": eligible,
        "elements": elements,
    }


def page_infections() -> dict:
    eligible = "{consent_survey} = 1 and {eligible} = 1"
    sti = "{sti_ever} = 1"
    active = "{sexually_active_12m} = 1"
    return {
        "name": "a6_infections",
        "title": "A6. Infections and pelvic health",
        "visibleIf": eligible,
        "elements": [
            radio(
                "sti_ever",
                "Has a health worker ever diagnosed you with a sexually transmitted infection (e.g. gonorrhoea, chlamydia, syphilis, trichomonas)?",
                YN_NS_PNA,
                isRequired=True,
            ),
            check(
                "sti_type",
                "Which infection(s)? (tick all that apply)",
                [
                    {"value": 1, "text": "Gonorrhoea"},
                    {"value": 2, "text": "Chlamydia"},
                    {"value": 3, "text": "Syphilis"},
                    {"value": 4, "text": "Trichomonas"},
                    {"value": 5, "text": "Other (specify)"},
                    {"value": 9, "text": "Don't know"},
                ],
                visibleIf=sti,
                isRequired=True,
            ),
            other_text(
                "sti_type_other",
                "Other STI — please specify",
                "{sti_type} contains 5",
            ),
            radio(
                "sti_treatment_complete",
                "Did you complete the full treatment?",
                YN_NS,
                visibleIf=sti,
            ),
            radio(
                "discharge_12m",
                "In the past 12 months, have you had unusual vaginal discharge (change in colour, smell or amount)?",
                YN,
            ),
            radio(
                "pid_treated",
                "Have you ever been treated for a pelvic infection (infection of the womb or tubes)?",
                YN_NS,
            ),
            radio(
                "pelvic_pain_fever",
                "Have you ever had lower abdominal pain lasting more than 7 days together with fever or discharge?",
                YN,
            ),
            radio(
                "sexually_active_12m",
                "Have you been sexually active in the past 12 months?",
                YN_PNA,
                isRequired=True,
            ),
            num(
                "partners_12m",
                "How many sexual partners have you had in the past 12 months?",
                0,
                20,
                visibleIf=active,
                description="Enter 9 if you prefer not to answer.",
            ),
            drop(
                "condom_use",
                "How often did you or your partner use a condom in the past 12 months?",
                [
                    {"value": 0, "text": "Never"},
                    {"value": 1, "text": "Sometimes"},
                    {"value": 2, "text": "Always"},
                    {"value": 3, "text": "Not applicable"},
                ],
                visibleIf=active,
            ),
        ],
    }


def page_family() -> dict:
    eligible = "{consent_survey} = 1 and {eligible} = 1"
    items = [
        ("fh_pcos", "Has any blood relative been diagnosed with PCOS?"),
        ("fh_fibroids", "Has any blood relative been diagnosed with uterine fibroids?"),
        ("fh_endometriosis", "Has any blood relative been diagnosed with endometriosis?"),
        (
            "fh_thyroid",
            "Has any blood relative been diagnosed with a thyroid disorder or goitre?",
        ),
        ("fh_infertility", "Has any blood relative had difficulty becoming pregnant?"),
        ("fh_diabetes", "Has any blood relative been diagnosed with diabetes?"),
        (
            "fh_early_menopause",
            "Did your mother or a sister reach menopause before age 40?",
        ),
    ]
    return {
        "name": "a7_family",
        "title": "A7. Family history",
        "description": (
            "First-degree relatives = mother, sisters, daughters. "
            "Second-degree = grandmothers, aunts."
        ),
        "visibleIf": eligible,
        "elements": [
            drop(name, title, FH_CODING, isRequired=True) for name, title in items
        ],
    }


def page_lifestyle() -> dict:
    eligible = "{consent_survey} = 1 and {eligible} = 1"
    return {
        "name": "a8_lifestyle",
        "title": "A8. Medical history and lifestyle",
        "visibleIf": eligible,
        "elements": [
            radio("dx_diabetes", "Have you ever been diagnosed with diabetes?", YN_NS),
            radio(
                "dx_hypertension",
                "Have you ever been diagnosed with high blood pressure?",
                YN_NS,
            ),
            check(
                "dx_other_chronic",
                "Any other long-term illness? (tick all that apply)",
                [
                    {"value": 0, "text": "None"},
                    {"value": 1, "text": "Asthma"},
                    {"value": 2, "text": "Epilepsy"},
                    {"value": 3, "text": "Kidney disease"},
                    {"value": 4, "text": "Sickle cell disease"},
                    {"value": 5, "text": "Cancer"},
                    {"value": 6, "text": "Mental health condition"},
                    {"value": 7, "text": "Tuberculosis (ever)"},
                    {"value": 8, "text": "Other (specify)"},
                ],
            ),
            other_text(
                "dx_other_chronic_other",
                "Other long-term illness — please specify",
                "{dx_other_chronic} contains 8",
            ),
            check(
                "meds_current",
                "Which medicines do you take regularly? (tick all that apply)",
                [
                    {"value": 0, "text": "None"},
                    {"value": 1, "text": "Metformin"},
                    {"value": 2, "text": "Steroids (e.g. prednisolone)"},
                    {"value": 3, "text": "Anti-epileptic (e.g. sodium valproate)"},
                    {"value": 4, "text": "Antipsychotic / antidepressant"},
                    {
                        "value": 5,
                        "text": "Hormone treatment other than contraception",
                    },
                    {"value": 6, "text": "Traditional / herbal medicine"},
                    {"value": 7, "text": "Other (specify)"},
                ],
            ),
            other_text(
                "meds_current_other",
                "Other medicine — please specify",
                "{meds_current} contains 7",
            ),
            drop(
                "iodised_salt",
                "How often does your household use iodised salt?",
                [
                    {"value": 0, "text": "Never"},
                    {"value": 1, "text": "Rarely"},
                    {"value": 2, "text": "Sometimes"},
                    {"value": 3, "text": "Often"},
                    {"value": 4, "text": "Always"},
                    {"value": 9, "text": "Don't know"},
                ],
            ),
            drop(
                "seafood_freq",
                "How often do you eat fish or other seafood?",
                [
                    {"value": 0, "text": "Never"},
                    {"value": 1, "text": "Less than once a month"},
                    {"value": 2, "text": "1–3 times a month"},
                    {"value": 3, "text": "About once a week"},
                    {"value": 4, "text": "Several times a week"},
                ],
            ),
            drop(
                "smoking",
                "Do you smoke tobacco?",
                [
                    {"value": 0, "text": "Never"},
                    {"value": 1, "text": "Former smoker"},
                    {"value": 2, "text": "Current smoker"},
                ],
            ),
            drop(
                "alcohol_freq",
                "How often do you drink alcohol (including urwagwa / ikigage)?",
                [
                    {"value": 0, "text": "Never"},
                    {"value": 1, "text": "Monthly or less"},
                    {"value": 2, "text": "2–4 times a month"},
                    {"value": 3, "text": "2–3 times a week"},
                    {"value": 4, "text": "4 or more times a week"},
                ],
            ),
            num(
                "physical_activity_days",
                "On how many days in a typical week do you do at least 30 minutes of physical activity that makes you breathe harder (walking fast, farming, sport)?",
                0,
                7,
            ),
            num("sleep_hours", "How many hours do you usually sleep at night?", 2, 14),
            drop(
                "stress_uncontrol",
                "In the past month, how often have you felt that you were unable to control the important things in your life?",
                [
                    {"value": 0, "text": "Never"},
                    {"value": 1, "text": "Almost never"},
                    {"value": 2, "text": "Sometimes"},
                    {"value": 3, "text": "Fairly often"},
                    {"value": 4, "text": "Very often"},
                ],
            ),
            drop(
                "phq2_interest",
                "Over the past 2 weeks, how often have you had little interest or pleasure in doing things?",
                [
                    {"value": 0, "text": "Not at all"},
                    {"value": 1, "text": "Several days"},
                    {"value": 2, "text": "More than half the days"},
                    {"value": 3, "text": "Nearly every day"},
                ],
            ),
            drop(
                "phq2_down",
                "Over the past 2 weeks, how often have you felt down, depressed or hopeless?",
                [
                    {"value": 0, "text": "Not at all"},
                    {"value": 1, "text": "Several days"},
                    {"value": 2, "text": "More than half the days"},
                    {"value": 3, "text": "Nearly every day"},
                ],
            ),
        ],
    }


def page_digital() -> dict:
    eligible = "{consent_survey} = 1 and {eligible} = 1"
    sought = "{care_sought_12m} = 1"
    no_care = "{care_sought_12m} = 0"
    return {
        "name": "a9_digital",
        "title": "A9. Care-seeking and digital / AI readiness",
        "visibleIf": eligible,
        "elements": [
            drop(
                "care_sought_12m",
                "In the past 12 months, did you seek care for any menstrual, pelvic or hormonal symptom?",
                [
                    {"value": 1, "text": "Yes"},
                    {"value": 0, "text": "No, had symptoms but did not seek care"},
                    {"value": 2, "text": "No symptoms"},
                ],
                isRequired=True,
            ),
            check(
                "care_place",
                "Where did you go? (tick all that apply)",
                [
                    {"value": 1, "text": "Health post"},
                    {"value": 2, "text": "Health centre"},
                    {"value": 3, "text": "District hospital"},
                    {"value": 4, "text": "Referral / provincial hospital"},
                    {"value": 5, "text": "Private clinic"},
                    {"value": 6, "text": "Pharmacy"},
                    {"value": 7, "text": "Traditional healer"},
                    {"value": 8, "text": "Community health worker"},
                ],
                visibleIf=sought,
                isRequired=True,
            ),
            check(
                "care_barrier",
                "What stopped you from seeking care? (tick all that apply)",
                [
                    {"value": 1, "text": "Cost"},
                    {"value": 2, "text": "Distance / transport"},
                    {"value": 3, "text": "Shame or stigma"},
                    {"value": 4, "text": "Did not think it was serious"},
                    {"value": 5, "text": "No time"},
                    {"value": 6, "text": "Poor past experience"},
                    {"value": 7, "text": "Did not know where to go"},
                    {"value": 8, "text": "Other (specify)"},
                ],
                visibleIf=no_care,
                isRequired=True,
            ),
            other_text(
                "care_barrier_other",
                "Other barrier — please specify",
                "{care_barrier} contains 8",
            ),
            drop(
                "phone_type",
                "Do you own a mobile phone?",
                [
                    {"value": 0, "text": "No"},
                    {"value": 1, "text": "Basic phone"},
                    {"value": 2, "text": "Smartphone"},
                ],
                isRequired=True,
            ),
            drop(
                "internet_use",
                "How often do you use the internet?",
                [
                    {"value": 0, "text": "Never"},
                    {"value": 1, "text": "Less than weekly"},
                    {"value": 2, "text": "Weekly"},
                    {"value": 3, "text": "Daily"},
                ],
            ),
            radio(
                "health_app_ever",
                "Have you ever used a phone app or SMS service for health (e.g. period tracker, pregnancy app)?",
                YN,
            ),
            drop(
                "att_app_tracking",
                "I would be willing to record my periods and symptoms in a phone app for a health service.",
                LIKERT5,
            ),
            drop(
                "att_wearable",
                "I would be willing to wear a device (e.g. smart watch or temperature sensor) that records health signals.",
                LIKERT5,
            ),
            drop(
                "att_ai_trust",
                "I would trust a computer system (AI) that uses my answers to tell me I should see a health worker.",
                LIKERT5,
            ),
            drop(
                "att_ai_vs_clinician",
                "I would prefer a health worker to review the AI result before I am contacted.",
                LIKERT5,
            ),
            drop(
                "att_data_share",
                "I am comfortable with my anonymised health data being used to train such systems.",
                LIKERT5,
            ),
            drop(
                "concern_main",
                "What is your main concern about AI health tools?",
                [
                    {"value": 1, "text": "Privacy of my data"},
                    {"value": 2, "text": "Accuracy / wrong results"},
                    {"value": 3, "text": "Cost"},
                    {"value": 4, "text": "Replacing health workers"},
                    {"value": 5, "text": "Difficulty using technology"},
                    {"value": 6, "text": "No concern"},
                    {"value": 7, "text": "Other (specify)"},
                ],
            ),
            other_text(
                "concern_main_other",
                "Other concern — please specify",
                "{concern_main} = 7",
            ),
            drop(
                "preferred_channel",
                "How would you prefer to receive health advice or alerts?",
                [
                    {"value": 1, "text": "SMS / USSD"},
                    {"value": 2, "text": "Smartphone app"},
                    {"value": 3, "text": "WhatsApp"},
                    {"value": 4, "text": "Phone call"},
                    {"value": 5, "text": "Visit from a community health worker"},
                    {"value": 6, "text": "At the health facility only"},
                ],
            ),
            drop(
                "preferred_language_digital",
                "Preferred language for digital health messages",
                [
                    {"value": 1, "text": "Kinyarwanda"},
                    {"value": 2, "text": "English"},
                    {"value": 3, "text": "French"},
                ],
            ),
        ],
    }


def build_survey() -> dict:
    return {
        "title": TITLE,
        "description": DESCRIPTION,
        "showProgressBar": "top",
        "progressBarType": "pages",
        "completedHtml": (
            "<h3>Thank you.</h3><p>Your answers have been recorded under your study code. "
            "Information will be used only for research and reported in aggregate.</p>"
        ),
        "pages": [
            page_admin(),
            page_socio(),
            page_menstrual(),
            page_obstetric(),
            page_diagnoses(),
            page_symptoms(),
            page_infections(),
            page_family(),
            page_lifestyle(),
            page_digital(),
        ],
        "showPreviewBeforeComplete": "showAllQuestions",
        "previewText": "Review Answers",
        "editText": "Edit",
        "completeText": "Submit",
    }


def main() -> None:
    survey = build_survey()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(survey, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    page_names = [p["name"] for p in survey["pages"]]
    n_q = 0

    def count(els):
        nonlocal n_q
        for e in els:
            if e.get("type") == "panel":
                count(e["elements"])
            elif e.get("type") not in ("html",):
                n_q += 1

    for p in survey["pages"]:
        count(p["elements"])
    print(f"Wrote {OUTPUT}")
    print(f"pages={page_names}")
    print(f"questions={n_q}")


if __name__ == "__main__":
    main()
