#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 05:03:11 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: This script contains a collection of functions that are
used to help create a plot of contours that represent the density of
sequences that either started or ended in that area of the field. This
plot is generated for each cluster identified by the Machine Learning
Cluster model chosen by the user to help determine what differentiates
the clusters from each other.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
from ast import literal_eval
import pandas as pd
import numpy as np
import swifter

# custom modules
from src.test import input_parameter_validation as ipv

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)


################################
### Define Modular Functions ###
################################
def event_starting_point_extractor(row) -> int:
    """
    Purpose
    -------
    NOTE THAT THIS FUNCTION IS INTENDED TO BE USED FOR THE `apply()`
    METHOD OF A PANDAS DATAFRAME WITH THE AXIS PARAMETER SET TO `"columns"`
    or `1`.

    The purpose of this function is to take the information about an event
    and return as a int the starting point of the event.

    Something that is important to note is that the convention that the
    creator's of the original event tracking data set followed was to
    indicate field positions from the prospective of the team initiating
    the corresponding event. Thus, for any given match, the positions listed
    may not be the same even if they're numeric values are the same.

    We chose to keep this convention because what matters more is the
    position of the event in the context of the initiating team's attack.

    Parameters
    ----------
    row : Pandas DataFrame row
        This argument allows the user to specify which row instance they
        are working with as the `apply()` iteratively gets applied to
        each row of the sequence DataFrame.

    Returns
    -------
    to_return : int
        This function returns a int that represents the starting point
        on the field that the
    """
    to_return = None
    # First, define the variables that we will need for the rest of this
    # function.
    positions_list = literal_eval(row["positions"])
    assert isinstance(positions_list, list)
    assert 1 <= len(positions_list) <= 2

    # Next, extract the starting and ending positions.
    raw_starting_x = positions_list[0].get("x")
    raw_starting_y = positions_list[0].get("y")

    starting_x = (raw_starting_x/100)*104
    starting_y = (raw_starting_y/100)*68

    # Finally, validate and return the result.
    to_return = [starting_x, starting_y]

    return to_return


def event_ending_point_extractor(row) -> int:
    """
    Purpose
    -------
    NOTE THAT THIS FUNCTION IS INTENDED TO BE USED FOR THE `apply()`
    METHOD OF A PANDAS DATAFRAME WITH THE AXIS PARAMETER SET TO `"columns"`
    or `1`.

    The purpose of this function is to take the information about an event
    and return as a int the ending point of the event.

    Something that is important to note is that the convention that the
    creator's of the original event tracking data set followed was to
    indicate field positions from the prospective of the team initiating
    the corresponding event. Thus, for any given match, the positions listed
    may not be the same even if they're numeric values are the same.

    We chose to keep this convention because what matters more is the
    position of the event in the context of the initiating team's attack.

    Parameters
    ----------
    row : Pandas DataFrame row
        This argument allows the user to specify which row instance they
        are working with as the `apply()` iteratively gets applied to
        each row of the sequence DataFrame.

    Returns
    -------
    to_return : int
        This function returns a int that represents the starting point
        on the field that the

    Raises
    ------
    AssertionError
        This error is raised when 

    References
    ----------
    1. https://stackoverflow.com/questions/1894269/how-to-convert-string-representation-of-list-to-a-list
    """
    to_return = None
    # First, define the variables that we will need for the rest of this
    # function.
    positions_list = literal_eval(row["positions"])
    assert isinstance(positions_list, list)
    assert 1 <= len(positions_list) <= 2

    # Next, extract the starting and ending positions.
    starting_x = positions_list[0].get("x")
    starting_y = positions_list[0].get("y")

    try:
        ending_x = positions_list[1].get("x")
        raw_ending_y = positions_list[1].get("y")
    except IndexError:
        # If the event is one where there is no ending point to list (i.e.,
        # a foul).
        ending_x, raw_ending_y = starting_x, starting_y

    ending_y = (raw_ending_y/100)*69

    # Finally, validate and return the result.
    to_return = [ending_x, ending_y]

    return to_return


def cluster_positions_extractor(
        cluster_events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to take a DataFrame that contains all
    of the events of set piece sequences that belong to a particular cluster
    of interest and create a new DataFrame that for each event explicitly
    lists its starting point and ending point on the soccer pitch.

    Parameters
    ----------
    cluster_events_df : Pandas DataFrame
        This parameter allows the user to specify the collection of events
        that comprise the sequences that belong to the particular cluster
        of interest.

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a Pandas DataFrame that contains the
        starting and ending field point information for each event in the
        cluster sequence data set provided by the user.

    Raises
    ------
    ValueError
    This error is raised when the user, for at least one parameter,
    passes in an object whose type is not among the accepted types
    for that parameter.

    References
    ----------
    1. https://stackoverflow.com/questions/53218931/how-to-unnest-explode-a-column-in-a-pandas-dataframe
    2. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html
    3. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
    4. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reset_index.html
    5. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rename.html
    """
    to_return = None
    # First, validate the input data
    ipv.parameter_type_validator(expected_type=pd.DataFrame,
                                 parameter_var=cluster_events_df)
    normed = cluster_events_df.reset_index(drop=True)

    # Next, run the above two functions to get starting and ending positions
    starting_positions_series = normed.apply(
        func=event_starting_point_extractor, 
        axis="columns"
    )
    starting_positions_df = pd.DataFrame(
        data=starting_positions_series.tolist(),
        index=normed.index,
        columns=["starting_x", "starting_y"]
    )

    ending_positions_series = normed.swifter.apply(
        func=event_ending_point_extractor,
        axis="columns"
    )
    ending_positions_df = pd.DataFrame(
        data=ending_positions_series.tolist(),
        index=normed.index,
        columns=["ending_x", "ending_y"]
    )

    # Create the new DataFrame that we will be returning.
    positions_df = pd.concat(
        objs=[normed.drop(columns="positions"),
              starting_positions_df,
              ending_positions_df],
        axis="columns",
        ignore_index=True
    )
    positions_df.rename(columns={0 : "seq_id",
                                 1 : "id",
                                 2 : "matchId",
                                 3 : "teamId",
                                 4 : "starting_x",
                                 5 : "starting_y",
                                 6 : "ending_x",
                                 7 : "ending_y"},
                        inplace=True)

    # Finally, validate and return the result
    ipv.parameter_type_validator(expected_type=pd.DataFrame,
                                 parameter_var=positions_df)
    to_return = positions_df

    return to_return


def cluster_positions_binning(
        cluster_positions_df: pd.DataFrame, beginning_points=True) -> tuple:
    """
    Purpose
    -------
    The purpose of this function is to take the positions (whether its the
    starting or ending as specified by the user) of the events that comprise
    the sequences that belong to the cluster of interest and conduct a
    2-dimensional binning so as to determine the spatial distribution of
    events in said cluster.

    Parameters
    ----------
    cluster_positions_df : Pandas DataFrame
        This parameter allows the user to specify the events of this cluster
        and their starting and ending points.
    beginning_points : Boolean
        This parameter allows the user to specify whether or not they would
        like a 2-dimensional binning to be conducted on the starting points
        of the events or the ending points.

    Returns
    -------
    to_return : Python tuple
        This function returns a tuple that contains three elements. These,
        in the order that they are given, are all Numpy Arrays and convey
        the following information:
            1. The number of points that belong to each bin. Note that
               these count quantities will be normalized and thus all be
               between 0 and 1.
            2. The bins along the x-axis that were used.
            3. The bins along the y-axis that were used.

    Raises
    ------
    ValueError
    This error is raised when the user, for at least one parameter,
    passes in an object whose type is not among the accepted types
    for that parameter.

    References
    ----------
    1. https://numpy.org/doc/stable/reference/generated/numpy.histogram2d.html
    """
    to_return = None
    # First, validate the input data
    ipv.parameter_type_validator(expected_type=pd.DataFrame,
                                 parameter_var=cluster_positions_df)

    # Next, define the variables that we will need for the rest of the
    # function.
    field_bins = np.arange(0, 101, 1)

    x_col = "starting_x" if beginning_points else "ending_x"
    x_vals = cluster_positions_df[x_col].to_numpy()

    y_col = "starting_y" if beginning_points else "ending_y"
    y_vals = cluster_positions_df[y_col].to_numpy()

    # Now we are ready to actually perform the 2D binning.
    field_bin_counts, xbins, ybins = np.histogram2d(
        x=x_vals,
        y=y_vals,
        bins=field_bins,
        range=[[0, 100], [0, 100]],
        density=True
    )

    # Finally, validate and return the result
    assert all([isinstance(field_bin_counts, np.ndarray),
                isinstance(xbins, np.ndarray),
                isinstance(ybins, np.ndarray)])
    assert xbins.shape == ybins.shape
    assert field_bin_counts.shape[0] == xbins.size - 1
    assert field_bin_counts.shape[0] == ybins.size - 1

    to_return = (field_bin_counts, xbins, ybins)

    return to_return
