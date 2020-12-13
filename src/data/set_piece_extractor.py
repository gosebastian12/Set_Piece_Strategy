#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Dec 08 06:14:02 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: Write functions that allow the user to take the raw
Wyscout event-log data and obtain a collection of all of the set pieces
and their subsequent plays that are present.
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
from shapely.geometry import Polygon, Point

# custom modules
from src.data import data_loader as dl
from src.data import common_tasks as ct

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
RAW_EVENTS_DF = dl.raw_event_data(league_name="all")


################################
### Define Modular Functions ###
################################
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
    """
    to_return = None
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)
    ct.id_checker(num_events)

    # Next, obtain the specific row from the full dataset that pertains
    # to the event that starts the set piece. NOTE that we have validated
    # that the `ID` column of this data is comprised of unique values.
    start_set_piece_row = RAW_EVENTS_DF[RAW_EVENTS_DF.id == set_piece_start_id]
    start_set_piece_index = start_set_piece_row.first_valid_index()
    assert start_set_piece_row.shape[0] == 1

    # Now, obtain the rest of the rows that we are interested in analyzing.
    row_indicies = list(range(start_set_piece_index,
                             start_set_piece_index + num_events + 1))

    sp_sequece_df = RAW_EVENTS_DF.iloc[row_indicies]

    # Validate the data you're about to return.
    half_of_set_piece = start_set_piece_row.iloc[0].matchPeriod
    assert isinstance(half_of_set_piece, str)
    match_id_of_set_piece = start_set_piece_row.iloc[0].matchId

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


def changed_possession_checker(
		set_piece_start_id: int, sequence_to_use=None) -> list:
    """
    Purpose
    -------
    The purpose of this function is to take the ID for the event that
    starts a set piece and analyze the next several plays to determine if
    the sequence that followed the set piece ended with the non-attacking
    team gaining possession.

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    sequence_to_use : Pandas DataFrame or None
    	This argument allows the user to specify a particular sequence of
    	events to use when testing to see when and how the set piece
    	sequence it contains ended. Its default value is `None`. When set
    	to `None`, the function will utilize the `subsequent_play_generator`
    	function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with possession
        changing and False otherwise. The second is the event ID of the
        event that marks the end of the set piece sequence of interest if
        the first element is True and `-1` if the first element is False.

    Raises
    ------
    ValueError
    	This error is raised when the user passes
    """
    to_return = [False, -1]
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)

    # Next obtain subsequent plays.
    if isinstance(sequence_to_use, type(None)):
    	# If the user did NOT specify a particular set piece sequence to
    	# use.
    	sequence_df = subsequent_play_generator(
    		set_piece_start_id=set_piece_start_id, num_events=20
    	)
    else:
    	# If the user DID specify a particular set piece sequence to
    	# use.
    	try:
    		assert isinstance(sequence_to_use, pd.DataFrame)
    	except AssertionError:
    		err_msg = "The data-type of the passed-in value for the \
    		`sequence_to_use` argument is invalid. It must be either `None` \
    		or a Pandas DataFrame. Received type: \
    		`{}`.".format(type(sequence_to_use))

    		print(err_msg)
    		raise ValueError

    	sequence_df = sequence_to_use
 
    # Now determine if the sequence of events that make up the set piece
    # of interest was ended by a change in possession. We check this by
    # determining if either the opposing team has possessed the ball for
    # an extended period of time, for an extended number of plays, or if
    # they have possession deep in their territory.
    beginning_row = sequence_df.iloc[0]

    opp_poss_time_threshold = 15     # measured in seconds.
    opp_poss_cons_time = 0           # measured in seconds.

    consec_passes_threshold = 3
    num_consecutive_opp_passes = 0
    consec_passes_ids = []
    past_event_by_opp = [False, -1]

    for event in sequence_df.to_numpy().tolist()[1::]:
        # Iterate over each event.
        if event[7] != beginning_row.teamId:
            # If the opposing team is initiating this event. Notice how
            # we have taken advantage of the fact that the `teamID` entry
            # is always in the 8th column of the data set.

            # Perform any necessary cumulative operations.
            if past_event_by_opp[0]:
                # If the last event we investigated was initiated by the
                # opposing team.
                opp_poss_cons_time += event[9] - past_event_by_opp[1]
                num_consecutive_opp_passes += 1

            start_x = event[4][0].get("x")
            end_x = event[4][1].get("x")

            # Threshold checks
            if num_consecutive_opp_passes > consec_passes_threshold:
                # If the opposing team has made several passes in a row.
                to_return = [True, consec_passes_ids[0]]
                break
            if opp_poss_cons_time >= opp_poss_time_threshold:
                # If the opposing team has had uninterrupted possession
                # for more than 30 seconds.
                to_return = [True, consec_passes_ids[0]]
                break
            if any([start_x > 50, end_x > 50]):
                # If the (originally) opposing team has fought its way to
                # the (originally) attacking team's side of the field.
                try:
                    to_return = [True, consec_passes_ids[0]]
                except IndexError:
                    to_return = [True, event[-1]]
                break
            if {"id": 1901} in event[2]:
                # If the event tracking has noted that there is a counter
                # attack going on.
                try:
                    to_return = [True, consec_passes_ids[0]]
                except IndexError:
                    to_return = [True, event[-1]]

            # Update necessary values.
            past_event_by_opp = [True, event[9]]
            consec_passes_ids.append(event[-1])
        else:
            # If the attacking team still has possession.
            num_consecutive_opp_passes = 0
            opp_poss_cons_time = 0
            consec_passes_ids = []

    return to_return


def attack_reset_checker(
		set_piece_start_id: int, sequence_to_use=None) -> list:
    """
    Purpose
    -------
    The purpose of this function is to take the ID for the event that
    starts a set piece and analyze the next several plays to determine if
    the sequence that followed the set piece ended with the attacking team
    deciding to "reset" their attack (i.e., passing back to players at
    midfield to start a new play).

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    sequence_to_use : Pandas DataFrame or None
    	This argument allows the user to specify a particular sequence of
    	events to use when testing to see when and how the set piece
    	sequence it contains ended. Its default value is `None`. When set
    	to `None`, the function will utilize the `subsequent_play_generator`
    	function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with the attacking
        team resetting and False otherwise. The second is the event ID
        of the event that marks the end of the set piece sequence of
        interest if the first element is True and `-1` if the first
            element is False.

    References
    ----------
    1. https://shapely.readthedocs.io/en/latest/manual.html#introduction
    """
    to_return = [False, -1]
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)

    # Next obtain subsequent plays.
    if isinstance(sequence_to_use, type(None)):
    	# If the user did NOT specify a particular set piece sequence to
    	# use.
    	sequence_df = subsequent_play_generator(
    		set_piece_start_id=set_piece_start_id, num_events=20
    	)
    else:
    	# If the user DID specify a particular set piece sequence to
    	# use.
    	try:
    		assert isinstance(sequence_to_use, pd.DataFrame)
    	except AssertionError:
    		err_msg = "The data-type of the passed-in value for the \
    		`sequence_to_use` argument is invalid. It must be either `None` \
    		or a Pandas DataFrame. Received type: \
    		`{}`.".format(type(sequence_to_use))

    		print(err_msg)
    		raise ValueError

    	sequence_df = sequence_to_use

    # Now let us determine if the set piece sequence ended with the attacking
    # team resetting their attack.
    attacking_team_id = sequence_df.iloc[0].teamId

    midfieldish_to_back_polygon = Polygon([
        [55, 0], [0, 0], [0, 100], [55, 100], [55, 0]
    ])

    for event in sequence_df.to_numpy().tolist()[1::]:
        # Iterate over each event that we have obtained.
        if event[7] == attacking_team_id:
            # Only do an analysis of events if they were initiated by
            # the attacking team. This is because events by the other team
            # do not tell us anything about any resets that were made by
            # the attacking team.
            initiating_player_pos = ct.player_position_extractor(
                player_wyscout_id=event[3],
                notation_to_return="three"
            )

            event_field_position = event[4]

            # First, take a look at where the event occurred. If it
            # occurred near mid-field or in the attacking team's side of
            # the pitch, then that may be because of a reset that was
            # initiated by the attacking team.
            starting_point = Point(
                event_field_position[0].get("x"),
                event_field_position[0].get("y")
            )
            ending_point = Point(
                event_field_position[1].get("x"),
                event_field_position[1].get("y")
            )

            # After defining these variables, make the position checks.
            reset_pos = ["DEF", "GKP"]
            if initiating_player_pos in reset_pos and event[0] != 10:
                # If the player initiating the event is a defender or
                # goal keeper and is not attempting a shot.
                to_return = [True, event[-1]]  # Give spot check for this test.

            is_back_field = [
                ending_point.within(midfieldish_to_back_polygon),
                starting_point.within(midfieldish_to_back_polygon)
            ]
            if any(is_back_field):
                # If this event is one where it starts or ends in the
                # attacking team's own side of the pitch.
                to_return = [True, event[-1]]

            consec_backward_pass = 0
            consec_backward_threshold = 3
            consec_backward_passes_ids = []
            # Recall how the field position goes up as the attacking
            # team gets closer to the opponent's goal.
            if starting_point.x > ending_point.x:
                # If this specific event is associated with a backwards
                # pass by the team that initiated the set piece.
                consec_backward_pass += 1
                consec_backward_passes_ids.append(event[-1])
            else:
                # If the event is not a backwards pass.
                consec_backward_pass = 0
                consec_backward_passes_ids = []
            if consec_backward_pass >= consec_backward_threshold:
                # If you have seen multiple backward passes in a road.
                to_return = [True, consec_backward_passes_ids[0]]

    return to_return


def goalie_save_checker(
		set_piece_start_id: int, sequence_to_use=None) -> list:
    """
    Purpose
    -------
    The purpose of this function is to take the ID for the event that
    starts a set piece and analyze the next several plays to determine if
    the sequence that followed the set piece ended with the opposing team's
    goalie saving a shot.

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    sequence_to_use : Pandas DataFrame or None
    	This argument allows the user to specify a particular sequence of
    	events to use when testing to see when and how the set piece
    	sequence it contains ended. Its default value is `None`. When set
    	to `None`, the function will utilize the `subsequent_play_generator`
    	function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with the goalie
        saving a shot and False otherwise. The second is the event ID of
        the event that marks the end of the set piece sequence of interest
        if the first element is True and `-1` if the first element is False.

    References
    ----------
    1. https://numpy.org/doc/stable/reference/generated/numpy.any.html
    """
    to_return = [False, -1]
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)

    # Next obtain subsequent plays.
    if isinstance(sequence_to_use, type(None)):
    	# If the user did NOT specify a particular set piece sequence to
    	# use.
    	sequence_df = subsequent_play_generator(
    		set_piece_start_id=set_piece_start_id, num_events=20
    	)
    else:
    	# If the user DID specify a particular set piece sequence to
    	# use.
    	try:
    		assert isinstance(sequence_to_use, pd.DataFrame)
    	except AssertionError:
    		err_msg = "The data-type of the passed-in value for the \
    		`sequence_to_use` argument is invalid. It must be either `None` \
    		or a Pandas DataFrame. Received type: \
    		`{}`.".format(type(sequence_to_use))

    		print(err_msg)
    		raise ValueError

    	sequence_df = sequence_to_use

    # Now let us determine if the set piece was finished by the goalie
    # saving a shot attempt.
    save_attempt_checker_series = sequence_df.eventId == 9
    if np.any(save_attempt_checker_series):
        # If there was a save attempt made in this sequence of plays.
        row_indicies_of_save_attempts = np.argwhere(
            save_attempt_checker_series).flatten().tolist()

        for row_index in row_indicies_of_save_attempts:
            # Iterate over each instance of a save (shot) attempt. For
            # each, check to see if the shot was accurate (meaning if the
            # goalie does not save it, a goal will be scored) and if the
            # event that immediately followed it was a pass initiated by
            # the goalie. Both of these conditions passing means that the
            # shot was in fact saved by the goalie. We opt for this series
            # of checks because the event tracking data does not make
            # note of goalie saves when they occur.
            event_row = sequence_df.iloc[row_index]

            next_event_row = sequence_df.iloc[row_index + 1]
            next_initiating_player_pos = ct.player_position_extractor(
                player_wyscout_id=next_event_row.playerId,
                notation_to_return="two"
            )

            was_save_checker = [next_initiating_player_pos == "GK",
                                {"id": 1801} in event_row.tags]
            if {"id": 101} in event_row.tags:
                # If a goal was scored (don't do anything since that is
                # checked by another function). We are checking for this
                # first because it will free us from having to do the two
                # goalie save checks for the instances in which a goal
                # was scored meaning that right off the bat, we know that
                # the goalie did not save the shot.
                pass
            elif was_save_checker:
                # If all of our checks for a successful save attempt
                # pass.
                to_return = [True, event_row.id]
                break

    return to_return


def goal_checker(
		set_piece_start_id: int, sequence_to_use=None) -> list:
    """
    Purpose
    -------
    The purpose of this function is to take the ID for the event that
    starts a set piece and analyze the next several plays to determine if
    the sequence that followed the set piece ended with the attacking
    team ultimately scoring a goal.

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    sequence_to_use : Pandas DataFrame or None
    	This argument allows the user to specify a particular sequence of
    	events to use when testing to see when and how the set piece
    	sequence it contains ended. Its default value is `None`. When set
    	to `None`, the function will utilize the `subsequent_play_generator`
    	function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with a goal being
        scored by the attacking team and False otherwise. The second is
        the event ID of the event that marks the end of the set piece
        sequence of interest if the first element is True and `-1` if the
            first element is False.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    """
    to_return = [False, -1]
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)

    # Next obtain subsequent plays.
    if isinstance(sequence_to_use, type(None)):
    	# If the user did NOT specify a particular set piece sequence to
    	# use.
    	sequence_df = subsequent_play_generator(
    		set_piece_start_id=set_piece_start_id, num_events=20
    	)
    else:
    	# If the user DID specify a particular set piece sequence to
    	# use.
    	try:
    		assert isinstance(sequence_to_use, pd.DataFrame)
    	except AssertionError:
    		err_msg = "The data-type of the passed-in value for the \
    		`sequence_to_use` argument is invalid. It must be either `None` \
    		or a Pandas DataFrame. Received type: \
    		`{}`.".format(type(sequence_to_use))

    		print(err_msg)
    		raise ValueError

    	sequence_df = sequence_to_use

    # Now let us determine if the set piece sequence of interest was ended
    # by a goal being scored.
    goal_checker_series = sequence_df.swifter.apply(
        func=lambda x: {"id": 101} in x.tags,
        axis="columns"
    )
    if np.any(goal_checker_series):
        # If there was a save attempt made in this sequence of plays.
        row_index_of_goal = np.argwhere(
            goal_checker_series).flatten()[0]
        to_return = [True,
                     sequence_df.iloc[row_index_of_goal].id]

    return to_return


def foul_checker(
		set_piece_start_id: int, sequence_to_use=None) -> list:
    """
    Purpose
    -------
    The purpose of this function is to take the ID for the event that
    starts a set piece and analyze the next several plays to determine if
    the sequence that followed the set piece ended with play stopping
    because of a foul being committed.

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    sequence_to_use : Pandas DataFrame or None
    	This argument allows the user to specify a particular sequence of
    	events to use when testing to see when and how the set piece
    	sequence it contains ended. Its default value is `None`. When set
    	to `None`, the function will utilize the `subsequent_play_generator`
    	function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with play being
        stopped because of a foul and False otherwise. The second is the
        event ID of the event that marks the end of the set piece
        sequence of interest if the first element is True and `-1` if the
            first element is False.

    References
    ----------
    1.
    """
    to_return = [False, -1]
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)

    # Next obtain subsequent plays.
    if isinstance(sequence_to_use, type(None)):
    	# If the user did NOT specify a particular set piece sequence to
    	# use.
    	sequence_df = subsequent_play_generator(
    		set_piece_start_id=set_piece_start_id, num_events=20
    	)
    else:
    	# If the user DID specify a particular set piece sequence to
    	# use.
    	try:
    		assert isinstance(sequence_to_use, pd.DataFrame)
    	except AssertionError:
    		err_msg = "The data-type of the passed-in value for the \
    		`sequence_to_use` argument is invalid. It must be either `None` \
    		or a Pandas DataFrame. Received type: \
    		`{}`.".format(type(sequence_to_use))

    		print(err_msg)
    		raise ValueError

    	sequence_df = sequence_to_use

    # Now let us determine if the set piece sequence of interest was ended
    # by a foul being committed.
    foul_checker_series = sequence_df.eventId == 2
    if np.any(foul_checker_series):
        # If there was a foul committed in this sequence of plays.
        row_index_of_foul = np.argwhere(
            foul_checker_series).flatten()[0]
        to_return = [True,
                     sequence_df.iloc[row_index_of_foul].id]

    return to_return


def offsides_checker(
		set_piece_start_id: int, sequence_to_use=None) -> list:
    """
    Purpose
    -------
    The purpose of this function is to take the ID for the event that
    starts a set piece and analyze the next several plays to determine if
    the sequence that followed the set piece ended with play stopping
    because of a player on the attacking team being offsides.

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    sequence_to_use : Pandas DataFrame or None
    	This argument allows the user to specify a particular sequence of
    	events to use when testing to see when and how the set piece
    	sequence it contains ended. Its default value is `None`. When set
    	to `None`, the function will utilize the `subsequent_play_generator`
    	function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with play being
        stopped because of an offside call and False otherwise. The second
        is the event ID of the event that marks the end of the set piece
        sequence of interest if the first element is True and `-1` if the
        first element is False.

    References
    ----------
    1.
    """
    to_return = [False, -1]
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)

    # Next obtain subsequent plays.
    if isinstance(sequence_to_use, type(None)):
    	# If the user did NOT specify a particular set piece sequence to
    	# use.
    	sequence_df = subsequent_play_generator(
    		set_piece_start_id=set_piece_start_id, num_events=20
    	)
    else:
    	# If the user DID specify a particular set piece sequence to
    	# use.
    	try:
    		assert isinstance(sequence_to_use, pd.DataFrame)
    	except AssertionError:
    		err_msg = "The data-type of the passed-in value for the \
    		`sequence_to_use` argument is invalid. It must be either `None` \
    		or a Pandas DataFrame. Received type: \
    		`{}`.".format(type(sequence_to_use))

    		print(err_msg)
    		raise ValueError

    	sequence_df = sequence_to_use

    # Now let us determine if the set piece sequence ended because of an
    # offsides call.
    offside_checker_series = sequence_df.eventId == 6
    if np.any(offside_checker_series):
        # If there was a player on the attacking team called offsides.
        row_index_of_offside = np.argwhere(
            offside_checker_series).flatten()[0]
        to_return = [True,
                     sequence_df.iloc[row_index_of_offside].id]

    return to_return


def out_of_play_checker(
		set_piece_start_id: int, sequence_to_use=None) -> list:
    """
    Purpose
    -------
    The purpose of this function is to take the ID for the event that
    starts a set piece and analyze the next several plays to determine if
    the sequence that followed the set piece ended with play stopping
    because of the ball ending up out of play.

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    sequence_to_use : Pandas DataFrame or None
    	This argument allows the user to specify a particular sequence of
    	events to use when testing to see when and how the set piece
    	sequence it contains ended. Its default value is `None`. When set
    	to `None`, the function will utilize the `subsequent_play_generator`
    	function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with play being
        stopped because of the ball ending up out of play and False
        otherwise. The second is the event ID of the event that marks the
        end of the set piece sequence of interest if the first element is
            True and `-1` if the first element is False.

    References
    ----------
    1.
    """
    to_return = [False, -1]
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)

    # Next obtain subsequent plays.
    if isinstance(sequence_to_use, type(None)):
    	# If the user did NOT specify a particular set piece sequence to
    	# use.
    	sequence_df = subsequent_play_generator(
    		set_piece_start_id=set_piece_start_id, num_events=20
    	)
    else:
    	# If the user DID specify a particular set piece sequence to
    	# use.
    	try:
    		assert isinstance(sequence_to_use, pd.DataFrame)
    	except AssertionError:
    		err_msg = "The data-type of the passed-in value for the \
    		`sequence_to_use` argument is invalid. It must be either `None` \
    		or a Pandas DataFrame. Received type: \
    		`{}`.".format(type(sequence_to_use))

    		print(err_msg)
    		raise ValueError

    	sequence_df = sequence_to_use

    # Now let us determine if the set piece sequence ended because of the
    # ball ending up out of bounds.
    out_of_bounds_checker_series = sequence_df.subEventId == 50
    if np.any(out_of_bounds_checker_series):
        # If there was a player on the attacking team called offsides.
        row_index_of_out = np.argwhere(
            out_of_bounds_checker_series).flatten()[0]
        to_return = [True,
                     sequence_df.iloc[row_index_of_out].id]

    return to_return


def end_of_regulation_checker(
		set_piece_start_id: int, sequence_to_use=None) -> list:
    """
    Purpose
    -------
    The purpose of this function is to take the ID for the event that
    starts a set piece and analyze the next several plays to determine if
    the sequence that followed the set piece ended with play stopping
    because of the half/game ending.

    Parameters
    ----------
    set_piece_start_id : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    sequence_to_use : Pandas DataFrame or None
    	This argument allows the user to specify a particular sequence of
    	events to use when testing to see when and how the set piece
    	sequence it contains ended. Its default value is `None`. When set
    	to `None`, the function will utilize the `subsequent_play_generator`
    	function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with play being
        stopped because of the half/game ending. and False otherwise. The
        second is the event ID of the event that marks the end of the set
        piece sequence of interest if the first element is True and `-1`
            if the first element is False.

    References
    ----------
    1.
    """
    to_return = [False, -1]
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)

    # Next obtain subsequent plays.
    if isinstance(sequence_to_use, type(None)):
    	# If the user did NOT specify a particular set piece sequence to
    	# use.
    	sequence_df = subsequent_play_generator(
    		set_piece_start_id=set_piece_start_id, num_events=20
    	)
    else:
    	# If the user DID specify a particular set piece sequence to
    	# use.
    	try:
    		assert isinstance(sequence_to_use, pd.DataFrame)
    	except AssertionError:
    		err_msg = "The data-type of the passed-in value for the \
    		`sequence_to_use` argument is invalid. It must be either `None` \
    		or a Pandas DataFrame. Received type: \
    		`{}`.".format(type(sequence_to_use))

    		print(err_msg)
    		raise ValueError

    	sequence_df = sequence_to_use

    # Now let us determine if the set piece sequence ended because of the
    # half or match ending.
    whistle_checker_series = sequence_df.subEventId == 51
    if np.any(whistle_checker_series):
        # If there was a referee whistle that caused an interruption in play.
        whistle_row_indicies = np.argwhere(
            whistle_checker_series).tolist()
        for while_index in whistle_row_indicies:
            # Iterate over each instance of a whistle occurring that caused
            # a pause in play.
            whistle_row = sequence_df.iloc[while_index]
            next_row = sequence_df.iloc[while_index + 1]

            half_match_checker = [
                whistle_row.matchPeriod != next_row.matchPeriod,
                whistle_row.matchId != next_row.matchId
            ]
            if any(half_match_checker):
                # If we have confirmed that the whistle was because of
                # an end in the half/match.
                to_return = [True, whistle_row.id]
                break

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
    	set_piece_start_id=set_piece_start_id, num_events=20
    )
    sequence_tests = [
    	changed_possession_checker(set_piece_start_id, sequence_df),
    	attack_reset_checker(set_piece_start_id, sequence_df),
    	goalie_save_checker(set_piece_start_id, sequence_df),
    	goal_checker(set_piece_start_id, sequence_df),
    	foul_checker(set_piece_start_id, sequence_df),
    	offsides_checker(set_piece_start_id, sequence_df),
    	out_of_play_checker(set_piece_start_id, sequence_df),
    	end_of_regulation_checker(set_piece_start_id, sequence_df)
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
    	this set piece sequence is `{}`.".format(start_set_piece_index)

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
