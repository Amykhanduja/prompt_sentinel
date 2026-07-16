TECHNIQUES = {

    "PT-009": {
        "name": "Instruction Override",
        "severity": "high",
        "family": "Instruction Manipulation"
    },

    "PT-012": {
        "name": "Indirect Prompt Injection",
        "severity": "high",
        "family": "Indirect Injection"
    },

    "PT-013": {
        "name": "System Prompt Extraction",
        "severity": "high",
        "family": "Prompt Extraction"
    },

    "PT-015": {
        "name": "Template Injection",
        "severity": "medium",
        "family": "Template Injection"
    },

    "PT-018": {
        "name": "Roleplay Injection",
        "severity": "high",
        "family": "Persona Manipulation"
    },

    "PT-021": {
        "name": "Metadata Injection",
        "severity": "medium",
        "family": "Metadata Manipulation"
    },

    "PT-023": {
        "name": "Website Prompt Injection",
        "severity": "medium",
        "family": "Remote Content"
    },

    "PT-024": {
        "name": "Context Switch",
        "severity": "medium",
        "family": "Conversation Manipulation"
    },

    "PT-025": {
        "name": "Tool Abuse",
        "severity": "high",
        "family": "Tool Exploitation"
    },

    "PT-026": {
        "name": "Delimiter Injection",
        "severity": "medium",
        "family": "Syntax Manipulation"
    },

    "PT-027": {
        "name": "Chained Injection",
        "severity": "high",
        "family": "Multi-stage Attack"
    },

    "PT-028": {
        "name": "Output Leakage",
        "severity": "critical",
        "family": "Data Exfiltration"
    },

    "PT-029": {
        "name": "API Wrapper Injection",
        "severity": "high",
        "family": "API Manipulation"
    },

    "PT-031": {
        "name": "Stored Prompt Injection",
        "severity": "critical",
        "family": "Persistent Injection"
    },

    "PT-033": {
        "name": "Thought Simulation",
        "severity": "medium",
        "family": "Reasoning Manipulation"
    },

    "PT-037": {
        "name": "Format Token Injection",
        "severity": "critical",
        "family": "Formatting Abuse"
    },

    "PT-040": {
        "name": "Privileged Identity Injection",
        "severity": "high",
        "family": "Identity Manipulation"
    }
}
def get_technique(technique_id):

    return TECHNIQUES.get(
        technique_id,
        {
            "name": "Unknown Technique",
            "severity": "low",
            "family": "Unknown"
        }
    )
