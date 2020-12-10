#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Dec 08 06:14:02 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: Write functions that allow the user to take the raw
Wyscout event-log data and obtain a collection of all of the set pieces
and their subsequent plays that are present.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import pandas as pd
import numpy as np

# custom modules
from src.data import data_loader as dl

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
RAW_EVENTS_DF = dl.raw_event_data(league_name="all")


################################
### Define Modular Functions ###
################################
def start_id_checker(set_piece_start_id: int) -> None:
	"""
	Purpose
	-------
	The purpose of this function is to use the 

	Parameters
	----------
	set_piece_start_id : int
		This argument allows the user to specify the event ID for the
		event/play that started the set piece whose subsequent sequence
		of plays we are trying to determine.

	Returns
	-------
	to_return : 
		This function returns 

	References
	----------
	1. https://docs.python.org/3/tutorial/errors.html
	"""
	try:
		assert isinstance(set_piece_start_id, int)
	except AssertionError as ass_err:
		error_msg = "Invalid input to function. The argument \
		`set_piece_start_id` must be an integer. Received type \
		`{}`.".format(type(set_piece_start_id))

		print(error_msg)
		raise ass_err

	pass

def subsequent_play_generator(
		set_piece_start_id: int, num_events: int) -> pd.DataFrame:
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
	"""
	to_return = None
	# First, let's validate the inputted data.
	_ = start_id_checker(set_piece_start_id)
	_ = start_id_checker(num_events)

	# Next, obtain the specific row from the full dataset that pertains
	# to the event that starts the set piece. NOTE that we have validated
	# that the `ID` column of this data is comprised of unique values.
	start_set_piece_row = RAW_EVENTS_DF[RAW_EVENTS_DF.id == set_piece_start_id]
	assert start_set_piece_row.shape[0] == 1

	# Now, obtain the rest of the rows that we are interested in analyzing.
	start_df_row_index = start_set_piece_row.index[0]
	row_indexes = list(range(start_set_piece_row,
		                     start_set_piece_row + num_events + 1))

	sp_sequece_df = RAW_EVENTS_DF.iloc[row_indexes]

	# Validate the data you're about to return.
	half_of_set_piece = start_set_piece_row.matchPeriod
	match_id_of_set_piece = start_set_piece_row.matchId

	try:
		assert all(sp_sequece_df.matchPeriod == half_of_set_piece)
		interim_sequence_df = sp_sequece_df
	except AssertionError:
		# If there are events that occur in a different half/period from
		# the event that corresponds to the beginning of the set piece.
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

	to_return = final_sequence_df.reset_index(drop=True)

	return to_return


def changed_possession_checker(set_piece_start_id: int) -> list:
	"""
	Purpose
	-------
	The purpose of this function is to take the ID for the event that
	starts a set piece and analyze the next several plays to determine if
	the sequence that followed the set piece ended with the non-attacking
	team gaining possession.

	Parameters
	----------
	set_piece_start_id : int
		This argument allows the user to specify the event ID for the
		event/play that started the set piece whose subsequent sequence
		of plays we are trying to determine.

	Returns
	-------
	to_return : list
		This function returns a list that contains two elements. The first
		is a Boolean that is True if the sequence ended with possession 
		changing and False otherwise. The second is the event ID of the
		event that marks the end of the set piece sequence of interest if
		the first element is True and `-1` if the first element is False.

	References
	----------
	1. 
	"""
	interim_to_return = None
	# First, let's validate the inputted data.
	_ = start_id_checker(set_piece_start_id)

	# Next obtain subsequent plays.
	sequence_df = subsequent_play_generator(
		set_piece_start_id=set_piece_start_id, num_events=25
	)

	# Now determine if the sequence of events that make up the set piece
	# of interest was ended by a change in possession. We check this by
	# determining if either the opposing team has possessed the ball for
	# an extended period of time, for an extended number of plays, or if
	# they have possession deep in their territory.
	beginning_row = sequence_df.iloc[0]
	attacking_team_id = beginning_row.teamId
	field_position_start = beginning_row.positions

	opp_poss_time_threshold = 15     # measured in seconds.
	opp_poss_cons_time = 0           # measured in seconds.

	consec_passes_threshold = 3
	num_consecutive_opp_passes = 0
	past_event_by_opp = [False, -1]

	for event in sequence_df.to_numpy().tolist():
		# Iterate over each event.
		if event[7] != attacking_team_id:
			# If the opposing team is initiating this event. Notice how
			# we have taken advantage of the fact that the `teamID` entry
			# is always in the 8th column of the data set.
			event_type = event[0]

			# Perform any necessary cumulative operations.
			if past_event_by_opp[0]:
				# If the last event we investigated was initiated by the
				# opposing team.
				opp_poss_cons_time += event[9] - past_event_by_opp[1]
				num_consecutive_opp_passes += 1

				event_field_position = event[4]
				start_x = event_field_position[0].get("x")
				start_y = event_field_position[0].get("y")
				end_x = event_field_position[1].get("x")
				end_y = event_field_position[1].get("y")

			# Threshold checks
			if num_consecutive_opp_passes > consec_passes_threshold:
				# If the opposing team has made several passes in a row.
				interim_to_return = [True, event[-1]]
				break
			if opp_poss_cons_time >= opp_poss_time_threshold:
				# If the opposing team has had uninterrupted possession
				# for more than 30 seconds.
				interim_to_return = [True, event[-1]]
				break
			if any([start_x > 50, start_y > 50, end_x > 50, end_y > 50]):
				# If the (originally) opposing team has fought its way to
				# the (originally) attacking team's side of the field.
				interim_to_return = [True, event[-1]]
				break

			# Update necessary values.
			past_event_by_opp = [True, event[9]]
		else:
			# If the attacking team still has possession.
			num_consecutive_opp_passes = 0
			opp_poss_cons_time = 0

	to_return = [False, -1] if isinstance(interim_to_return, type(None)) \
	                        else interim_to_return

	return to_return


def attack_reset_checker(set_piece_start_id: int) -> list:
	"""
	Purpose
	-------
	The purpose of this function is to take the ID for the event that
	starts a set piece and analyze the next several plays to determine if
	the sequence that followed the set piece ended with the attacking team
	deciding to "reset" their attack (i.e., passing back to players at 
	midfield to start a new play).

	Parameters
	----------
	set_piece_start_id : int
		This argument allows the user to specify the event ID for the
		event/play that started the set piece whose subsequent sequence
		of plays we are trying to determine.

	Returns
	-------
	to_return : list
		This function returns a list that contains two elements. The first
		is a Boolean that is True if the sequence ended with the attacking 
		team resetting and False otherwise. The second is the event ID
		of the event that marks the end of the set piece sequence of
		interest if the first element is True and `-1` if the first
		element is False.

	References
	----------
	1. 
	"""
	to_return = None
	# First, let's validate the inputted data.
	_ = start_id_checker(set_piece_start_id)

	# Next,

	return to_return


def goalie_save_checker(set_piece_start_id: int) -> list:
	"""
	Purpose
	-------
	The purpose of this function is to take the ID for the event that
	starts a set piece and analyze the next several plays to determine if
	the sequence that followed the set piece ended with the opposing team's
	goalie saving a shot.

	Parameters
	----------
	set_piece_start_id : int
		This argument allows the user to specify the event ID for the
		event/play that started the set piece whose subsequent sequence
		of plays we are trying to determine.

	Returns
	-------
	to_return : list
		This function returns a list that contains two elements. The first
		is a Boolean that is True if the sequence ended with the goalie
		saving a shot and False otherwise. The second is the event ID of
		the event that marks the end of the set piece sequence of interest
		if the first element is True and `-1` if the first element is False.

	References
	----------
	1. 
	"""
	to_return = None
	# First, let's validate the inputted data.
	_ = start_id_checker(set_piece_start_id)

	# Next,

	return to_return


def goal_checker(set_piece_start_id: int) -> list:
	"""
	Purpose
	-------
	The purpose of this function is to take the ID for the event that
	starts a set piece and analyze the next several plays to determine if
	the sequence that followed the set piece ended with the attacking
	team ultimately scoring a goal.

	Parameters
	----------
	set_piece_start_id : int
		This argument allows the user to specify the event ID for the
		event/play that started the set piece whose subsequent sequence
		of plays we are trying to determine.

	Returns
	-------
	to_return : list
		This function returns a list that contains two elements. The first
		is a Boolean that is True if the sequence ended with a goal being
		scored by the attacking team and False otherwise. The second is
		the event ID of the event that marks the end of the set piece
		sequence of interest if the first element is True and `-1` if the
		first element is False.

	References
	----------
	1. 
	"""
	to_return = None
	# First, let's validate the inputted data.
	_ = start_id_checker(set_piece_start_id)

	# Next,

	return to_return


def stop_in_play_checker(set_piece_start_id: int) -> list:
	"""
	Purpose
	-------
	The purpose of this function is to take the ID for the event that
	starts a set piece and analyze the next several plays to determine if
	the sequence that followed the set piece ended with play stopping for
	some reason. Such reasons could include a foul being committed, a 
	player on the attacking team being offsides, the ball ended up out of
	play, the half/game ended, etc...

	Parameters
	----------
	set_piece_start_id : int
		This argument allows the user to specify the event ID for the
		event/play that started the set piece whose subsequent sequence
		of plays we are trying to determine.

	Returns
	-------
	to_return : list
		This function returns a list that contains two elements. The first
		is a Boolean that is True if the sequence ended with play being
		stopped for some reason and False otherwise. The second is the
		event ID of the event that marks the end of the set piece
		sequence of interest if the first element is True and `-1` if the
		first element is False.

	References
	----------
	1. 
	"""
	to_return = None
	# First, let's validate the inputted data.
	_ = start_id_checker(set_piece_start_id)

	# Next,

	return to_return


def set_piece_sequence_generator(set_piece_start_id: int) -> :
	"""
	Purpose
	-------
	The purpose of this function is to

	Parameters
	----------
	set_piece_start_id : int
		This argument allows the user to specify the event ID for the
		event/play that started the set piece whose subsequent sequence
		of plays we are trying to determine.

	Returns
	-------
	to_return : list
		This function returns 

	References
	----------
	1. 
	"""
	to_return = None
	# First,

	return to_return