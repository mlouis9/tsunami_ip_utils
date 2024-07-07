import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
from .scatter_plot import InteractiveScatterLegend
from .pie_plot import InteractivePieLegend

# Style constants
GRAPH_STYLE = {
    'flex': '1',
    'minWidth': '800px',
    'height': '500px',
    'padding': '10px',
    'borderRight': '1px solid black',
    'borderBottom': '1px solid black',
    'borderTop': '0px',
    'borderLeft': '0px'
}

def create_app(external_stylesheets):
    return dash.Dash(__name__, external_stylesheets=external_stylesheets)

def create_column_headers(num_cols):
    return [html.Div(
        f'Application {i+1}', 
        style={
            'flex': '1', 
            'minWidth': '800px', 
            'textAlign': 'center', 
            'padding': '10px', 
            'borderRight': '1px solid black', 
            'borderBottom': '1px solid black', 
            'display': 'flex', 
            'alignItems': 'center', 
            'justifyContent': 'center'
        }
    ) for i in range(num_cols)]

def create_row_label(i):
    return html.Div(
        html.Span(
            f'Experiment {i+1}',
            style={
                'display': 'block',
                'overflow': 'visible',
                'transform': 'rotate(-90deg)',
                'transformOrigin': 'center',
                'whiteSpace': 'nowrap',
            }
        ), 
        style={
            'flex': 'none',
            'width': '50px', 
            'textAlign': 'center', 
            'marginRight': '0', 
            'padding': '10px', 
            'borderRight': '1px solid black', 
            'borderBottom': '1px solid black', 
            'display': 'flex', 
            'alignItems': 'center', 
            'justifyContent': 'center'
        }
    )

def create_plot_element(i, j, plot_object):
    if isinstance(plot_object, InteractiveScatterLegend):
        graph_id = f"interactive-scatter-{i}-{j}"
        return dcc.Graph(id=graph_id, figure=plot_object.fig, style=GRAPH_STYLE)
    elif isinstance(plot_object, InteractivePieLegend):
        with plot_object.app.test_client() as client:
            response = client.get('/')
            html_content = response.data.decode('utf-8')
            return html.Iframe(srcDoc=html_content, style=GRAPH_STYLE)
    else:
        return dcc.Graph(figure=plot_object, style=GRAPH_STYLE)

def create_update_figure_callback(app, graph_id, app_instance):
    @app.callback(
        Output(graph_id, 'figure'),
        Input(graph_id, 'restyleData'),
        State(graph_id, 'figure')
    )
    def update_figure_on_legend_click(restyleData, current_figure_state):
        if restyleData and 'visible' in restyleData[0]:
            current_fig = go.Figure(current_figure_state)

            # Get the index of the clicked trace
            clicked_trace_index = restyleData[1][0]

            # Get the name of the clicked trace
            clicked_trace_name = current_fig.data[clicked_trace_index].name

            # Update excluded isotopes based on the clicked trace
            if restyleData[0]['visible'][0] == 'legendonly' and clicked_trace_name not in app_instance.excluded_isotopes:
                app_instance.excluded_isotopes.append(clicked_trace_name)
            elif restyleData[0]['visible'][0] == True and clicked_trace_name in app_instance.excluded_isotopes:
                app_instance.excluded_isotopes.remove(clicked_trace_name)

            # Update DataFrame based on excluded isotopes
            updated_df = app_instance.df.copy()
            updated_df = updated_df[~updated_df['Isotope'].isin(app_instance.excluded_isotopes)]

            # Recalculate the regression and summary statistics
            app_instance.add_regression_and_stats(updated_df)

            # Update trace visibility based on excluded isotopes
            for trace in app_instance.fig.data:
                if trace.name in app_instance.excluded_isotopes:
                    trace.visible = 'legendonly'
                else:
                    trace.visible = True

            return app_instance.fig

        return dash.no_update

def generate_layout(app, rows):
    app.layout = html.Div([
        html.H1("Matrix of Plots", style={'textAlign': 'center', 'marginLeft': '121px'}),
        html.Div(rows, style={'display': 'flex', 'flexDirection': 'column', 'width': '100%', 'overflowX': 'auto'}),
        html.Script("""
        window.addEventListener('resize', function() {
            const graphs = Array.from(document.querySelectorAll('.js-plotly-plot'));
            graphs.forEach(graph => {
                Plotly.Plots.resize(graph);
            });
        });
        """)
    ])

def interactive_matrix_plot(plot_objects_array: np.ndarray):
    current_directory = Path(__file__).parent
    external_stylesheets = [str(current_directory / 'css' / 'matrix_plot.css')]
    app = create_app(external_stylesheets)

    num_rows = plot_objects_array.shape[0]
    num_cols = plot_objects_array.shape[1]

    column_headers = create_column_headers(num_cols)
    header_row = html.Div([html.Div('', style={'flex': 'none', 'width': '71px', 'borderBottom': '1px solid black'})] + column_headers, style={'display': 'flex'})

    rows = [header_row]
    for i in range(num_rows):
        row = [create_row_label(i)]
        for j in range(num_cols):
            plot_object = plot_objects_array[i, j]
            plot_element = create_plot_element(i, j, plot_object) if plot_object else html.Div('Plot not available', style=GRAPH_STYLE)
            row.append(plot_element)
            if isinstance(plot_object, InteractiveScatterLegend):
                create_update_figure_callback(app, f"interactive-scatter-{i}-{j}", plot_object)
        rows.append(html.Div(row, style={'display': 'flex'}))

    generate_layout(app, rows)
    return app