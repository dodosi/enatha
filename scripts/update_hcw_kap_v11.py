#!/usr/bin/env python3
"""Align HCW KAP JSON with shared CHW v1.1 changes (facilities, version, structured insurance item)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "database" / "samples" / "hcw_kap_survey.json"

FACILITIES = [
    {"value": "GAS-KIB-DH", "text": "GAS-KIB-DH — Kibagabaga DH (Gasabo, Public DH)"},
    {"value": "GAS-KAG-HC", "text": "GAS-KAG-HC — Kagugu HC (Gasabo, Public HC)"},
    {"value": "GAS-KIN-HC", "text": "GAS-KIN-HC — Kinyinya HC (Gasabo, Public HC)"},
    {"value": "GAS-URW-HP", "text": "GAS-URW-HP — Urwego Health Post (Gasabo, Public HP)"},
    {"value": "GAS-KAG-MC", "text": "GAS-KAG-MC — Kagugu Medical Clinic (Gasabo, Public HP)"},
    {"value": "GAS-PLA-PC", "text": "GAS-PLA-PC — Plateau Clinic / Polyclinique du Plateau (Gasabo, Private Clinic)"},
    {"value": "GAS-LCS-PC", "text": "GAS-LCS-PC — La Croix du Sud (Gasabo, Private Clinic)"},
    {"value": "GAS-BCP-PH", "text": "GAS-BCP-PH — Bella Care Pharmacy (Gasabo, Private Pharmacy)"},
    {"value": "GAS-NGA-PH", "text": "GAS-NGA-PH — Ngabo Pharmacy (Gasabo, Private Pharmacy)"},
    {"value": "BUG-NYA-DH", "text": "BUG-NYA-DH — Nyamata DH (Bugesera, Public DH)"},
    {"value": "BUG-NYA-HC", "text": "BUG-NYA-HC — Nyamata HC (Bugesera, Public HC)"},
    {"value": "BUG-MAY-HC", "text": "BUG-MAY-HC — Mayange HC (Bugesera, Public HC)"},
    {"value": "BUG-NY2-HP", "text": "BUG-NY2-HP — Nyamata Second Generation HP (Bugesera, Public HP)"},
    {"value": "BUG-KIB-HP", "text": "BUG-KIB-HP — Kibenga HP (Bugesera, Public HP)"},
    {"value": "BUG-BDC-PC", "text": "BUG-BDC-PC — Benefactor David Clinic (Bugesera, Private Clinic)"},
    {"value": "BUG-STE-PC", "text": "BUG-STE-PC — Stella Clinic (Bugesera, Private Clinic)"},
    {"value": "BUG-ESP-PH", "text": "BUG-ESP-PH — Emma Sanitas Pharmacy LTD (Bugesera, Private Pharmacy)"},
    {"value": "BUG-TGP-PH", "text": "BUG-TGP-PH — The Guardian Pharmacy (Bugesera, Private Pharmacy)"},
    {"value": "GAK-NEM-DH", "text": "GAK-NEM-DH — Nemba DH (Gakenke, Public DH)"},
    {"value": "GAK-CYA-HC", "text": "GAK-CYA-HC — Cyabingo HC (Gakenke, Public HC)"},
    {"value": "GAK-NEM-HC", "text": "GAK-NEM-HC — Nemba HC (Gakenke, Public HC)"},
    {"value": "GAK-GAH-HP", "text": "GAK-GAH-HP — Gahinga HP (Gakenke, Public HP)"},
    {"value": "GAK-GIS-HP", "text": "GAK-GIS-HP — Gisozi HP (Gakenke, Public HP)"},
    {"value": "GAK-PLM-PC", "text": "GAK-PLM-PC — Polyclinic La Medicale (Gakenke, Private Clinic)"},
    {"value": "GAK-CMP-PC", "text": "GAK-CMP-PC — Clinique Medicale Peace (Gakenke, Private Clinic)"},
    {"value": "GAK-MUS-PH", "text": "GAK-MUS-PH — Pharmacy Musasa Ltd (Gakenke, Private Pharmacy)"},
    {"value": "GAK-SUC-PH", "text": "GAK-SUC-PH — Success Pharmacy Ltd (Gakenke, Private Pharmacy)"},
]


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))

    data["description"] = (
        "Stream A1 - Healthcare Provider KAP. IRB Ref. No. 279/CMHSIRB/2026. "
        "Form version HCW-KAP-v1.1 (aligned with study facility codes and shared preview settings)."
    )
    data["showPreviewBeforeComplete"] = "showAllQuestions"
    data["previewText"] = "Review Answers"
    data["editText"] = "Edit"
    data["completeText"] = "Submit"
    data["completedHtml"] = (
        "<h3>Thank you.</h3><p>Your responses will contribute to research aimed at "
        "improving rational antimicrobial use and antimicrobial stewardship in Rwanda.</p>"
    )

    for page in data["pages"]:
        elements = page.get("elements", [])
        for i, el in enumerate(elements):
            if el.get("name") == "site_code":
                elements[i] = {
                    "type": "dropdown",
                    "name": "facility_code",
                    "title": "Study health facility (select from approved list)",
                    "isRequired": True,
                    "choices": FACILITIES,
                }

            # Align sex field name with CHW form for cross-stream analysis
            if el.get("name") == "gender":
                el["name"] = "sex"
                el["title"] = "What is your sex?"

            # Structure Mutuelle diagnostics item (was free-text comment)
            if el.get("name") == "insurance_diagnostics":
                elements[i] = {
                    "type": "radiogroup",
                    "name": "insurance_diagnostics",
                    "title": (
                        "Do community health insurance schemes (Mutuelle de Sante / CBHI) "
                        "cover diagnostic tests that help reduce unnecessary antibiotic use?"
                    ),
                    "isRequired": True,
                    "choices": [
                        "Yes, fully",
                        "Yes, partially",
                        "No",
                        "Don't know / Not sure",
                    ],
                }
                # Insert explain after if not already present
                next_names = {e.get("name") for e in elements}
                if "insurance_diagnostics_explain" not in next_names:
                    elements.insert(
                        i + 1,
                        {
                            "type": "comment",
                            "name": "insurance_diagnostics_explain",
                            "title": "Please briefly explain your answer",
                            "visibleIf": "{insurance_diagnostics} notempty",
                        },
                    )

    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {PATH}")
    print(f"Facilities: {len(FACILITIES)}")


if __name__ == "__main__":
    main()
