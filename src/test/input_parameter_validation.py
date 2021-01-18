#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 17 07:02:44 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: This script contains a collection of functions that
each perform tasks associated with the validation of different objects
that the parameters of the various function found in the scripts of this
project receive.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import numpy as np

# visualization packages
import matplotlib.pyplot as plt

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)

RANDOM_FIG, RANDOM_AX = plt.subplots()
RANDOM_FIG.clear()
AXES_TYPE = type(RANDOM_AX)


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
                         isinstance(id_to_check, np.int),
                         isinstance(id_to_check, np.int0),
                         isinstance(id_to_check, np.int8),
                         isinstance(id_to_check, np.int16),
                         isinstance(id_to_check, np.int32),
                         isinstance(id_to_check, np.int64),
                         isinstance(id_to_check, np.int_),
                         isinstance(id_to_check, np.integer)]
        assert any(integer_check)
        assert id_to_check > 0
    except AssertionError as ass_err:
        error_msg = "Invalid input to function. The argument passed in\
		must be non-zero integer. Received type \
		`{}` and value `{}`.".format(type(id_to_check), id_to_check)

        if verbose:
            print(error_msg)
        raise ass_err


def error_message_generator(
        expected_type: type, parameter_var: object) -> str:
    """
    Purpose
    -------
    The purpose of this function is to generate error messages in the
    event that a `ValueError` is raised when the user passes in an object
    whose type is not accepted by the parameter of a function.

    Parameters
    ----------
    expected_type : Python type objects or tuple of types
        This argument allows the user to specify the type(s) of the object
        for the parameter of interest that are accepted.
    parameter_var : Python object
        This argument allows the user to specify the parameter whose type
        we are interested in. All the user has to pass in to this argument
        is the variable created for the argument when the function was
        called.

    Returns
    -------
    to_return : str
        This functions returns a string that contains the error message
        describing the type received by the function for the parameter of
        interest (whose name is also specified) and the type(s) that
        is (are) accepted for that parameter.

    References
    ----------
    1. https://www.w3schools.com/python/ref_string_format.asp
    2. https://stackoverflow.com/questions/1534504/convert-variable-name-to-string

    Raises
    ------
    ValueError
        This error is raised when the user, for at least one parameter,
        passes in an object whose type is not among the accepted types
        for that parameter.
    """
    to_return = None
    # First, validate the input data.
    received_type = type(parameter_var)
    try:
        if isinstance(expected_type, tuple):
            assert all([t != received_type for t in expected_type])
        else:
            assert received_type != expected_type
    except AssertionError:
        err_msg = "The type of the object passed-in to the parameter of\
		interest is identical to the expected type for this parameter.\
		This function should only be called when these two Python types\
		are different."

        print(err_msg)
        raise ValueError

    # Next, generate the error message. Return the result.
    parameter_name = None
    for name in globals():
        if eval(name) == parameter_var:
            parameter_name = name

    if isinstance(parameter_name, str):
        # If we were able to successfully create a string that contains
        # the name of the parameter of interest.
        err_msg = "The received type for the parameter of interest, `{}`,\
		is: `{}`. Note that this function only accepts objects of type(s):\
		{}".format(parameter_name, received_type, expected_type)
    else:
        # If we were NOT able to successfully create a string that contains
        # the name of the parameter of interest.
        err_msg = "The received type for the parameter of interest is: \
		`{}`. Note that this function only accepts objects of type(s):\
		{}".format(received_type, expected_type)

    to_return = err_msg

    return to_return


def parameter_type_validator(expected_type: type, parameter_var: object):
    """
    Purpose
    -------
    The purpose of this function is to

    Parameters
    ----------
    expected_type : Python type objects or tuple of types
        This argument allows the user to specify the type(s) of the object
        for the parameter of interest that are accepted.
    parameter_var : Python object
        This argument allows the user to specify the parameter whose type
        we are interested in. All the user has to pass in to this argument
        is the variable created for the argument when the function was
        called.

    Returns
    -------
    to_return : None
        This function does not return anything since it is only determining
        if it will raise a ValueError in the event that the user passed-in
        an object whose type is not among the accepted types for the
        parameter of interest.

    Raises
    ------
    ValueError
        This error is raised when

    References
    ----------
    1. https://docs.python.org/3/tutorial/errors.html
    """
    to_return = None
    # Next, determine if the received type is an accepted one.
    try:
        # Begin by trying to tell Python that the two types have to be
        # identical. In the event that the parameter of interest accepts
        # multiple types, we will only assert that one of these accepted
        # types is identical to the received type.
        if isinstance(expected_type, tuple):
            # If there are multiple types that the parameter of interest
            # accepts.
            assert any([
                isinstance(parameter_var, t) for t in expected_type
            ])
        else:
            # If the parameter of interest only accepts one specific type.
            assert isinstance(parameter_var, expected_type)
    except AssertionError:
        # If the user did NOT pass in an object of the correct type.
        err_msg = error_message_generator(expected_type, parameter_var)

        raise ValueError(err_msg)

    return to_return
