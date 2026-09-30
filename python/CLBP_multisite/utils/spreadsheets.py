#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from CLBP_multisite.utils.plots import plot_metric_jitter


def read_table(filename):
    """Read a CSV or Excel file into a pandas DataFrame."""
    filename = Path(filename)

    if not filename.exists():
        raise FileNotFoundError(f"File not found: {filename}")

    if filename.suffix.lower() == ".csv":
        return pd.read_csv(filename)

    if filename.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(filename)

    raise ValueError(
        f"Unsupported file format: {filename.suffix}. "
        "Use CSV or Excel."
    )


def plot_stats_jitter(data, metrics, group_column, fig_prefix, nb_rows=3, nb_cols=3):
    """
    Parameters
    ----------
    data: pandas DataFrame
        The data table.
    metrics: list[str]
        The metrics to plot amongst the stats table.
    group_column: str
    fig_prefix: str
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
            plot_metric_jitter(ax, data, metric_name, group_column)

        # Hide unused subplots on the last figure.
        if end < start + nb_plots_per_fig:
            for ax in axes[end:]:
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
        print(f"Saved: {output_file}")