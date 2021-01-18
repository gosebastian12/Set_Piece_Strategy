#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 03:14:39 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: This script contains a collection of functions that
each perform tasks associated with the collecting and wrangling of the
team-related data downloaded from Wyscout.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import json
from unidecode import unidecode
import numpy as np
import pandas as pd

# custom modules
from src.test import input_parameter_validation as ipv

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)


################################
### Define Modular Functions ###
################################
def encoded_accent_normalizer(row) -> str:
    """
    Purpose
    -------
    NOTE THAT THIS FUNCTION IS INTENDED TO BE USED FOR THE `apply()`
    METHOD OF A PANDAS DATAFRAME WITH THE AXIS PARAMETER SET TO `"columns"`
    or `1`.

    The purpose of this function is to

    Parameters
    ----------
    row : Pandas DataFrame row
        This argument allows the user to specify

    Returns
    -------
    to_return : str
        This function returns a

    Raises
    ------
    ValueError
        This error is raised when the user passes in incorrect data types
        to the parameters of this function.

    References
    ----------
    1. https://realpython.com/python-string-formatting/
    """
    to_return = None
    # First, define the variables that we are going to need later on in
    # this function
    given_name = row["name"]
    assert isinstance(given_name, str)
    name_in_dict = '{"%s" : 0}' % given_name

    # Next, perform the conversion
    converted_name_in_dict = json.loads(name_in_dict)
    converted_name = list(converted_name_in_dict.keys())[0]

    # Finally, validate and return the result.
    assert isinstance(converted_name, str)
    to_return = converted_name

    return to_return


def team_data_loader(
        rel_dir="../../data/raw/",
        file_name="teams.json",
        normalize_accents=True) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to

    Parameters
    ----------
    rel_dir : str
        This argument allows the user to specify
    file_name : str
        This argument allows the user to specify
    normalize_accents : bool
        This argument allows the user to specify

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a

    Raises
    ------
    ValueError
        This error is raised when the user passes in incorrect data types
        to the parameters of this function.
    FileNotFoundError
        This error is raised when

    References
    ----------
    1. https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
    2. https://docs.python.org/3/library/json.html
    """
    to_return = None
    # First, validate the input data
    ipv.parameter_type_validator(expected_type=str,
                                 parameter_var=rel_dir)
    ipv.parameter_type_validator(expected_type=str,
                                 parameter_var=file_name)
    ipv.parameter_type_validator(expected_type=bool,
                                 parameter_var=normalize_accents)

    # Next, load in the raw data as is.
    team_data_dir = os.path.join(SCRIPT_DIR, rel_dir)
    try:
        assert os.path.exists(team_data_dir)
    except AssertionError:
        err_msg = "The function attempted to locate the data about the\
		teams in the following directory: `{}`. However, that directory\
		does not exist.".format(team_data_dir)

        print(err_msg)
        raise FileNotFoundError

    raw_teams_df = pd.read_json("{}/{}".format(team_data_dir, file_name))

    # Next, normalize some of the text data if the user specified that
    # they would like for the function to do so.
    if normalize_accents:
        final_teams_df = raw_teams_df
        final_teams_df["normalized_name"] = raw_teams_df.apply(
            func=encoded_accent_normalizer,
            axis="columns"
        )

        final_teams_df["no_accent_name"] = final_teams_df.apply(
            func=lambda x: unidecode(x["normalized_name"]),
            axis="columns"
        )

        final_teams_df["name_acronym"] = final_teams_df.apply(
            func=lambda x: "".join(
                [l for l in list(x["normalized_name"]) if l.isupper()]
            ),
            axis="columns"
        )

        to_return = final_teams_df
    else:
        to_return = raw_teams_df

    # Finally, validate and return the result.
    assert isinstance(to_return, pd.DataFrame)

    return to_return


def team_id_extractor(team_name: str, teams_df=team_data_loader()) -> int:
    """
    Purpose
    -------
    The purpose of this function is to

    Parameters
    ----------
    team_name : str
        This argument allows the user to specify
    teams_df : Pandas DataFrame
        This argument allows the user to specify

        This parameter defaults to the output of the `team_data_loader`
        found in this script when all of its arguments are set to their
        default values.

    Returns
    -------
    to_return : int
        This function returns a

    Raises
    ------
    ValueError
        This error is raised when the user passes in incorrect data types
        to the parameters of this function.

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html
    """
    to_return = None
    # First, validate the input data
    ipv.parameter_type_validator(expected_type=str, parameter_var=team_name)
    ipv.parameter_type_validator(expected_type=pd.DataFrame,
                                 parameter_var=teams_df)

    # Next, normalize the user's input for easier search in the team
    # dataframe.
    normed_team_name = " ".join(
        [word for word in team_name.split() if word.lower() != "fc"]
    )
    team_name_acronym = "".join(
        [letter for letter in list(normed_team_name) if letter.isupper()]
    )

    # Now, attempt to search for this team given their name.
    search_attempt_df1 = pd.concat(
        objs=[teams_df[teams_df.normalized_name == normed_team_name],
              teams_df[teams_df.no_accent_name == normed_team_name]],
        ignore_index=True
    )
    if len(team_name_acronym) > 1:
        # If there is a viable acronym for this team. We include this check
        # to guard against cases where the acronym would have just been
        # "B" which is counter-productive since there are many team names
        # that begin with that letter and only have one word to their team
        # name.
        raw_search_attempt_df = pd.concat(
            objs=[search_attempt_df1,
                  teams_df[teams_df.name_acronym == team_name_acronym]],
            ignore_index=True
        )
    else:
        raw_search_attempt_df = search_attempt_df1

    search_attempt_df = raw_search_attempt_df[
        ["name", "wyId", "normalized_name", "no_accent_name"]
    ].drop_duplicates()

    if search_attempt_df.shape[0] > 0:
        # If the function was able to find the team of interest using the
        # collection of team names that DOES include accents on letters.
        try:
            assert search_attempt_df.shape[0] == 1
        except AssertionError:
            err_msg = "For some reason there were multiple matches for the\
			team of interest when searching for them in the teams dataframe."

            print(err_msg)
            raise ValueError

        to_return = search_attempt_df.iloc[0].wyId
    else:
        #
        err_msg = "Attempted to search for the team name `{}` (that is,\
		a normalized version of the input to the `team_name` argument) in\
		the output of the `team_data_loader` function when its parameters\
		are set to their default values. This search was unsuccessful.\
		Perhaps the spelling of the team of interest is incorrect\
		?".format(normed_team_name)

        print(err_msg)
        raise ValueError

    # Finally, validate and return the result.
    assert isinstance(to_return, (int, np.int64, np.int))

    return to_return
