#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 13 02:21:39 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: Write functions that allow the user to determine how and
when set piece sequences end.
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
from src.data import set_piece_extractor as spe

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
RAW_EVENTS_DF = dl.raw_event_data(league_name="all")
FINAL_EVENTS_DF = RAW_EVENTS_DF[RAW_EVENTS_DF.playerId > 0]


################################
### Define Modular Functions ###
################################
def checker_function_set_up(
        set_piece_start_id: int, sequence_to_use=None) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to contain all of the code that must
    be run at the beginning of each checker function in this script so
    that all that code just lives in one place.

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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
        function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a Pandas DataFrame that specifies the
        collection of events that will be investigated to determine a set
        piece sequence.

    Raises
    ------
    AssertionError
        This error is raised when the user does not use the `sequence_to_use`
        argument correctly. See the Parameters section for directions
        regarding proper use.
    """
    to_return = None
    # First, let's validate the inputted data.
    ct.id_checker(set_piece_start_id)

    # Next obtain subsequent plays.
    if isinstance(sequence_to_use, type(None)):
        # If the user did NOT specify a particular set piece sequence to
        # use.
        sequence_df = spe.subsequent_play_generator(
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

    to_return = sequence_df
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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
        function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with possession
        changing and False otherwise. The second is the event ID of the
        event that marks the end of the set piece sequence of interest if
        the first element is True and `-1` if the first element is False.
    """
    to_return = [False, -1]
    # First, define the variables that we need.
    sequence_df = checker_function_set_up(set_piece_start_id,
                                          sequence_to_use)

    # Now determine if the sequence of events that make up the set piece
    # of interest was ended by a change in possession. We check this by
    # determining if either the opposing team has possessed the ball for
    # an extended period of time, for an extended number of plays, or if
    # they have possession deep in their territory.
    opp_poss_time_threshold = 15     # measured in seconds.
    opp_poss_cons_time = 0           # measured in seconds.

    consec_passes_threshold = 3
    num_consecutive_opp_passes = 0
    consec_passes_ids = []
    past_event_by_opp = [False, -1]

    for event in sequence_df.to_numpy().tolist()[1::]:
        # Iterate over each event.
        if event[7] != sequence_df.iloc[0].teamId:
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
            checks_list = [
                num_consecutive_opp_passes > consec_passes_threshold,
                opp_poss_cons_time >= opp_poss_time_threshold,
                any([start_x > 50, end_x > 50]),
                {"id": 1901} in event[2]
            ]
            if any(checks_list):
                try:
                    first_cp_row_index = np.argwhere(
                        (sequence_df.id == consec_passes_ids[0]).to_numpy()
                    ).flatten()[0]

                    to_return = [
                        True, sequence_df.iloc[first_cp_row_index - 1].id
                    ]
                except IndexError:
                    to_return = [True, event[-1]]
                break

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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
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
    # First, define the variables that we need.
    sequence_df = checker_function_set_up(set_piece_start_id,
                                          sequence_to_use)

    # Now let us determine if the set piece sequence ended with the attacking
    # team resetting their attack.
    midfieldish_to_back_polygon = Polygon([
        [55, 0], [0, 0], [0, 100], [55, 100], [55, 0]
    ])

    for event in sequence_df.to_numpy().tolist()[1::]:
        # Iterate over each event that we have obtained.
        if event[7] == sequence_df.iloc[0].teamId:
            # Only do an analysis of events if they were initiated by
            # the attacking team. This is because events by the other team
            # do not tell us anything about any resets that were made by
            # the attacking team.
            initiating_player_pos = ct.player_position_extractor(
                player_wyscout_id=event[3],
                notation_to_return="three"
            )
            # First, take a look at where the event occurred. If it
            # occurred near mid-field or in the attacking team's side of
            # the pitch, then that may be because of a reset that was
            # initiated by the attacking team.
            starting_point = Point(
                event[4][0].get("x"), event[4][0].get("y")
            )
            ending_point = Point(
                event[4][1].get("x"), event[4][1].get("y")
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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
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
    # First, define the variables that we need.
    sequence_df = checker_function_set_up(set_piece_start_id,
                                          sequence_to_use)

    # Now let us determine if the set piece was finished by the goalie
    # saving a shot attempt.
    save_attempt_checker_arr = (sequence_df.eventId == 9).to_numpy()
    if np.any(save_attempt_checker_arr):
        # If there was a save attempt made in this sequence of plays.
        row_indicies_of_save_attempts = np.argwhere(
            save_attempt_checker_arr).flatten().tolist()

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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
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
    # First, define the variables that we need.
    sequence_df = checker_function_set_up(set_piece_start_id,
                                          sequence_to_use)

    # Now let us determine if the set piece sequence of interest was ended
    # by a goal being scored.
    goal_checker_arr = sequence_df.swifter.progress_bar(False).apply(
        func=lambda x: {"id": 101} in x.tags,
        axis="columns"
    ).to_numpy()
    if np.any(goal_checker_arr):
        # If there was a save attempt made in this sequence of plays.
        row_index_of_goal = np.argwhere(
            goal_checker_arr).flatten()[0]
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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
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
    # First, define the variables that we need.
    sequence_df = checker_function_set_up(set_piece_start_id,
                                          sequence_to_use)

    # Now let us determine if the set piece sequence of interest was ended
    # by a foul being committed.
    foul_checker_arr = (sequence_df.eventId == 2).to_numpy()
    if np.any(foul_checker_arr):
        # If there was a foul committed in this sequence of plays.
        row_index_of_foul = np.argwhere(
            foul_checker_arr).flatten()[0]
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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
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
    # First, define the variables that we need.
    sequence_df = checker_function_set_up(set_piece_start_id,
                                          sequence_to_use)

    # Now let us determine if the set piece sequence ended because of an
    # offsides call.
    offside_checker_arr = (sequence_df.eventId == 6).to_numpy()
    if np.any(offside_checker_arr):
        # If there was a player on the attacking team called offsides.
        row_index_of_offside = np.argwhere(
            offside_checker_arr).flatten()[0]
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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
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
    # First, define the variables that we need.
    sequence_df = checker_function_set_up(set_piece_start_id,
                                          sequence_to_use)

    # Now let us determine if the set piece sequence ended because of the
    # ball ending up out of bounds.
    out_of_bounds_checker_arr = (sequence_df.subEventId == 50).to_numpy()
    if np.any(out_of_bounds_checker_arr):
        # If there was a player on the attacking team called offsides.
        row_index_of_out = np.argwhere(
            out_of_bounds_checker_arr).flatten()[0]
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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
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
    """
    to_return = [False, -1]
    # First, define the variables that we need.
    sequence_df = checker_function_set_up(set_piece_start_id,
                                          sequence_to_use)

    # Now let us determine if the set piece sequence ended because of the
    # half or match ending.
    whistle_checker_arr = (sequence_df.subEventId == 51).to_numpy()
    if np.any(whistle_checker_arr):
        # If there was a referee whistle that caused an interruption in play.
        whistle_row_indicies = np.argwhere(
            whistle_checker_arr).tolist()
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


def effective_clearance_checker(
        set_piece_start_id: int, sequence_to_use=None) -> list:
    """
    Purpose
    -------
    The purpose of this function is to take the ID for the event that
    starts a set piece and analyze the next several plays to determine if
    the sequence that followed the set piece ended with an effective
    clearance by the (originally) defending team. By an effective clearance,
    it is meant that the ball ended up more than 60 total yards away from
    where it started and/or more than 40 lateral yards from where it started
    laterally. Even if the (originally) attacking team regains possession,
    this is still considered the end of the set piece sequence because as
    a result of the ball traveling such a far distance, whatever strategy
    the (originally) attacking team was employing had to be abandoned in
    the interest of defense.

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
        to `None`, the function will utilize the `spe.subsequent_play_generator`
        function with the user-value for the `set_piece_start_id` argument.

    Returns
    -------
    to_return : list
        This function returns a list that contains two elements. The first
        is a Boolean that is True if the sequence ended with play being
        stopped because of an effective clearance. and False otherwise.
        The second is the event ID of the event that marks the end of the
        set piece sequence of interest if the first element is True and
        `-1` if the first element is False.

    References
    ----------
    1. https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html
    2. https://www.geeksforgeeks.org/calculate-the-euclidean-distance-using-numpy/
    """
    to_return = [False, -1]
    # First, define the variables that we need.
    sequence_df = checker_function_set_up(set_piece_start_id,
                                          sequence_to_use)

    # Next, see if the set piece sequence ended with an effective
    # clearance.
    clearance_checker_arr = (sequence_df.subEventId == 71).to_numpy()
    if any(clearance_checker_arr):
        # If there was a clearance made in this sequence of events.
        clearances_row_indicies = np.argwhere(
            clearance_checker_arr).flatten().tolist()

        for clearance_row_index in clearances_row_indicies:
            clearance_row = sequence_df.iloc[clearance_row_index]

            # Make position calculations. Note that since clearances can
            # only be made by the defending team, an effective clearance
            # will correspond to at least the x value increasing.
            start_pos_dict = clearance_row.positions[0]
            end_pos_dict = clearance_row.positions[1]

            start_pos_arr = np.array(list(start_pos_dict.values()))
            end_pos_arr = np.array(list(end_pos_dict.values()))

            lateral_pos_delta = end_pos_dict.get("x") - start_pos_dict.get("x")
            total_pos_delta = np.linalg.norm(end_pos_arr - start_pos_arr)

            # Evaluate position calculations.
            if total_pos_delta >= 60 and lateral_pos_delta > 0:
                # If the clearance traveled more than 60 total yards and
                # is in a direction away from the defending team's own
                # goal.
                to_return = [
                    True, sequence_df.iloc[clearance_row_index - 1].id
                ]
            elif lateral_pos_delta >= 40:
                to_return = [
                    True, sequence_df.iloc[clearance_row_index - 1].id
                ]

    return to_return
