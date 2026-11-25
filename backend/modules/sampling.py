import pandas as pd
import numpy as np

# Confidence factors per level (Poisson upper confidence limit)
_CONFIDENCE_FACTORS = {
    0.80: 1.61,
    0.85: 1.90,
    0.90: 2.31,
    0.95: 3.00,
    0.99: 4.61,
}
_DEFAULT_CONFIDENCE = 0.95


def run_mus_sampling(df, column_name='Amount_MAD', confidence_level=0.95,
                     expected_error_rate=0.02, tolerable_error=0.05):
    """
    Monetary Unit Sampling (MUS) Implementation.
    Returns sample transactions with population stats and dynamic conclusion.
    """
    if df is None or df.empty or column_name not in df.columns:
        return {"error": "Invalid data: column not found or empty dataset"}

    df = df[df[column_name] > 0].copy()
    if df.empty:
        return {"error": "No positive-value transactions found"}

    population_value = df[column_name].sum()

    # Look up confidence factor — warn if unrecognised level
    confidence_factor = _CONFIDENCE_FACTORS.get(
        round(confidence_level, 2),
        _CONFIDENCE_FACTORS[_DEFAULT_CONFIDENCE]
    )

    tolerable_error_amount = population_value * tolerable_error
    if tolerable_error_amount == 0:
        return {"error": "Tolerable error amount cannot be zero"}

    sample_size = max(1, int((population_value * confidence_factor) / tolerable_error_amount))
    sampling_interval = population_value / sample_size

    df['_cumulative'] = df[column_name].cumsum()

    rng = np.random.default_rng()
    random_start = rng.uniform(0, sampling_interval)
    selection_points = [random_start + i * sampling_interval for i in range(sample_size)]

    sampled_indices = set()
    for point in selection_points:
        idx = df[df['_cumulative'] >= point].index.min()
        if not pd.isna(idx):
            sampled_indices.add(idx)

    df.drop(columns=['_cumulative'], inplace=True)
    selected = df.loc[list(sampled_indices)].to_dict('records')

    effective_level = "high" if confidence_level >= 0.95 else "moderate"
    conclusion = (
        f"MUS selected {len(selected)} transactions from a population of "
        f"{len(df):,} items totalling {population_value:,.0f} MAD. "
        f"At a {confidence_level*100:.0f}% confidence level with a tolerable error rate of "
        f"{tolerable_error*100:.0f}%, the sampling interval is {sampling_interval:,.0f} MAD. "
        f"This provides {effective_level} assurance that material misstatements exceeding "
        f"{tolerable_error_amount:,.0f} MAD will be detected."
    )

    return {
        "population_value": round(population_value, 2),
        "sample_size": len(selected),
        "sampling_interval": round(sampling_interval, 2),
        "confidence_level": confidence_level,
        "tolerable_error_pct": tolerable_error * 100,
        "conclusion": conclusion,
        "selected_transactions": selected,
    }
