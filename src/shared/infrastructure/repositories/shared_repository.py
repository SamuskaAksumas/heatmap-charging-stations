"""SharedRepository - File I/O for shared data sources."""
import os

import pandas as pd


class SharedRepository:
    """Repository for reading CSV/geodata files."""

    def read_csv_with_header_detection(self, path, sep=';'):
        """Read CSV with auto-detected header row."""
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
        """Load PLZ geometry mapping from CSV."""
        if os.path.exists(path):
            return pd.read_csv(path, sep=';')
        return None
