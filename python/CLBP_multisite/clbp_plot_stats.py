#!/usr/bin/env python3

"""
Plot statistics as jitter plots.

The statistics file must contain:
    - one row per subject
    - one column per metric
    - the first column containing subject names/IDs

The demographics file must contain:
    - one row per subject
    - a column named "group" containing groups (ex, "CLBP" or "HC")
    - the first column containing subject names/IDs

CSV and Excel (.xlsx/.xls) files are supported.
"""

import argparse
import logging
import os
from pathlib import Path

from CLBP_multisite.utils.spreadsheets import read_table
from CLBP_multisite.utils.plots import prepare_many_plots_jitter


def _prepare_argparser():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("stats_file", type=Path,
                   help="CSV or Excel file containing the statistics.",)
    p.add_argument("demographics_file", type=Path,
                   help="CSV file containing subject demographics and group.")

    g = p.add_argument_group("Data loading")
    g.add_argument('--group_column', type=str, default="group",
                   help="Name of the group column in the demographics file.\n"
                        "Default: 'group'.")
    gg = g.add_mutually_exclusive_group()
    gg.add_argument('--metrics', nargs='+', type=str, default=None,
                    help="List of metrics to plot. If not set, uses all metrics.")
    gg.add_argument('--skip', nargs='+', type=str, default=None,
                    help="List of metrics to skip from plotting.")

    g = p.add_argument_group("Data processing")
    g.add_argument('--use_prefix_subjs', action='store_true',
                   help="If set, subjects prefix will be used. \n"
                        "(sub-xxx, removing anything after an underscore _)")
    g.add_argument('--ignore_mismatch', action='store_true',
                   help="If set, continue even if subjects do not match \n"
                        "fully across both files.")
    p.add_argument('--hide_outliers', action='store_true',
                   help="If set, hide outliers. Else, show them as gray stars.\n"
                        "(They are still removed from the mean).")
    p.add_argument('--percent', type=str, default=None,
                   help="If set, plot all metrics as a percentage of the given"
                        "metric.")

    g = p.add_argument_group("Saving options")
    g.add_argument("--out_dir", type=Path, default='./',
                   help="Output prefix for figures. May contain a full path.")
    g.add_argument('--out_prefix', type=str, default='fig',
                   help="Prefix for the output filenames. Default: fig")

    p.add_argument('-v', '--verbose', action='store_true',
                   help="Be more verbose (debug).")

    return p


def main():
    p = _prepare_argparser()
    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    args.out_dir.mkdir(parents=True, exist_ok=True)

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
    groups = list(set(demographics[args.group_column]))
    if len(groups) != 2:
        raise NotImplementedError("Currently implemented for 2 groups only!\n"
                                  "Got: {}".format(groups))

    # METRICS
    all_metrics = list(stats.columns[1:])
    if args.percent is not None:
        if args.percent not in all_metrics:
            raise ValueError("The choice of reference for --percent ({}) was \n"
                             "not found in the metrics. Choices: {}"
                             .format(args.percent, all_metrics))
        all_metrics.remove(args.percent)
    if args.metrics is not None:
        for metric in args.metrics:
            if metric not in all_metrics:
                raise ValueError("The chosen metric {} does not exist in stats file."
                                 "Choices: {}".format(metric, all_metrics))
        metrics = args.metrics
    elif args.skip is not None:
        metrics = all_metrics
        for metric in args.skip:
            if metric not in all_metrics:
                logging.warning("You asked to skip metric {}, but it was not found in "
                                "file (options were: {}). Ignored"
                                .format(metric, all_metrics))
            else:
                metrics.remove(metric)

    # SUBJECTS
    # The first column is assumed to contain subject IDs.
    stats_subject_column = stats.columns[0]
    demographics_subject_column = demographics.columns[0]
    if args.use_prefix_subjs:
        stats[stats_subject_column] = (
            stats[stats_subject_column].astype(str).str.split('_').str[0])
        demographics[demographics_subject_column] = (
            demographics[demographics_subject_column].astype(str).str.split('_').str[0])

    # Renaming the subject column to make the merge easier
    stats = stats.rename(
        columns={stats_subject_column: "subject"})
    demographics = demographics.rename(
        columns={demographics_subject_column: "subject"})

    # Make sure we have the same subjects
    intersection = list(set(stats["subject"]) &
                        set(demographics["subject"]))

    if len(intersection) == 0:
        raise ValueError("The subjects in both files are completely different!\n"
                         "Example of subjects in stats file: {}\n"
                         "Example of subjects in demographics file: {}"
                         .format(list(stats["subject"][0:5]),
                                 list(demographics["subject"][0:5])))

    difference1 = list(set(stats["subject"]) - set(demographics["subject"]))
    difference2 = list(set(demographics["subject"]) - set(stats["subject"]))
    difference1.sort()
    difference2.sort()
    if len(difference1) > 0 or len(difference2) > 0:
        logging.warning("Some subjects do not match!")
        msg = ("In stats but not in demographics: {}\n\n"
               "In demographics but not in stats: {}"
               .format(difference1, difference2))
        if args.ignore_mismatch:
            logging.info("(mismatch subjects will be ignored)")
            logging.debug(msg)
        else:
            raise ValueError(msg)

    # MERGING
    # Keep only subjects present in both files.
    data = stats.merge(
        demographics[["subject", args.group_column]],
        on="subject", how="inner")

    if args.percent is not None:
        data[metrics] = data[metrics].div(data[args.percent], axis=0) * 100

    logging.info(f"Statistics file:     {args.stats_file}")
    logging.info(f"Demographics file:   {args.demographics_file}")
    logging.info(f"Subjects in stats:   {len(stats)}")
    logging.info(f"Subjects in demographics:  {len(demographics)}")
    logging.info(f"Subjects matched:    {len(data)}")
    logging.info(f"Number of metrics:   {len(metrics)}")
    logging.info(f"Groups:    {groups}")

    # PREPARE FIGURES
    prepare_many_plots_jitter(data, metrics, args.group_column,
                              os.path.join(args.out_dir, args.out_prefix),
                              args.hide_outliers)


if __name__ == "__main__":
    main()