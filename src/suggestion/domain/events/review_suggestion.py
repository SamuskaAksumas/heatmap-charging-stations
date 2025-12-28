from datetime import datetime

def review_suggestion(suggestion, status, reviewer, notes):
    """
    Domain Event: Logic for approving or rejecting.
    Pure business logic—no JSON or OS logic allowed here.
    """
    suggestion['status'] = status
    suggestion['reviewed_by'] = reviewer
    suggestion['review_date'] = datetime.now().isoformat()
    suggestion['review_notes'] = notes
    return suggestion