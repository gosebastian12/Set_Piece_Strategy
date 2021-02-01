#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Jan 19 09:40:01 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: Collection of functions that are used for visualizations
created that involve some sort of overlay on a soccer field which helps
put the displayed data in its proper soccer context.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import pandas as pd
import numpy as np

# visualization packages
import matplotlib.pyplot as plt
import seaborn as sns

# custom modules
from src.visualizations import cluster_bar_chart_prep as cbcp
from src.visualizations import contour_position_prep as cpp
from src.test import input_parameter_validation as ipv

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)

RANDOM_FIG, RANDOM_AX = plt.subplots()
RANDOM_FIG.clear()
FIG_TYPE = type(RANDOM_FIG)
AXES_TYPE = type(RANDOM_AX)


################################
### Define Modular Functions ###
################################
def draw_pitch(
        pitch_color="w", lines_color="k",
        pitch_orientation="h") -> (FIG_TYPE, AXES_TYPE):
    """
    Purpose
    -------
    NOTE THAT THE CODE FOR THIS FUNCTION IS ADAPTED FROM THE REPLICATION
    GIVEN FOR THE PLOTS DISPLAYED IN THE PAPER DETAILING THE PUBLICLY
    AVAILABLE DATASET USED BY THIS PROJECT. SEE 1. IN THE REFERENCES
    SECTION FOR A LINK TO WHERE THAT CODE CAN BE DOWNLOADED.

    The purpose of this function is to generate a plot using Matplotlib
    that displays a soccer field. The function then returns the plot's
    `figure` and `axis` object in the event that the user would like to
    use them to create more complicated plots with more data.

    Parameters
    ----------
    pitch_color : str
        This parameter allows the user to specify the color that they would
        like the pitch to be. The accepted values for this parameter are
        identical to the list of accepted color specifications in Matplotlib.
        See 2. in the Reference section of this function's docstring.

        Note that this parameter will default to the string "w" which means
        that the color of the pitch will be white.
    lines_color : str
        his parameter allows the user to specify the color that they would
        like the lines on the pitch to be. The accepted values for this
        parameter are identical to the list of accepted color
        specifications in Matplotlib. See 2. in the Reference section of
        this function's docstring.

        Note that this parameter will default to the string "k" which means
        that the color of the lines on the pitch will be black.
    pitch_orientation : str
        This parameter allows the user to specify the orientation of the
        resulting pitch-figure. The accepted values include:
            1. Some variation of the string "horizontal". This can include
               an all lower-case version, an all upper-case version, a
               random casing, or even just the letter h in a string.
            2. Some variation of the string "vertical". This can include
               an all lower-case version, an all upper-case version, a
               random casing, or even just the letter v in a string.

        Note that this parameter will default to the string "h" which
        corresponds to a horizontal display of the pitch.

    Returns
    -------
    to_return : (Matplotlib figure object, Matplotlib axis object)
        This function returns a tuple of Matplotlib figure and axis objects
        that make up the pitch-plot that get displayed by this function.

    Raises
    ------
    ValueError
        This error is raised when the user, for at least one parameter,
        passes in an object whose type is not among the accepted types
        for that parameter.

    References
    ----------
    1. https://figshare.com/articles/software/Plots_replication_code_of_Nature_Scientific_Data_paper/11473365?backTo=/collections/Soccer_match_event_dataset/4415000
    2. https://matplotlib.org/3.1.0/gallery/color/named_colors.html
    """
    to_return = None
    # First, validate the input data.
    ipv.parameter_type_validator(expected_type=str,
                                 parameter_var=pitch_color)
    ipv.parameter_type_validator(expected_type=str,
                                 parameter_var=lines_color)
    ipv.parameter_type_validator(expected_type=str,
                                 parameter_var=pitch_orientation)

    # Next,
    if pitch_orientation.lower().startswith("h"):
        pitch_fig, pitch_ax = plt.subplots(figsize=(10.4, 6.8))
        plt.xlim(-1, 105)
        plt.ylim(-1, 69)
        pitch_ax.axis('off')  # this hides the x and y ticks

        # side and goal lines_colors #
        ly1 = [0, 0, 68, 68, 0]
        lx1 = [0, 104, 104, 0, 0]

        plt.plot(lx1, ly1, color=lines_color, zorder=5)

        # boxes, 6 yard box and goals
        #outer boxes#
        ly2 = [13.84, 13.84, 54.16, 54.16]
        lx2 = [104, 87.5, 87.5, 104]
        plt.plot(lx2, ly2, color=lines_color, zorder=5)

        ly3 = [13.84, 13.84, 54.16, 54.16]
        lx3 = [0, 16.5, 16.5, 0]
        plt.plot(lx3, ly3, color=lines_color, zorder=5)

        #goals#
        ly4 = [30.34, 30.34, 37.66, 37.66]
        lx4 = [104, 104.2, 104.2, 104]
        plt.plot(lx4, ly4, color=lines_color, zorder=5)

        ly5 = [30.34, 30.34, 37.66, 37.66]
        lx5 = [0, -0.2, -0.2, 0]
        plt.plot(lx5, ly5, color=lines_color, zorder=5)

        #6 yard boxes#
        ly6 = [24.84, 24.84, 43.16, 43.16]
        lx6 = [104, 99.5, 99.5, 104]
        plt.plot(lx6, ly6, color=lines_color, zorder=5)

        ly7 = [24.84, 24.84, 43.16, 43.16]
        lx7 = [0, 4.5, 4.5, 0]
        plt.plot(lx7, ly7, color=lines_color, zorder=5)

        # Halfway lines_color, penalty spots, and kickoff spot
        ly8 = [0, 68]
        lx8 = [52, 52]
        plt.plot(lx8, ly8, color=lines_color, zorder=5)

        plt.scatter(93, 34, color=lines_color, zorder=5)
        plt.scatter(11, 34, color=lines_color, zorder=5)
        plt.scatter(52, 34, color=lines_color, zorder=5)

        circle1 = plt.Circle((93.5, 34),
                             9.15,
                             ls='solid',
                             lw=1.5,
                             color=lines_color,
                             fill=False,
                             zorder=1,
                             alpha=1)
        circle2 = plt.Circle((10.5, 34),
                             9.15,
                             ls='solid',
                             lw=1.5,
                             color=lines_color,
                             fill=False,
                             zorder=1,
                             alpha=1)
        circle3 = plt.Circle((52, 34),
                             9.15,
                             ls='solid',
                             lw=1.5,
                             color=lines_color,
                             fill=False,
                             zorder=2,
                             alpha=1)

        ## Rectangles in boxes
        rec1 = plt.Rectangle((87.5, 20),
                             16, 30,
                             ls='-',
                             color=pitch_color,
                             zorder=1,
                             alpha=1)
        rec2 = plt.Rectangle((0, 20),
                             16.5,
                             30, ls='-',
                             color=pitch_color,
                             zorder=1,
                             alpha=1)

        # Pitch rectangle
        rec3 = plt.Rectangle((-1, -1),
                             106, 70,
                             ls='-',
                             color=pitch_color,
                             zorder=1,
                             alpha=1)

        pitch_ax.add_artist(rec3)
        pitch_ax.add_artist(circle1)
        pitch_ax.add_artist(circle2)
        pitch_ax.add_artist(rec1)
        pitch_ax.add_artist(rec2)
        pitch_ax.add_artist(circle3)

    else:
        pitch_fig, pitch_ax = plt.subplots(figsize=(6.8, 10.4))

        plt.ylim(-1, 105)
        plt.xlim(-1, 69)

        pitch_ax.axis('off')  # this hides the x and y ticks

        # side and goal lines_colors #
        lx1 = [0, 0, 68, 68, 0]
        ly1 = [0, 104, 104, 0, 0]

        plt.plot(lx1, ly1, color=lines_color, zorder=5)

        # boxes, 6 yard box and goals

        #outer boxes#
        lx2 = [13.84, 13.84, 54.16, 54.16]
        ly2 = [104, 87.5, 87.5, 104]
        plt.plot(lx2, ly2, color=lines_color, zorder=5)

        lx3 = [13.84, 13.84, 54.16, 54.16]
        ly3 = [0, 16.5, 16.5, 0]
        plt.plot(lx3, ly3, color=lines_color, zorder=5)

        #goals#
        lx4 = [30.34, 30.34, 37.66, 37.66]
        ly4 = [104, 104.2, 104.2, 104]
        plt.plot(lx4, ly4, color=lines_color, zorder=5)

        lx5 = [30.34, 30.34, 37.66, 37.66]
        ly5 = [0, -0.2, -0.2, 0]
        plt.plot(lx5, ly5, color=lines_color, zorder=5)

        #6 yard boxes#
        lx6 = [24.84, 24.84, 43.16, 43.16]
        ly6 = [104, 99.5, 99.5, 104]
        plt.plot(lx6, ly6, color=lines_color, zorder=5)

        lx7 = [24.84, 24.84, 43.16, 43.16]
        ly7 = [0, 4.5, 4.5, 0]
        plt.plot(lx7, ly7, color=lines_color, zorder=5)

        # Halfway lines_color, penalty spots, and kickoff spot
        lx8 = [0, 68]
        ly8 = [52, 52]
        plt.plot(lx8, ly8, color=lines_color, zorder=5)

        plt.scatter(34, 93, color=lines_color, zorder=5)
        plt.scatter(34, 11, color=lines_color, zorder=5)
        plt.scatter(34, 52, color=lines_color, zorder=5)

        circle1 = plt.Circle((34, 93.5),
                             9.15,
                             ls='solid',
                             lw=1.5,
                             color=lines_color,
                             fill=False,
                             zorder=1,
                             alpha=1)
        circle2 = plt.Circle((34, 10.5),
                             9.15,
                             ls='solid',
                             lw=1.5,
                             color=lines_color,
                             fill=False,
                             zorder=1,
                             alpha=1)
        circle3 = plt.Circle((34, 52),
                             9.15,
                             ls='solid',
                             lw=1.5,
                             color=lines_color,
                             fill=False,
                             zorder=2,
                             alpha=1)

        ## Rectangles in boxes
        rec1 = plt.Rectangle((20, 87.5), 30, 16.5, ls='-',
                             color=pitch_color, zorder=1, alpha=1)
        rec2 = plt.Rectangle((20, 0), 30, 16.5, ls='-',
                             color=pitch_color, zorder=1, alpha=1)

        # Pitch rectangle
        rec3 = plt.Rectangle((-1, -1), 70, 106, ls='-',
                             color=pitch_color, zorder=1, alpha=1)

        pitch_ax.add_artist(rec3)
        pitch_ax.add_artist(circle1)
        pitch_ax.add_artist(circle2)
        pitch_ax.add_artist(rec1)
        pitch_ax.add_artist(rec2)
        pitch_ax.add_artist(circle3)

    # Finally, validate and return the result
    ipv.parameter_type_validator(expected_type=FIG_TYPE,
                                 parameter_var=pitch_fig)
    ipv.parameter_type_validator(expected_type=AXES_TYPE,
                                 parameter_var=pitch_ax)

    to_return = (pitch_fig, pitch_ax)
    return to_return


def pitch_positions_cluster_generator(
        feat_pred_df: pd.DataFrame, cluster_id: int,
        pitch_plot_objs=None, beginning_points=True, 
        save_plot=False, **kwargs) -> tuple:
    """
    Purpose
    -------
    The purpose of this function is to take a cluster id and a "canvas" of
    a Matplotlib soccer pitch plot and generate a contour map that
    graphically displays

    Parameters
    ----------
    feat_pred_df : pd.DataFrame
        Short for feature-prediction dataframe, this argument allows the
        user to specify the entire collection of events and set piece
        sequences that we have data for.
    cluster_id : int
        This argument allows the user to specify the ID of the cluster
        that we would like to use to filter out the events passed to the
        `feat_pred_df` argument.
    pitch_plots_obj : tuple or Python None object
        This argument allows the user to specify the Matplotlib `fig` and
        `axis` objects that currently just display a soccer pitch to use
        a background for the position contour plot generated by this function.
    beginning_points : bool
        This argument allows the user to specify whether or not they want
        a contour plot of the beginning points for all of the events of
        interest or a contour plot of all of their ending points.
    save_plot : Boolean
        This argument allows the user to specify whether or not the function
        will save the plot that it generates.

        This parameter defaults to `False`.
    **kwargs : dict
        This function allows for keyword arguments. The current version
        only acts on the `file_name` keyword argument; this specific
        keyword argument allows the user to specify the name of the file
        that they would like to write the generated subplot to.

    Returns
    -------
    to_return : Python tuple
        This function returns a tuple that contains the Matplotlib `fig`
        and `axis` objects that display the contour plot overlaid on a
        soccer pitch that is generated by this function.

    Raises
    ------
    ValueError
        This error is raised when the user, for at least one parameter,
        passes in an object whose type is not among the accepted types
        for that parameter.

    References
    ----------
    1. https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.contour.html
    2. https://numpy.org/doc/stable/reference/generated/numpy.meshgrid.html
    3. https://seaborn.pydata.org/generated/seaborn.kdeplot.html
    """
    to_return = None
    # First, validate the input data.
    ipv.parameter_type_validator(expected_type=pd.DataFrame,
                                 parameter_var=feat_pred_df)
    ipv.parameter_type_validator(expected_type=int,
                                 parameter_var=cluster_id)
    ipv.parameter_type_validator(expected_type=(tuple, type(None)),
                                 parameter_var=pitch_plot_objs)
    ipv.parameter_type_validator(expected_type=bool,
                                 parameter_var=beginning_points)

    # Next, define any variable that we will need later on in the function
    if isinstance(pitch_plot_objs, type(None)):
        # If the user is using the default value for this parameter.
        pitch_fig, pitch_ax = draw_pitch()
    else:
        pitch_fig, pitch_ax = pitch_plot_objs
        ipv.parameter_type_validator(expected_type=RANDOM_FIG,
                                     parameter_var=pitch_fig)
        ipv.parameter_type_validator(expected_type=RANDOM_AX,
                                     parameter_var=pitch_ax)

    # Now, let's obtain the data that we will need to generate the contour
    # plots.
    cluster_events_df = cbcp.cluster_events_extractor(
        feat_pred_df=feat_pred_df,
        cluster_id=cluster_id,
        col1="id",
        col2="positions",
        col3="matchId",
        col4="teamId"
    )

    cluster_positions_df = cpp.cluster_positions_extractor(cluster_events_df)

    field_bin_counts, x_bins, y_bins = cpp.cluster_positions_binning(
        cluster_positions_df=cluster_positions_df,
        beginning_points=beginning_points
    )

    mesh_x, mesh_y = np.meshgrid(x_bins, y_bins)

    # We are now finally ready to generate and display the contour plot.
    num_pts_to_sample = 250_000
    if cluster_positions_df.shape[0] > num_pts_to_sample:
        # If the data has so much data that it will take forever to
        # generate the contour plot of interest.
        sampled_pos_df = cluster_positions_df.sample(num_pts_to_sample)
    else:
        sampled_pos_df = cluster_positions_df
        
    sns.kdeplot(sampled_pos_df["starting_x"].to_numpy(),
                sampled_pos_df["starting_y"].to_numpy(), 
                fill=True,
                cmap="Greens",
                cbar=False,
                common_norm=True,
                clip=[[0, 104], [0, 68]])
    
    pitch_ax.set_title(
        label="2D Spatial Distribution of Events in Cluster {}".format(cluster_id),
        fontdict={"fontsize": 22},
        loc="center",
        pad=10
    )
    pitch_fig.set_figheight(13)
    pitch_fig.set_figwidth(20)

    pitch_fig.show()

    if save_plot:
        # If the user would like to save the resulting figure.
        plot_dir = os.path.join(
            SCRIPT_DIR, 
            "../../visualizations/clusters_investigation/kmeans"
        )

        file_name = kwargs.get("file_name", None)
        try:
            assert not isinstance(file_name, type(None))
        except BaseException:
            err_msg = "The user has specified that they would like the\
            subplot generated by this function to be saved. When this is\
            done, the user must pass in the name of the file that the subplot\
            image will be written to. This is has not been done in this\
            function call. Please do so."

            print(err_msg)
            raise ValueError

        if "." not in file_name:
            file_name += ".png"

        pitch_fig.savefig("{}/{}".format(plot_dir, file_name), 
                          bbox_inches="tight")

    # Finally, validate and return the result.
    to_return = (pitch_fig, pitch_ax)

    return to_return
