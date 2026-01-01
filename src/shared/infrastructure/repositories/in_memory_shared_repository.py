import pandas as pd

class InMemorySharedRepository:
    def __init__(self):
        # We store "fake" data here to simulate files
        self._fake_csv_data = None
        self._fake_geodata = None

    def set_fake_csv_data(self, df: pd.DataFrame):
        """Pre-load a dataframe to be returned by the reader."""
        self._fake_csv_data = df

    def set_fake_geodata(self, df: pd.DataFrame):
        """Pre-load a dataframe to be returned by the geodata loader."""
        self._fake_geodata = df

    def read_csv_with_header_detection(self, path, sep=';'):
        """Returns the pre-loaded fake CSV instead of reading from disk."""
        return self._fake_csv_data

    def load_geodata(self, path):
        """Returns the pre-loaded fake Geodata instead of reading from disk."""
        return self._fake_geodata