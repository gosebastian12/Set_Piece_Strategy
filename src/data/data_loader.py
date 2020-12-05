#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 7:20:02 2020

@author: Sebastian E. Gonzalez

Script Purpose: Write functions to allow for easy access to tracking data
in Wyscout API.
"""
####################################
### Neccessary Import Statements ###
####################################
# data manipulation
import numpy as np
from base64 import b64encode

# API-specific packages
import requests as req

################################
### Define Modular Functions ###
################################
def authentication_header_generator(
		user_name: str, password: str) -> str:
	"""
	Purpose
	-------
	The purpose of this function is to

	Parameters
	----------
	user_name : str
		This parameter allows the user to specify
	password : str
		This parameter allows the user to specify

	Returns
	-------
	to_return : str
		This function returns

	References
	----------
	1. https://stackabuse.com/encoding-and-decoding-base64-strings-in-python/
	2. https://apidocs.wyscout.com/#section/Authentication
	3. https://stackoverflow.com/questions/18139093/base64-authentication-python
	4. 
	"""
	to_return = None
	# First, validate the inputted data and define the non-decoded version
	# of the authentification header.
	assert isinstance(user_name, str)
	assert isinstance(password, str)

	raw_auth_str = "{}:{}".format(user_name, password)

	# Now encode this authentification string.
	encoded_auth_str = b64encode(
		raw_auth_str.encode("ascii")).decode("ascii")
	assert isinstance(encoded_auth_str, str)

	auth_header = "Authorization: Basic {}".format(encoded_auth_str)

	to_return = auth_header

	return to_return

