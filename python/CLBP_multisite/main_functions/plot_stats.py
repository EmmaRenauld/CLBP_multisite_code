#!/usr/bin/env python3
import logging

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from CLBP_multisite.utils.plots import add_violin, add_jitter_to_x, add_significance_bracket
from CLBP_multisite.utils.stats import find_outliers, get_significant_pairs


def plot_metric_jitter_with_violin(ax, values, metric_name, group_column,
                                   separate_outliers=True, hide_outliers=False):
    """
    Plot one metric for N subgroups.
    Returns the p-value (t-test if two groups, else ANOVA).

    Parameters
    ----------
    ax : matplotlib axis
    values : pandas.Series
    metric_name : str
    group_column: str
    separate_outliers : bool
        Using ±4SD
    hide_outliers : bool

    Returns
    -------
    p_value: float
        The p-value.
    """
    NB_SD_OUTLIERS = 4

    groups = list(set(values[group_column].dropna()))
    groups.sort()
    groups_values = []  # Values per group
    groups_n = []       # Number of subjects
    groups_n_outliers = []   # Number of outliers
    the_min = np.inf    # Total minimum (no outliers), for ylim
    the_max = - np.inf  # Total maximum (no outliers), for ylim
    titre = metric_name

    for position, group in enumerate(groups):
        # Extract values for subjects belonging to this group
        group_values = values.loc[values[group_column] == group, metric_name]
        group_values = pd.to_numeric(group_values,
                                     errors="coerce").dropna().to_numpy()

        if separate_outliers:
            outliers, non_outliers = find_outliers(
                group_values, technique='SD', nb=NB_SD_OUTLIERS)
        else:
            outliers = []
            non_outliers = group_values

        # Remember values
        logging.debug("Group {} -- Total: {}, included: {}. Outliers (±{}SD): {}"
                      .format(group, len(group_values), len(non_outliers),
                              NB_SD_OUTLIERS, len(outliers)))
        groups_n.append(len(non_outliers))
        groups_values.append(non_outliers)
        groups_n_outliers.append(len(outliers))

        # Update the min, max
        if hide_outliers:
            the_min = min(the_min, np.min(non_outliers))
            the_max = max(the_max, np.max(non_outliers))
        else:
            the_min = min(the_min, np.min(group_values))
            the_max = max(the_max, np.max(group_values))

        # Plot the violin
        add_violin(non_outliers, ax, position)

        # Plot the jitter
        x = add_jitter_to_x(non_outliers, position)
        ax.scatter(x, non_outliers, alpha=0.7, s=25)
        if len(outliers) > 0 and not hide_outliers:
            x = [position ] * len(outliers) # No jitter for them
            ax.scatter(x, outliers, alpha=0.7, s=25, c='gray', marker='*')

        # Add a horizontal line at the mean
        mean = np.mean(non_outliers)
        ax.plot([position - 0.15, position + 0.15], [mean, mean],
                color="black", linewidth=2)

        # Add a vertical line for the STD
        std = np.std(non_outliers)
        ax.errorbar(position, mean, yerr=std, fmt="none",
                    color="black", linewidth=2, capsize=4)

    # Computing t-test
    p_value, significant_pairs = get_significant_pairs(groups_values)
    titre += f". p={p_value:.0e}"
    if p_value < 0.05:
        ax.set_facecolor("0.9")

    # Adding a line between pairs of significant group
    if len(significant_pairs) > 0:
        for position_1, position_2, pair_p_value in significant_pairs:
            if pair_p_value < 0.001:
                text = f"** p = {pair_p_value:.0e}"
            else:  # Means < 0.05
                text = f"* p = {pair_p_value:.3f}"

            add_significance_bracket(ax, position_1, position_2, y, text)

            # Next text (and ylim) will be a bit higher
            the_max += 0.08 * (the_max - the_min)

    # Adding the number of subjects in the title
    titre += (f"\nN: {' / '.join(map(str, groups_n))}. "
              f"Outliers: {' / '.join(map(str, groups_n_outliers))}")
    ax.set_title(titre)

    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    ax.set_xlim(-0.5, len(groups) - 1 + 0.5)
    the_range = the_max - the_min
    ax.set_ylim(the_min - 0.1*the_range, the_max + 0.1*the_range)
    ax.grid(axis="y", alpha=0.3)

    return p_value


def prepare_many_plots_jitter(data, metrics, group_column, fig_prefix,
                              hide_outliers, nb_rows=3, nb_cols=3):
    """
    Parameters
    ----------
    data: pandas DataFrame
        The data table.
    metrics: list[str]
        The metrics to plot amongst the data table.
    group_column: str
    fig_prefix: str
    hide_outliers: bool
    nb_rows: int
    nb_cols: int
    """
    nb_metrics = len(metrics)
    nb_plots_per_fig = nb_rows * nb_cols
    n_figures = int(np.ceil(nb_metrics / nb_plots_per_fig))
    print(f"Number of figures:   {n_figures}")

    all_pvalues = []
    for figure_number in range(n_figures):
        start = figure_number * nb_plots_per_fig
        end = min(start + nb_plots_per_fig, nb_metrics)

        fig, axes = plt.subplots(nb_rows, nb_cols,
                                 figsize=(15, 12))
        axes = np.asarray(axes).ravel()

        for ax, metric_name in zip(axes, metrics[start:end]):
            # Main plot!
            logging.debug(f"   Plotting {metric_name}")
            pval = plot_metric_jitter_with_violin(ax, data, metric_name,
                                                  group_column,
                                                  hide_outliers=hide_outliers)

            all_pvalues.append(pval)

        # Hide unused subplots on the last figure.
        if end < start + nb_plots_per_fig:
            n_plots = end - start
            for ax in axes[n_plots:]:
                ax.set_visible(False)

        # Save output
        fig.tight_layout()
        output_file = fig_prefix + f"{figure_number + 1:02d}.png"
        fig.savefig(output_file, dpi=300, bbox_inches="tight")

        plt.close(fig)
        logging.info(f"Saved: {output_file}")

    return all_pvalues
