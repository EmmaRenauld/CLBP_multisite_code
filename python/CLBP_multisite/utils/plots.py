#!/usr/bin/env python3

import numpy as np
from scipy.stats import gaussian_kde


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


def add_violin(values, ax, position, max_width=0.3):
    density = gaussian_kde(values)
    y = np.linspace(np.min(values), np.max(values), 200)
    width = density(y)
    width = width / np.max(width) * max_width     # Normalize the width

    ax.fill_betweenx(y, position - width, position + width, alpha=0.2)


def add_significance_bracket(ax, position_1, position_2, y, text):
    """Add a significance bracket between two groups."""
    height = 0.02 * (ax.get_ylim()[1] - ax.get_ylim()[0])

    ax.plot([position_1, position_1, position_2, position_2],
            [y, y + height, y + height, y],
            color="black", linewidth=1)

    ax.text((position_1 + position_2) / 2, y + height, text,
            ha="center", va="bottom", fontsize=12)
