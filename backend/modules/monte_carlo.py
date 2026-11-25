import numpy as np

# Fixed constants — extracted from magic numbers
_BASE_COST_PER_UNIT = 150_000   # MAD per risk score unit
_STD_DEV_RATIO = 0.40           # Standard deviation as fraction of base cost
_SIMULATION_ITERATIONS = 10_000
_SEED = 42


def run_simulation(risks):
    """
    Run Monte Carlo simulation for each risk.
    Uses a seeded Generator instance (thread-safe, unlike np.random.seed).
    Returns dict keyed by risk_id with P10/P50/P90 exposure values.
    """
    rng = np.random.default_rng(_SEED)
    results = {}

    for r in risks:
        base_cost = r['impact'] * r['likelihood'] * _BASE_COST_PER_UNIT
        std_dev = base_cost * _STD_DEV_RATIO

        simulation = rng.normal(base_cost, std_dev, _SIMULATION_ITERATIONS)
        simulation = np.maximum(simulation, 0)  # No negative exposure

        results[r['risk_id']] = {
            "min_exposure":      round(float(np.percentile(simulation, 10)), 2),
            "expected_exposure": round(float(np.percentile(simulation, 50)), 2),
            "max_exposure":      round(float(np.percentile(simulation, 90)), 2),
        }

    return results
