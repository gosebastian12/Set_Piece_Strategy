#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Dec 08 06:14:02 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: Write functions that allow the user to take the raw
Wyscout event-log data and obtain a collection of all of the set pieces
and their subsequent plays that are present in the data.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import pandas as pd
import numpy as np
import swifter

# custom modules
from src.data import data_loader as dl
from src.data import common_tasks as ct
from src.data import set_piece_ending_checker as check

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
RAW_EVENTS_DF = dl.raw_event_data(league_name="all")
FINAL_EVENTS_DF = RAW_EVENTS_DF[RAW_EVENTS_DF.playerId > 0]


################################
### Define Modular Functions ###
################################
def set_piece_initating_events_extractor(
        type_to_return="list", events_data=FINAL_EVENTS_DF):
    """
    Purpose
	-------
	The purpose of this function is to comb through the full event
	tracking data set and find the instances that corresponds to the
	beginning of set piece sequences to return to the user.

	Parameters
	----------
	type_to_return : list
	    This argument allows the user to specify how the function will
	    return its result. The available options are:
            1. "list" which will result in the function giving the IDs
               for all of the events that initiate a set piece sequence.
            2. "dataframe" which will result in the function returning
               a Pandas DataFrame where each row corresponds to an event
               that starts a set piece. Thus, this option allows access
               to the rest of the information associated with each event.
    The default value for this argument is `"list"`.
	events_data : Pandas DataFrame
	    This argument allows the user to specify the data set to look for
	    set piece sequence initiating events. Its default value is all of
	    events that we have logging data for.

	Returns
	-------
	to_return : list or Pandas DataFrame
	    This function returns either a list or Pandas DataFrame (which is
	    controlled by the argument `type_to_return`) that specifies all
	    of the events in the specified dataset (see the `events_data`
	    argument) that correspond to the beginning of set piece sequences.

	Raises
	------
	ValueError
	    This error is raised when the value and/or type of the passed-in
	    values for `type_to_return` and `events_data` respectively are
	    not correct. See the Parameters section for what are accepted values
	    and types for these arguments.
    """
    to_return = None
    # First, validate the input data.
    accepted_return_types = ["list", "dataframe"]
    normed_type_to_return = "".join(type_to_return.lower().split())
    try:
        assert normed_type_to_return in accepted_return_types
    except AssertionError:
        err_msg = "This function requires that the passed-in value for\
		the `type_to_return` argument must be either of the strings\
		'list' or 'dataframe'. The received value was: `{}`.".format(type_to_return)

        print(err_msg)
        raise ValueError

    try:
        assert isinstance(events_data, pd.DataFrame)
    except AssertionError:
        err_msg = "This function requires that the passed-in value for\
		the `events_data` argument be an instance of `pd.DataFrame`. The\
		received type was `{}`".format(type(events_data))

    # Now extract the events that correspond to the beginning of set pieces.
    beginning_of_sps_df = events_data[events_data.eventId == 3]
    to_return_dict = {
        "list": beginning_of_sps_df.id.to_numpy().tolist(),
        "dataframe": beginning_of_sps_df
    }

    to_return = to_return_dict.get(normed_type_to_return)

    return to_return


def subsequent_play_generator(
        set_piece_start_id: int, num_events: int) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to use the event ID that indicates the
    beginning of a set piece and then return several plays

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    num_events : int
        This argument allows the user to specify the maximum number of events
        after the beginning of the set piece that the function will return.
        Note that the function may return fewer than the value of this
        argument if it runs into events from a different half, match, etc.

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a Pandas DataFrame that contains all of the
        plays that immediately followed the beginning of the set piece.

    Raises
    ------
    AssertionError
        Such an error will be raised if the function for some reason finds
        two row instances in the events data set that corresponds to the
        same event ID. This should not occur however since each instance
        has a unique event ID; this error serves as a guard against the
        unlikely scenario of non-unique event ID's.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.first_valid_index.html
    2. https://scipython.com/book/chapter-4-the-core-python-language-ii/questions/determining-if-an-array-is-monotonically-increasing/
    """
    to_return = None
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)
    ct.id_checker(num_events)

    # Next, obtain the specific row from the full dataset that pertains
    # to the event that starts the set piece. NOTE that we have validated
    # that the `ID` column of this data is comprised of unique values.
    start_sp_row_index = np.argwhere(
    	(FINAL_EVENTS_DF.id == set_piece_start_id).to_numpy()
    ).flatten()[0]
    start_set_piece_row = FINAL_EVENTS_DF.iloc[start_sp_row_index]
    assert isinstance(start_set_piece_row, pd.Series)

    # Now, obtain the rest of the rows that we are interested in analyzing.
    row_indicies = list(range(start_sp_row_index,
                              start_sp_row_index + num_events + 1))

    sp_sequece_df = FINAL_EVENTS_DF.iloc[row_indicies]

    # Validate the data you're about to return.
    assert sp_sequece_df.iloc[0].id == set_piece_start_id
    assert sp_sequece_df.iloc[0].eventId == 3

    half_of_set_piece = start_set_piece_row.matchPeriod
    assert isinstance(half_of_set_piece, str)
    match_id_of_set_piece = start_set_piece_row.matchId

    try:
        assert all(sp_sequece_df.matchPeriod == half_of_set_piece)
        interim_sequence_df = sp_sequece_df
    except AssertionError:
        # If there are events that occur in a different half/period from
        # the event that corresponds to the beginning of the set piece.
        interim_sequence_df = sp_sequece_df[
            sp_sequece_df.matchPeriod == half_of_set_piece
        ]

    try:
        assert all(sp_sequece_df.matchId == match_id_of_set_piece)
        final_sequence_df = interim_sequence_df
    except AssertionError:
        # If there are events that pertain to a different match than the
        # event that corresponds to the beginning of the set piece.
        final_sequence_df = interim_sequence_df[
            interim_sequence_df.matchId == match_id_of_set_piece
        ]

    try:
        assert np.all(np.diff(final_sequence_df.eventSec) >= 0)
    except AssertionError:
        # If for some reason the events are not in order.
        err_msg = "The events that immediately followed the set piece \
    	initiating event in the data set were found to be out of order. \
    	Have you modified the data in some way?"

        print(err_msg)
        raise AssertionError

    to_return = final_sequence_df.reset_index(drop=True)

    return to_return


def set_piece_sequence_generator(
        set_piece_start_id: int) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to run all of the tests written above
    to determine how a particular set piece sequence ended and thus be
    able to collect the full set of events/plays that make up that set
    piece sequence of interest.

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a DataFrame that contains all of the events
        that make up the set piece sequence that starts with the event
        specified by the argument `set_piece_start_id`.

    Raises
    ------
    AssertionError
        This error is raised when the function determines that none of
        the tests ran to determine when and why the set piece sequence of
        interest ended pass. When this error is raised, the ID
        corresponding to the start of the set piece sequence is printed
        out for debugging purposes.
    """
    to_return = None
    # First, validate the input data.
    ct.id_checker(set_piece_start_id)

    # Next, run all of the tests to see how and when the set piece sequence
    # ended.
    sequence_df = subsequent_play_generator(
        set_piece_start_id=set_piece_start_id, num_events=25
    )
    sequence_tests = [
        check.changed_possession_checker(set_piece_start_id, sequence_df),
        check.attack_reset_checker(set_piece_start_id, sequence_df),
        check.goalie_save_checker(set_piece_start_id, sequence_df),
        check.goal_checker(set_piece_start_id, sequence_df),
        check.foul_checker(set_piece_start_id, sequence_df),
        check.offsides_checker(set_piece_start_id, sequence_df),
        check.out_of_play_checker(set_piece_start_id, sequence_df),
        check.end_of_regulation_checker(set_piece_start_id, sequence_df)
    ]

    # Now we must investigate the results of the checks
    results_list = [test[0] for test in sequence_tests]
    ids_list = [test[1] for test in sequence_tests]

    try:
        # It must be true that at least one of the test returned true.
        assert any(results_list)
    except AssertionError as ass_err:
        # If none of the test passed, we must let the user know.
        err_msg = "While running all of the tests to figure out when and \
    	where the set piece sequence of interest ended, it was determined \
    	that none of those tests passed. The ID for the event that started \
    	this set piece sequence is `{}`.".format(set_piece_start_id)

        print(err_msg)
        raise ass_err

    which_test_passed = np.argwhere(results_list).flatten()[0]
    last_row_id = ids_list[which_test_passed]
    index_of_passed_test = sequence_df[
        sequence_df.id == last_row_id
    ].first_valid_index()

    sequence_row_indicies = list(range(0, index_of_passed_test + 1, 1))
    final_sequence_df = sequence_df.iloc[sequence_row_indicies]

    # Validate and return result.
    assert final_sequence_df.iloc[-1].id == ids_list[which_test_passed]
    assert final_sequence_df.shape[0] <= sequence_df.shape[0]
    assert final_sequence_df.shape[1] == sequence_df.shape[1]
    assert np.all(np.diff(final_sequence_df.eventSec) >= 0)

    to_return = final_sequence_df

    return to_return


def set_piece_sequences_compiler(
		initiating_events=None) -> pd.DataFrame:
	"""
	Purpose
    -------
    The purpose of this function is to take all of the IDs that correspond
    to the beginning of set piece sequences of interest and return the

    Parameters
    ----------
    initiating_events: Pandas DataFrame or None
    	This argument allows the user to specify which initiating events
    	to use when compiling the data set of set piece sequences. Its
    	default value is None which results in this function calling
    	`set_piece_initating_events_extractor` with its default values.
    	If this is not the behavior the user desires, then they must
    	specify a different collection of initiating events with this
    	argument.

    Returns
    -------
    to_return : Pandas DataFrame
    	This function returns a Pandas DataFrame that contains all of
    	the set piece sequences that it compiled. While making this
    	collection of sequences, the function assigns custom IDs for each
    	set piece sequence it finds. These IDs can be found in the new
    	column `sequence_id`.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html
    2. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rename.html
	"""
	to_return = None
	# First, set the necessary variables using the settings specified by
	# the user.
	if isinstance(initiating_events, type(None)):
		# If the user has left the `initiating_events` to its
		# default value.
		initiating_event_ids = set_piece_initating_events_extractor()
	else:
		initiating_event_ids = initiating_events.id.to_numpy().tolist()

	# Next, compile the sequences.
	sequences_dfs_list = [
		set_piece_sequence_generator(event_id) \
		for event_id in initiating_event_ids
	]

	interim_sequences_df = pd.concat(
		objs=sequences_dfs_list, 
		keys=range(1, len(sequences_dfs_list) + 1)
	)
	final_sequences_df = interim_sequences_df.reset_index().drop(
		columns="level_1").rename(columns={"level_0":"seq_id"})

	to_return = final_sequences_df

	return to_return

