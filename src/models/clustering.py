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
from dask.distributed import Client

# ML related packages
import joblib
import kneed
from sklearn.externals.joblib import parallel_backend
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
DASK_CLIENT = Client()


################################
### Define Modular Functions ###
################################
def kmeans_cluster(training_x: np.array, get_best_num_clusters=True):
    """
    Purpose
    -------
    The purpose of this function is to contain all of the code that comprises
    the pipeline of data validation and pre-processing to ultimately train
    a K-Means Clustering model.

    Parameters
    ----------
    training_x : Numpy Array
    	This argument allows the user to specify the collection of data
    	that will be used to train the K Means model. This array follows
    	the convention of the rows representing different training instances
    	and the columns representing different features.
    get_best_num_clusters : Boolean
    	This argument allows the user to specify whether or not the function
    	will simply train a single K Means model with a specified number
    	of clusters or will train several and return the model that is
    	deemed to yield the best clustering using the "Elbow Method".

    	The value of this parameter defaults to `True`.

    Returns
    -------
    to_return : Sklearn model object
    	This function returns a Sklearn model that represents the K Means
    	model that the function recommends for the user to use in future
    	work.

    Raises
    ------
    ValueError
        This error is raised when the user passes in incorrect data types
        to the parameters of this function.

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
    The purpose of this function is to contain all of the code that comprises
    the pipeline of data validation and pre-processing to ultimately train
    a Mean-Shift model using a Dask client.

    Parameters
    ----------
    training_x : Numpy Array
    	This argument allows the user to specify the collection of data
    	that will be used to train the Mean Shift model. This array follows
    	the convention of the rows representing different training instances
    	and the columns representing different features.

    Returns
    -------
    to_return : Sklearn model object
    	This function returns a Sklearn model that represents the Mean
    	Shift model that the function recommends for the user to use in
    	future work.

    Raises
    ------
    ValueError
    	This error is raised when the user passes in incorrect data types
        to the parameters of this function.

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
                                   n_samples=100,
                                   random_state=5569,
                                   n_jobs=-1)
    mean_shift = MeanShift(bandwidth=bandwidth, 
    	                   n_jobs=-1,
    	                   bin_seeding=True,
    	                   min_bin_freq=20)

    # Fit the model and then return that updated model object.
    with parallel_backend("dask"):
    	mean_shift.fit(training_x)
    DASK_CLIENT.close()

    to_return = mean_shift

    return to_return
