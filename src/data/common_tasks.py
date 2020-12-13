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

# custom modules
from src.data import data_loader as dl

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
PLYR_DF = dl.player_data()


################################
### Define Modular Functions ###
################################
def id_checker(id_to_check: int) -> None:
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
        assert isinstance(id_to_check, int)
        assert id_to_check > 0
    except AssertionError as ass_err:
        error_msg = "Invalid input to function. The argument passed in\
		must be non-zero integer. Received type \
		`{}` and value `{}`.".format(type(id_to_check), id_to_check)

        print(error_msg)
        raise ass_err


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
        the player of interest.

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
    id_checker(player_wyscout_id)

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

    player_position = PLYR_DF[
        PLYR_DF.wyId == player_wyscout_id
    ].role.iloc[0].get(code_to_use)

    to_return = player_position
    return to_return
