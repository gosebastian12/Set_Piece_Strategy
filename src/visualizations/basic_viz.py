#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Dec 29 01:40:10 CST 2020

@author: Sebastian E. Gonzalez

Script Purpose: Collection of functions that are used for visualizations
created and show in the Jupyter Notebooks contained in this project.
"""
###################################
### Necessary Import Statements ###
###################################
# file access
import os

# data manipulation
import numpy as np
import pandas as pd

# visualization packages
import matplotlib.pyplot as plt
import plotly.express as px

# ML-related packages
from sklearn.manifold import TSNE

# custom modules
from src.visualizations import cluster_bar_chart_prep as cbcp

# define variables that will be used throughout script
SCRIPT_DIR = os.path.dirname(__file__)
RANDOM_FIG, RANDOM_AX = plt.subplots()
RANDOM_FIG.clear()


################################
### Define Modular Functions ###
################################
def create_graph(figure_size=None, nrow=1, ncol=1) -> tuple:
    """
    Purpose
    -------
    The purpose of this function is to

    Parameters
    ----------
    figure_size : None or Tuple
        This parameter allows the user to specify the size of the figure
        that gets instantiate with the function by using the `subplots`
        function (see 2. in the References section).

        The default value for this parameter is `None` in which case the
        size of the instantiated `figure` object is `(21,10)`.
    nrow : int
        This parameter allows the user to specify how many rows of figures
        with

        The default value for this parameter is `1`.
    ncol : int
        This parameter allows the user to specify

        The default value for this parameter is `1`.

    Returns
    -------
    to_return : tuple
        This function returns a tuple that contains a Matplotlib `figure()`
        object and either an `axes` object (if the `nrow` and `ncol`
        parameters are both `1` or an array of `axes` objects.

    Raises
    ------
    ValueError
        This error is raised when

    References
    ----------
    1. https://matplotlib.org/3.3.3/api/_as_gen/matplotlib.axes.Axes.tick_params.html
    2. https://matplotlib.org/3.3.3/api/_as_gen/matplotlib.pyplot.subplots.html
    3. https://stackoverflow.com/questions/6541123/improve-subplot-size-spacing-with-many-subplots-in-matplotlib
    """
    to_return = None
    # First, validate the input data
    try:
        assert any([isinstance(figure_size, type(None)),
                    isinstance(figure_size, tuple)])
    except AssertionError:
        err_msg = "The type received for the `figure_size` argument is:\
		`{}`. The only accepted data types for this argument are either\
		`None` or `tuple`.".format(type(figure_size))

        print(err_msg)
        raise ValueError

    try:
        assert all([isinstance(nrow, int), isinstance(ncol, int)])
    except AssertionError:
        err_msg = "The types received for the `nrow` and `ncol` arguments\
		are `{}` and`{}` respectively. The only accepted data type for these\
		arguments is `int`.".format(type(nrow), type(ncol))

        print(err_msg)
        raise ValueError

    # Next, instantiate the figure and axes objects.
    figsize = (21, 10) if isinstance(figure_size, type(None)) \
        else figure_size
    fig, axes = plt.subplots(figsize=figsize, nrows=nrow, ncols=ncol)

    # Pretty up the graph's appearance.
    #fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    fig.subplots_adjust(hspace=0.275, wspace=0.075)

    if isinstance(axes, type(RANDOM_AX)):
        axes.minorticks_on()
        axes.tick_params(axis="both",
                         which="major",
                         direction="in",
                         top=True,
                         right=True,
                         length=7)
        axes.tick_params(axis="both",
                         which="minor",
                         direction="in",
                         top=True,
                         right=True,
                         length=3)
    else:
        if all([nrow > 1, ncol > 1]):
            assert axes.shape == (nrow, ncol)
            for i in range(axes.shape[0]):
                for j in range(axes.shape[1]):
                    axes[i, j].minorticks_on()
                    axes[i, j].tick_params(axis="both",
                                           which="major",
                                           direction="in",
                                           top=True,
                                           right=True,
                                           length=7)
                    axes[i, j].tick_params(axis="both",
                                           which="minor",
                                           direction="in",
                                           top=True,
                                           right=True,
                                           length=3)
        else:
            for i in range(axes.size):
                axes[i].minorticks_on()
                axes[i].tick_params(axis="both",
                                    which="major",
                                    direction="in",
                                    top=True,
                                    right=True,
                                    length=7)
                axes[i].tick_params(axis="both",
                                    which="minor",
                                    direction="in",
                                    top=True,
                                    right=True,
                                    length=3)

    # Return result
    to_return = (fig, axes)

    return to_return


def add_scatter_to_ax_obj(
        ax_obj: type(RANDOM_AX), x_data: np.array, y_data: np.array,
        color_arr: np.array, x_lab: str, y_lab: str,
        title_lab: str) -> type(RANDOM_AX):
    """
    Purpose
    -------
    The purpose of this function is to take a Matplotlib `axis` object
    and create a scatter plot that is used to visually evaluate the
    effectiveness of the cluster assignments you received from your model.
    This scatter plot not only contains the data, but also labels for each
    axis and the graph itself (assuming each parameter in this function
    received a correct value).

    Parameters
    ----------
    ax_obj : Matplotlib `axis` object.
        This parameter allows the user to specify the Matplotlib `axis`
        object that they have instantiated beforehand and thus would like
        for this function to use to create their scatter plot.
    x_data : Numpy Array
        This parameter allows the user to specify the data that they would
        like the be displayed along the x-axis.
    y_data : Numpy Array
        This parameter allows the user to specify the data that they would
        like the be displayed along the y-axis.
    color_arr : Numpy Array
        This parameter allows the user to specify the class labels for each
        data instance in `x_data` and `y_data` that will be used to specify
        the color of each data point in the scatter plot.
    x_lab : str
        This parameter allows the user to specify the label they would like
        to be used for the x-axis.
    y_lab : str
        This parameter allows the user to specify the label they would like
        to be used for the x-axis.
    title_lab : str
        This parameter allows the user to specify the label they would like
        to be used for the entire graph.

    Returns
    -------
    to_return :
        This function returns the same axis object it received in the
        `ax_obj` argument, but with updated attribute values as a result
        of making the scatter plot with all of its labels.

    Raises
    ------
    AssertionError
        This error is raised when the data inputted to the function's
        arguments is not as expected. The various possibilities include:
            1. The object passed to the `ax_obj` argument is not a
               Matplotlib `axis` object.
            2. At least one of the objects passed to the arguments `x_data`,
               `y_data`, and `color_arr` is not a Numpy Array.
            3. The arrays passed to the `x_data` and `y_data` arguments
               are not the same size.
            4. The arrays passed to the `x_data` and `color_arr` arguments
               are not the same size.
            5. At least one of the objects passed to the arguments `x_lab`.
               `y_lab`, and `title_lab` is not a string.

    References
    ----------
    1. https://matplotlib.org/3.3.3/gallery/lines_bars_and_markers/scatter_with_legend.html#sphx-glr-gallery-lines-bars-and-markers-scatter-with-legend-py
    2. https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.legend.html
    3. https://matplotlib.org/3.3.3/api/_as_gen/matplotlib.pyplot.scatter.html
    """
    to_return = None
    # First, validate the input data
    assert isinstance(ax_obj, type(RANDOM_AX))
    assert all(
        [isinstance(x_data, np.ndarray),
         isinstance(y_data, np.ndarray),
         isinstance(color_arr, np.ndarray)]
    )
    assert x_data.size == y_data.size
    assert x_data.size == color_arr.size
    assert all(
        [isinstance(x_lab, str),
         isinstance(y_lab, str),
         isinstance(title_lab, str)]
    )

    # Next, plot the given data
    scatter_obj = ax_obj.scatter(
        x_data.flatten(),
        y_data.flatten(),
        c=color_arr)

    # Now, create a legend.
    ax_obj.legend(*scatter_obj.legend_elements(),
                  loc="best",
                  title="Predicted Class",
                  title_fontsize=15,
                  fontsize="x-large",
                  frameon=False,
                  ncol=2)

    # Now add the specified labels.
    ax_obj.set_title(label=title_lab, size=22, pad=10)
    ax_obj.set_ylabel(ylabel=y_lab, size=17, labelpad=3)
    ax_obj.set_xlabel(xlabel=x_lab, size=17, labelpad=3)

    # Return the updated axes
    to_return = ax_obj

    return to_return


def cluster_subplot_generator(
        feature_data: np.array, predicted_labels: np.array,
        plot_objs=None, save_plot=False, **kwargs):
    """
    Purpose
    -------
    The purpose of this function is to

    Parameters
    ----------
    feature_data : Numpy Array
        This argument allows the user to specify
    predicted_labels: Numpy Array
        This argument allows the user to specify
    plot_objs : None or tuple
        This argument allows the user to specify

        This parameter defaults to `None`.
    save_plot : Boolean
        This argument allows the user to specify

        This parameter defaults to `False`.
    **kwargs : dict
        This function allows for keyword arguments. The current version
        only acts on the `file_name` keyword argument; this specific
        keyword argument allows the user to specify the name of the file
        that they would like to write the generated subplot to.

    Returns
    -------
    to_return :
        This function

    Raises
    ------
    ValueError
        This error is raised when

    References
    ----------
    1. https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html
    2. https://numpy.org/doc/stable/reference/random/generated/numpy.random.choice.html
    3. https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.savefig.html
    4. https://stackoverflow.com/questions/9622163/save-plot-to-image-file-instead-of-displaying-it-using-matplotlib
    """
    to_return = None

    # First, validate the input data.
    try:
        assert isinstance(plot_objs, tuple)
        assert len(plot_objs) == 2
        fig, axes = plot_objs
    except AssertionError:
        err_msg = "The accepted type for the `plot_objs` argument is `tuple`\
		which must be of length 2. Received type `{}`.".format(plot_objs)

        if isinstance(plot_objs, type(None)):
            # If the `plot_objs` is set to its default value.
            fig, axes = create_graph(figure_size=(30, 23), nrow=4, ncol=2)
        else:
            print(err_msg)
            raise ValueError

    try:
        assert feature_data.shape[1] == 10
        assert axes.size == 8
    except AssertionError:
        raise ValueError

    try:
        assert feature_data.shape[0] == predicted_labels.size
    except AssertionError:
        raise ValueError

    # Next, begin creating the subplots with the feature data.
    add_scatter_to_ax_obj(
        ax_obj=axes[0, 0],
        x_data=feature_data[:, 0],
        y_data=feature_data[:, 1],
        color_arr=predicted_labels,
        x_lab="Time in Match",
        y_lab="Score Differential",
        title_lab="Score Differential v. Time in Match"
    )   # score diff. v. time
    add_scatter_to_ax_obj(
        ax_obj=axes[0, 1],
        x_data=feature_data[:, 0],
        y_data=feature_data[:, 6],
        color_arr=predicted_labels,
        x_lab="Time in Match",
        y_lab=r"$\Delta$ Position Dist.",
        title_lab=r"$\Delta$ Position Dist. v. Time in Match"
    )   # pos. delta v. time

    add_scatter_to_ax_obj(
        ax_obj=axes[1, 0],
        x_data=feature_data[:, 0],
        y_data=feature_data[:, 7],
        color_arr=predicted_labels,
        x_lab="Time in Match",
        y_lab=r"$\Delta$ To Goal Dist.",
        title_lab=r"$\Delta$ To Goal Dist. v. Time in Match"
    )   # to goal delta v. time
    add_scatter_to_ax_obj(
        ax_obj=axes[1, 1],
        x_data=feature_data[:, 1],
        y_data=feature_data[:, 6],
        color_arr=predicted_labels,
        x_lab="Score Differential",
        y_lab=r"$\Delta$ Position Dist.",
        title_lab=r"$\Delta$ Position Dist. v. Score Differential"
    )   # pos. delta v. score diff.

    add_scatter_to_ax_obj(
        ax_obj=axes[2, 0],
        x_data=feature_data[:, 1],
        y_data=feature_data[:, 7],
        color_arr=predicted_labels,
        x_lab="Score Differential",
        y_lab=r"$\Delta$ To Goal Dist.",
        title_lab=r"$\Delta$ To Goal Dist. v. Score Differential"
    )  # to goal delta v. score diff.
    add_scatter_to_ax_obj(
        ax_obj=axes[2, 1],
        x_data=feature_data[:, 7],
        y_data=feature_data[:, 6],
        color_arr=predicted_labels,
        x_lab=r"$\Delta$ To Goal Dist.",
        y_lab=r"$\Delta$ Position Dist.",
        title_lab=r"$\Delta$ Position Dist. v. $\Delta$ To Goal Dist."
    )  # pos. delta v. to goal delta

    add_scatter_to_ax_obj(
        ax_obj=axes[3, 0],
        x_data=feature_data[:, 8],
        y_data=feature_data[:, 9],
        color_arr=predicted_labels,
        x_lab=r"No. Attacking Events",
        y_lab=r"Max-Avg. $\Delta$ Dists.",
        title_lab=r"Max-Avg. $\Delta$ Dists. v. No. Attacking Events"
    )  # max-avg. delta positions v. num of attacking events

    # Now we want to create the TSNE graph.
    tsne_transformer = TSNE(n_components=2, random_state=1169, n_jobs=-1)
    if feature_data.shape[0] > 75000:
        wout_replace_indicies = np.random.choice(
            a=np.arange(0, feature_data.shape[0]), size=75000, replace=False
        )
        feat_data_to_transform = feature_data[wout_replace_indicies]
        wout_predicted_labs = predicted_labels[wout_replace_indicies]
    else:
        feat_data_to_transform = feature_data
        wout_predicted_labs = predicted_labels
    features_embedded = tsne_transformer.fit_transform(feat_data_to_transform)

    assert features_embedded.shape[1] == 2
    assert features_embedded.shape[0] == feat_data_to_transform.shape[0]
    add_scatter_to_ax_obj(
        ax_obj=axes[3, 1],
        x_data=features_embedded[:, 0],
        y_data=features_embedded[:, 1],
        color_arr=wout_predicted_labs,
        x_lab="TSNE Feature 1",
        y_lab="TSNE Feature 2",
        title_lab="TSNE Plot w/2 Components")

    # Finally, display the final result and save the result if specified
    # by the user.
    fig.show()
    if save_plot:
        plot_dir = os.path.join(
            SCRIPT_DIR, "../../visualizations/initial_clustering")

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

        fig.savefig("{}/{}".format(plot_dir, file_name), bbox_inches="tight")

    return to_return


def plotly_bar_chart(count_df: pd.DataFrame, args_dict: dict, cluster_id: int):
    """
    Purpose
    -------
    The purpose of this function is to

    Parameters
    ----------
    count_df : Pandas DataFrame
        This argument allows the user to specify
    args_dict : Dictionary
        This argument allows the user to specify

    Returns
    -------
    to_return :
        This function returns

    Raises
    ------
    ValueError
        This error is raised when

    References
    ----------
    1. https://plotly.com/python/bar-charts/
    2. https://plotly.com/python-api-reference/generated/plotly.express.bar
    """
    to_return = None

    # First, validate the input data.
    try:
        assert isinstance(count_df, pd.DataFrame)
    except AssertionError:
        err_msg = "The "

        print(err_msg)
        raise ValueError

    # Next, define necessary values that will be used later on.
    x_arg, y_arg = args_dict.get("x"), args_dict.get("y")
    text_arg = args_dict.get("text")
    is_for_subevents = "sub" in x_arg

    opacity_lvl = 0.65
    bar_color = "rgb(195, 62, 227)"
    plot_width = 1200
    plot_height = 700
    x_label_tilt = 45

    x_label = "Sub-Event Type Name" if is_for_subevents \
              else "Event Type Name"
    axes_label_dict = {x_arg : x_label,
                       y_arg : "Normalized Count"}
    plot_title = \
        "Sub-Event Types Bar Chart for Cluster {}".format(cluster_id) if is_for_subevents\
        else "Event Types Bar Chart for Cluster {}".format(cluster_id)

    # Now we can create the bar chart itself.
    bar_obj = px.bar(data_frame=count_df,
                     x=x_arg,
                     y=y_arg,
                     text=text_arg,
                     labels=axes_label_dict,
                     opacity=opacity_lvl,
                     width=plot_width,
                     height=plot_height)
    bar_obj.update_traces(marker_color=bar_color,
                          marker_line_color='rgb(0, 0, 0)',
                          marker_line_width=.75)
    bar_obj.update_layout(font={"family": "Times New Roman",
                                "size": 18,
                                "color": "black"},
                          title={"text": plot_title,
                                 "y": 0.965,
                                 "x": 0.5,
                                 "xanchor": "center",
                                 "yanchor": "top"},
                          xaxis_tickangle=x_label_tilt)

    to_return = bar_obj

    return to_return
