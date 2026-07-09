import json
from pathlib import Path

from taxonomy.techniques import TECHNIQUES


EXAMPLES_DIR = Path(__file__).parent / "examples"

VALID_TECHNIQUES = set(TECHNIQUES.keys())


def load_knowledge_base() -> dict:
    """
    Loads and validates the semantic knowledge base.
    """

    knowledge_base = {}

    required_fields = {
        "technique",
        "name"
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
        # Required fields
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
        # Duplicate validation
        # --------------------------------------------------

        if technique in knowledge_base:
            raise ValueError(
                f"Duplicate knowledge base entry for '{technique}'."
            )

        # --------------------------------------------------
        # Validate every *_examples field
        # --------------------------------------------------

        example_fields = {}

        for field, value in data.items():

            if not field.endswith("_examples"):
                continue

            if not isinstance(value, list):
                raise TypeError(
                    f"{file_path.name}: '{field}' must be a list."
                )

            if not all(
                isinstance(example, str)
                for example in value
            ):
                raise TypeError(
                    f"{file_path.name}: Every item in '{field}' must be a string."
                )

            example_fields[field] = value

        if "canonical_examples" not in example_fields:
            raise ValueError(
                f"{file_path.name}: Missing 'canonical_examples'."
            )

        if "paraphrase_examples" not in example_fields:
            raise ValueError(
                f"{file_path.name}: Missing 'paraphrase_examples'."
            )

        data["example_fields"] = list(
            example_fields.keys()
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

ALL_EXAMPLE_FIELDS = (
    "canonical_examples",
    "paraphrase_examples",
    "polite_examples",
    "aggressive_examples",
    "negative_examples",
    "roleplay_examples",
    "indirect_examples"
)


def get_positive_examples(entry: dict) -> list:
    """
    Returns every positive semantic example for a technique.
    """

    examples = []

    for field in ALL_EXAMPLE_FIELDS:

        if field == "negative_examples":
            continue

        examples.extend(
            entry.get(field, [])
        )

    return examples


def get_negative_examples(entry: dict) -> list:
    """
    Returns every negative semantic example for a technique.
    """

    return entry.get(
        "negative_examples",
        []
    )
