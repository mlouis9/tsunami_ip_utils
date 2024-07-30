"""
Matrix Plots
============
This example demonstrates the use of the :func:`tsunami_ip_utils.viz.viz.matrix_plot` function to generate a matrix of plots. 
This is useful for comparing multiple applications and experiments in a single figure.
"""

# %%
# Interactive Matrix Plots
# ------------------------
# Interactive matrix plots wrap several Plotly plots in an html grid that's served by a Dash app that allows users to interact
# with each of the individual plots. This is useful for comparing multiple applications and experiments in a single figure.
# Specifically, it is useful for viewing all combinations of a given set of SDF files in a single figure

# %%
# Matrix of Contribution Correlation Plots
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# The first type of (interactive) similarity plot that we will view in matrix form is the contribution correlation plot discussed
# in :ref:`sphx_glr_auto_examples_contribution_correlation_plot.py`. This shows the contribution correlation plot between all
# pairs of applications and experiments in a (symmetric) matrix. First we consider the case of a square matrix where the set
# of applications and experiments are the same.

from tsunami_ip_utils.viz.viz import matrix_plot
from tsunami_ip_utils.viz.plot_utils import generate_plot_objects_array_from_contributions
from tsunami_ip_utils.integral_indices import get_uncertainty_contributions
from paths import EXAMPLES

application_files = [ EXAMPLES / 'data' / 'example_sdfs' / 'MCT' / f'MIX-COMP-THERM-001-00{i}.sdf' for i in range(1,4) ]
experiment_files = application_files

# %%
# Now we need to get the uncertainty contributions for each experiment and each application using 
# :func:`tsunami_ip_utils.integral_indices.get_uncertainty_contributions` (described in 
# :ref:`sphx_glr_auto_examples_uncertainty_contributions.py`).

contributions_nuclide, contributions_nuclide_reaction = get_uncertainty_contributions(application_files, experiment_files)

# %%
# Nuclide-Wise Contributions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Now, the :func:`tsunami_ip_utils.viz.viz.matrix_plot` function needs a numpy array of plot objects to generate the matrix plot.
# We can generate this array using the :func:`tsunami_ip_utils.viz.plot_utils.generate_plot_objects_array_from_contributions` function.
# This function takes a dictionary of contributions and the name of the integral index, and returns a numpy array of plot objects
# that can be passed to the :func:`tsunami_ip_utils.viz.viz.matrix_plot` function.

plot_objects_array_nuclide = generate_plot_objects_array_from_contributions(contributions_nuclide, '(Δk/k)^2')

# %%
# Now the matrix plot can easily be generated

fig = matrix_plot(plot_objects_array_nuclide, plot_type='interactive')
fig.show()

# %%
# This plot is fully interactive. You can hold shift and scroll using the mousewheel to scroll horizontally, or just use the
# mousewheel alone to scroll vertically. Individual subfigures can also be saved by clicking the camera icon in the top right,
# or the entire plot can be saved by calling the ``to_image`` method on the figure object.

fig = matrix_plot(plot_objects_array_nuclide, plot_type='interactive')
fig.to_image( EXAMPLES / '_static' / 'matrix_plot.png' )

# sphinx_gallery_thumbnail_path = '../../examples/_static/matrix_plot.png'

# %%
# Note if the default, nondescriptive labels aren't preferred, an arbitrary dictionary of labels for the applications and
# experiments may be passed instead. Perhaps the most useful is the SDF file names.

labels = {
    'applications': [ application_file.name for application_file in application_files ],
    'experiments': [ experiment_file.name for experiment_file in experiment_files ],
}
fig = matrix_plot(plot_objects_array_nuclide, plot_type='interactive', labels=labels)
fig.show()

# %% 
# Changing the Diagonal Plot Type
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# On the diagonals, where the application and experiment are the same, the plot is a pie chart of contributions to the
# nuclear-data indcued uncertainty, as shown in :ref:`sphx_glr_auto_examples_visualizing_contributions.py`. However, other
# types of plots, such as static bar plots can be used instead. This is done by specifying the ``diagonal_type`` in 
# the :func:`tsunami_ip_utils.viz.plot_utils.generate_plot_objects_array_from_contributions` function. Note that any plot type
# available in :func:`tsunami_ip_utils.viz.viz.contribution_plot` can be used.

# %%
# Static Pie Chart Diagonals
# """"""""""""""""""""""""""
# For a static pie chart, the ``diagonal_type`` should be set to ``'pie'``

plot_objects_array_nuclide = generate_plot_objects_array_from_contributions(
    contributions_nuclide, 
    '(Δk/k)^2', 
    diagonal_type='pie'
)
fig = matrix_plot(plot_objects_array_nuclide, plot_type='interactive', labels=labels)
fig.show()

# %%
# Static Bar Chart Diagonals
# """"""""""""""""""""""""""
# For a static pie chart, the ``diagonal_type`` should be set to ``'bar'``

plot_objects_array_nuclide = generate_plot_objects_array_from_contributions(
    contributions_nuclide, 
    '(Δk/k)^2', 
    diagonal_type='bar'
)
fig = matrix_plot(plot_objects_array_nuclide, plot_type='interactive', labels=labels)
fig.show()

# test test

# %%
# Matrix of Perturbation Correlation Plots
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

from tsunami_ip_utils.viz.plot_utils import generate_plot_objects_array_from_perturbations

# %%
# Static Matrix Plots
# -------------------
# Static matrix plots are used for creating an analogous figure using static matplotlib plots, so that it can be saved as a
# static image. This is useful for creating publication-quality figures. This option is currently not implemented.

# %%
# Non-Square Matrices
# -------------------

# %%
# Matrices with Different Sets of Applications and Experiments
# ------------------------------------------------------------