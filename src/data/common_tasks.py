#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 10:21:55 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: This script contains a collection of functions that
individually do not comprise a general category of functions, but are
still used throughout the project and thus require being written in their
own script.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import numpy as np
import pandas as pd
import swifter

# custom modules
from src.data import data_loader as dl
from src.test import input_parameter_validation as ipv

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
PLYR_DF = dl.player_data()
MATCHES_DF = dl.matches_data(league_name="all")
EVENTS_DF = dl.raw_event_data(league_name="all")


################################
### Define Modular Functions ###
################################
def subsequent_play_generator(
        set_piece_start_id: int,
        num_events: int, trim_data=True) -> pd.DataFrame:
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
    trim_data : Boolean
        This argument allows the user to control whether or not the function
        removes data instances if it finds that they correspond to a
        different match and/or half. The default value for this argument
        is true.

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
    ValueError
        This error is raised when the user, for at least one parameter,
        passes in an object whose type is not among the accepted types
        for that parameter.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.first_valid_index.html
    2. https://scipython.com/book/chapter-4-the-core-python-language-ii/questions/determining-if-an-array-is-monotonically-increasing/
    """
    to_return = None
    # First, let's validate the inputted data.
    ipv.id_checker(set_piece_start_id)
    ipv.id_checker(num_events)
    ipv.parameter_type_validator(bool, trim_data)

    # Next, obtain the specific row from the full dataset that pertains
    # to the event that starts the set piece. NOTE that we have validated
    # that the `ID` column of this data is comprised of unique values.
    start_sp_row_index = np.argwhere(
        (EVENTS_DF.id == set_piece_start_id).to_numpy()
    ).flatten()[0]
    start_set_piece_row = EVENTS_DF.iloc[start_sp_row_index]
    assert isinstance(start_set_piece_row, pd.Series)

    # Now, obtain the rest of the rows that we are interested in analyzing.
    row_indicies = list(range(start_sp_row_index,
                              start_sp_row_index + num_events + 1))

    sp_sequece_df = EVENTS_DF.iloc[row_indicies]

    # Validate the data you're about to return.
    assert sp_sequece_df.iloc[0].id == set_piece_start_id
    assert sp_sequece_df.iloc[0].eventId == 3

    if trim_data:
        # If the user would only like instances that correspond to the
        # same half and/or match.
        half_of_set_piece = start_set_piece_row.matchPeriod
        assert isinstance(half_of_set_piece, str)
        match_id_of_set_piece = start_set_piece_row.matchId

        try:
            assert all(sp_sequece_df.matchPeriod == half_of_set_piece)
            interim_sequence_df = sp_sequece_df
        except AssertionError:
            # If there are events that occur in a different half/period
            # from the event that corresponds to the beginning of the set
            # piece.
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
    else:
        # If the user DOES want instances from a different half and/or
        # match.
        final_sequence_df = sp_sequece_df

    to_return = final_sequence_df.reset_index(drop=True)

    return to_return


def player_position_extractor(
        player_wyscout_id: int, notation_to_return: str) -> str:
    """
    Purpose
    -------
    The purpose of this function is to take a player's Wyscout ID and use
    the Wyscout player data to return that player's position.

    Parameters
    ----------
    player_wyscout_id : int
        This argument allows the user to
    notation_to_return : str
        This argument allows the user to specify how many characters
        the returned string that specifies the player's position is
        comprised of. The available options and what they would return
        for a player who plays in the midfield are as follows:
            1. "two", i.e. "MD"
            2. "three", i.e. "MID"
            3. "full", i.e. "Midfielder"

    Returns
    -------
    to_return : str
        This function returns a string that specifies the position of
        the player of interest. NOTE that if the function returns the
        string "-1", that means that the user passed in the player ID
        0 which is listed as the entries for the event instances in the
        full tracking data set. This means that the initiating player
        was not tracked and thus a 0 for the ID was specified instead.

    Raises
    ------
    TypeError
        This error is raised when the user passed-in values for the
        arguments of this function are not the correct types. The required
        type for `player_wyscout_id` is an `int` and it is a `str` for
        `notation_to_return`.
    ValueError
        This error is raised when the user, for at least one parameter,
        passes in an object whose type is not among the accepted types
        for that parameter.
    """
    to_return = None
    # First, validate your input data.
    try:
        ipv.id_checker(player_wyscout_id, verbose=0)
    except AssertionError:
        return "-1"

    ipv.parameter_type_validator(expected_type=str,
                                 parameter_var=notation_to_return)

    accepted_values = ["two", "three", "full"]
    normed_notation = "".join(notation_to_return.lower().split())
    try:
        assert normed_notation in accepted_values
    except BaseException:
        err_msg = "The passed-in value for the `notation_to_return` \
		argument must be one of the three values `two`, `three`, or \
		`full`. The passed-in value was {}.".format(notation_to_return)

        print(err_msg)
        raise ValueError

    # Next, extract the player's position.
    notation_mapper = {"two": "code2",
                       "three": "code3",
                       "full": "name"}
    code_to_use = notation_mapper.get(normed_notation)

    player_row = PLYR_DF[PLYR_DF.wyId == player_wyscout_id]
    try:
        assert player_row.shape[0] == 1
    except AssertionError:
        raise AssertionError

    player_position = player_row.role.iloc[0].get(code_to_use)

    to_return = player_position
    return to_return


def goal_checker(row) -> bool:
    """
    Purpose
    -------
    NOTE THAT THIS FUNCTION IS INTENDED TO BE USED FOR THE `apply()`
    METHOD OF A PANDAS DATAFRAME WITH THE AXIS PARAMETER SET TO `"columns"`
    or `1`.

    The purpose of this function is to examine a row instance of the events
    data set and determine if a goal was scored during it.

    Parameters
    ----------
    row : row of a Pandas DataFrame
        This argument allows the user to specify which row instance they
        are working with as the `apply()` iteratively gets applied to
        each row of the sequence DataFrame.

    Returns
    -------
    to_return : Boolean
        This function returns a Boolean that specifies whether or not a
        goal was scored during the event corresponding to the row of interest.

        NOTE that when this function is passed to the `apply()` method of
        the sequence dataset, the result will be a Pandas Series comprising
        of the logical results for all of the row instances.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    2. https://github.com/jmcarpenter2/swifter
    """
    to_return = False
    # First, define necessary variables.
    row_tags_list = row.tags
    tags_that_indicate_a_goal = [{"id": 101},
                                 {"id": 102}]

    # Next, perform checks.
    if row.eventId != 9:
        # If the event is not listed as a save attempt. This check is
        # included to protect against cases where two different event really
        # correspond to the same thing, in case a shot on goal. We only
        # want to take a look at the event that specifies the shot itself
        # because that will tell us about the team that scored the goal
        # if the shot was successful.
        for goal_tag in tags_that_indicate_a_goal:
            passed = goal_tag in row_tags_list
            if passed:
                to_return = passed
                break

    return to_return


def match_scores_generator(
        match_events: pd.DataFrame) -> pd.Series:
    """
    Purpose
    -------
    The purpose of this function is to take all of the events that occurred
    during a match and return a Pandas Series that specifies the score of the match
    at that particular point of the game.

    Parameters
    ----------
    match_events : Pandas DataFrame
        This argument allows the user to specify the collection of events
        of the match of interest.

    Returns
    -------
    to_return : Pandas Series
        This function returns a Pandas Series that specifies the score of
        the match at each event that each row corresponds to. Thus, the
        size of this Series will be equivalent to the number of rows in
        the data frame passed-in to the `match_events` argument.

    Raises
    ------
    ValueError
        This error is raised when the user, for at least one parameter,
        passes in an object whose type is not among the accepted types
        for that parameter.
    """
    to_return = None
    # First, validate input data.
    ipv.parameter_type_validator(expected_type=pd.DataFrame,
                                 parameter_var=match_events)

    assert np.all(match_events.id.value_counts() == 1)
    assert np.all(match_events.matchId.value_counts() == match_events.shape[0])

    # Next, determine home-away designations.
    match_row = MATCHES_DF[
        MATCHES_DF.wyId == match_events.iloc[0].matchId
    ].iloc[0]

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

    # Next, iterate through the events of the first half.
    # Initialize certain values.
    half1_events = match_events[match_events.matchPeriod == "1H"]
    scores_in_half1_series = half1_events.swifter.progress_bar(False).apply(
        func=goal_checker, axis="columns"
    )
    assert scores_in_half1_series.size == half1_events.shape[0]
    half1_scores_list = []

    current_away_score = 0
    current_home_score = 0
    current_score = "{}-{}".format(current_away_score,
                                   current_home_score)

    if np.any(scores_in_half1_series):
        # If there was at least one goal scored in the first half of
        # the match of interest.
        indicies_of_goals = np.argwhere(
            scores_in_half1_series.to_numpy()).flatten().tolist()

        for goal_index in indicies_of_goals:
            # Iterate through each instance of a goal being scored.
            goal_row = match_events.iloc[goal_index]
            side_of_goal = inverted_sides_dict[goal_row.teamId]
            was_own_goal = {"id": 102} in goal_row.tags

            if side_of_goal == "away":
                if was_own_goal:
                    # If a team committed an own goal, then that counts
                    # as a score for the other team.
                    current_home_score += 1
                else:
                    # If this was just a regular ol'goal.
                    current_away_score += 1
            elif side_of_goal == "home":
                if was_own_goal:
                    # If a team committed an own goal, then that counts
                    # as a score for the other team.
                    current_away_score += 1
                else:
                    # If this was just a regular ol'goal.
                    current_home_score += 1
            new_score = "{}-{}".format(current_away_score,
                                       current_home_score)
            half1_scores_list += [
                current_score] * (goal_index - len(half1_scores_list))
            half1_scores_list.append(new_score)

            # Update initialized values.
            current_score = new_score

        # Fill in the remaining values since the last goal found above.
        half1_scores_list += [current_score] * (
            scores_in_half1_series.size - len(half1_scores_list))
    else:
        half1_scores_list = [current_score] * scores_in_half1_series.size

    # Validate final first half score we arrived at.
    assert len(half1_scores_list) == scores_in_half1_series.size

    end_of_half1_away_score = match_row.teamsData.get(
        team_sides_dict.get("away")
    ).get("scoreHT")
    end_of_half1_home_score = match_row.teamsData.get(
        team_sides_dict.get("home")
    ).get("scoreHT")
    end_of_half1_score = "{}-{}".format(end_of_half1_away_score,
                                        end_of_half1_home_score)
    try:
        assert end_of_half1_score == current_score
    except AssertionError as not_right_score_error:
        print("Match ID: {}".format(match_events.iloc[0].matchId))
        print("Halftime score from match dataset: {}".format(end_of_half1_score))
        print("Halftime score we found: {}".format(current_score))
        raise not_right_score_error

    half1_scores_series = pd.Series(half1_scores_list)

    # Next, iterate through the events of the second half.
    current_score = half1_scores_series.iloc[-1]
    current_away_score = int(current_score[0])
    current_home_score = int(current_score[-1])

    half2_events = match_events[match_events.matchPeriod == "2H"]
    scores_in_half2_series = half2_events.swifter.progress_bar(False).apply(
        func=goal_checker, axis="columns"
    )
    assert half2_events.shape[0] == scores_in_half2_series.size
    half2_scores_list = []

    if np.any(scores_in_half2_series):
        # If there was at least one goal scored in the second half of
        # the match of interest.
        indicies_of_goals = np.argwhere(
            scores_in_half2_series.to_numpy()).flatten().tolist()

        for goal_index in indicies_of_goals:
            corrected_goal_index = goal_index + half1_scores_series.size
            assert corrected_goal_index <= match_events.shape[0]

            goal_row = match_events.iloc[corrected_goal_index]
            side_of_goal = inverted_sides_dict.get(goal_row.teamId)
            was_own_goal = {"id": 102} in goal_row.tags

            if side_of_goal == "away":
                if was_own_goal:
                    current_home_score += 1
                else:
                    current_away_score += 1
            else:
                if was_own_goal:
                    current_away_score += 1
                else:
                    current_home_score += 1
            new_score = "{}-{}".format(current_away_score,
                                       current_home_score)

            half2_scores_list += [current_score] * (
                goal_index - len(half2_scores_list))
            half2_scores_list.append(new_score)

            current_score = new_score

        # Fill in the remaining values since the last goal found above.
        half2_scores_list += [current_score] * (
            scores_in_half2_series.size - len(half2_scores_list))
    elif match_row.wyId == 2499781:
        # If we are dealing with a match that, for some reason, does not
        # have a specified goal event despite there in fact being a goal
        # scored in the match. This particular match is the Chelsea,
        # Manchester City match from 09/30/2017 that ended 0-1 thanks to
        # Kevin De Bruyne's goal in the 67th minute.
        events_times = match_events[match_events.matchPeriod == "2H"].eventSec

        goal_threshold = np.argwhere(
            (events_times >= (67 - 45) * 60).to_numpy()
        ).flatten()[0]
        half2_scores_list = ["0-0"] * goal_threshold + \
            ["1-0"] * (events_times.size - goal_threshold)

        current_score = "1-0"
    else:
        half2_scores_list = [current_score] * scores_in_half2_series.size

    # Validate final second half score we arrived at.
    assert len(half2_scores_list) == scores_in_half2_series.size

    end_of_half2_away_score = match_row.teamsData.get(
        team_sides_dict.get("away")
    ).get("score")
    end_of_half2_home_score = match_row.teamsData.get(
        team_sides_dict.get("home")
    ).get("score")
    end_of_half2_score = "{}-{}".format(end_of_half2_away_score,
                                        end_of_half2_home_score)
    try:
        assert end_of_half2_score == current_score
    except AssertionError as not_right_score_error:
        print("Match ID: {}".format(match_events.iloc[0].matchId))
        print("End of second half score from match dataset: {}".format(
            end_of_half2_score))
        print("End of second half score we found: {}".format(current_score))
        raise not_right_score_error

    half2_scores_series = pd.Series(half2_scores_list)

    # Next, iterate through the events of the extra period (if there was
    # one).
    match_duration = match_row.duration
    if match_duration == "Regular":
        # If there was no extra-time played.
        et_scores_series = pd.Series([], dtype="object")
        penalties_scores_series = pd.Series([], dtype="object")
    elif match_duration in ["ExtraTime", "Penalties"]:
        # If there was a pair of extra-time periods played.
        current_score = half2_scores_series.iloc[-1]
        current_away_score = int(current_score[0])
        current_home_score = int(current_score[-1])

        extra_period_events = match_events[
            np.logical_or(match_events.matchPeriod == "E1",
                          match_events.matchPeriod == "E2")
        ]
        scores_in_et_series = extra_period_events.swifter.progress_bar(
            False).apply(func=goal_checker, axis="columns")
        et_scores_list = []

        if np.any(scores_in_et_series):
            # If there was at least one goal scored in an extra period.
            indicies_of_goals = np.argwhere(
                scores_in_et_series.to_numpy()).flatten().tolist()

            for goal_index in indicies_of_goals:
                corrected_goal_index = goal_index + half2_scores_series.size
                assert corrected_goal_index <= match_events.shape[0]

                side_of_goal = inverted_sides_dict.get(
                    match_events.iloc[corrected_goal_index].teamId
                )

                if side_of_goal == "away":
                    current_away_score += 1
                else:
                    current_home_score += 1
                new_score = "{}-{}".format(current_away_score,
                                           current_home_score)

                et_scores_list += [current_score] * (
                    goal_index - len(et_scores_list))
                et_scores_list.append(new_score)

                current_score = new_score

            # Fill in the remaining values since the last goal found above.
            et_scores_list += [current_score] * (
                scores_in_et_series.size - len(et_scores_list))

            et_scores_series = pd.Series(et_scores_list)
            assert et_scores_series.size == scores_in_et_series.size
        else:
            # If there were no goals scored in the extra time period.
            et_scores_series = pd.Series(
                [current_score] * extra_period_events.shape[0],
                dtype="object"
            )

        # Finally, add on whatever last score we arrived at for penalty
        # events that were tracked.
        penalties_events = match_events[match_events.matchPeriod == "P"]
        penalties_scores_series = pd.Series(
            [current_score] * penalties_events.shape[0]
        )

    # Put together all three of your results.
    score_series = pd.concat(objs=[half1_scores_series,
                                   half2_scores_series,
                                   et_scores_series,
                                   penalties_scores_series],
                             ignore_index=True
                             )
    try:
        assert score_series.size == match_events.shape[0]
    except AssertionError as no_scores_for_each_event:
        print(match_events.iloc[0].matchId)
        print("Number of Scores Compiled: {}".format(score_series.size))
        print("Number of Events Specified: {}".format(match_events.shape[0]))
        raise no_scores_for_each_event

    to_return = score_series

    return to_return


def score_compiler(
        events_data=EVENTS_DF,
        as_series=True,
        subset_search=False) -> str:
    """
    Purpose
    -------
    The purpose of this function is to take the raw tracking data and output
    the score of the match at the time in which the event occurred. The
    score will be in the format  "{away-team-score}-{home-team-score}".
    This is obtained by iteratively going through the data set and finding
    the instances where goals are scored.

    Parameters
    ----------
    events_data : Pandas DataFrame
        This argument allows the user to specify the entire collections
        of events that they would like to work with when determining scores
        of games.

        This parameter's value defaults to the dataframe comprising all
        of the events we have tracking data for that is loaded-in at the
        beginning of this script.
    as_series : Boolean
        This argument allows the user to control what DataType the function
        will return its results as. If specified as `True`, then the collection
        of scores will be returned as a Pandas Series. If specified as
        `False`, then the collection of scores will be appended as a new
        column the DataFrame specified with the `events_data` argument and
        that new DataFrame will be returned. The version of this function
        only supports these two options.

        This parameter's value default to `True`.
    subset_search : Boolean
        This argument allows the user to control

        This parameter's value default to `True`.

    Returns
    -------
    to_return : str
        This function returns a string that specifies the score of the
        match at the time in which the event pertaining to a specific
        row occurs. It will be in the format "{away-team-score}-{home-team-score}".

    Raises
    ------
    AssertionError
        This error is raised when the user does NOT pass in the correct
        DataType for the `events_data` argument. It must be a Pandas
        DataFrame.
    ValueError
        This error is raised when the user, for at least one parameter,
        passes in an object whose type is not among the accepted types
        for that parameter.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html
    """
    to_return = None

    # First, validate the input to the function.
    ipv.parameter_type_validator(expected_type=pd.DataFrame,
                                 parameter_var=events_data)
    ipv.parameter_type_validator(expected_type=bool,
                                 parameter_var=as_series)
    ipv.parameter_type_validator(expected_type=bool,
                                 parameter_var=subset_search)

    # Next, obtain a list of all of the match IDs that we have in this
    # dataset.
    match_ids_list = list(events_data.matchId.value_counts().index)
    assert len(match_ids_list) == np.unique(match_ids_list).size

    # Now we can iteratively go through each match and update the scores
    # at each point of an event accordingly.
    objs_to_concat = []

    starting_index_to_search = 0
    num_rows_to_search = 3000
    ending_index_to_search = 3000
    for match_id in match_ids_list:
        if subset_search:
            # Notice that we're starting by taking a look at each match
            # individually. We make this less computationally redundant
            # by only subset-ing a subset of the full data set.
            candidate_match_events = events_data[
                starting_index_to_search:ending_index_to_search:
            ]
            match_events = candidate_match_events[
                candidate_match_events.matchId == match_id
            ]
            if match_events.shape[0] == candidate_match_events.shape[0]:
                # If we included all of the candidates in our collection of
                # match events. This means that there is a chance that there
                # are more events that we are not including.
                more_candidates = events_data[
                    ending_index_to_search:ending_index_to_search + 2000
                ]
                more_events = more_candidates[
                    more_candidates.matchId == match_id
                ]
                final_mes = pd.concat([match_events, more_events],
                                      ignore_index=True)
            else:
                # `final_mes` stands for final match events.
                final_mes = match_events
        else:
            final_mes = events_data[events_data.matchId == match_id]

        # Add a score column to each row in the match. Since we are given
        # the scores at the end of every half in the matches data set, we
        # perform our score compilation on a half-by-half-basis so as to
        # validate our results along the way.
        scores_series = match_scores_generator(final_mes)
        if as_series:
            # If the user would like the results to be returned as a
            # Pandas Series.
            objs_to_concat.append(scores_series)
        else:
            final_mes["score"] = scores_series
            objs_to_concat.append(final_mes)

        # Update necessary values.
        starting_index_to_search = final_mes.last_valid_index() + 1
        ending_index_to_search = starting_index_to_search + num_rows_to_search

    # Finally, validate and return the result
    to_return = pd.concat(objs_to_concat, ignore_index=True)
    assert to_return.shape[0] == events_data.shape[0]
    if not as_series:
        assert to_return.shape[1] + 1 == events_data.shape[1]

    return to_return
