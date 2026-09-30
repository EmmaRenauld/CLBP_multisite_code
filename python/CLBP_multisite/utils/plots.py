#!/usr/bin/env python3

import numpy as np
import pandas as pd


def add_jitter(values, center, width=0.15):
    """Return x positions with random horizontal jitter."""
    return center + np.random.uniform(-width, width, size=len(values))


def plot_metric_jitter(ax, values, metric_name, group_column):
    """Plot one metric for CLBP_multisite and HC subjects.

    Parameters
    ----------
    ax : matplotlib axis
    values : pandas.Series
    metric_name : str
    """
    groups = list(set(values[group_column]))
    for position, group in enumerate(groups):
        group_values = values.loc[values[group_column] == group, metric_name]
        group_values = pd.to_numeric(group_values, errors="coerce").dropna()

        x = add_jitter(group_values.to_numpy(), position)

        ax.scatter(x, group_values,
                   alpha=0.7, s=25)

    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    ax.set_title(metric_name)
    ax.grid(axis="y", alpha=0.3)
