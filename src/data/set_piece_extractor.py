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
import swifter as swift
from shapely.geometry import Polygon, Point

# custom modules
from src.data import data_loader as dl
from src.data import common_tasks as ct

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
RAW_EVENTS_DF = dl.raw_event_data(league_name="all")


################################
### Define Modular Functions ###
################################
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
	_ = ct.start_id_checker(set_piece_start_id)
	_ = ct.start_id_checker(num_events)

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
	_ = ct.start_id_checker(set_piece_start_id)

	# Next obtain subsequent plays.
	sequence_df = subsequent_play_generator(
		set_piece_start_id=set_piece_start_id, num_events=20
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
	consec_passes_ids = []
	past_event_by_opp = [False, -1]

	for event in sequence_df.to_numpy().tolist()[1::]:
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
				interim_to_return = [True, consec_passes_ids[0]]
				break
			if opp_poss_cons_time >= opp_poss_time_threshold:
				# If the opposing team has had uninterrupted possession
				# for more than 30 seconds.
				interim_to_return = [True, consec_passes_ids[0]]
				break
			if any([start_x > 50, end_x > 50]):
				# If the (originally) opposing team has fought its way to
				# the (originally) attacking team's side of the field.
				try:
					interim_to_return = [True, consec_passes_ids[0]]
				except IndexError:
					interim_to_return = [True, event[-1]]
				break
			if {"id":1901} in event[2]:
				# If the event tracking has noted that there is a counter
				# attack going on.
				try:
					interim_to_return = [True, consec_passes_ids[0]]
				except IndexError:
					in

			# Update necessary values.
			past_event_by_opp = [True, event[9]]
			consec_passes_ids.append(event[-1])
		else:
			# If the attacking team still has possession.
			num_consecutive_opp_passes = 0
			opp_poss_cons_time = 0
			consec_passes_ids = []

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
	1. https://shapely.readthedocs.io/en/latest/manual.html#introduction
	"""
	to_return = None
	# First, let's validate the inputted data.
	_ = ct.start_id_checker(set_piece_start_id)

	# Next obtain subsequent plays.
	sequence_df = subsequent_play_generator(
		set_piece_start_id=set_piece_start_id, num_events=20
	)

	# Now let us determine if the set piece sequence ended with the attacking
	# team resetting their attack.
	beginning_row = sequence_df.iloc[0]
	attacking_team_id = beginning_row.teamId
	field_position_start = beginning_row.positions

	midfieldish_to_back_polygon = Polygon([
		[55, 0], [0, 0], [0, 100], [55, 100], [55, 0]
	])

	for event in sequence_df.to_numpy().tolist()[1::]:
		# Iterate over each event that we have obtained.
		if event[7] == attacking_team_id:
			# Only do an analysis of events if they were initiated by
			# the attacking team. This is because events by the other team
			# do not tell us anything about any resets that were made by
			# the attacking team.
			event_id = event[0]
			sub_event_id = event[-2]

			initiating_player_id = event[3]
			initiating_player_pos = ct.player_position_extractor(
				player_wyscout_id=initiating_player_id,
				notation_to_return="three"
			)

			event_field_position = event[4]

			# First, take a look at where the event occurred. If it
			# occurred near mid-field or in the attacking team's side of
			# the pitch, then that may be because of a reset that was
			# initiated by the attacking team.
			starting_point = Point(
				event_field_position[0].get("x"), 
				event_field_position[0].get("y")
			)
			ending_point = Point(
				event_field_position[1].get("x"), 
				event_field_position[1].get("y")
			)

			# After defining these variables, make the position checks.
			reset_pos = ["DEF", "GKP"]
			if initiating_player_pos in reset_pos and event_id != 10:
				# If the player initiating the event is a defender or
				# goal keeper and is not attempting a shot.
				to_return = [True, event[-1]] # Give spot check for this test.

			is_back_field = [
				ending_point.within(midfieldish_to_back_polygon),
				starting_point.within(midfieldish_to_back_polygon)
			]
			if any(is_back_field):
				# If this event is one where it starts or ends in the
				# attacking team's own side of the pitch.
				to_return = [True, event[-1]]

			consec_backward_pass = 0
			consec_backward_threshold = 3
			consec_backward_passes_ids = []
			attack_going_backward = starting_point.x > ending_point.x
				# Recall how the field position goes up as the attacking
				# team gets closer to the opponent's goal.
			if attack_going_backward:
				# If this specific event is associated with a backwards
				# pass by the team that initiated the set piece.
				consec_backward_pass += 1
				consec_backward_passes_ids.append(event[-1])
			else:
				# If the event is not a backwards pass.
				consec_backward_pass = 0
				consec_backward_passes_ids = []
			if consec_backward_pass >= consec_backward_threshold:
				# If you have seen multiple backward passes in a road.
				to_return = [True, consec_backward_passes_ids[0]]

	to_return = [False, -1] if isinstance(interim_to_return, type(None)) \
	                        else interim_to_return

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
	1. https://numpy.org/doc/stable/reference/generated/numpy.any.html
	"""
	to_return = [False, -1]
	# First, let's validate the inputted data.
	_ = ct.start_id_checker(set_piece_start_id)

	# Next obtain subsequent plays.
	sequence_df = subsequent_play_generator(
		set_piece_start_id=set_piece_start_id, num_events=20
	)

	# Now let us determine if the set piece was finished by the goalie
	# saving a shot attempt.
	save_attempt_checker_series = sequence_df.eventId == 9
	if np.any(save_attempt_checker_series):
		# If there was a save attempt made in this sequence of plays.
		row_indicies_of_save_attempts = np.argwhere(
			save_attempt_checker_series).flatten().tolist()

		for row_index in row_indicies_of_save_attempts:
			# Iterate over each instance of a save (shot) attempt. For
			# each, check to see if the shot was accurate (meaning if the
			# goalie does not save it, a goal will be scored) and if the
			# event that immediately followed it was a pass initiated by
			# the goalie. Both of these conditions passing means that the
			# shot was in fact saved by the goalie. We opt for this series
			# of checks because the event tracking data does not make
			# note of goalie saves when they occur.
			event_row = sequence_df.iloc[row_index]
			if {"id":101} in event_row.tags:
				# If a goal was scored (don't do anything since that is
				# checked by another function). We are checking for this
				# first because it will free us from having to do the two
				# goalie save checks for the instances in which a goal
				# was scored meaning that right off the bat, we know that
				# the goalie did not save the shot.
				pass

			next_event_row = sequence_df.iloc[row_index + 1]
			next_initiating_player_pos = ct.player_position_extractor(
				player_wyscout_id=next_event_row.playerId,
				notation_to_return="two"
			)

			was_save_checker = [next_initiating_player_pos=="GK",
			                    {"id":1801} in event_row.tags]
			elif was_save_checker:
				# If all of our checks for a successful save attempt
				# pass.
				to_return = [True, event_row.id]

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
	1. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
	"""
	to_return = [False, -1]
	# First, let's validate the inputted data.
	_ = ct.start_id_checker(set_piece_start_id)

	# Next obtain subsequent plays.
	sequence_df = subsequent_play_generator(
		set_piece_start_id=set_piece_start_id, num_events=20
	)

	# Now let us determine if the set piece sequence of interest was ended
	# by a goal being scored.
	goal_checker_series = sequence_df.swift.apply(
		func=lambda x: {"id":101} in x.tags, 
		axis="columns"
	)
	if np.any(goal_checker_series):
		# If there was a save attempt made in this sequence of plays.
		row_index_of_goal = np.argwhere(
			goal_checker_series).flatten()[0]
		to_return = [True, 
		             sequence_df.iloc[row_index_of_goal].id]

	return to_return


def foul_checker(set_piece_start_id: int) -> list:
	"""
	Purpose
	-------
	The purpose of this function is to take the ID for the event that
	starts a set piece and analyze the next several plays to determine if
	the sequence that followed the set piece ended with play stopping
	because of a foul being committed.

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
		stopped because of a foul and False otherwise. The second is the
		event ID of the event that marks the end of the set piece
		sequence of interest if the first element is True and `-1` if the
		first element is False.

	References
	----------
	1. 
	"""
	to_return = [False, -1]
	# First, let's validate the inputted data.
	_ = ct.start_id_checker(set_piece_start_id)

	# Next obtain subsequent plays.
	sequence_df = subsequent_play_generator(
		set_piece_start_id=set_piece_start_id, num_events=20
	)

	# Now let us determine if the set piece sequence of interest was ended
	# by a foul being committed.
	foul_checker_series = sequence_df.eventId == 2
	if np.any(foul_checker_series):
		# If there was a foul committed in this sequence of plays.
		row_index_of_foul = np.argwhere(
			foul_checker_series).flatten()[0]
		to_return = [True, 
		             sequence_df.iloc[row_index_of_foul].id]

	return to_return


def offsides_checker(set_piece_start_id: int) -> list:
	"""
	Purpose
	-------
	The purpose of this function is to take the ID for the event that
	starts a set piece and analyze the next several plays to determine if
	the sequence that followed the set piece ended with play stopping 
	because of a player on the attacking team being offsides.

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
		stopped because of an offside call and False otherwise. The second
		is the event ID of the event that marks the end of the set piece
		sequence of interest if the first element is True and `-1` if the
		first element is False.

	References
	----------
	1. 
	"""
	to_return = None
	# First, let's validate the inputted data.
	_ = ct.start_id_checker(set_piece_start_id)

	# Next obtain subsequent plays.
	sequence_df = subsequent_play_generator(
		set_piece_start_id=set_piece_start_id, num_events=20
	)

	# Now let us determine if

	return to_return


def out_of_play_checker(set_piece_start_id: int) -> list:
	"""
	Purpose
	-------
	The purpose of this function is to take the ID for the event that
	starts a set piece and analyze the next several plays to determine if
	the sequence that followed the set piece ended with play stopping 
	because of the ball ending up out of play.

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
		stopped because of the ball ending up out of play and False
		otherwise. The second is the event ID of the event that marks the
		end of the set piece sequence of interest if the first element is
		True and `-1` if the first element is False.

	References
	----------
	1. 
	"""
	to_return = None
	# First, let's validate the inputted data.
	_ = ct.start_id_checker(set_piece_start_id)

	# Next obtain subsequent plays.
	sequence_df = subsequent_play_generator(
		set_piece_start_id=set_piece_start_id, num_events=20
	)

	# Now let us determine if

	return to_return


def end_of_regulation_checker(set_piece_start_id: int) -> list:
	"""
	Purpose
	-------
	The purpose of this function is to take the ID for the event that
	starts a set piece and analyze the next several plays to determine if
	the sequence that followed the set piece ended with play stopping
	because of the half/game ending.

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
		stopped because of the half/game ending. and False otherwise. The
		second is the event ID of the event that marks the end of the set
		piece sequence of interest if the first element is True and `-1`
		if the first element is False.

	References
	----------
	1. 
	"""
	to_return = None
	# First, let's validate the inputted data.
	_ = ct.start_id_checker(set_piece_start_id)

	# Next obtain subsequent plays.
	sequence_df = subsequent_play_generator(
		set_piece_start_id=set_piece_start_id, num_events=20
	)

	# Now let us determine if

	return to_return


def set_piece_sequence_generator(
		set_piece_start_id: int) -> pd.DataFrame:
	"""
	Purpose
	-------
	The purpose of this function is to run all of the tests written above
	to determine how a particular set piece sequence ended and thus be
	able to collect the full set of events/plays that make up that set
	piece sequence of interest.

	Parameters
	----------
	set_piece_start_id : int
		This argument allows the user to specify the event ID for the
		event/play that started the set piece whose subsequent sequence
		of plays we are trying to determine.

	Returns
	-------
	to_return : Pandas DataFrame
		This function returns a DataFrame that contains all of the events
		that make up the set piece sequence that starts with the event
		specified by the argument `set_piece_start_id`.

	References
	----------
	1. 
	"""
	to_return = None
	# First,

	return to_return