import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

_DATASETS = {
    'general_ledger':  ('general_ledger.xlsx', 0),
    'supplier_master': ('supplier_master.csv',  0),
    'payroll_master':  ('payroll.xlsx',         'Employee_Master'),
    'payroll_trans':   ('payroll.xlsx',         'Monthly_Transactions'),
    'kpi_data':        ('kpi_data.xlsx',        0),
}


def _read_file(path, sheet_name=None):
    """Read an Excel or CSV file and return a DataFrame, or None on failure."""
    if not os.path.exists(path):
        logger.warning("Dataset file not found: %s", path)
        return None
    try:
        if path.endswith('.csv'):
            return pd.read_csv(path)
        return pd.read_excel(path, sheet_name=sheet_name)
    except (ValueError, KeyError) as e:
        logger.error("Failed to read %s (sheet=%s): %s", path, sheet_name, e)
        return None
    except Exception as e:
        logger.error("Unexpected error reading %s: %s", path, e)
        return None


def load_demo_data(data_dir):
    """Load all synthetic demo datasets from data_dir. Missing files return None."""
    datasets = {}
    for key, (filename, sheet) in _DATASETS.items():
        filepath = os.path.join(data_dir, filename)
        datasets[key] = _read_file(filepath, sheet_name=sheet)
    return datasets
