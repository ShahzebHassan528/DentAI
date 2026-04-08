from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

TREATMENTS: dict[str, dict] = {
    "cavity": {
        "condition": "Dental Cavity (Caries)",
        "severity_note": "Early-stage cavities can be reversed; advanced ones require restorative treatment.",
        "treatments": [
            {
                "name": "Fluoride Treatment",
                "description": "Remineralizes early-stage enamel decay. Applied as gel, varnish, or rinse.",
                "when": "Early cavities (white spot lesions, no structural loss)",
            },
            {
                "name": "Dental Filling",
                "description": "Removes decayed tissue and fills the cavity with composite resin or amalgam.",
                "when": "Cavities with structural enamel/dentin loss",
            },
            {
                "name": "Dental Crown",
                "description": "Covers the entire tooth after removing decay. Used when too much tooth structure is lost.",
                "when": "Large or deep cavities",
            },
            {
                "name": "Root Canal Treatment",
                "description": "Removes infected pulp, cleans the canals, and seals the tooth.",
                "when": "Cavity has reached the pulp (nerve)",
            },
            {
                "name": "Tooth Extraction",
                "description": "Removal of the tooth when it is unsalvageable.",
                "when": "Severely decayed tooth with no remaining structure",
            },
        ],
        "prevention": [
            "Brush twice daily with fluoride toothpaste",
            "Floss daily to remove interdental plaque",
            "Limit sugary and acidic food/drinks",
            "Routine dental checkups every 6 months",
        ],
    },
    "healthy": {
        "condition": "Healthy Dentition",
        "severity_note": "No active disease detected. Maintain current oral hygiene routine.",
        "treatments": [
            {
                "name": "Professional Cleaning (Prophylaxis)",
                "description": "Removes plaque and tartar buildup that brushing cannot reach.",
                "when": "Every 6 months as routine maintenance",
            },
            {
                "name": "Dental Sealants",
                "description": "Protective coating applied to back teeth to prevent future cavities.",
                "when": "Recommended for children and high-risk adults",
            },
            {
                "name": "Fluoride Application",
                "description": "Strengthens enamel and prevents future decay.",
                "when": "At routine checkup visits",
            },
        ],
        "prevention": [
            "Continue brushing twice daily and flossing",
            "Visit the dentist every 6 months",
            "Use fluoride toothpaste",
            "Maintain a balanced, low-sugar diet",
        ],
    },
    "impacted": {
        "condition": "Impacted Tooth (Commonly Wisdom Tooth)",
        "severity_note": "Impacted teeth can damage adjacent teeth and cause infection if untreated.",
        "treatments": [
            {
                "name": "Monitoring (Watchful Waiting)",
                "description": "Regular X-rays to track the impacted tooth if it is asymptomatic.",
                "when": "No pain, swelling, or adjacent tooth damage",
            },
            {
                "name": "Surgical Extraction",
                "description": "Oral surgery to remove the impacted tooth under local or general anesthesia.",
                "when": "Pain, infection, cyst formation, or damage to adjacent teeth",
            },
            {
                "name": "Orthodontic Exposure",
                "description": "Surgically exposes the tooth and uses braces to guide it into proper position.",
                "when": "Impacted canines or teeth with orthodontic value",
            },
            {
                "name": "Pain Management",
                "description": "NSAIDs (ibuprofen) and warm salt-water rinses for temporary relief.",
                "when": "While awaiting surgical appointment",
            },
        ],
        "prevention": [
            "Early orthodontic evaluation can identify impaction risk",
            "Regular dental X-rays to monitor tooth development",
        ],
    },
    "infection": {
        "condition": "Dental Infection / Abscess",
        "severity_note": "Dental infections can spread to the jaw, neck, and brain. Seek immediate dental care.",
        "treatments": [
            {
                "name": "Antibiotics",
                "description": "Prescribed to control bacterial spread (amoxicillin or metronidazole). Does not cure the source.",
                "when": "Signs of spreading infection (swelling, fever, difficulty swallowing)",
            },
            {
                "name": "Abscess Drainage",
                "description": "Dentist makes a small incision to drain pus and relieve pressure.",
                "when": "Visible or palpable abscess with pus",
            },
            {
                "name": "Root Canal Treatment",
                "description": "Removes infected pulp and seals the tooth, eliminating the infection source.",
                "when": "Periapical abscess with salvageable tooth",
            },
            {
                "name": "Tooth Extraction",
                "description": "Removes the infected tooth entirely to eliminate the infection source.",
                "when": "Tooth is unsalvageable or patient cannot afford root canal",
            },
            {
                "name": "Emergency Hospitalization",
                "description": "IV antibiotics and surgical drainage for severe, spreading infections.",
                "when": "Swelling spreading to neck/throat, difficulty breathing or swallowing",
            },
        ],
        "prevention": [
            "Treat cavities early before they reach the pulp",
            "Maintain good oral hygiene",
            "Do not ignore toothache — seek dental care promptly",
            "Regular dental checkups for early detection",
        ],
    },
    "other": {
        "condition": "Other Dental Condition",
        "severity_note": "Diagnosis requires clinical examination. AI confidence may be lower for this category.",
        "treatments": [
            {
                "name": "Dental Consultation",
                "description": "A dentist should examine you in person for an accurate diagnosis.",
                "when": "Always — AI cannot replace clinical examination",
            },
            {
                "name": "X-ray & Clinical Assessment",
                "description": "Full mouth X-rays and physical exam to identify the specific condition.",
                "when": "First step for unclassified symptoms",
            },
            {
                "name": "Specialist Referral",
                "description": "Referral to periodontist, endodontist, or oral surgeon as needed.",
                "when": "Complex or specialty conditions (TMJ, gum disease, fractures)",
            },
        ],
        "prevention": [
            "See a dentist for proper diagnosis",
            "Maintain good oral hygiene while awaiting appointment",
            "Avoid self-medicating beyond OTC pain relief",
        ],
    },
}


class TreatmentResponse(BaseModel):
    condition: str
    severity_note: str
    treatments: list[dict]
    prevention: list[str]


@router.get(
    "/{condition}",
    response_model=TreatmentResponse,
    summary="Get treatment suggestions for a diagnosed condition",
)
async def get_treatments(condition: str):
    key = condition.lower().strip()
    if key not in TREATMENTS:
        raise HTTPException(
            status_code=404,
            detail=f"No treatment data for condition '{condition}'. "
                   f"Valid conditions: {', '.join(TREATMENTS.keys())}."
        )
    return TREATMENTS[key]
