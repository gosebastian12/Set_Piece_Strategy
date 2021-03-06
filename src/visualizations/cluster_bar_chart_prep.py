#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 6 07:43:58 CST 2021

@author: Sebastian E. Gonzalez

Script Purpose: This script contains a collection of functions that are
used to perform all of the necessary computations to obtain the data that
will be displayed in a Plotly bar chart that is generated by the code in
the `plotly_bar_chart` function that can be found in `basic_viz` script
in this directory.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import pandas as pd
import numpy as np

# custom modules
from src.data.data_loader import sequence_data, event_id_mapper
from src.test import input_parameter_validation as ipv

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
SEQUENCES_DF = sequence_data()
EVENT_ID_TO_NAME_DF = event_id_mapper()


################################
### Define Modular Functions ###
################################
def cluster_events_extractor(
        feat_pred_df: pd.DataFrame, cluster_id: int, **kwargs) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to take all of the events that make up
    the set piece sequences that we have data for and an ID that specifies
    the cluster of interest and return all of the events that whose set
    piece sequence falls into that cluster.

    Parameters
    ----------
    feat_pred_df : pd.DataFrame
        Short for feature-prediction dataframe, this argument allows the
        user to specify the entire collection of events and set piece
        sequences that we have data for.
    cluster_id : int
        This argument allows the user to specify the ID of the cluster
        that we would like to use to filter out the events passed to the
        `feat_pred_df` argument.
    kwargs : dict
        This function accepts keyword arguments that give the user the
        ability to specify which columns of the original sequence data
        are returned with the result. Note that:
            1. The function does not only accept specific keyword argument
               names (that is, the keys of the dictionary in the function's
               local scope under the variable name `kwargs`). However, the
               values assigned to these keyword variables must be strings
               that are exactly identical to one of the column labels in
               the original sequence data. If not a `KeyError` will be
               raised by this function.
            2. If there are no keyword arguments, the default columns
               contained in the result are `eventId`, `eventName`,
               `subEventId`, and `subEventName` with `seq_id` being the
               index of the DataFrame.

    Returns
    -------
    to_return : pd.DataFrame
        This function returns a new Pandas DataFrame that is a collection
        of all of the events (and thus set piece sequences) that belong
        to the cluster of interest.

    Raises
    ------
    ValueError
        This error is raised when the user, for at least one parameter,
        passes in an object whose type is not among the accepted types
        for that parameter.
    """
    to_return = None
    # First, validate the input data.
    ipv.parameter_type_validator(expected_type=pd.DataFrame,
                                 parameter_var=feat_pred_df)
    ipv.parameter_type_validator(expected_type=int, parameter_var=cluster_id)

    are_keywords = len(kwargs.keys()) > 0 
    if are_keywords:
        # If the user passed in keyword arguments to this function.
        try:
            for val in kwargs.values():
                ipv.parameter_type_validator(str, val)
                assert val in SEQUENCES_DF.columns
        except (ValueError, AssertionError):
            err_msg = "This function only accepts Python string-objects\
            that are equivalent to one of the column labels in the original\
            sequence data. One or more of this values passed in by the\
            user did not meet this criteria."
            raise KeyError(err_msg)

    # Next, compile all of the events that fall in to the cluster that is
    # specified by the `cluster_id` parameter.
    cluster_seq_ids = list(
        feat_pred_df[feat_pred_df.predicted_cluster_id == cluster_id].index
    )

    columns_to_keep = list(kwargs.values()) if are_keywords \
                      else ["eventId", "eventName", "subEventId", "subEventName"]
    cluster_events_df = SEQUENCES_DF.set_index("seq_id").loc[
        cluster_seq_ids][columns_to_keep]

    # Finally, validate and return the result.
    feat_pred_cluster_counts = feat_pred_df.predicted_cluster_id.value_counts()
    assert feat_pred_cluster_counts[cluster_id] == cluster_events_df.index.unique(
    ).size

    to_return = cluster_events_df

    return to_return


def cluster_counts(
        cluster_events_df: pd.DataFrame) -> tuple:
    """
    Purpose
    -------
    The purpose of this function is to take all of the events corresponding
    to a particular cluster and create two new dataframes that contain all
    of the type and subtype event possibilities and their corresponding
    counts in the cluster event data respectively. The function is set up
    in this way because the output is perfectly suited for use with Plotly
    Express bar chart function (see `basic_viz` script that is found in
    this directory).

    Parameters
    ----------
    cluster_events_df : Pandas DataFrame
        This argument allows the user to specify the collection of events
        that belong to the cluster of interest.

    Returns
    -------
    to_return : tuple of two Pandas DataFrame
        This function returns a tuple that contains two Pandas DataFrames.
        The first DataFrame corresponds to the count values for all of the
        possible event types while the second DataFrame corresponds to the
        count values for all of the possible sub-event types

    Raises
    ------
    ValueError
        This error is raised when the user, for at least one parameter,
        passes in an object whose type is not among the accepted types
        for that parameter.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.sort_values.html
    """
    to_return = None
    # First, validate the input data.
    ipv.parameter_type_validator(expected_type=pd.DataFrame,
                                 parameter_var=cluster_events_df)

    # Next, define some variables that will be helpful later on
    all_possible_events_arr = EVENT_ID_TO_NAME_DF.event_label.unique()
    all_possible_subevents_arr = EVENT_ID_TO_NAME_DF.subevent_label.unique()

    # Now, get the counts of events
    events_counts_series = cluster_events_df.eventName.value_counts()
    n0events_counts_df = events_counts_series.reset_index().rename(
        columns={"eventName": "event_count", "index": "event_name"}
    )
    if n0events_counts_df.shape[0] != all_possible_events_arr.size:
        # If we do NOT have a count value for each possible event ID.
        events_that_have_count = \
            n0events_counts_df.event_name.to_numpy().tolist()
        events_missing_list = [
            event_label for event_label in all_possible_events_arr.tolist()
            if event_label not in events_that_have_count
        ]
        assert len(events_missing_list) + len(events_that_have_count) == \
            all_possible_events_arr.size

        missing_events_counts_df = pd.DataFrame(
            {"event_count": [0] * len(events_missing_list),
             "event_name": events_missing_list}
        )

        nevents_counts_df = pd.concat(
            [n0events_counts_df, missing_events_counts_df]
        ).reset_index(drop=True)
        assert nevents_counts_df.shape[0] == all_possible_events_arr.size
    else:
        nevents_counts_df = n0events_counts_df

    nevents_counts_df["nevent_count"] = \
        nevents_counts_df.event_count / nevents_counts_df.event_count.sum()
    nevents_counts_df.sort_values(
        by="event_name", axis="index", inplace=True, ignore_index=True
    )

    # Now, get the counts of sub events if the user would like the function
    # to.
    sub_events_counts_series = cluster_events_df.subEventName.value_counts()
    n0sub_events_counts_df = sub_events_counts_series.reset_index().rename(
        columns={"subEventName": "sub_event_count", "index": "sub_event_name"}
    )
    if n0sub_events_counts_df.shape[0] != all_possible_subevents_arr.size:
        # If we do NOT have a count value for each possible subevent
        # ID.
        sub_events_that_have_count = \
            n0sub_events_counts_df.sub_event_name.to_numpy().tolist()
        sub_events_missing_list = [
            sub_event_label for sub_event_label in all_possible_subevents_arr.tolist()
            if sub_event_label not in sub_events_that_have_count
        ]
        assert len(sub_events_missing_list) + len(sub_events_that_have_count) == \
            all_possible_subevents_arr.size

        missing_subevents_counts_df = pd.DataFrame(
            {"sub_event_count": [0] * len(sub_events_missing_list),
             "sub_event_name": sub_events_missing_list}
        )

        nsub_events_counts_df = pd.concat(
            [n0sub_events_counts_df, missing_subevents_counts_df]
        ).reset_index(drop=True)
        assert nsub_events_counts_df.shape[0] == all_possible_subevents_arr.size
    else:
        nsub_events_counts_df = n0sub_events_counts_df

    nsub_events_counts_df["nsub_event_count"] = \
        nsub_events_counts_df.sub_event_count / nsub_events_counts_df.sub_event_count.sum()
    nsub_events_counts_df.sort_values(
        by="sub_event_name", axis="index", inplace=True, ignore_index=True
    )

    # Finally, validate and return the result.
    assert np.isclose(nevents_counts_df.nevent_count.sum(), 1)
    assert np.isclose(nsub_events_counts_df.nsub_event_count.sum(), 1)

    to_return = (nevents_counts_df, nsub_events_counts_df)

    return to_return
