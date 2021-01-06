#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Dec 22 10:20:01 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: Collection of functions that perform all of the clustering
algorithm implementations done in various parts of this project.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import numpy as np

# ML related packages
import kneed
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)


################################
### Define Modular Functions ###
################################
def kmeans_cluster(training_x: np.array, get_best_num_clusters=True):
    """
    Purpose
    -------
    The purpose of this function is to

    Parameters
    ----------
    training_x : Numpy Array
    	This argument allows the user to specify
    get_best_num_clusters : Boolean
    	This argument allows the user to specify

    	The value of this parameter defaults to `True`.

    Returns
    -------
    to_return :
    	This function returns a

    Raises
    ------
    ValueError
        This error is raised when

    References
    ----------
    1. https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
    """
    to_return = None

    # First, validate the input data.
    try:
        assert isinstance(training_x, np.ndarray)
    except AssertionError:
        err_msg = "The data type of the object passed in to the `training_x`\
		argument is invalid. It must be a Numpy Array; received type `{}`\
		instead.".format(type(training_x))

        print(err_msg)
        raise ValueError
    try:
        assert isinstance(get_best_num_clusters, bool)
    except AssertionError:
        err_msg = "The data type of the value passed in to the `get_best_num_clusters`\
		argument is invalid. It must be of type `Boolean`. Received type\
		`{}` instead.".format(type(get_best_num_clusters))

        print(err_msg)
        raise ValueError

    # Next, instantiate the model.
    if get_best_num_clusters:
        kmeans_kwargs = {
            "init": "k-means++",
            "n_init": 15,
            "max_iter": 300,
            "random_state": 69,
        }
        sse_vals = []
        fitted_models_dict = {}

        for k in range(3, 11, 1):
            kmeans_model = KMeans(n_clusters=k, **kmeans_kwargs)
            kmeans_model.fit(training_x)

            sse_vals.append(kmeans_model.inertia_)
            fitted_models_dict[k] = kmeans_model

        knee_locator = kneed.KneeLocator(
            range(3, 11), sse_vals, curve="convex", direction="decreasing"
        )
        best_num_clusters = knee_locator.elbow
    else:
        pass

    # Return the fitted model.
    to_return = fitted_models_dict.get(best_num_clusters)

    return to_return


def meanshift_cluster(training_x: np.array):
    """
    Purpose
    -------

    Parameters
    ----------
    The purpose of this function is to

    Parameters
    ----------
    training_x : Numpy Array
    	This argument allows the user to specify

    Returns
    -------
    to_return :
    	This function returns a

    Raises
    ------
    ValueError
    	This error is raised when

    References
    ----------
    1. https://scikit-learn.org/stable/modules/generated/sklearn.cluster.MeanShift.html
    2. https://www.machinecurve.com/index.php/2020/04/23/how-to-perform-mean-shift-clustering-with-python-in-scikit/
    3. https://scikit-learn.org/stable/modules/generated/sklearn.cluster.estimate_bandwidth.html
    """
    to_return = None

    # First, validate the input data.
    try:
        assert isinstance(training_x, np.ndarray)
    except AssertionError:
        err_msg = "The data type of the object passed in to the `training_x`\
		argument is invalid. It must be a Numpy Array; received type `{}`\
		instead.".format(type(training_x))

        print(err_msg)
        raise ValueError

    # Next, instantiate the model.
    bandwidth = estimate_bandwidth(X=training_x,
                                   quantile=0.3,
                                   n_samples=1000,
                                   random_state=5569,
                                   n_jobs=-1)
    mean_shift = MeanShift(bandwidth=bandwidth, n_jobs=-1)

    # Fit the model and then return that updated model object.
    mean_shift.fit(training_x)

    return to_return


# def hi() ->:
# 	"""
# 	Purpose
# 	-------
# 	The purpose of this function is to

# 	Parameters
# 	----------
# 	arg_1 :
# 		This argument allows the user to specify

# 	Returns
# 	-------
# 	to_return :
# 		This function returns a

# 	Raises
# 	------

# 	References
# 	----------
# 	1.
# 	"""
# 	to_return = None

# 	# First,

# 	return to_return
