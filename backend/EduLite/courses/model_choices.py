# courses/model_choices.py
import json
import logging
from pathlib import Path
from django.conf import settings

from typing import List

logger = logging.getLogger(__name__)

# Course Privacy Setting Choices
COURSE_VISIBILITY_CHOICES = [
    ("public", "Public"),
    ("restricted", "Restricted"),
    ("private", "Private"),
]
COURSE_ROLE_CHOICES = [
    ("teacher", "Teacher"),
    ("student", "Student"),
    ("assistant", "Assistant"),
]
COURSE_MEMBERSHIP_STATUS = [
    ("pending", "Pending Approval"),
    ("enrolled", "Enrolled"),
    ("invited", "Invited"),
]

CHOICES_DATA_DIR = Path(settings.BASE_DIR).parent / "project_choices_data"


def load_choices_from_json(file_name: str) -> List[tuple]:
    """

    Loads a list of (value, label) tuples from a JSON file.
    Expects JSON to be a list of objects, each with "value" and "label" keys.

    Returns a list of tuples. [(value, label), ...]
    """
    file_path = CHOICES_DATA_DIR / file_name
    choices_list = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                if isinstance(item, dict) and "value" in item and "label" in item:
                    choices_list.append((item["value"], item["label"]))
                else:
                    # Using logging to showup warning
                    logger.warning(f"Warning: Malformed item in {file_name}: {item}")
    except FileNotFoundError:
        logger.warning(
            f"Warning: Choices file not found: {file_path}. Returning empty list."
        )
    except json.JSONDecodeError:
        logger.warning(
            f"Warning: Could not decode JSON from {file_path}. Returning empty list."
        )
    except Exception as e:
        logger.warning(
            f"Warning: An unexpected error occurred loading {file_name}: {e}. Returning empty list."
        )
    return choices_list


# Load choices (these will be loaded once when Django starts and this module is imported)
OCCUPATION_CHOICES = load_choices_from_json("occupations.json")
COUNTRY_CHOICES = load_choices_from_json("countries.json")
LANGUAGE_CHOICES = load_choices_from_json("languages.json")
SUBJECT_CHOICES = load_choices_from_json("subjects.json")
