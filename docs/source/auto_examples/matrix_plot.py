"""
Placeholder
===========

This is a placeholder description
"""
from tsunami_ip_utils.viz import correlation_plot, matrix_plot, contribution_plot
from tsunami_ip_utils.integral_indices import get_uncertainty_contributions
import numpy as np

filenames = [ f'../3d-sphere/sphere_model_{i}.out' for i in range(1, 13) ]

indices = range(12)
application_filenames = [ filenames[index] for index in indices ]
experiment_filenames = [ filenames[index] for index in indices ]

isotope_total, isotope_reaction = get_uncertainty_contributions(application_filenames, experiment_filenames)
num_applications = len(isotope_reaction['application'])
num_experiments = len(isotope_reaction['experiment'])

# Construct plot matrix
plot_objects_array = np.empty( ( num_applications, num_experiments ), dtype=object )

for application_index in range(num_applications):
    for experiment_index in range(num_experiments):
        if experiment_index == application_index:
            plot_objects_array[application_index, experiment_index] = \
            contribution_plot(
                isotope_reaction['application'][application_index],
                plot_type='interactive_pie',
                integral_index_name='%Δk/k',
                interactive_legend=True,     
            )
        else:
            plot_objects_array[application_index, experiment_index] = \
            correlation_plot(
                isotope_reaction['application'][application_index], 
                isotope_reaction['experiment'][experiment_index], 
                plot_type='interactive_scatter',
                integral_index_name='%Δk/k', 
                plot_redundant_reactions=True, 
                interactive_legend=True
            )

# Now generate the matrix plot
fig = matrix_plot(plot_objects_array, 'interactive')
fig.save_state('results/matrix_plot_example.pkl')