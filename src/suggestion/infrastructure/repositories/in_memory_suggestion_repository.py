class InMemorySuggestionRepository:
    def __init__(self):
        # We replace the JSON file with a simple list in RAM
        self._data = []

    def fetch_raw_data(self) -> list:
        """Returns the list from memory instead of reading a file."""
        return self._data

    def add(self, suggestion_dict: dict):
        """Appends to the list in memory."""
        self._data.append(suggestion_dict)

    def save(self, suggestions_list: list):
        """Updates the internal list with the new version."""
        self._data = suggestions_list