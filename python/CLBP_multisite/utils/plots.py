#!/usr/bin/env python3
import logging

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import gaussian_kde

from CLBP_multisite.utils.stats import find_outliers, compute_ttest


def add_jitter_to_x(y, x_center, max_width=0.25):
    """
    Return x positions with random horizontal jitter.

    Parameters
    ----------
    y : array-like
        Values to plot.
    x_center : float
        Central x-position of the group.
    max_width : float
        Maximum horizontal width of the jitter.

    Returns
    -------
    numpy.ndarray
        Jittered x-positions.
    """
    y = np.asarray(y)
    n = len(y)

    if n <= 1:
        return np.full(n, x_center)

    density = gaussian_kde(y)
    density_values = density(y)
    density_values = density_values / np.max(density_values)
    jitter = np.random.uniform(-density_values, density_values) * max_width

    return x_center + jitter


def prepare_violin(values, max_width=0.3):
    density = gaussian_kde(values)
    y = np.linspace(np.min(values), np.max(values), 200)
    width = density(y)
    width = width / np.max(width) * max_width     # Normalize the width
    return y, width


def plot_metric_jitter(ax, values, metric_name, group_column,
                       separate_outliers=True, hide_outliers=False):
    """Plot one metric for N subgroups.

    Parameters
    ----------
    ax : matplotlib axis
    values : pandas.Series
    metric_name : str
    separate_outliers : bool
        Using ±4SD
    hide_outliers : bool
    """
    groups = list(set(values[group_column]))
    groups_values = []
    groups_means = []
    the_min = np.inf
    the_max = - np.inf
    for position, group in enumerate(groups):
        group_values = values.loc[values[group_column] == group, metric_name]
        group_values = pd.to_numeric(group_values, errors="coerce").dropna().to_numpy()

        if separate_outliers:
            outliers, non_outliers = find_outliers(group_values,
                                                   technique='SD', nb=4)
        else:
            outliers = []
            non_outliers = group_values

        # Update the min, max
        if hide_outliers:
            the_min = min(the_min, np.min(non_outliers))
            the_max = max(the_max, np.max(non_outliers))
        else:
            the_min = min(the_min, np.min(group_values))
            the_max = max(the_max, np.max(group_values))

        # Plot the violin
        y, width = prepare_violin(non_outliers)
        ax.fill_betweenx(y, position - width, position + width,
                         alpha=0.2)

        # Plot the jitter
        x = add_jitter_to_x(non_outliers, position)
        ax.scatter(x, non_outliers, alpha=0.7, s=25)
        if len(outliers) > 0:
            x = [position]*len(outliers)
            ax.scatter(x, outliers, alpha=0.7, s=25, c='gray', marker='*')

        # Add a horizontal line at the mean
        mean = np.mean(non_outliers)
        ax.plot([position - 0.15, position + 0.15], [mean, mean],
                color="black", linewidth=2)

        # Remember values
        groups_values.append(non_outliers)
        groups_means.append(mean)

    if len(groups_values) != 2:
        raise NotImplementedError

    # Computing t-test
    p_value = compute_ttest(groups_values[0], groups_values[1])

    # Plotting the significance
    if p_value < 0.001:
        significance = f"** p = {p_value:.0e}"
    elif p_value < 0.05:
        significance = f"* p = {p_value:.3f}"
    else:
        significance = f"p = {p_value:.3f}"
    ax.plot([0.2, 0.8], [groups_means[0], groups_means[1]],
            color="black", linewidth=1)
    ax.text(0.5, np.mean(groups_means), significance,
        ha="center", va="bottom", fontsize=12)

    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    ax.set_xlim(-0.5, len(groups) - 1 + 0.5)
    the_range = the_max - the_min
    ax.set_ylim(the_min - 0.1*the_range, the_max+0.1*the_range)
    ax.set_title(metric_name)
    ax.grid(axis="y", alpha=0.3)


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

    for figure_number in range(n_figures):
        start = figure_number * nb_plots_per_fig
        end = min(start + nb_plots_per_fig, nb_metrics)

        fig, axes = plt.subplots(nb_rows, nb_cols,
                                 figsize=(15, 12))
        axes = np.asarray(axes).ravel()

        for ax, metric_name in zip(axes, metrics[start:end]):
            # Main plot!
            logging.info(f"Plotting {metric_name}")
            plot_metric_jitter(ax, data, metric_name, group_column,
                               hide_outliers=hide_outliers)

        # Hide unused subplots on the last figure.
        if end < start + nb_plots_per_fig:
            n_plots = end - start
            for ax in axes[n_plots:]:
                ax.set_visible(False)

        # Make figure nice
        fig.suptitle(
            f"Statistics by group — Figure {figure_number + 1}/{n_figures}",
            fontsize=16)
        fig.tight_layout()

        # Save output
        output_file = fig_prefix + f"{figure_number + 1:02d}.png"
        fig.savefig(output_file, dpi=300, bbox_inches="tight")

        plt.close(fig)
        logging.info(f"Saved: {output_file}")
