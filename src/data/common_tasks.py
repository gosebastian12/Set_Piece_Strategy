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
import numpy
import pandas as pd
import swifter

# custom modules
from src.data import data_loader as dl

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
PLYR_DF = dl.player_data()
MATCHES_DF = dl.matches_data(league_name="all")
EVENTS_DF = dl.raw_event_data(league_name="all")


################################
### Define Modular Functions ###
################################
def id_checker(id_to_check: int, verbose=1) -> None:
    """
    Purpose
    -------
    The purpose of this function is to run validation tests on any ID
    arguments that the user passes in to the functions that make up the
    source code of this project.

    Parameters
    ----------
    id_to_check : int
        This argument allows the user to specify the event ID for the
        event/play that started the set piece whose subsequent sequence
        of plays we are trying to determine.
    verbose : int
        This argument allows the user to specify whether or not the
        function will print out an error message detailing the error that
        it raises.

    Returns
    -------
    to_return : None
        This function does not return anything regardless of how the
        argument `id_to_check` does in the tests done by this function.

    Raises
    ------
    AssertionError
        This type of error is raised when either the user passes in a
        non-integer ID or a non-positive integer.

    References
    ----------
    1. https://docs.python.org/3/tutorial/errors.html
    """
    try:
        integer_check = [isinstance(id_to_check, int),
                         isinstance(id_to_check, numpy.int),
                         isinstance(id_to_check, numpy.int0),
                         isinstance(id_to_check, numpy.int8),
                         isinstance(id_to_check, numpy.int16),
                         isinstance(id_to_check, numpy.int32),
                         isinstance(id_to_check, numpy.int64),
                         isinstance(id_to_check, numpy.int_),
                         isinstance(id_to_check, numpy.integer)]
        assert any(integer_check)
        assert id_to_check > 0
    except AssertionError as ass_err:
        error_msg = "Invalid input to function. The argument passed in\
		must be non-zero integer. Received type \
		`{}` and value `{}`.".format(type(id_to_check), id_to_check)

        if verbose:
            print(error_msg)
        raise ass_err


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
        (ct.EVENTS_DF.id == set_piece_start_id).to_numpy()
    ).flatten()[0]
    start_set_piece_row = ct.EVENTS_DF.iloc[start_sp_row_index]
    assert isinstance(start_set_piece_row, pd.Series)

    # Now, obtain the rest of the rows that we are interested in analyzing.
    row_indicies = list(range(start_sp_row_index,
                              start_sp_row_index + num_events + 1))

    sp_sequece_df = ct.EVENTS_DF.iloc[row_indicies]

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
        This error is raised when the passed-in value for the `notation_to_return`
        argument is not one of the three accepted value. See the Parameters
        section for what those accepted values are.
    """
    to_return = None
    # First, validate your input data.
    try:
        id_checker(player_wyscout_id, verbose=0)
    except AssertionError:
        return "-1"

    try:
        assert isinstance(notation_to_return, str)
    except BaseException:
        err_msg = "The type for the `notation_to_return` argument must be\
		a string. Received type `{}`.".format(type(notation_to_return))

        print(err_msg)
        raise TypeError

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
    code_to_use = notation_mapper.get("normed_notation")

    player_row = PLYR_DF[PLYR_DF.wyId == player_wyscout_id]
    try:
        assert player_row.shape[0] == 1
    except AssertionError:
        print(player_wyscout_id)
        print(player_row)
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
    tags_that_indicate_a_goal = [{"id":101},
                                 {"id":102},
                                 {"id":1201},
                                 {"id":1202},
                                 {"id":1203},
                                 {"id":1204},
                                 {"id":1205},
                                 {"id":1206},
                                 {"id":1207},
                                 {"id":1208},
                                 {"id":1209}]

    # Next, perform checks.
    for goal_tag in tags_that_indicate_a_goal:
        passed = goal_tag in row_tags_list
        if passed:
            to_return = passed
            break

    return to_return


def score_generator(events_data=EVENTS_DF) -> str:
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

    Returns
    -------
    to_return : str
        This function returns a string that specifies the score of the
        match at the time in which the event pertaining to a specific
        row occurs. It will be in the format "{away-team-score}-{home-team-score}".

    Raises
    ------
    AssertionError
        This error is raised when 

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html
    """
    to_return = None

    # First, validate the input to the function.
    try:
        assert isinstance(events_data, pd.DataFrame)
    except AssertionError:
        err_msg = "The specification for the events data set is invalid.\
        This function accepts a Pandas DataFrame for the `events_data`\
        argument. Received type `{}`.".format(type(events_data))

        print(err_msg)
        raise AssertionError

    # Next, obtain a list of all of the match IDs that we have in this
    # dataset. 
    match_ids_list = list(events_data.matchId.value_counts().index)
    assert len(match_ids_list) == np.unique(match_ids_list).size

    # Now we can iteratively go through each match and update the scores
    # at each point of an event accordingly.
    matches_dfs_list = []

    starting_index_to_search = 0
    num_rows_to_search = 3000
    ending_index_to_search = 3000
    for match_id in match_ids_list:
        # Notice that we're starting by taking a look at each match
        # individually. We make this less computationally redundant by
        # only subset-ing a section of the full data set.
        match_row = MATCHES_DF.wyId == match_id
        assert match_row.shape[0] == 1
        team_ids_arr = np.array(list(match_row.teamsData.keys()))
        team_sides_dict = {
            match_row.teamsData.get(team_ids_arr[0]).get("side").lower(): 
                team_ids_arr[0],
            match_row.teamsData.get(team_ids_arr[1]).get("side").lower(): 
                team_ids_arr[1]
        }

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
                ending_index_to_search:ending_index_to_search+2000
            ]
            more_events = more_candidates[
                more_candidates.matchId == match_id
            ]
            final_mes = pd.concat([match_events, more_events],
                                           ignore_index=True)
        else:
            final_mes = match_events

        # Add a score column to each row in the match.
        scores_in_half1 = final_mes[
            final_mes.matchPeriod == "1H"
        ].swifter.apply(func=goal_checker, axis="columns")
        if np.any(scores_in_half1):
            # If there was at least one goal scored in the first half of
            # the match of interest.
            indicies_of_goals = np.argwhere(
                scores_in_half1).flatten().tolist()

            current_away_score = 0
            current_home_score = 0 
            current_score = "{}-{}".format(current_away_score,
                                           current_home_score)

            half1_scores_list = [current_score]*scores_in_half1.size
            starting_index = 0
            for goal_index in indicies_of_goals:
                side_of_goal = list(team_sides_dict.keys())[
                    np.arghwere(
                        team_ids_arr == final_mes.iloc[goal_index].teamId
                ).flatten()[0]]

                if side_of_goal == "away":
                    current_away_score += 1
                else:
                    current_home_score += 1
                new_score = "{}-{}".format(current_away_score,
                                           current_home_score)
                if starting_index > 0:
                    # If there have been goals scored already.
                    half1_scores_list[starting_index:goal_index] = current_score
                half1_scores_list[goal_index] = new_score

                starting_index = goal_index + 1
                current_score = new_score

            half1_scores_series = pd.Series(half1_scores_list)
        else:
            # If there were no goals scored in the first half.
            away_goals = match_row.teamsData.get(
                team_sides_dict.get("home")
            ).get("scoreHT")
            home_goals = match_row.teamsData.get(
                team_sides_dict.get("away")
            ).get("scoreHT")
            end_of_half1_score = "{}-{}".format(away_goals, home_goals)
            assert end_of_half1_score == "0-0"

            half1_scores_series = pd.Series(
                [end_of_half1_score]*scores_in_half1.size
            )

        scores_in_half2 = final_mes[
            final_mes.matchPeriod == "2H"
        ].swifter.apply(func=goal_checker, axis="columns")
        if np.any(scores_in_half2):
            # If there was at least one goal scored in the second half of
            # the match of interest.
            indicies_of_goals = np.argwhere(
                scores_in_half2).flatten().tolist()

            current_score = half1_scores_series.iloc[-1]
            current_away_score = int(current_score[0])
            current_home_score = int(current_score[-1])

            half2_scores_list = [current_score]*scores_in_half2.size
            starting_index = 0
            for goal_index in indicies_of_goals:
                side_of_goal = list(team_sides_dict.keys())[
                    np.arghwere(
                        team_ids_arr == final_mes.iloc[goal_index].teamId
                ).flatten()[0]]

                if side_of_goal == "away":
                    current_away_score += 1
                else:
                    current_home_score += 1
                new_score = "{}-{}".format(current_away_score,
                                           current_home_score)
                if starting_index > 0:
                    # If there have been goals scored already.
                    half2_scores_list[starting_index:goal_index] = current_score
                half2_scores_list[goal_index] = new_score

                starting_index = goal_index + 1
                current_score = new_score

            half2_scores_series = pd.Series(half2_scores_list)
        else:
            # If there were no goals scored in the second half.
            away_goals = match_row.teamsData.get(
                team_sides_dict.get("home")
            ).get("score")
            home_goals = match_row.teamsData.get(
                team_sides_dict.get("away")
            ).get("score")
            end_of_half2_score = "{}-{}".format(away_goals, home_goals)
            assert end_of_half2_score == end_of_half1_score

            half2_scores_series = pd.Series(
                [end_of_half2_score]*scores_in_half2.size
            )


        score_series = pd.concat([half1_scores_series, half2_scores_series], 
                                 ignore_index=True)
        final_mes["score"] = score_series

        # Update necessary values.
        starting_index_to_search = final_mes.last_valid_index() + 1
        ending_index_to_search = starting_index_to_search + num_rows_to_search

    # Finally, validate the result using the end-of-half and end-of-match
    # score specified in the matches data set.

    return to_return
