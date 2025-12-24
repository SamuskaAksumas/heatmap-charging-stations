import json
import os
from datetime import datetime
from .load_suggestion import load_suggestions

PROJECT_ROOT = os.path.abspath(os.getcwd())

def save_suggestion(suggestion):
    """Save a new suggestion to JSON file"""
    suggestions = load_suggestions()
    suggestion['id'] = len(suggestions) + 1
    suggestion['timestamp'] = datetime.now().isoformat()
    suggestion['status'] = 'pending'  # pending, approved, rejected
    suggestion['reviewed_by'] = None
    suggestion['review_date'] = None
    suggestion['review_notes'] = None
    suggestions.append(suggestion)

    suggestions_file = os.path.join(PROJECT_ROOT, 'suggestions.json')
    with open(suggestions_file, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, indent=2, ensure_ascii=False)
