import pandas as pd
import numpy as np
from scipy.stats import chisquare
import math

# Benford threshold: deviation > 2 percentage points flags an anomaly
_BENFORD_DEVIATION_THRESHOLD = 2.0
# Duplicate detection window in days
_DUPLICATE_WINDOW_DAYS = 7
# Threshold avoidance bands (MAD) — just below approval limits
_THRESHOLD_BANDS = [(9100, 9900), (48000, 49800)]


def analyze_benford(df, column_name='Amount_MAD'):
    """Analyze numerical data against Benford's Law distribution."""
    if df is None or df.empty:
        return {"error": "Empty dataset"}

    amounts = df[column_name].dropna()
    amounts = amounts[amounts > 0]

    if len(amounts) < 10:
        return {"error": "Not enough data (minimum 10 records required)"}

    # Extract first digit using vectorized string operation
    first_digits = (
        amounts.astype(str)
        .str.replace(r'[^1-9]', '', regex=True)
        .str[0]
        .dropna()
    )
    first_digits = pd.to_numeric(first_digits, errors='coerce').dropna().astype(int)
    first_digits = first_digits[first_digits.between(1, 9)]

    counts = first_digits.value_counts().sort_index()
    total_count = len(first_digits)

    actual_freq = []
    expected_freq = []

    for i in range(1, 10):
        c = counts.get(i, 0)
        actual_freq.append(c / total_count * 100)
        expected_freq.append(math.log10(1 + 1 / i) * 100)

    expected_counts = [math.log10(1 + 1 / i) * total_count for i in range(1, 10)]
    actual_counts = [int(counts.get(i, 0)) for i in range(1, 10)]

    chi2, p_val = chisquare(f_obs=actual_counts, f_exp=expected_counts)

    return {
        "actual_frequencies": [round(x, 2) for x in actual_freq],
        "expected_frequencies": [round(x, 2) for x in expected_freq],
        "chi_square": round(chi2, 2),
        "p_value": round(p_val, 4),
        "is_anomaly": bool(p_val < 0.05)
    }


def detect_anomalies(df):
    """
    Detect duplicate payments and threshold avoidance patterns.
    Uses vectorized pandas operations instead of row-by-row iteration.
    """
    results = {}

    # ── 1. Duplicate payments (vectorized) ──────────────────────────────────
    required_cols = {'Vendor_Customer', 'Date', 'Amount_MAD'}
    if required_cols.issubset(df.columns):
        gl = df[['Vendor_Customer', 'Amount_MAD', 'Date']].copy()
        gl['Date'] = pd.to_datetime(gl['Date'], errors='coerce')
        gl = gl.dropna(subset=['Date'])
        gl = gl.sort_values(['Vendor_Customer', 'Amount_MAD', 'Date']).reset_index(drop=True)

        # Shift to compare consecutive rows
        gl['_v_next'] = gl['Vendor_Customer'].shift(-1)
        gl['_a_next'] = gl['Amount_MAD'].shift(-1)
        gl['_d_next'] = gl['Date'].shift(-1)

        mask = (
            (gl['Vendor_Customer'] == gl['_v_next']) &
            (gl['Amount_MAD'] == gl['_a_next']) &
            ((gl['_d_next'] - gl['Date']).dt.days.abs() <= _DUPLICATE_WINDOW_DAYS)
        )

        dups_df = gl[mask].copy()
        duplicates = []
        for _, row in dups_df.iterrows():
            duplicates.append({
                "Vendor_Customer": row['Vendor_Customer'],
                "Amount_MAD": float(row['Amount_MAD']),
                "Date": str(row['Date'].date()),
                "Date_2": str(pd.Timestamp(row['_d_next']).date()),
                "Days_Apart": int(abs((pd.Timestamp(row['_d_next']) - row['Date']).days))
            })
        results['duplicates'] = duplicates

    # ── 2. Threshold avoidance ────────────────────────────────────────────────
    if 'Amount_MAD' in df.columns:
        band_masks = [
            (df['Amount_MAD'] >= lo) & (df['Amount_MAD'] <= hi)
            for lo, hi in _THRESHOLD_BANDS
        ]
        combined = band_masks[0]
        for m in band_masks[1:]:
            combined = combined | m
        avoidance_df = df[combined]
        results['threshold_avoidance'] = len(avoidance_df)

        keep_cols = [c for c in ['Date', 'Vendor_Customer', 'Amount_MAD', 'Department']
                     if c in avoidance_df.columns]
        results['avoidance_data'] = avoidance_df[keep_cols].to_dict('records')

    return results
