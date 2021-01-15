#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 07:37:56 CST 2021

@author: Sebastian E. Gonzalez

Script Purpose: Collection of functions that are used to take new instances
of match event data and run it through a pre-determined pipeline that results
in a prediction per the user's choosing.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import numpy as np
import pandas as pd

# custom modules

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)


################################
### Define Modular Functions ###
################################
def new_data_validation(event_data: pd.DataFrame):
	"""
	Purpose
	-------
	The purpose of this function is to begin the data pre-processing
	component of the model pipelines trained in this project using the
	publicly available event tracking data (see project repository for
	more information on this data set). Specifically, this function will
	perform validation tests on this new data (i.e., the data is organized
	by match, half, and time).

	Parameters
	----------
	event_data : Pandas DataFrame
		This parameter allows the user to specify the collection of match
		events that make up their new dataset. 

	Returns
	-------
	to_return : None
		This function does not return anything due to the fact that all
		it is doing is running validation tests on the data passed in to
		the `event_data` argument.

	Raises
	------
	ValueError
		This error is raised either when the passed-in data is not of the
		correct type (see the Parameters section) or if it fails one of
		the validation tests run by this function. These include:
			1. 

	References
	----------
	1.
	"""
	to_return = None
	# First, validate the input data
	try:
		assert isinstance(event_data, pd.DataFrame)
	except AssertionError:
		err_msg = "The received type for the `event_data` argument was:\
		`{}`. This function only accepts Pandas DataFrames for this\
		argument.".format(type(event_data))

		print(err_msg)
		raise ValueError

	# Assert that the data is organized

	# Assert that there are set piece initiating events

	return to_return
	

# def hi():
# 	"""
# 	Purpose
# 	-------
# 	The purpose of this function is to

# 	Parameters
# 	----------
# 	arg_1 : 
# 		This parameter allows the user to specify

# 	Returns
# 	-------
# 	to_return : 
# 		This function returns a 

# 	Raises
# 	------
# 	ValueError
# 		This error is raised when 

# 	References
# 	----------
# 	1.
# 	"""
# 	to_return = None
# 	# First, validate the input data

# 	# Next,

# 	# Finally, validate and return the result
# 	return to_return
# 	