from dash import html, register_page, dcc, get_app, State, callback, Output, Input
import dash_bootstrap_components as dbc
from data.data import get_projects, get_datepicker_dates, update_table, get_projects_table, get_inventory_instruments_number, get_projects_timeline
import pandas as pd
import dash_ag_grid as dag
from view.utils import create_gantt, create_heatmap, timeslots_for_projects, generate_instrument_availability, create_pivot_table_for_heatmap
from view.style import cell_style, tab_style, tabs_styles, tab_selected_style

register_page(__name__, path="/")  # Register the home page at the root path


def layout():
    projects_pure = get_projects()
    projects_table = get_projects_table()
    projects_timeline = get_projects_timeline()
    inventory_numbers = get_inventory_instruments_number()
    time_slots = timeslots_for_projects(projects_table)
    availability_table = generate_instrument_availability(inventory_numbers, projects_pure, time_slots)
    heatmap_data = create_pivot_table_for_heatmap(availability_table, 'Availability')
    return html.Div([
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id='dropdown-instruments-availability',
                        options=[
                            {'label': 'Availability', 'value': 'Availability'},
                            {'label': 'Occupation', 'value': 'Occupation'},
                        ],
                        value='Availability',  # Default value
                    ),
                    width=3,
                ),
            ]
        ),
        html.Hr(),
        html.Div(
            id="heatmap-container",
            children=[
                dcc.Graph(
                    figure=create_heatmap(heatmap_data, "Availability")
                ),
            ]
        ),
        html.Hr(),
        html.P("Filter based on:"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='dropdown-projects-date',
                                        options=[
                                            {'label': 'None', 'value': 'none'},
                                            {'label': 'Dates', 'value': 'option_dates'},
                                            #{'label': 'Date Range', 'value': 'date_range'}
                                        ],
                                        value='none',  # Default value
                                        placeholder="Select an option",
                                    ),
                                    width=3,
                                ),
                                dbc.Col(
                                    html.Div(id='dropdown-projects-date-content'),
                                    width=9,
                                ),
                            ]
                        )
                    ],
                    width=10
                ),
                dbc.Col(
                    dbc.Button(
                        "Apply", id="apply-date-filter", className="me-2", n_clicks=0, disabled=True
                    ),
                    width=2
                )
            ],
            align="center",
        ),
        html.Hr(),
        dbc.Row(
            id="custom-timeline",
            children=(
                dcc.Graph(
                    figure=create_gantt(
                        data=projects_timeline, 
                        parameter_name="Name",
                        start_column_name="pickup_date",
                        end_column_name="return_date",
                        color="Name",
                        labels={'Sensor_Type': 'Sensor Type'},
                    ),
                ),
            )
        )
    ],style={"flex": "1"})

@callback(Output('overview-tabs-content', 'children'),
              [Input('overview-tabs', 'value')])

def render_content(tab):
    projects_pure = get_projects()
    projects_table = get_projects_table()
    projects_timeline = get_projects_timeline()
    inventory_numbers = get_inventory_instruments_number()
    time_slots = timeslots_for_projects(projects_table)
    availability_table = generate_instrument_availability(inventory_numbers, projects_pure, time_slots)
    
    if tab == 'inventory-availability':
        heatmap_data = create_pivot_table_for_heatmap(availability_table, 'Availability')
        return html.Div(
            [
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id='dropdown-instruments-availability',
                                options=[
                                    {'label': 'Availability', 'value': 'Availability'},
                                    {'label': 'Occupation', 'value': 'Occupation'},
                                ],
                                value='Availability',  # Default value
                            ),
                            width=3,
                        ),
                    ]
                ),
                html.Hr(),
                html.Div(
                    id="heatmap-container",
                    children=[
                        dcc.Graph(
                            figure=create_heatmap(heatmap_data, "Availability")
                        ),
                    ]
                )
            ]
        )
    elif tab == 'projects-timeline':
        return html.Div(
            [
                html.Hr(),
                html.P("Filter based on:"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id='dropdown-projects-date',
                                                options=[
                                                    {'label': 'None', 'value': 'none'},
                                                    {'label': 'Dates', 'value': 'option_dates'},
                                                    #{'label': 'Date Range', 'value': 'date_range'}
                                                ],
                                                value='none',  # Default value
                                                placeholder="Select an option",
                                            ),
                                            width=3,
                                        ),
                                        dbc.Col(
                                            html.Div(id='dropdown-projects-date-content'),
                                            width=9,
                                        ),
                                    ]
                                )
                            ],
                            width=10
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Apply", id="apply-date-filter", className="me-2", n_clicks=0, disabled=True
                            ),
                            width=2
                        )
                    ],
                    align="center",
                ),
                html.Hr(),
                dbc.Row(
                    id="custom-timeline",
                    children=(
                        dcc.Graph(
                            figure=create_gantt(
                                data=projects_timeline, 
                                parameter_name="Name",
                                start_column_name="pickup_date",
                                end_column_name="return_date",
                                color="Name",
                                labels={'Sensor_Type': 'Sensor Type'},
                            ),
                        ),
                    )
                )
            ]
        )
    
