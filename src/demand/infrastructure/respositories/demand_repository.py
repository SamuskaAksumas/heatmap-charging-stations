class DemandRepository:
    def __init__(self):
        # We don't need a file_path because we aren't saving to disk
        self._current_analysis = None

    def get_analysis(self):
        """Returns the currently held analysis results."""
        return self._current_analysis

    def update_analysis(self, df):
        """Updates the results held in memory."""
        self._current_analysis = df