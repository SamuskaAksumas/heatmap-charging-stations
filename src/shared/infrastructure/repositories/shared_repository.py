import pandas as pd
import os

class SharedRepository:
    def read_csv_with_header_detection(self, path, sep=';'):
        """Detects headers and reads CSV files (e.g., Ladesaeulenregister)."""
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='latin1') as fh:
            header_row = 0
            for i, line in enumerate(fh):
                if 'Postleitzahl' in line or 'Ladeeinrichtungs-ID' in line:
                    header_row = i
                    break
        return pd.read_csv(path, sep=sep, header=header_row, encoding='latin1')

    def load_geodata(self, path):
        """Loads the PLZ geometry mapping."""
        if os.path.exists(path):
            return pd.read_csv(path, sep=';')
        return None