#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 6 07:43:58 CST 2021

@author: Sebastian E. Gonzalez

Script Purpose: Collection of functions that are used to perform all of
the necessary computations to obtain the data that will be displayed in a
Plotly bar chart that is generated by the code in the `plotly_bar_chart`
function that can be found in `basic_viz` script in this directory.
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

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
SEQUENCES_DF = sequence_data()
EVENT_ID_TO_NAME_DF = event_id_mapper()


################################
### Define Modular Functions ###
################################
def cluster_events_extractor(
        feat_pred_df: pd.DataFrame, cluster_id: int) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to

    Parameters
    ----------
    feat_pred_df : pd.DataFrame
        Short for feature-prediction dataframe, this argument allows the
        user to specify
    cluster_id : int
        This argument allows the user to specify

    Returns
    -------
    to_return : pd.DataFrame
        This function returns a

    Raises
    ------
    ValueError
        This error is raised when

    References
    ----------
    1.
    """
    to_return = None
    # First, validate the input data.
    try:
        assert isinstance(feat_pred_df, pd.DataFrame)
    except AssertionError:
        err_msg = "The argument `feat_pred_df` only accepts Pandas DataFrame\
		objects. The received type is `{}`.".format(type(feat_pred_df))

        print(err_msg)
        raise ValueError
    try:
        assert feat_pred_df.index.name == "seq_id"
    except AssertionError:
        err_msg = "The Pandas DataFrame that the user passed in to the\
		`feat_pred_df` argument must either have an index that has the label\
		`seq_id` or a column with that label that can be set as the index.\
		Neither criteria was passed."
        try:
            feat_pred_df.set_index("seq_id", inplace=True)
        except KeyError:
            print(err_msg)
            raise ValueError

    # Next, compile all of the events that fall in to the cluster that is
    # specified by the `cluster_id` parameter.
    cluster_seq_ids = list(
        feat_pred_df[feat_pred_df.predicted_cluster_id == cluster_id].index
    )
    cluster_events_df = SEQUENCES_DF.set_index("seq_id").loc[
        cluster_seq_ids
    ][["eventId", "eventName", "subEventId", "subEventName"]]

    # Finally, validate and return the result.
    feat_pred_cluster_counts = feat_pred_df.predicted_cluster_id.value_counts()
    assert feat_pred_cluster_counts[cluster_id] == cluster_events_df.index.unique(
    ).size

    to_return = cluster_events_df

    return to_return


def cluster_counts(
        cluster_events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to

    Parameters
    ----------
    cluster_events_df : Pandas DataFrame
        This argument allows the user to specify
    subevent_count : Boolean
        This argument allows the user to specify

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a

    Raises
    ------
    ValueError
        This error is raised when

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.sort_values.html
    """
    to_return = None
    # First, validate the input data.
    try:
        assert isinstance(cluster_events_df, pd.DataFrame)
    except AssertionError:
        err_msg = "The argument `cluster_events_df` only accepts Pandas \
		DataFrame objects. The received type is `{}`.".format(type(cluster_events_df))

        print(err_msg)
        raise ValueError

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


# def hi() ->:
# 	"""
# 	Purpose
# 	-------
# 	The purpose of this function is to

# 	Parameters
# 	----------
# 	arg_1
# 		This argument allows the user to specify

# 	Returns
# 	-------
# 	to_return :
# 		This function returns a

# 	Raises
# 	------
# 	Error
# 		This error is raised when

# 	References
# 	----------
# 	1.
# 	"""
# 	to_return = None
# 	# First, validate the input data.

# 	# Next,

# 	# Finally, validate and return the result.

# 	return to_return