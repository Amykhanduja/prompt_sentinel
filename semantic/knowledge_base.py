import json
from pathlib import Path

from taxonomy.techniques import TECHNIQUES


EXAMPLES_DIR = Path(__file__).parent / "examples"

VALID_TECHNIQUES = set(
    TECHNIQUES.keys()
)

def load_knowledge_base() -> dict:
    """
    Loads and validates the semantic knowledge base.
    """

    knowledge_base = {}

    required_fields = {
        "technique",
        "name",
        "canonical_examples",
        "paraphrase_examples"
    }

    for file_path in sorted(
        EXAMPLES_DIR.glob("*.json")
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        # --------------------------------------------------
        # Required fields validation
        # --------------------------------------------------

        missing = required_fields - data.keys()

        if missing:
            raise ValueError(
                f"{file_path.name} is missing required fields: "
                f"{sorted(missing)}"
            )

        technique = data["technique"]

        # --------------------------------------------------
        # Technique validation
        # --------------------------------------------------

        if technique not in VALID_TECHNIQUES:
            raise ValueError(
                f"{file_path.name}: Unknown technique '{technique}'."
            )

        # --------------------------------------------------
        # Duplicate technique validation
        # --------------------------------------------------

        if technique in knowledge_base:
            raise ValueError(
                f"Duplicate knowledge base entry for '{technique}'."
            )

        # --------------------------------------------------
        # Type validation
        # --------------------------------------------------

        if not isinstance(
            data["canonical_examples"],
            list
        ):
            raise TypeError(
                f"{file_path.name}: "
                f"'canonical_examples' must be a list."
            )

        if not isinstance(
            data["paraphrase_examples"],
            list
        ):
            raise TypeError(
                f"{file_path.name}: "
                f"'paraphrase_examples' must be a list."
            )

        if not all(
            isinstance(example, str)
            for example in data["canonical_examples"]
        ):
            raise TypeError(
                f"{file_path.name}: "
                f"Every canonical example must be a string."
            )

        if not all(
            isinstance(example, str)
            for example in data["paraphrase_examples"]
        ):
            raise TypeError(
                f"{file_path.name}: "
                f"Every paraphrase example must be a string."
            )

        knowledge_base[technique] = data

    return knowledge_base


KNOWLEDGE_BASE = load_knowledge_base()


def get_knowledge_base() -> dict:
    """
    Returns the complete semantic knowledge base.
    """

    return KNOWLEDGE_BASE


def get_technique(technique: str) -> dict | None:
    """
    Returns the semantic entry for a technique.
    """

    return KNOWLEDGE_BASE.get(technique)


def get_examples(technique: str) -> list[str]:
    """
    Returns all semantic examples for a technique.
    """

    entry = get_technique(technique)

    if entry is None:
        return []

    return (
        entry["canonical_examples"]
        + entry["paraphrase_examples"]
    )


def techniques() -> list[str]:
    """
    Returns all loaded technique IDs.
    """

    return sorted(KNOWLEDGE_BASE.keys())
