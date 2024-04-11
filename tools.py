from statistics import mean, stdev
from math import sqrt
from scipy.stats import t


def confidence_interval(values, alpha, num_replications):
    """Returns the confidence interval for the mean of a set of values"""

    # degrees of freedom for the t-student
    df = num_replications - 1
    # value for a t-student with df degrees of freedom and a tail of alpha/2
    t_value = t.ppf(1-alpha/2, df)
    # confidence interval for the mean of values
    return f'{round(mean(values), 1)} \u00B1 {round(t_value * stdev(values)/sqrt(num_replications), 1)}'
