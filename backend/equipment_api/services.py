"""
CSV parsing and analytics using Pandas.
"""
import pandas as pd
from django.conf import settings


EXPECTED_COLUMNS = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']


def normalize_columns(df):
    """Normalize column names (strip, optional case handling)."""
    df.columns = df.columns.str.strip()
    return df


def parse_and_analyze(file_obj):
    """
    Read CSV into DataFrame, validate columns, compute summary.
    Returns (summary_dict, rows_list) or raises ValueError.
    """
    try:
        df = pd.read_csv(file_obj)
    except Exception as e:
        raise ValueError(f"Invalid CSV: {e}")

    df = normalize_columns(df)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}. Expected: {EXPECTED_COLUMNS}")

    # Numeric columns
    for col in ['Flowrate', 'Pressure', 'Temperature']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    total_count = len(df)
    avg_flowrate = df['Flowrate'].mean()
    avg_pressure = df['Pressure'].mean()
    avg_temperature = df['Temperature'].mean()
    type_distribution = df['Type'].value_counts().to_dict()

    rows = df.to_dict(orient='records')
    for r in rows:
        for k, v in r.items():
            if pd.isna(v):
                r[k] = None
            elif isinstance(v, (float,)):
                r[k] = round(float(v), 4) if v == v else None  # avoid NaN

    summary = {
        'total_count': int(total_count),
        'avg_flowrate': round(float(avg_flowrate), 4) if pd.notna(avg_flowrate) else None,
        'avg_pressure': round(float(avg_pressure), 4) if pd.notna(avg_pressure) else None,
        'avg_temperature': round(float(avg_temperature), 4) if pd.notna(avg_temperature) else None,
        'type_distribution': {str(k): int(v) for k, v in type_distribution.items()},
        'raw_rows': rows,
    }
    return summary
