#!/usr/bin/env python3
from pathlib import Path

import pandas as pd


def read_table(filename, sort=True):
    """Read a CSV or Excel file into a pandas DataFrame."""
    filename = Path(filename)
    suffix = filename.suffix.lower()

    if not filename.exists():
        raise FileNotFoundError(f"File not found: {filename}")

    if suffix == ".csv":
        table = pd.read_csv(filename)
    elif suffix in [".xlsx", ".xls"]:
        table = pd.read_excel(filename)
    elif suffix == ".tsv":
        table = pd.read_csv(filename, sep="\t")
    else:
        raise ValueError(
            f"Unsupported file format: {filename.suffix}. "
            "Use CSV, TSV or Excel.")

    if sort:
        table = table.sort_values(by=table.columns[0])
    return table
