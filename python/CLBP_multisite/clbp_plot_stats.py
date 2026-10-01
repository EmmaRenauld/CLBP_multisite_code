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

If there are two groups: t-tests (using Welch's - not assumption on equivalence
of variance).
If there are more groups: one-way anova first, then if it is significative,
post-hocs are tukey_hsd.

CSV and Excel (.xlsx/.xls) files are supported.
"""

import argparse
import glob
import logging
import os
from pathlib import Path

from CLBP_multisite.main_functions.plot_stats import prepare_many_plots_jitter
from CLBP_multisite.utils.spreadsheets import read_table


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
    g.add_argument('--exclude', nargs='+', type=str, default=None,
                   help="List of columns to use as exclusion criteria in the \n"
                        "demographics file. Will exclude if value is 0 or NaN.")

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
                   help="Output directory.")
    g.add_argument('--fig_prefix', type=str, default='fig',
                   help="Prefix for the figures filenames. Default: fig. \n"
                        "Suffix will be the figure number based on the number \n"
                        "of metrics. Each figure contains 9 metrics.")
    g.add_argument('--pvals_file', default=None, metavar='file',
                   help="If set, will save the p-values in a .tsv file in "
                        "--out_dir.\n (one per metric).")

    p.add_argument('-v', '--verbose', action='store_true',
                   help="Be more verbose (debug).")
    p.add_argument('-f', '--force', action='store_true',
                   help="Overwrite existing files.")

    return p


def _verify_the_data(args, demographics, stats):
    # groups?
    if args.group_column not in demographics.columns:
        raise ValueError(
            'The demographics file must contain a column named --group_column, '
            'but I did not find {} in {}'
            .format(args.group_column, demographics.columns))

    # metrics?
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
    else:
        metrics = all_metrics
        if args.skip is not None:
            for metric in args.skip:
                if metric not in all_metrics:
                    logging.warning("You asked to skip metric {}, but it was not found in "
                                    "file. Ignored.".format(metric))
                else:
                    metrics.remove(metric)

    if args.group_column in metrics:
        raise ValueError("Can't show stats for column {} based on demographic "
                         "column {}, merging will go bad. Please rename."
                         .format(args.group_column, args.group_column))

    # subjects?
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

    # Making sure there are no duplicate subjects in each file
    for file, name in zip([stats, demographics], ['stats', 'demographics']):
        subjects = file["subject"].tolist()
        duplicates = set(subject for subject in subjects
                         if subjects.count(subject) > 1)
        if duplicates:
            raise ValueError(
                f"Duplicate subjects in {name}: {sorted(duplicates)}")

    # Exclusion criteria
    if args.exclude is not None:
        for column in args.exclude:
            nb_subjects_before = len(demographics)
            if column not in demographics.columns:
                raise ValueError(f"Column '{column}' specified with --exclude "
                                 "does not exist in the demographics file.")
            demographics = demographics[demographics[column].notna() &
                                        demographics[column] != 0]
            nb_subjects_dropped = nb_subjects_before - len(demographics)
            logging.warning(f"Excluded {nb_subjects_dropped} subjects based "
                            f"on exclusion criteria '{column}'.")

    # Make sure we have mostly the same subjects in both files
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

    metrics.sort()
    return stats, demographics, metrics


def main():
    p = _prepare_argparser()
    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    # CHECKS
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if args.pvals_file is not None:
        args.pvals_file = os.path.join(args.out_dir, args.pvals_file)
        if os.path.isfile(args.pvals_file) and not args.force:
            p.error("--pvals_file file already exists. Use -f to overwrite.")
        assert args.pvals_file[-4:] == '.tsv', "--pvals_file file must end with .tsv"
    if not args.force:
        existing = glob.glob(os.path.join(args.out_dir, args.fig_prefix + '*'))
        if len(existing) > 0:
            p.error("--out_dir already contains files with prefix --fig_prefix")

    # LOADING AND VERIFYING DATA
    stats = read_table(args.stats_file)
    demographics = read_table(args.demographics_file)
    stats, demographics, metrics = _verify_the_data(args, demographics, stats)

    # MERGING
    # Keep only subjects present in both files.
    columns_to_keep_stats = ["subject"] + metrics
    if args.percent is not None:
        columns_to_keep_stats += [args.percent]
    data = stats[columns_to_keep_stats].merge(
        demographics[["subject", args.group_column]],
        on="subject", how="inner", validate='one_to_one',
        suffixes=('_stats', '_demographics'))

    if args.percent is not None:
        data[metrics] = data[metrics].div(data[args.percent], axis=0) * 100

    logging.info(f"Statistics file:     {args.stats_file}")
    logging.info(f"Demographics file:   {args.demographics_file}")
    logging.info(f"Subjects in stats:   {len(stats)}")
    logging.info(f"Subjects in demographics:  {len(demographics)}")
    logging.info(f"Subjects matched:    {len(data)}")
    logging.info(f"Number of metrics:   {len(metrics)}")

    # PREPARE FIGURES
    fig_prefix = os.path.join(args.out_dir, args.fig_prefix)
    pvals = prepare_many_plots_jitter(data, metrics, args.group_column,
                                      fig_prefix, args.hide_outliers)

    # Save p-values
    if args.pvals_file is not None:
        logging.info("Saving pvalues to file {}".format(args.pvals_file))
        with open(args.pvals_file, "w") as f:
            f.write("metric\tp_value\n")
            for metric, p_value in zip(metrics, pvals):
                f.write(f"{metric}\t{p_value:.10g}\n")


if __name__ == "__main__":
    main()