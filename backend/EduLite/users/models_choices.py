# users/models_choices.py

import json
from pathlib import Path
from django.conf import settings

from typing import List

# get the parent of the parent of BASE_DIR (project root)
CHOICES_DATA_DIR = Path(settings.BASE_DIR).parent.parent / "project_choices_data"


def load_choices_from_json(filename: str) -> List[tuple]:
    """
    Loads a list of (value, label) tuples from a JSON file.
    Expects JSON to be a list of objects, each with "value" and "label" keys.

    Returns a list of tuples. [(value, label), ...]
    """
    file_path = CHOICES_DATA_DIR / filename
    choices_list = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                if isinstance(item, dict) and "value" in item and "label" in item:
                    choices_list.append((item["value"], item["label"]))
                else:
                    # Log a warning
                    print(f"Warning: Malformed item in {filename}: {item}")
    except FileNotFoundError:
        print(f"Warning: Choices file not found: {file_path}. Returning empty list.")
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {file_path}. Returning empty list.")
    except Exception as e:
        print(
            f"Warning: An unexpected error occurred loading {filename}: {e}. Returning empty list."
        )
    return choices_list


# Load choices (these will be loaded once when Django starts and this module is imported)
OCCUPATION_CHOICES = load_choices_from_json("occupations.json")
COUNTRY_CHOICES = load_choices_from_json("countries.json")
LANGUAGE_CHOICES = load_choices_from_json("languages.json")
SUBJECT_CHOICES = load_choices_from_json("subjects.json")
