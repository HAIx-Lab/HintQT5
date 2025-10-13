import json
import os

FEEDBACK_FILE = "feedback_data.json"

def load_feedback() -> list:
    """Loads feedback data from the JSON file."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, 'r') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_feedback(feedback_list: list):
    """Saves the complete feedback list to the JSON file."""
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_list, f, indent=4)

