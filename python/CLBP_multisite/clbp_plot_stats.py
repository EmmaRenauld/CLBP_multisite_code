#!/usr/bin/env python3

"""
Plot statistics for CLBP_multisite and HC subjects.

The statistics file must contain:
    - one row per subject
    - one column per metric
    - the first column containing subject names/IDs

The demographics file must contain:
    - one row per subject
    - a column named "group" containing "CLBP_multisite" or "HC"
    - the first column containing subject names/IDs

CSV and Excel (.xlsx/.xls) files are supported.

Example:
    python clbp_plot_stats.py stats.csv demographics.csv
    python clbp_plot_stats.py stats.xlsx demographics.csv --output figures
"""

import argparse
from pathlib import Path

from utils.spreadsheets import read_table, plot_stats_jitter

SUBPLOTS_PER_FIGURE = 9
N_ROWS = 3
N_COLS = 3


def _prepare_argparser():
    p = argparse.ArgumentParser(
        description="Plot statistics for CLBP_multisite and HC subjects.")
    p.add_argument("stats_file", type=Path,
                   help="CSV or Excel file containing the statistics.",)
    p.add_argument("demographics_file", type=Path,
                   help="CSV file containing subject demographics and group.")
    p.add_argument("output", type=Path,
                   help="Output prefix for figures. May contain a full path.")
    p.add_argument('--group', type=str, default="group",
                   help="Name of the group column in the demographics file.\n"
                        "Default: 'group'.")
    return p


def main():
    p = _prepare_argparser()
    args = p.parse_args()

    out_dir = args.output.parents
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load
    stats = read_table(args.stats_file)
    demographics = read_table(args.demographics_file)

    if stats.shape[1] < 2:
        raise ValueError("The statistics file must contain at least one metric.")

    # GROUPS
    if "group" not in demographics.columns:
        raise ValueError(
            'The demographics file must contain a column named "group".'
        )
    groups = list(set(demographics[args.group]))
    if len(groups) != 2:
        raise NotImplementedError("Currently implemented for 2 groups only!")

    # METRICS
    metrics = stats.columns[1:]

    # SUBJECTS
    # The first column is assumed to contain subject IDs.
    stats_subject_column = stats.columns[0]
    demographics_subject_column = demographics.columns[0]
    intersection = list(set(stats_subject_column) & set(demographics_subject_column))
    if len(intersection) == 0:
        raise ValueError("The subjects in both files are different!")

    # Keep only subjects present in both files.
    data = stats.merge(demographics[["subject", "group"]],
                       on="subject", how="inner")

    print(f"Statistics file:     {args.stats_file}")
    print(f"Demographics file:   {args.demographics_file}")
    print(f"Subjects in stats:   {len(stats)}")
    print(f"Subjects matched:    {len(data)}")
    print(f"Number of metrics:   {len(metrics)}")
    print("Groups:    ", groups)

    # PREPARE FIGURES
    plot_stats_jitter(data, metrics, args.group, args.output)


if __name__ == "__main__":
    main()