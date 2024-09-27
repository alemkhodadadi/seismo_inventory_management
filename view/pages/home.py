from dash import html, register_page, dcc, get_app, State, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from data.data import get_projects, get_datepicker_dates, update_project, get_projects_table, get_inventory_instruments_number, get_projects_timeline
import pandas as pd
import dash_ag_grid as dag
from view.utils import create_gantt, create_heatmap, timeslots_for_projects, generate_instrument_availability

register_page(__name__, path="/")  # Register the home page at the root path

tabs_styles = {
    'height': '44px'
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

def layout():
    return html.Div([
        dcc.Tabs(
            value='table',
            id='projects-tabs',
            style=tabs_styles,
            children=[
                dcc.Tab(
                    label='Table', 
                    value='table', 
                    style=tab_style, 
                    selected_style=tab_selected_style
                ),
                dcc.Tab(
                    label='Inventory Availability', 
                    value='inventory-availability', 
                    style=tab_style, 
                    selected_style=tab_selected_style
                ),
                dcc.Tab(
                    label='Timeline (This Year)', 
                    value='timeline-this-year', 
                    style=tab_style, 
                    selected_style=tab_selected_style
                ),
            ]
        ),
        
        html.Div(id='projects-tabs-content')
        
    
    ],style={"flex": "1"})


@callback(Output('projects-tabs-content', 'children'),
              [Input('projects-tabs', 'value')])

def render_content(tab):
    
    projects_table = get_projects_table()
    projects_timeline = get_projects_timeline()
    inventory_numbers = get_inventory_instruments_number()
    print("get_inventory_instruments_number:",inventory_numbers)
    time_slots = timeslots_for_projects(projects_table)
    availability_table = generate_instrument_availability(inventory_numbers, projects_table, time_slots)
    print("availability_table results", availability_table)
    if tab == 'table':
        return html.Div(
            [
                html.Div(
                    [
                        html.Hr(),
                        html.Div([
                            dcc.Link(
                                dbc.Button(
                                    "Create Project", 
                                    color="primary",  # Bootstrap button style
                                    className="me-1"
                                ),
                                href="/create-project"  # Set the path for the navigation
                            ),
                            dbc.Button(
                                "Update Table",
                                id="update-table-button",
                                color="dark",  # Bootstrap button style
                                className="me-1",
                                disabled=True,
                                n_clicks=0
                            ),
                        ]),
                        html.Hr(),
                    ]
                ),
                dbc.Row([
                    dag.AgGrid(
                        id="table-projects-editable",
                        rowData=projects_table.to_dict("records"),
                        columnDefs=[{"field": i} for i in projects_table.columns],
                        defaultColDef={"filter": True, 'editable': True},
                        dashGridOptions={"pagination": True},
                        style={"minHeight":"800px"},
                    ),
                    dcc.Store(id='table-projects-editable-changes', data=[]),
                ])
            ]
        )
    elif tab == 'inventory-availability':
        return dcc.Graph(
            figure=create_heatmap(availability_table)
        ),
    elif tab == 'timeline-this-year':
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
    
@callback(
    Output('apply-date-filter', 'disabled'),
    [
        Input('start-date-picker', 'date'),
        Input('end-date-picker', 'date')
    ]
)
def make_apply_btn_active(start, end):
    return False


@callback(
    [
        Output('custom-timeline', 'children'),  # Second output
        Output('apply-date-filter', 'disabled', allow_duplicate=True)
    ],
    Input('apply-date-filter', 'n_clicks'),
    State('start-date-picker', 'date'),   # Get the value of the start date
    State('end-date-picker', 'date'),      # Get the value of the end date
    prevent_initial_call=True
    
)
def check_dates(n_clicks, from_date, to_date):
    print('apply clicked:')
    # Convert string dates to Timestamps
    start_period = pd.Timestamp(from_date)
    end_period = pd.Timestamp(to_date)

    # Assuming `get_projects_timeline()` returns a DataFrame
    projects_timeline = get_projects_timeline()

    # Ensure that pickup_date and return_date are in datetime format
    projects_timeline['pickup_date'] = pd.to_datetime(projects_timeline['pickup_date'])
    projects_timeline['return_date'] = pd.to_datetime(projects_timeline['return_date'])

    # Filter the DataFrame based on the date range
    projects_timeline = projects_timeline[
        (projects_timeline['pickup_date'] <= end_period) & 
        (projects_timeline['return_date'] >= start_period)
    ]

    return dcc.Graph(
        figure=create_gantt(
            data=projects_timeline, 
            parameter_name="Name", 
            start_column_name="pickup_date", 
            end_column_name="return_date",
            color="Name",
            labels={'Sensor_Type': 'Sensor Type'},
        ),
    ), True
    
    
@callback(
    Output('dropdown-projects-date-content', 'children'),
    [Input('dropdown-projects-date', 'value')]
)

def display_date_picker(selected_option):
    earliest_day, latest_day, today = get_datepicker_dates()
    if selected_option == 'none':
        return html.Div()  # No date picker if "None" is selected
    
    elif selected_option == 'option_dates':
        # Display two DatePickerSingle components for start and end date
        return html.Div(
            [
                html.Div(
                    [
                        html.Label("From: "),
                        dcc.DatePickerSingle(
                            min_date_allowed=earliest_day,
                            id='start-date-picker',
                            placeholder='From',
                            date='2024-07-01'
                        ),
                    ], style={'display': 'inline-block', 'margin-right': '20px'}
                ),
                
                html.Div(
                    [
                        html.Label("To: "),
                        dcc.DatePickerSingle(
                            max_date_allowed=latest_day,
                            id='end-date-picker',
                            placeholder='To',
                            date=latest_day
                        ),
                    ], style={'display': 'inline-block'}
                )
            ]
        )
    
    elif selected_option == 'date_range':
        # Display a DatePickerRange component
        return dcc.DatePickerRange(
            id='date-range-picker',
            start_date_placeholder_text='Start Date',
            end_date_placeholder_text='End Date'
        ) 

@callback(
    [
        Output('table-projects-editable-changes', 'data'),
        Output('update-table-button', 'disabled', allow_duplicate=True),
    ],
    Input('table-projects-editable', 'cellValueChanged'),
    State('table-projects-editable-changes', 'data'),
    prevent_initial_call=True
)
def track_table_changes(event, changes):
    print("ffffffftrack_table_changes")
    # If no change was detected, return the current data and keep the button disabled
    if event is None or len(event) == 0:
        return changes, True
    if len(event) == 1:
       event = event[0]
    # Extract the updated row from the event
    updated_row = event['data']  # The row that was updated
    row_id = int(event['rowId'])  # Assuming 'id' is a unique identifier
    change = {"rowIndex": row_id, "status": "update", "row":updated_row}
    changes.append(change)
    # We want to enable the button after a change is made
    button_disabled = False  # Enable the button once a change has been detected    
    # Return the updated data and set button state to enabled (button_disabled=False)
    return changes, button_disabled


@callback(
    [
        Output('toast-store', 'data', allow_duplicate=True),
        Output('update-table-button', 'disabled', allow_duplicate=True)
    ],
    Input('update-table-button', 'n_clicks'),
    State('table-projects-editable-changes', 'data'),
    prevent_initial_call=True
)
def update_table(n_clicks, changes):
    if n_clicks > 0:
        response = update_project(changes, "Projects")
        toast = {
            'is_open': False, 
            'message': '', 
            'header': 'Success :)', 
            'icon': 'success'
        }
        if response["status"] == "success":
            # Show success message
            toast = {
                'is_open': True, 
                'message': 'Table updated successfully!', 
                'header': 'Success :)', 
                'icon': 'success'
            }
            
        else:
            # Handle the error
            toast = {
                'is_open': True, 
                'message': 'There is something wrong!', 
                'header': 'Failure :(', 
                'icon': 'failure'
            }

        
        return toast, True
    