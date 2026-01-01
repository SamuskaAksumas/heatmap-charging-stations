def load_suggestions(raw_data):
    """Load suggestions from JSON file"""
    return [item for item in raw_data if item.get('status') != 'deleted']