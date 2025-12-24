import json
import os

PROJECT_ROOT = os.path.abspath(os.getcwd())

def load_suggestions():
    """Load suggestions from JSON file"""
    suggestions_file = os.path.join(PROJECT_ROOT, 'suggestions.json')
    if os.path.exists(suggestions_file):
        try:
            with open(suggestions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []
