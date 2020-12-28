#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 7:20:02 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: Write functions to allow for easy access to tracking data
in Wyscout API and saved locally.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os
from zipfile import ZipFile

# data manipulation
from base64 import b64encode
import pandas as pd

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)


################################
### Define Modular Functions ###
################################
def authentication_header_generator(
        user_name: str, password: str) -> str:
    """
    Purpose
    -------
    The purpose of this function is to provide a tool for the user to
    quickly generate an authentication string header to access the
    Wyscout Events API. This API requires a Basic Authentication header
    which is what this function generates using the specified user name
    and password. More specifically, the generated string is of the form
    "Authorization: Basic {xxxxxx}" where the last part is a base64-encoded
    version of "{user_name}:{password}".

    Parameters
    ----------
    user_name : str
        This parameter allows the user to specify the user name they have
        for their Wyscout account.
    password : str
        This parameter allows the user to specify the password name they
        have for their Wyscout account.

    Returns
    -------
    to_return : str
        This function returns a string of the format
        "Authorization: Basic {xxxxxx}" where the last part is a
        base64-encoded version of "{user_name}:{password}".

    References
    ----------
    1. https://stackabuse.com/encoding-and-decoding-base64-strings-in-python/
    2. https://apidocs.wyscout.com/#section/Authentication
    3. https://stackoverflow.com/questions/18139093/base64-authentication-python
    """
    to_return = None
    # First, validate the inputted data and define the non-decoded version
    # of the authentication header.
    assert isinstance(user_name, str)
    assert isinstance(password, str)

    raw_auth_str = "{}:{}".format(user_name, password)

    # Now encode this authentication string.
    encoded_auth_str = b64encode(
        raw_auth_str.encode("ascii")).decode("ascii")
    assert isinstance(encoded_auth_str, str)

    auth_header = "Authorization: Basic {}".format(encoded_auth_str)

    to_return = auth_header

    return to_return


def raw_event_data(league_name: str) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to allow the user to quickly load in
    any event tracking data they want. Since there are different files
    for the different leagues/competitions we have data for (EPL, Ligue 1,
    La Liga, Serie A, Bundesliga, European Championships, and World Cup),
    all the user has to specify is the league they want data for. By raw
    data, it is meant that it is the data that can be obtained at the link
    specified in 2. in the References section.

    Parameters
    ----------
    league_name : str
        This parameter allows the user to specify for which league they
        would like event tracking data for. Inputs must be one of the
        following:
            1. "england" for EPL data.
            2. "france" for Ligue 1 data.
            3. "spain" for La Liga data.
            4. "italy" for Serie A data.
            5. "germany" for Bundesliga data.
            6. "euro" for European Championships data.
            7. "worldcup" for World Cup data.
            8. "all" for all league/competition data.

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a DataFrame that contains all of the desired
        data that has been loaded in.

    Raises
    ------
    ValueError
        Such an error is raised when the user does not specify one of the
        accepted values for the `league_name` argument.
    FileNotFoundError
        Such an error is raised when the function cannot locate the directory

    References
    ----------
    1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html
    2. https://figshare.com/collections/Soccer_match_event_dataset/4415000
    """
    to_return = None
    # First, let's validate the input data.
    available_leagues = ["england",
                         "france",
                         "spain",
                         "italy",
                         "germany",
                         "euro",
                         "worldcup",
                         "all"]

    normalized_league_name = "".join(league_name.lower().split())
    try:
        # Carry out the test for whether or not the inputted data is
        # valid.
        assert normalized_league_name in available_leagues
    except AssertionError:
        # If the test fails, raise a `ValueError` and print the appropriate
        # error message.
        error_msg = "Inputted data ({}) is not valid. Refer to function\
		documentation for accepted inputs to the `league_name` \
		argument.".format(league_name)

        print(error_msg)
        raise ValueError

    # Next, navigate to the appropriate directory.
    data_rel_dir = "../../data/raw/events/"
    data_dir = os.path.join(SCRIPT_DIR, data_rel_dir)

    try:
        os.chdir(data_dir)
    except FileNotFoundError as error_with_dir:
        error_msg = "Data directory {} could not be located. Has the \
		structure of the cloned repository been modified?".format(data_dir)

        print(error_msg)
        raise error_with_dir

    # Finally, load in data.
    data_file_names = [file for file in os.listdir() if ".json" in file]
    league_file_mapper = {"all": data_file_names,
                          "england": "events_England.json",
                          "france": "events_France.json",
                          "spain": "events_Spain.json",
                          "italy": "events_Italy.json",
                          "germany": "events_Germany.json",
                          "euro": "events_European_Championship.json",
                          "worldcup": "events_World_Cup.json"}
    file_to_load = league_file_mapper.get(normalized_league_name)

    if isinstance(file_to_load, list):
        # If the user is loading every file in the directory.
        loaded_files = [pd.read_json(file) for file in file_to_load]
        final_df = pd.concat(loaded_files).reset_index(drop=True)
    else:
        # If the user is loading a specific file.
        final_df = pd.read_json(file_to_load)

    to_return = final_df

    return to_return


def event_id_mapper(rel_path=None) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to provide a quick and easy way to
    load in the ID mapper file created by Wyscout.

    Parameters
    ----------
    rel_path : str or NoneType
        This argument allows the user to specify a relative path from this
        script to the Event ID Mapper CSV file. Its default value is `None`,
        then it will default to the relative path that is present when
        the project repository is cloned.

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a Pandas DataFrame that contains all of the
        contents loaded in from the Event ID Mapper CSV.
    """
    to_return = None
    # First, let's navigate to the appropriate directory.
    mapper_rel_dir = "../../data/raw/" if not rel_path else rel_path
    mapper_dir = os.path.join(SCRIPT_DIR, mapper_rel_dir)

    try:
        os.chdir(mapper_dir)
    except FileNotFoundError as error_with_dir:
        error_msg = "Data directory {} could not be located. Has the \
		structure of the cloned repository been modified?".format(mapper_dir)

        print(error_msg)
        raise error_with_dir

    # Finally, load in the data with Pandas.
    mapper_df = pd.read_csv("eventid2name.csv")
    to_return = mapper_df

    return to_return


def player_data(rel_path=None) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to provide a quick and easy way to
    load in the ID mapper file created by Wyscout.

    Parameters
    ----------
    rel_path : str or NoneType
        This argument allows the user to specify a relative path from this
        script to the Event ID Mapper CSV file. Its default value is `None`,
        then it will default to the relative path that is present when
        the project repository is cloned.

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a Pandas DataFrame that contains all of the
        contents loaded in from the players data set.
    """
    to_return = None
    # First, let's navigate to the appropriate directory.
    player_rel_dir = "../../data/raw/" if not rel_path else rel_path
    player_dir = os.path.join(SCRIPT_DIR, player_rel_dir)

    try:
        os.chdir(player_dir)
    except FileNotFoundError as error_with_dir:
        error_msg = "Data directory {} could not be located. Has the \
        structure of the cloned repository been modified?".format(player_dir)

        print(error_msg)
        raise error_with_dir

    # Finally, load in the data with Pandas.
    players_df = pd.read_json("players.json")
    to_return = players_df

    return to_return


def matches_data(league_name: str, rel_path=None) -> pd.DataFrame:
    """
    Purpose
    -------
    The purpose of this function is to provide a quick and easy way to
    load in the ID mapper file created by Wyscout.

    Parameters
    ----------
    league_name : str
        This parameter allows the user to specify for which league they
        would like event tracking data for. Inputs must be one of the
        following:
            1. "england" for EPL data.
            2. "france" for Ligue 1 data.
            3. "spain" for La Liga data.
            4. "italy" for Serie A data.
            5. "germany" for Bundesliga data.
            6. "euro" for European Championships data.
            7. "worldcup" for World Cup data.
            8. "all" for all league/competition data.
    rel_path : str or NoneType
        This argument allows the user to specify a relative path from this
        script to the Event ID Mapper CSV file. Its default value is `None`,
        then it will default to the relative path that is present when
        the project repository is cloned.

    Returns
    -------
    to_return : Pandas DataFrame
        This function returns a Pandas DataFrame that contains all of the
        contents loaded in from the matches data set.

    Raises
    ------
    ValueError
        Such an error is raised when the user does not specify one of the
        accepted values for the `league_name` argument.

    References
    ----------
    1. https://discuss.analyticsvidhya.com/t/how-to-read-zip-file-directly-in-python/1659
    """
    to_return = None
    # First, let's navigate to the appropriate directory.
    matches_rel_dir = "../../data/raw/" if not rel_path else rel_path
    matches_dir = os.path.join(SCRIPT_DIR, matches_rel_dir)

    try:
        os.chdir(matches_dir)
    except FileNotFoundError as error_with_dir:
        error_msg = "Data directory {} could not be located. Has the \
        structure of the cloned repository been modified?".format(matches_dir)

        print(error_msg)
        raise error_with_dir

    available_leagues = ["england",
                         "france",
                         "spain",
                         "italy",
                         "germany",
                         "euro",
                         "worldcup",
                         "all"]

    normalized_league_name = "".join(league_name.lower().split())
    try:
        # Carry out the test for whether or not the inputted data is
        # valid.
        assert normalized_league_name in available_leagues
    except AssertionError:
        # If the test fails, raise a `ValueError` and print the appropriate
        # error message.
        error_msg = "Inputted data ({}) is not valid. Refer to function\
        documentation for accepted inputs to the `league_name` \
        argument.".format(league_name)

        print(error_msg)
        raise ValueError

    # Finally, load in the data with Pandas.
    matches_zip_obj = ZipFile("matches.zip", "r")
    data_file_names = [
        file.filename for file in matches_zip_obj.filelist \
        if file.filename.endswith(".json") and file.filename.startswith("matches")
    ]

    league_file_mapper = {"all": data_file_names,
                          "england": "matches_England.json",
                          "france": "matches_France.json",
                          "spain": "matches_Spain.json",
                          "italy": "matches_Italy.json",
                          "germany": "matches_Germany.json",
                          "euro": "matches_European_Championship.json",
                          "worldcup": "matches_World_Cup.json"}
    file_to_load = league_file_mapper.get(normalized_league_name)

    if isinstance(file_to_load, list):
        # If the user is loading every file in the directory.
        loaded_files = [
            pd.read_json(matches_zip_obj.open(file))
            for file in file_to_load
        ]
        final_df = pd.concat(loaded_files).reset_index(drop=True)
    else:
        # If the user is loading a specific file.
        final_df = pd.read_json(matches_zip_obj.open(file_to_load))

    to_return = final_df

    return to_return
