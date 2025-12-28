class InMemoryDemandRepository:
    def __init__(self):
        self._data = None

    def get_analysis(self):
        return self._data

    def update_analysis(self, df):
        self._data = df