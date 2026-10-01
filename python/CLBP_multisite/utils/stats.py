#!/usr/bin/env python3
import logging

import numpy as np
from scipy.stats import levene, ttest_ind


def find_outliers(data: np.ndarray, technique='SD', nb=None):
    if technique == 'SD':
        nb = nb or 3  # Default: ±3SD

        sd = np.std(data)
        mean = np.mean(data)
        upper_limit = mean + nb * sd
        lower_limit = mean - nb * sd
    elif technique == 'iQR':
        nb = nb or 1.5  # Default: 1.5 * iqr

        q1 = np.quantile(data, 0.25)
        q3 = np.quantile(data, 0.75)
        iqr = q3 - q1

        lower_limit = q1 - nb * iqr
        upper_limit = q3 + nb * iqr

    else:
        raise ValueError("Unknown technique. Expected 3SD, or iQR.")

    outliers = data[(data < lower_limit) | (data > upper_limit)]
    non_outliers = data[(data >= lower_limit) & (data <= upper_limit)]

    return outliers, non_outliers


def compute_ttest(group_1_values, group_2_values, check_variances=False):

    if check_variances:
        statistic, p_value_var = levene(group_1_values, group_2_values)

        if p_value_var < 0.05:
            logging.debug("Variances are significantly different. Uses Welch's t-test")
            _, p_value = ttest_ind(group_1_values, group_2_values,
                                   equal_var=False)
            return False, p_value
        else:
            logging.debug("No significant evidence that variances are different.")
            _, p_value = ttest_ind(group_1_values, group_2_values,
                                   equal_var=True)
            return True, p_value
    else:
        logging.debug("Assuming different variances. Uses Welch's t-test.")
        _, p_value = ttest_ind(group_1_values, group_2_values,
                               equal_var=False)
        return p_value