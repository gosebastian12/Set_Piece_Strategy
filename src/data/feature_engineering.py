#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 09:50:37 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: Collection of functions that collectively perform all of
the necessary calculations and transformations to the sequence data set
that result in the features we use for model training and evaluation.
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
from src.data import common_tasks as ct

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)


################################
### Define Modular Functions ###
################################
def position_engineer(row) -> list:
    """
    Purpose
    -------
    NOTE THAT THIS FUNCTION IS INTENDED TO BE USED FOR THE `apply()`
    METHOD OF A PANDAS DATAFRAME WITH THE AXIS PARAMETER SET TO `"columns"`
    or `1`.

    The purpose of this function is to

    Parameters
    ----------
    row : row of a Pandas DataFrame
            This argument allows the user to specify which row instance they
            are working with as the `apply()` iteratively gets applied to
            each row of the sequence DataFrame.

    Returns
    -------
    to_return : list of 4 Boolean-integers
        This function returns a list that contains different integers
        that each correspond to an indicator value of whether or not a
        player is listed at that position.
            1. The first value indicates if the player is a goalie.
            2. The second value indicates if the player is a midfielder.
            3. The third value indicates if the player is a defender.
            4. The fourth value indicates if the player is a forward.
        NOTE that there can only be one value in this list that is `1`
        since a player is only listed at one position (the event tracking
        data does not list the position the player played in that game so
        all we have access to is the player's general listed position which
        is fine since that is a proxy for their general skill-set). Also
        NOTE that there will be instances where none of the indicator
        variables are 1 because the initiating player for some events were
        not listed.

        NOTE that when this function is passed to the `apply()` method of
        the sequence dataset, the result will be a Pandas Series comprising
        of the list results for all of the row instances.

    Raises
    ------
    ValueError
        This error is raised when the user is utilizing this function with
        either the incorrect specification of the `axis` argument in the
        `apply()` method for a Pandas DataFrame or they passed in a Pandas
        DataFrame that does not have the proper column(s) needed to run
        this function.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    2. https://github.com/jmcarpenter2/swifter
    """
    to_return = [0] * 4

    # First, validate the input data.
    try:
        player_id = row.playerId
    except AttributeError:
        # If the row/DataFrame passed to the function does not have the
        # proper column(s).
        err_msg = "The row/DataFrame passed to this function does not have\
		the column `playerId`. This column is required to run this function."

        print(err_msg)
        raise ValueError

    # Next, determine the player's position.
    index_of_positions = {"GK": 0, "MD": 1, "DF": 2, "FW": 3}
    if player_id:
        # If the initiating player WAS tracked (if the initiating player
        # was not noted, the entry for the `playerId` column will be 0.
        player_position = ct.player_position_extractor(
            player_wyscout_id=player_id, notation_to_return="two"
        )
        to_return[index_of_positions.get(player_position)] = 1

    # Validate result
    if np.any(to_return):
        # If the initiating player WAS tracked.
        assert np.argwhere(to_return).size == 1
    assert np.argwhere(to_return).size + \
        np.argwhere(np.array(to_return) == 0).size == 4

    return to_return


def delta_distance_engineer(row) -> float:
    """
    Purpose
    -------
    NOTE THAT THIS FUNCTION IS INTENDED TO BE USED FOR THE `apply()`
    METHOD OF A PANDAS DATAFRAME WITH THE AXIS PARAMETER SET TO `"columns"`
    or `1`.

    The purpose of this function is to calculate the Euclidean distance
    between the starting point and the ending point of the event of
    interest.

    Parameters
    ----------
    row : row of a Pandas DataFrame
        This argument allows the user to specify which row instance they
        are working with as the `apply()` iteratively gets applied to
        each row of the sequence DataFrame.

    Returns
    -------
    to_return : float
        This function returns a floating-point value that specifies the
        Euclidean distance between the starting point and the ending point
        of the event of interest.

        NOTE that when this function is passed to the `apply()` method o
        the sequence dataset, the result will be a Pandas Series comprisin
        of the numerical results for all of the row instances.

    Raises
    ------
    ValueError
        This error is raised when the user is utilizing this function with
        either the incorrect specification of the `axis` argument in the
        `apply()` method for a Pandas DataFrame or they passed in a Pandas
        DataFrame that does not have the proper column(s) needed to run
        this function.

    References
    ----------
    1. https://www.geeksforgeeks.org/calculate-the-euclidean-distance-using-numpy/
    2. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    3. https://github.com/jmcarpenter2/swifter
    """
    to_return = None

    # First, validate the input data.
    try:
        event_positions = row.positions
    except AttributeError:
        # If the row/DataFrame passed to the function does not have the
        # proper column(s).
        err_msg = "The row/DataFrame passed to this function does not have\
		the column `positions`. This column is required to run this function."

        print(err_msg)
        raise ValueError

    # Next, perform necessary calculation to arrive at feature value.
    starting_point_arr = np.array([event_positions[0].get("x"),
                                   event_positions[0].get("y")])
    try:
        ending_point_arr = np.array([event_positions[1].get("x"),
                                     event_positions[1].get("y")])
    except IndexError:
        # If the ending field position of the event was NOT tracked. Upon
        # investigation of the data, this only occurs when a foul is
        # committed which makes sense since the ball cannot advance any
        # further from where it started which is where the foul was
        # committed (there are a handful of cases where an ending point
        # was not specified for a pass, but there are so few that we elect
        # to ignore these cases).
        ending_point_arr = starting_point_arr

    eucliden_delta_dist = np.linalg.norm(
        ending_point_arr - starting_point_arr
    )

    # Validate and return result.
    assert eucliden_delta_dist >= 0
    to_return = eucliden_delta_dist

    return to_return


def delta_goal_distance_engineer(row) -> float:
    """
    Purpose
    -------
    NOTE THAT THIS FUNCTION IS INTENDED TO BE USED FOR THE `apply()`
    METHOD OF A PANDAS DATAFRAME WITH THE AXIS PARAMETER SET TO `"columns"`
    or `1`.

    The purpose of this function is to calculate the difference between
    two distances. THe first is the distance between where the event of
    interest started and the middle of the goal line of the defending team
    and the second is the same distance but for where the event of interest
    ended.

    Parameters
    ----------
    row : row of a Pandas DataFrame
        This argument allows the user to specify which row instance they
        are working with as the `apply()` iteratively gets applied to
        each row of the sequence DataFrame.

    Returns
    -------
    to_return : float
        This function returns a floating-point value that specifies the
        difference between the two distances to goal.

        NOTE that when this function is passed to the `apply()` method of
        the sequence dataset, the result will be a Pandas Series comprising
        of the numerical results for all of the row instances.

    Raises
    ------
    ValueError
        This error is raised when the user is utilizing this function with
        either the incorrect specification of the `axis` argument in the
        `apply()` method for a Pandas DataFrame or they passed in a Pandas
        DataFrame that does not have the proper column(s) needed to run
        this function.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    2. https://github.com/jmcarpenter2/swifter
    """
    to_return = None

    # First, validate the input data.
    try:
        event_positions = row.positions
    except AttributeError:
        # If the row/DataFrame passed to the function does not have the
        # proper column(s).
        err_msg = "The row/DataFrame passed to this function does not have\
		the column `positions`. This column is required to run this function."

        print(err_msg)
        raise ValueError

    # Next, perform necessary calculation to arrive at feature value.
    middle_goal_line_point_arr = np.array([100, 50])

    starting_point_arr = np.array([event_positions[0].get("x"),
                                   event_positions[0].get("y")])
    try:
        ending_point_arr = np.array([event_positions[1].get("x"),
                                     event_positions[1].get("y")])
    except IndexError:
        # If the ending field position of the event was NOT tracked. Upon
        # investigation of the data, this only occurs when a foul is
        # committed which makes sense since the ball cannot advance any
        # further from where it started which is where the foul was
        # committed (there are a handful of cases where an ending point
        # was not specified for a pass, but there are so few that we elect
        # to ignore these cases).
        ending_point_arr = starting_point_arr

    starting_goal_dist = np.linalg.norm(
        middle_goal_line_point_arr - starting_point_arr
    )
    ending_goal_dist = np.linalg.norm(
        middle_goal_line_point_arr - ending_point_arr
    )

    goal_delta_dist = ending_goal_dist - starting_goal_dist

    # Validate and return the result.
    to_return = goal_delta_dist

    return to_return


def time_in_match_engineer(row) -> float:
    """
    Purpose
    -------
    NOTE THAT THIS FUNCTION IS INTENDED TO BE USED FOR THE `apply()`
    METHOD OF A PANDAS DATAFRAME WITH THE AXIS PARAMETER SET TO `"columns"`
    or `1`.

    The purpose of this function is to return a normalized version of the
    time in the match in which this event occurs. By normalized, we mean
    that the value specified in the sequence and tracking datasets, number
    of seconds since the beginning of the game, is divided by 5400, the
    number of seconds in 90 minutes.

    Parameters
    ----------
    row : row of a Pandas DataFrame
        This argument allows the user to specify which row instance they
        are working with as the `apply()` iteratively gets applied to
        each row of the sequence DataFrame.

    Returns
    -------
    to_return : float
        This function returns a floating-point value that is (quasi-strictly
        because of extra-time and added-time) between 0 and 1. This specifies
        the proportion through the game in which this event of interest
        occurred (i.e., a value of 0.6 means that the event occurred as
        the game has been 60% completed).

        NOTE that when this function is passed to the `apply()` method of
        the sequence dataset, the result will be a Pandas Series comprising
        of the numerical results for all of the row instances.

    Raises
    ------
    ValueError
        This error is raised when the user is utilizing this function with
        either the incorrect specification of the `axis` argument in the
        `apply()` method for a Pandas DataFrame or they passed in a Pandas
        DataFrame that does not have the proper column(s) needed to run
        this function.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    2. https://github.com/jmcarpenter2/swifter
    """
    to_return = None

    # First, validate the input data.
    try:
        match_time_since_half = row.eventSec
    except AttributeError:
        # If the row/DataFrame passed to the function does not have the
        # proper column(s).
        err_msg = "The row/DataFrame passed to this function does not have\
		the column `eventSec`. This column is required to run this function."

        print(err_msg)
        raise ValueError

    # Next, perform necessary calculation to arrive at feature value.
    total_match_time = 90 * 60    # Note how this is measured in seconds.
    match_time = match_time_since_half
    if row.matchPeriod == "2H":
        # If we have to add the time elapsed in the first half to the
        # time in the match specified in the data.
        match_time += 45 * 60
    elif row.matchPeriod == "E1":
        # If we have to add the times elapsed in the first and second halves
        #  to the time in the match specified in the data.
        match_time += 90 * 60
    elif row.matchPeriod == "E2":
        # If we have to add the time elapsed in the first and second halves
        # as well as the time elapsed in the first period of the extra time
        # to the time in the match specified in the data.
        match_time += 90 * 60 + 15 * 60

    normed_match_time = match_time / total_match_time

    to_return = normed_match_time

    return to_return


def score_differential_engineer(row) -> int:
    """
    Purpose
    -------
    NOTE THAT THIS FUNCTION IS INTENDED TO BE USED FOR THE `apply()`
    METHOD OF A PANDAS DATAFRAME WITH THE AXIS PARAMETER SET TO `"columns"`
    or `1`.

    The purpose of this function is to return the score differential

    Parameters
    ----------
    row : row of a Pandas DataFrame
        This argument allows the user to specify which row instance they
        are working with as the `apply()` iteratively gets applied to
        each row of the sequence DataFrame.

    Returns
    -------
    to_return : int
        This function returns an integer that specifies the score differential
        of the match at the point of the event *from the perspective* of
        the initiating team. That is, a negative integer is returned when
        the initiating team is losing, zero when the two teams are tied,
        and positive when they are winning.

        NOTE that when this function is passed to the `apply()` method of
        the sequence dataset, the result will be a Pandas Series comprising
        of the numerical results for all of the row instances.

    Raises
    ------
    AttributeError
        This error is raised when the user is utilizing this function with
        either the incorrect specification of the `axis` argument in the
        `apply()` method for a Pandas DataFrame or they passed in a Pandas
        DataFrame that does not have the `score` column needed to run
        this function.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    2. https://github.com/jmcarpenter2/swifter
    """
    to_return = None

    # First, validate the input data.
    try:
        score_at_event = row.score
    except AttributeError:
        # If the row/DataFrame passed to the function does not have the
        # proper column(s).
        err_msg = "In order for this function to be run, the passed in\
		data frame row must include the row `score`. If you are using the\
		raw events data set, you must pass it to `score_compiler` function\
		found in the `common_tasks` module to have this necessary column."

        print(err_msg)
        raise AttributeError

    # Next, use the `score` to calculate the score differential for this
    # row. Start by figuring out whether or not the initiating team
    # corresponding to this row is the home team.
    match_row = ct.MATCHES_DF[
        ct.MATCHES_DF.wyId == row.matchId].iloc[0]

    team_ids_list = list(match_row.teamsData.keys())
    team_sides_dict = {
        match_row.teamsData.get(team_ids_list[0]).get("side").lower():
        team_ids_list[0],
        match_row.teamsData.get(team_ids_list[1]).get("side").lower():
        team_ids_list[1]
    }
    inverted_sides_dict = {
        int(j): i for i, j in team_sides_dict.items()
    }

    # Now that we have the initiating team side designation, parse the entry
    # in the score column to figure out the score differential from the
    # perspective of the initiating team.
    initiating_team_side = inverted_sides_dict.get(row.teamId)
    if initiating_team_side == "away":
        # If the team corresponding to this row is the away team.
        initiating_team_score = int(score_at_event[0])
        oppossing_team_score = int(score_at_event[-1])
    elif initiating_team_side == "home":
        # If the team corresponding to this row is the home team.
        initiating_team_score = int(score_at_event[-1])
        oppossing_team_score = int(score_at_event[0])

    score_differntial = initiating_team_score - oppossing_team_score
    to_return = score_differntial

    return to_return


def basic_instance_features(
        events_data_set: pd.DataFrame) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to take the compiled sequence dataset
    and create a a set of basic features for each and every row instance
    in the data set. This "engineered" data will then be used in clustering
    algorithms that will help in the initial signal determination. The
    features "engineered" by this function are:
        1. A set of one-hot encoded variables that specify the position
           of the player that initiated the event corresponding to that
           row instance.
        2. A variable whose value specifies the Euclidean distance between
           the point on the field where the event started and that of where
           it ended.
        3. A variable whose value specifies the difference of the Euclidean
           distances between the event's initial field position and the
           middle point of the goal line of the defending team and that
           corresponding to the event's final field position.
        4. A variable whose value specifies the time of the match (measured
           in seconds since the start of the match) in which the event
           corresponding to the row instance occurred.
        5. A variable whose value specifies the score differential of the
           match at the time at which the event occurred. Specifically,
           the value will be positive if the team initiating the event
           corresponding to that particular row instances is winning the
           match at that time, negative if they are losing, and zero if
           they are currently tied with their opposition.
    NOTE that the code that "engineers" will be broken up into functions
    that each correspond to a specific feature. This function merely calls
    all of those specific, modular functions and puts together their
    results.

    Parameters
    ----------
    events_data_set : Pandas DataFrame
        This argument allows the user to specify the compiled sequence
        dataset that will be transformed to create the training/testing
        feature set.

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a DataFrame that contains the new set of
        row instances that all have values for the engineered features
        described in the Purpose section of this function's documentation.

    Raises
    ------
    ValueError
        This error is raised when the user does specify the right data
        types for the arguments of this function. See function documentation
        and/or printed messages when errors are raised for what the accepted
        types are.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    2. https://stackoverflow.com/questions/35491274/pandas-split-column-of-lists-into-multiple-columns
    """
    to_return = None

    # First, validate the input data.
    try:
        assert isinstance(events_data_set, pd.DataFrame)
    except (AssertionError, IndexError) as errs:
        # If the user did not specify the sequence dataset in a Pandas
        # DataFrame.
        err_msg = "The passed-in value of the `events_data_set` argument\
		must be a Pandas DataFrame. The received type was\
        `{}`".format(type(events_data_set))

        print(err_msg)
        raise ValueError

    # Before we run any of the feature engineering functions, let's first
    # save relevant information that we will potentially need to identify
    # events, matches, and sequences.
    feat_eng_df = pd.DataFrame([])
    feat_eng_df["seq_id"] = events_data_set.seq_id
    feat_eng_df["id"] = events_data_set.id
    feat_eng_df["matchId"] = events_data_set.matchId

    # Next, call all of the functions that engineer each of the new
    # features.

    # Match time feature.
    print("Putting together time in match feature.")
    feat_eng_df["match_time"] = events_data_set.swifter.apply(
        func=time_in_match_engineer, axis="columns"
    )

    # Score feature.
    print("Putting together score differential feature.")
    if "score" in events_data_set.columns:
        feat_eng_df["score_diff"] = events_data_set.swifter.apply(
            func=score_differential_engineer, axis="columns"
        )
    else:
        # If the passed in data set for events do NOT have a `score` column.
        events_data_set["score"] = ct.score_compiler(events_data_set)

        feat_eng_df["score_diff"] = events_data_set.swifter.apply(
            func=score_differential_engineer, axis="columns"
        )
    
    # Position one-hot-encoded-variables.
    print("Putting together player position indicator features.")
    position_indicators = events_data_set.swifter.apply(
        func=position_engineer, axis="columns"
    )
    pos_inds_labels_list = ["is_goalie", "is_mid", "is_def", "is_foward"]
    feat_eng_df[pos_inds_labels_list] = pd.DataFrame(
        position_indicators.tolist(), position_indicators.index
    )

    # Distance-related features.
    print("Putting together distance-related features.")
    feat_eng_df["pos_delta_diff"] = events_data_set.swifter.apply(
        func=delta_distance_engineer, axis="columns"
    )

    feat_eng_df["to_goal_delta_diff"] = events_data_set.swifter.apply(
        func=delta_goal_distance_engineer, axis="columns"
    )

    # Validate result and then return it to the user.
    to_return = feat_eng_df

    return to_return
