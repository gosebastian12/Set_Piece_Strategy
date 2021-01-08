#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 08 09:40:30 CST 2021

@author: Sebastian E. Gonzalez

Script Purpose: Collection of functions that are used to build an LSTM model
that is used to classify a sequence of set piece-related events in a set
of pre-determined classes.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import numpy as np
import pandas as pd

# deep learning modules
from tf.keras import Sequential, layers
from tf.keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
from tf.distribute import MirroredStrategy
from tf.keras.optimizers import Adam

# custom modules

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)


################################
### Define Modular Functions ###
################################
def hi():
	"""
	Purpose
	-------
	The purpose of this function is to

	Parameters
	----------
	arg_1 : 
		This parameter allows the user to specify

	Returns
	-------
	to_return : 
		This function returns a 

	Raises
	------
	ValueError
		This error is raised when 

	References
	----------
	1.
	"""
	to_return = None
	# First, validate the input data

	# Next,

	# Finally, validate and return the result
	return to_return
	