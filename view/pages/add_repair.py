# /pages/page2.py
from dash import html, register_page, callback, dcc
from dash.exceptions import PreventUpdate
import dash as dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components import Row, Col, Label, Input
from datetime import datetime
import pandas as pd
from data.data import get_inventory_instruments_number, add_to_table
register_page(__name__, path="/add-repair", name="Add repair")  # Register a page at /add-repair


layout = html.Div([
    dcc.Interval(id='interval_add_repair', interval=1, n_intervals=0, max_intervals=1),
    dbc.Form(
        dbc.Row(
            [
                dbc.Col(
                    children=(
                        [
                            html.H4("Add new repair"),
                            html.Hr(),
                            dbc.Row(
                                [
                                    dbc.Label("Instrument ID*", html_for="instrument-dropdown-repair", width=6),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id='instrument-dropdown-repair',
                                            options=[
                                                
                                            ],
                                            value=None,  # Default value
                                            placeholder="Select an option",
                                        ),
                                        width=6,
                                    )
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Number*", html_for="repair-number", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="number", id="repair-number", value=0
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Owner*", html_for="repair-owner", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="text", id="repair-owner", placeholder="Owner"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Status*", html_for="repair-status", width=6),
                                    dbc.Col(
                                        dbc.Input(
                                            type="text", id="repair-status", placeholder="Status"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("Description", html_for="repair-description", width=6),
                                    dbc.Col(
                                        dbc.Textarea(
                                            id="repair-description", placeholder="Description"
                                        ),
                                        width=6,
                                    ),
                                ],
                                className="mb-3 justify-content-between align-items-center",
                            ),
                            html.Hr(),
                            dbc.Row(
                                dbc.Col(dbc.Button("Submit", id="submit-form-repair", n_clicks=0, color="primary", disabled=True), width="auto"),
                                className="mb-3",
                            ),
                        ]
                    ),
                    width=8,
                    class_name="px-5 py-3"
                )
              
            ]
        )
    )
])

# Callback triggered automatically at app start
@callback(
    dash.Output('instrument-dropdown-repair', 'options'),
    [dash.Input('interval_add_repair', 'n_intervals')]
)
def update_content(n_intervals):
    if n_intervals == 0 or n_intervals == 1:
        instruments = get_inventory_instruments_number()  # Get the instruments DataFrame
        # Assuming instruments is a DataFrame with columns 'ID' and 'Number'
        options = [
            {'label': f"{Name} ({ID})", 'value': f"{ID}"}
            for ID, Number, Name in zip(instruments['ID'], instruments['Number_sum'], instruments['Instrument name'])
        ]
        return options  # Return the dynamically created rows with input fields
    else:
        return [{'label': 'No instrument to show :('}]

@callback(
    
    dash.Output('submit-form-repair', 'disabled'),
    [
        dash.Input('instrument-dropdown-repair', 'value'),
        dash.Input('repair-number', 'value'),
        dash.Input('repair-owner', 'value'),
        dash.Input('repair-status', 'value'),
    ],
)
def check_if_required_inputs_are_filledIn(selected_option, number, owner, status):
    if not selected_option or number == 0 or not owner or not status:
        return True
    return False

@callback(
    dash.Output('toast-store', 'data', allow_duplicate=True), 
    dash.Input('submit-form-repair', 'n_clicks'),
    dash.State('instrument-dropdown-repair', 'value'),   
    dash.State('repair-number', 'value'),
    dash.State('repair-owner', 'value'), 
    dash.State('repair-status', 'value'),
    dash.State('repair-description', 'value'),
    prevent_initial_call=True
)
def submit_form_repair(n_clicks, selected_option, number, owner, status, description):
    print("submit repair", n_clicks)
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    else:
        toast = {
            'is_open': False, 
            'message': '', 
            'header': 'Success', 
            'icon': 'success'
        }
        # Create the new inventory row
        repair_row = {
            'ID': selected_option,
            'Number': number,
            'Owner': owner,
            'Status': status,
            'Description': description
        }

        response = add_to_table(repair_row, "Inventory_Repair")
        if response["status"] == "success":
            # Show success message
            toast = {
                'is_open': True, 
                'message': 'Repair report created successfully!', 
                'header': 'Success', 
                'icon': 'success'
            }
        else:
            # Handle the error
            toast = { 
                'is_open': True, 
                'message': 'There is something wrong!', 
                'header': 'Failure', 
                'icon': 'failure'
            }
    return toast
   
   