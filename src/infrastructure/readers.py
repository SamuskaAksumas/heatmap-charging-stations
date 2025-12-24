import pandas as pd
import os

def read_csv_with_header_detection(path, sep=';'):
    """Original logic preserved exactly."""
    with open(path, 'r', encoding='latin1') as fh:
        header_row = 0
        for i, line in enumerate(fh):
            if 'Ladeeinrichtungs-ID' in line or 'Postleitzahl' in line or (line.count(sep) > 1 and 'Postleitzahl' in line):
                header_row = i
                break
    return pd.read_csv(path, sep=sep, header=header_row, encoding='latin1')

def load_geodata(path):
    return pd.read_csv(path, sep=';')