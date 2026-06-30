from fastapi import APIRouter


router = APIRouter()


DETECTOR_COVERAGE = [

    {
        "technique": "PT-009",
        "name": "Instruction Override",
        "status": "implemented"
    },

    {
        "technique": "PT-013",
        "name": "System Prompt Extraction",
        "status": "implemented"
    },

    {
        "technique": "PT-018",
        "name": "Roleplay Injection",
        "status": "implemented"
    },

    {
        "technique": "PT-027",
        "name": "Privileged Identity Injection",
        "status": "implemented"
    },

    {
        "technique": "PT-028",
        "name": "Output Leakage Request",
        "status": "implemented"
    },

    {
        "technique": "PT-029",
        "name": "API Wrapper Injection",
        "status": "implemented"
    },

    {
        "technique": "PT-033",
        "name": "Thought Simulation Bypass",
        "status": "implemented"
    },

    {
        "technique": "PT-037",
        "name": "Format Token Injection",
        "status": "implemented"
    },

    {
        "technique": "PT-034",
        "name": "EXIF / Metadata Injection",
        "status": "planned"
    },

    {
        "technique": "PT-035",
        "name": "Website / Document Injection",
        "status": "planned"
    },

    {
        "technique": "PT-036",
        "name": "API Response Poisoning",
        "status": "planned"
    }

]


@router.get("/coverage")
def get_coverage():

    implemented = [
        x for x in DETECTOR_COVERAGE
        if x["status"] == "implemented"
    ]

    planned = [
        x for x in DETECTOR_COVERAGE
        if x["status"] == "planned"
    ]

    return {
        "total": len(DETECTOR_COVERAGE),
        "implemented": len(implemented),
        "planned": len(planned),
        "coverage": DETECTOR_COVERAGE
    }
